from __future__ import annotations

import logging
from datetime import datetime, timedelta
from time import perf_counter
from typing import Dict, List, Tuple

import pytz

from daily_transit.aspect_detection import AspectEvent
from daily_transit.ayanamsa import get_ayanamsa_offset
from daily_transit.config import GeneratorConfig
from daily_transit.cycles.engine_factory import get_cycle_detection_engine
from daily_transit.ics_builder import (
    build_aspect_event,
    build_compact_aspect_event,
    build_daily_summary,
    build_lunar_phase_event,
)
from daily_transit.ics_writer import fold_ical_lines, serialize_calendar
from daily_transit.lunar_phases import compute_lunar_phases
from daily_transit.zodiac_metadata import PlanetZodiacInfo, build_context_from_longitudes
from daily_transit.houses import assign_houses


def run_detection(eph, ts, config: GeneratorConfig, detection_end: datetime):
    skip_aspects = getattr(config.args, "skip_aspect_detection", False)
    aspects: List[AspectEvent] = []
    if skip_aspects:
        logging.info("Skipping aspect detection (--skip-aspect-detection)")
    else:
        engine = config.engine_factory(config.engine)
        logging.info(
            "Using aspect engine=%s; coarse=%s min refine=%s min orb=%.2f°",
            engine.name,
            config.coarse_step_mins,
            config.refine_step_mins,
            config.orb,
        )
        aspects = engine.detect(eph, ts, config, detection_end)

    cycle_events = []
    cycle_engine = None
    if config.cycle_config:
        try:
            cycle_engine = get_cycle_detection_engine(config.cycle_config.engine)
            logging.info(
                "Using cycle engine=%s; types=%s; phase_angles=%s; ingress_signs=%s",
                cycle_engine.name,
                ",".join(config.cycle_config.cycle_types or []),
                ",".join(str(a) for a in (config.cycle_config.phase_angles or [])),
                ",".join(config.cycle_config.ingress_signs or []),
            )
        except ValueError as exc:
            logging.error(str(exc))
            cycle_engine = None

    if cycle_engine is not None:
        cycle_events = cycle_engine.detect(eph, ts, config, detection_end)
        logging.info("Detected %s cycle events.", len(cycle_events))

    logging.info("Detected %s aspect events within orb %.2f°.", len(aspects), config.orb)
    return aspects, cycle_events


def build_events(
    eph,
    ts,
    config: GeneratorConfig,
    aspects: List[AspectEvent],
    cycle_events: List,
):
    collected_events: List = []
    zodiac_context_cache: Dict[datetime, Dict[str, PlanetZodiacInfo]] = {}

    if not config.args.no_aspects:
        window_start = config.start_date
        exclusive_cutoff = config.end_date + timedelta(days=1)
        inclusive_cutoff = exclusive_cutoff - timedelta(seconds=1)
        for ev in aspects:
            if ev.time < window_start:
                continue
            if config.inclusive_end:
                if ev.time > inclusive_cutoff:
                    continue
            else:
                if ev.time >= exclusive_cutoff:
                    continue
            context = zodiac_context_cache.get(ev.time)
            if context is None:
                offset = get_ayanamsa_offset(ev.time, config.ayanamsa)
                if config.verbose:
                    logging.debug(
                        "Ayanamsa %s offset=%.6f° at %s", config.ayanamsa, offset, ev.time.isoformat()
                    )
                longitudes = config.compute_body_longitudes_fn(
                    eph,
                    ts,
                    ev.time,
                    config.planets,
                    ayanamsa_offset=offset,
                )
                raw_longitudes = config.compute_body_longitudes_fn(
                    eph,
                    ts,
                    ev.time,
                    config.planets,
                    ayanamsa_offset=0.0,
                )
                houses_map = {}
                if config.latitude is not None and config.longitude is not None:
                    house_result = config.assign_houses_fn(
                        ev.time,
                        longitudes,
                        latitude=config.latitude,
                        longitude=config.longitude,
                        elevation_m=config.elevation_m,
                        prefer_system='placidus',
                    )
                    houses_map = house_result.houses
                    if house_result.fallback and config.verbose:
                        logging.warning(
                            "House fallback used (%s) at %s", house_result.reason, ev.time.isoformat()
                        )
                context = build_context_from_longitudes(
                    longitudes,
                    raw_longitudes=raw_longitudes,
                    ayanamsa_name=config.ayanamsa,
                    houses=houses_map,
                )
                zodiac_context_cache[ev.time] = context
            if config.mode == 'compact':
                collected_events.append(
                    build_compact_aspect_event(
                        ev,
                        config.timezone,
                        config.planets,
                        context,
                        precision_deg=config.precision_deg,
                        precision_time=config.precision_time,
                        ascii_only=config.ascii_only,
                    )
                )
            else:
                collected_events.append(
                    build_aspect_event(
                        ev,
                        config.timezone,
                        config.status,
                        config.thunderbird_friendly,
                        config.planets,
                        config.aspect_meanings,
                        config.interpretation_mode,
                        config.ascii_only,
                        ayanamsa_offset=get_ayanamsa_offset(ev.time, config.ayanamsa),
                        zodiac_context=context,
                        show_debug_ayanamsa=(config.verbose or config.timing_debug),
                    )
                )

    if config.args.daily_summary:
        current = config.start_date
        while current <= config.end_date:
            aspects_today = [a for a in aspects if a.time.date() == current.date()]
            offset = get_ayanamsa_offset(current, config.ayanamsa)
            if config.verbose:
                logging.debug(
                    "Ayanamsa %s offset=%.6f° at %s", config.ayanamsa, offset, current.isoformat()
                )
            raw_longitudes = config.compute_body_longitudes_fn(
                eph,
                ts,
                current,
                config.planets,
                ayanamsa_offset=0.0,
            )
            collected_events.append(
                build_daily_summary(
                    current,
                    config.timezone,
                    eph,
                    ts,
                    aspects_today,
                    config.status,
                    config.thunderbird_friendly,
                    config.planets,
                    config.aspect_meanings,
                    config.interpretation_mode,
                    config.ascii_only,
                    ayanamsa_offset=offset,
                )
            )
            current += timedelta(days=1)

    if config.include_lunar_phases:
        lunar_phase_events = compute_lunar_phases(
            eph,
            ts,
            config.start_date,
            config.end_date,
        )
        logging.info("Detected %s lunar phase events in range.", len(lunar_phase_events))
        for phase_event in lunar_phase_events:
            collected_events.append(
                build_lunar_phase_event(
                    phase_event,
                    config.timezone,
                    config.status,
                    config.thunderbird_friendly,
                    config.ascii_only,
                )
            )

    if cycle_events:
        cycle_ics_events = config.build_cycle_events(
            cycle_events,
            config.timezone,
            config.status,
            config.thunderbird_friendly,
            ascii_only=config.ascii_only,
        )
        collected_events.extend(cycle_ics_events)

    collected_events.sort(key=config.event_sort_key)
    return collected_events


def write_calendar(events: List, product_id: str) -> str:
    raw_calendar = serialize_calendar(events, product_id)
    return fold_ical_lines(raw_calendar)