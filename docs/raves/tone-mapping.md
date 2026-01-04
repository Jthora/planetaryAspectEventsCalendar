# Raves Tone Mapping (Elements, Modalities, Signs)

## Element Tones
- Fire: high-octane hype, peak drops, sweat and lasers
- Earth: grounded grooves, steady four-on-the-floor, reliable logistics
- Air: social buzz, lightfooted house, meetups and chatter
- Water: fluid flow, emotive melodies, immersive lights and feels

## Modality Tones
- Cardinal: kickoff energy, bold openers, set the tone early
- Fixed: locked-in groove, enduring stamina, consistent vibe
- Mutable: genre-blend, flexible pacing, spontaneous shifts

## Sign Tones (short, profile-friendly)
- Aries: charged, upfront, fast breaks
- Taurus: lush, sensual, steady beats
- Gemini: chatty, mixed genres, quick pivots
- Cancer: cozy, emotive, nurturing spaces
- Leo: showy, expressive, mainstage sparkle
- Virgo: precise, clean mixes, dialed logistics
- Libra: balanced, stylish, social harmony
- Scorpio: intense, shadowy, bass-heavy
- Sagittarius: expansive, adventurous, festival roam
- Capricorn: structured, elevated production, VIP control
- Aquarius: experimental, techy, unexpected twists
- Pisces: dreamy, trancey, dissolving edges

## Implementation Notes
- Add element_raves_tone, modality_raves_tone, sign_raves_tone in zodiac_metadata.
- In ics_builder planet profiles, select tone helpers based on interpretation_mode (raves vs business).
- Keep lines concise for profile bullets.
- Define a per-sign genre/theme hint table (7-ish entries per sign) to bias music_genre/music_subgenre/music_theme defaults; align with element/modality and sign tones.
- Map music dimensions to tones: speed (slow/mid/fast/peak), tone (uplifting/moody/dark/euphoric/hypnotic/gritty/playful), vibe (chill/groovy/communal/high-energy/rowdy/floaty).
