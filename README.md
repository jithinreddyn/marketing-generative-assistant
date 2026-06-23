# Generative Media Marketing Assistant - Prudential Health

A brand-aware AI media tool for **Prudential sHealth Insurance Limited**. Describe any media idea in plain language — photo, video, animation, mascot, campaign, social post — and get back a brand-aligned creative brief plus a generated image or video, all in Prudential's visual world.

---

## How it works

1. **You describe any idea** — as rough or detailed as you like
2. **Gemini** (acting as a senior creative director who has internalised the Prudential brand) writes a natural, warm creative brief
3. **Pollinations.AI** generates the image (FLUX) or video (Wan / Seedance / Nova-Reel) — free, no extra key needed

---

## Setup

### Requirements

- Python 3.10+
- A free Gemini API key from [aistudio.google.com](https://aistudio.google.com)

### Install

```bash
pip install streamlit google-generativeai requests Pillow
```

### Run

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501` in your browser. Paste your Gemini API key in the expander at the top.

> **Windows note:** If `streamlit` isn't recognised as a command, always use `python -m streamlit run app.py`.

---

## Example prompts to try

| Idea | What you get |
|---|---|
| `A dancing cat in a red scarf celebrating a health checkup. Bhangra energy, warm and Indian.` | Animation brief + video |
| `A grandmother teaching her granddaughter yoga in a bright Indian kitchen on a Sunday morning.` | Photo brief + image |
| `A Diwali reel — family lighting diyas, each one representing a health goal for the year.` | Video brief + video |
| `A working professional sneaking in a 10-minute walk during lunch break in Mumbai. Relatable, a little funny.` | Reel brief + video |
| `World Heart Day — montage of everyday heart-healthy moments. Old couple on an evening walk. Kid choosing fruit over chips.` | Video brief + video |
| `A LinkedIn post visual — someone journaling on a balcony with chai. Soft morning light. Mental health awareness.` | Image brief + image |

---

## Video models

Available via the **Video generation options** expander before you generate:

| Model | Best for |
|---|---|
| `wan` | General scenes, good quality (default) |
| `wan-fast` | Fastest — try this if generation times out |
| `seedance` | Smooth motion, characters, animation feel |
| `nova-reel` | Longer clips |

Video generation takes **60–120 seconds**. If it times out, the image prompt is shown — paste it at [pollinations.ai](https://pollinations.ai) or switch to `wan-fast`.

---

## Brand identity baked in

The Gemini system prompt encodes the full Prudential brand so every output automatically reflects:

- **Prudential Red** `#C8102E` — present in every scene naturally (a scarf, a banner, a doorframe)
- **Warm lighting** — golden hour or soft indoor; never harsh studio white
- **Real Indian faces** — multi-generational, genuine expressions, inclusive of Tier 2/3 India
- **The PruWay values** — customer-first warmth living in the subtext
- **Voice** — plain, warm, never jargony; celebrates everyday health wins
- **Legal safety** — never promises specific policy terms (IRDAI approval in process)

---

## Files

```
app.py              Main Streamlit application
requirements.txt    Python dependencies
README.md           This file
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `google-generativeai` | Gemini 2.0 Flash Lite (brand brief generation) |
| `requests` | Pollinations.AI API calls |
| `Pillow` | Image handling and display |

Image and video generation is powered by [Pollinations.AI](https://pollinations.ai) — free, no API key required.

---

