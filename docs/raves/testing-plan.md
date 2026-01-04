# Raves Testing Plan

## Unit Tests
- Interpretations: mode="raves" uses structured guidance; fallback path when aspect missing; summary trimming obeyed; planet themes switched for mode; optional extras do not break output.
- ICS builder: description includes rave copy; pair insight present; planet profiles use rave tones (element/modality/sign) when context available; "Rave Extras" section renders when extras are provided and is omitted when absent.
- Validator: strict mode fails on crafted bad dict (missing key, bad severity, long summary, bad extras); passes on minimal good fixture.

## Fixtures
- Minimal guidance fixture with one major aspect filled to assert structured mode use (with and without extras).
- Crafted invalid entries for validator failure cases (bad severity, long summary, empty extras field).
- Aspect event sample for ICS builder description checks including extras block.

## Coverage Goals
- Exercise both major and minor aspect paths
- Verify default_pair_message fallback when no override
- Ensure interpretation_mode propagation to profiles
- Validate extras rendering and omission behavior

## Test Files
- tests/test_raves_interpretations.py
- tests/test_raves_ics_builder.py (or extend existing ICS builder tests)
- tests/test_validate_raves_dicts.py (optional wrapper for validator invocation)
