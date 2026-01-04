# Raves Dictionary Contract

## Schema
- raves_aspect_guidance: {"major_aspects": {aspect: entry}, "minor_aspects": {aspect: entry}}
- Entry required keys: severity, headline, impact, action, watch, summary
- Entry optional extras (raves-only): music_genre, music_subgenre, music_theme, music_style, music_speed, music_tone, music_vibe, outfit_cue, social_mode, friend_making_risk, chaos_order, safety_flag, conflict_risk, crowd_profile
- Summary length: <= 120 characters after trim
- Optional fields, if present, must be non-empty and under length limits (e.g., 80–120 chars)
- Severity enum: Opportunity | Watch | High Risk | Info
- Non-empty strings required for required keys

## Coverage
- Aspects: every key in astrological_aspects["aspect_degrees"] present in a bucket
- Planets: DEFAULT_PLANETS plus North Node, South Node, Chiron covered in themes

## Pair Overrides
- Keys: tuple(sorted((planet_a, planet_b)))
- Provide overrides for high-traffic pairs; ensure default_pair_message is non-empty

## Fallback Behavior
- If headline/impact/action are blank, interpretation emits pending info copy
- Summary uses guidance summary, else headline/impact/action, else fallback

## Valid vs Invalid Examples
- Valid: severity in enum, all required keys filled, summary <= 120, optional extras either omitted or populated within length limits
- Invalid: missing required keys, empty strings, severity outside enum, summary too long, optional extras present but empty or overly long
