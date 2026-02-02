from daily_transit.cycles.step_tables import (
    ingress_step_minutes,
    ingress_step_minutes_with_overrides,
    synodic_pair_key,
    synodic_pair_step_minutes,
    synodic_pair_step_minutes_with_overrides,
)


def test_ingress_step_table_classes():
    assert ingress_step_minutes("Moon") == 10
    assert ingress_step_minutes("Mercury") == 30
    assert ingress_step_minutes("Venus") == 30
    assert ingress_step_minutes("Sun") == 60
    assert ingress_step_minutes("Mars") == 60
    assert ingress_step_minutes("Jupiter") == 120
    assert ingress_step_minutes("Saturn") == 120
    assert ingress_step_minutes("Uranus") == 240
    assert ingress_step_minutes("Neptune") == 240
    assert ingress_step_minutes("Pluto") == 240
    assert ingress_step_minutes("Chiron") == 240
    assert ingress_step_minutes("Unknown") == 120


def test_synodic_pair_step_table_classes():
    assert synodic_pair_step_minutes("Moon", "Mars") == 15
    assert synodic_pair_step_minutes("Mercury", "Mars") == 45
    assert synodic_pair_step_minutes("Venus", "Neptune") == 45
    assert synodic_pair_step_minutes("Jupiter", "Saturn") == 240
    assert synodic_pair_step_minutes("Uranus", "Pluto") == 240
    assert synodic_pair_step_minutes("Sun", "Mars") == 90


def test_ingress_step_overrides():
    overrides = {"Moon": 5, "Mercury": 20}
    assert ingress_step_minutes_with_overrides("Moon", overrides) == 5
    assert ingress_step_minutes_with_overrides("Mercury", overrides) == 20
    assert ingress_step_minutes_with_overrides("Venus", overrides) == ingress_step_minutes("Venus")


def test_synodic_pair_step_overrides():
    overrides = {synodic_pair_key("Sun", "Mars"): 30}
    assert synodic_pair_step_minutes_with_overrides("Sun", "Mars", overrides) == 30
    assert synodic_pair_step_minutes_with_overrides("Mars", "Sun", overrides) == 30
    assert synodic_pair_step_minutes_with_overrides("Moon", "Mars", overrides) == 15
