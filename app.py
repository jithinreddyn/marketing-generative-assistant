"""
Prudential Health India — Generative Media Assistant
Prompt → Gemini crafts brand-aligned brief → Pollinations.AI generates image OR video (free, no key).
"""

import streamlit as st
import google.generativeai as genai
import requests
import urllib.parse
from datetime import datetime
from PIL import Image
import io
import tempfile
import os

st.set_page_config(
    page_title="Prudential Health India — Media Assistant",
    page_icon="🔴",
    layout="centered",
)

BRAND = {
    "red":       "#C8102E",
    "dark_red":  "#9B0D22",
    "white":     "#FFFFFF",
    "off_white": "#F8F4F4",
    "charcoal":  "#1A1A1A",
    "grey":      "#6B6B6B",
    "gold":      "#C89B20",
    "light":     "#F0EBEB",
}

SYSTEM = """
You are the creative mind behind Prudential Health India's media — a joint venture between
Prudential plc (175+ years of global legacy) and HCL Group. You have completely internalised
this brand. When someone gives you any idea — a photo concept, a video, an animation, a mascot,
a campaign, a social post, a script, anything — you respond as a senior creative director
who breathes this brand every day.

You respond naturally and creatively — But in a brief and short way, like a talented creative director would brief
a photographer or animator over a quick call.

THE BRAND IN YOUR BONES:

FEEL
  Warm. Hopeful. Never clinical. Never corporate. Never scary. Never cold.
  India lives here — its culture, its wildlife, its everyday moments.

COLOURS (you think in these automatically)
  Prudential Red #C8102E — the heartbeat of everything
  White #FFFFFF — space, breath, clarity
  Charcoal #1A1A1A — grounded, real
  Gold #C89B20 — a touch of warmth, used lightly
  Never: neons, cold blues, garish anything

PEOPLE & PHOTOGRAPHY
  Real Indian faces. Multi-generational. Warm skin tones. Natural expressions.
  Grandmothers, toddlers, working professionals, small-town families — all belong here.
  Lighting is always warm — golden hour or soft indoor. Never harsh white studio.
  No stock-photo clichés. No stethoscopes on white. No pill piles.

VIDEO & ANIMATION
  Pacing is warm and familiar. Motion is smooth. Playful when fun, gentle when emotional.
  Music: acoustic, folk fusion, or upbeat-but-never-anxious.
  Brand red appears naturally — a scarf, a doorframe, a banner, a costume.

VOICE
  Tagline: "Partnering with you at every step"
  Mission: "For Every Life, For Every Future"
  Plain, warm, never jargony. Celebrates everyday health wins, not crisis moments.
  Never promises specific insurance terms (IRDAI approval is still in process).

VALUES — The PruWay (live in the subtext of everything)
  Customer is the compass. Entrepreneurial spirit. Succeed together.
  Respect and care. Deliver on commitments.

When someone gives you an idea, show them exactly what it looks like inside the
Prudential world. Make it feel alive and on-brand without them having to ask.

Always end your response with ONE of these two sections depending on the idea:

For photo/image ideas — end with:
**IMAGE PROMPT**
One detailed paragraph for FLUX image generation — warm lighting, Prudential red present,
real Indian feel, brand-perfect. No bullet points.

For video/animation/reel/motion ideas — end with:
**VIDEO PROMPT**
One detailed paragraph for AI video generation (Wan/Seedance/Veo) — warm, human pacing,
Prudential red in the scene, Indian context. No bullet points. Keep to 2-3 sentences max
since video models work better with concise prompts.

If the idea is ambiguous, default to IMAGE PROMPT.
"""

VIDEO_MODELS = {
    "wan (fast, good quality)": "wan",
    "wan-fast (fastest)": "wan-fast",
    "seedance (smooth motion)": "seedance",
    "nova-reel (longer clips)": "nova-reel",
}
IMAGE_MODELS = {
    "flux (high quality)": "flux",
    "seedream (detailed)": "seedream",
    "zimage (default)": "zimage",
}


def generate_image(prompt: str) -> Image.Image | None:
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&model=flux&nologo=true"
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            return Image.open(io.BytesIO(r.content))
    except Exception:
        pass
    return None


def generate_video(prompt: str, model: str = "wan", duration: int = 5) -> tuple[bytes | None, str]:
    """
    Calls Pollinations video generation.
    Returns (mp4_bytes, error_message).
    """
    encoded = urllib.parse.quote(prompt)
    # Pollinations video endpoint (gen.pollinations.ai)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?model={model}&width=854&height=480"
        f"&nologo=true&output=mp4"
    )
    try:
        r = requests.get(url, timeout=180, stream=False)
        ct = r.headers.get("content-type", "")
        if r.status_code != 200:
            return None, f"Server returned {r.status_code}"
        # Accept video/* or large binary (video won't declare content-type always)
        if "video" in ct or (r.content[:4] in (b'\x00\x00\x00\x18', b'\x00\x00\x00\x20',
                                                 b'ftyp', b'\x1a\x45\xdf\xa3')
                              or len(r.content) > 100_000):
            return r.content, ""
        # If we got an image back instead of video (model fallback)
        if "image" in ct:
            return None, "Model returned an image instead of video — try a different video model or rephrase your prompt."
        return None, f"Unexpected content type: {ct}"
    except requests.exceptions.Timeout:
        return None, "Generation timed out (>180s). Try wan-fast or a shorter prompt."
    except Exception as e:
        return None, str(e)


def extract_prompt(text: str) -> tuple[str, str, str]:
    """Returns (brief, prompt_text, prompt_type) where type is 'image' or 'video'."""
    for marker, kind in [("**VIDEO PROMPT**", "video"), ("**IMAGE PROMPT**", "image")]:
        if marker in text:
            idx = text.index(marker)
            return text[:idx].strip(), text[idx + len(marker):].strip(), kind
    return text.strip(), "", "image"


def get_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM,
    )


def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400;500;600&display=swap');
    .stApp {{ background:{BRAND['off_white']}; font-family:'Inter',sans-serif; }}
    .pru-header {{
        background: linear-gradient(130deg, {BRAND['red']} 0%, {BRAND['dark_red']} 100%);
        color:white; padding:1.6rem 2rem; border-radius:12px; margin-bottom:1.8rem;
        position:relative; overflow:hidden;
    }}
    .pru-header::after {{
        content:''; position:absolute; right:-30px; top:-30px;
        width:140px; height:140px; border-radius:50%; background:rgba(255,255,255,0.06);
    }}
    .pru-header h1 {{ font-family:'Playfair Display',serif; font-size:1.6rem; font-weight:700; margin:0 0 0.2rem; }}
    .pru-header p {{ margin:0; font-size:0.82rem; opacity:0.65; font-style:italic; }}
    .stTextArea textarea {{
        border:2px solid #e8dada !important; border-radius:10px !important;
        font-size:0.95rem !important; padding:1rem !important;
        background:{BRAND['white']} !important; color:{BRAND['charcoal']} !important;
    }}
    .stTextArea textarea:focus {{
        border-color:{BRAND['red']} !important;
        box-shadow:0 0 0 3px rgba(200,16,46,0.1) !important;
    }}
    .stButton > button {{
        background:{BRAND['red']} !important; color:white !important;
        border:none !important; border-radius:10px !important;
        font-weight:600 !important; font-size:1rem !important;
        padding:0.7rem 2rem !important; width:100% !important; transition:all 0.2s !important;
    }}
    .stButton > button:hover {{
        background:{BRAND['dark_red']} !important;
        transform:translateY(-1px) !important;
        box-shadow:0 6px 18px rgba(200,16,46,0.3) !important;
    }}
    .output-bubble {{
        background:{BRAND['white']}; border-radius:12px; padding:1.8rem 2rem;
        margin-top:1.2rem; box-shadow:0 2px 20px rgba(0,0,0,0.07);
        border-left:4px solid {BRAND['red']}; font-size:0.95rem;
        line-height:1.85; color:{BRAND['charcoal']}; white-space:pre-wrap;
    }}
    .gen-prompt-box {{
        background:#f9f4ff; border:1px dashed #b89fd4;
        border-radius:8px; padding:0.9rem 1.1rem;
        font-size:0.8rem; color:#4a3060; margin-top:0.8rem; line-height:1.6;
    }}
    .media-badge {{
        display:inline-flex; align-items:center; gap:0.4rem;
        background:{BRAND['charcoal']}; color:white; border-radius:20px;
        padding:0.25rem 0.8rem; font-size:0.72rem; font-weight:600;
        letter-spacing:0.04em; margin-bottom:0.8rem;
    }}
    .media-badge.video {{ background:#1a3a5c; }}
    .media-badge.image {{ background:{BRAND['red']}; }}
    .disclaimer {{
        background:#fffbee; border-left:3px solid {BRAND['gold']};
        border-radius:6px; padding:0.7rem 1rem;
        font-size:0.76rem; color:#6b5000; margin-top:1rem;
    }}
    .video-options {{
        background:{BRAND['white']}; border:1px solid #e8dada;
        border-radius:10px; padding:1rem 1.2rem; margin-bottom:1rem;
    }}
    .empty-state {{
        text-align:center; padding:3rem 1rem; color:{BRAND['grey']};
    }}
    .empty-state .icon {{ font-size:2.5rem; margin-bottom:0.8rem; }}
    .empty-state .title {{
        font-size:1rem; font-weight:600; color:{BRAND['charcoal']}; margin-bottom:0.4rem;
    }}
    .empty-state .sub {{ font-size:0.83rem; line-height:1.7; }}
    #MainMenu,footer,header {{ visibility:hidden; }}
    .block-container {{ max-width:760px; padding-top:1.5rem; }}
    </style>
    """, unsafe_allow_html=True)


for k, v in [("history", []), ("brief", None), ("media_bytes", None), ("video_bytes", None),
             ("media_type", None), ("gen_prompt", ""), ("api_key", ""), ("video_error", "")]:
    if k not in st.session_state:
        st.session_state[k] = v


def main():
    inject_css()

    st.markdown("""
    <div class='pru-header'>
      <h1>Prudential Health India</h1>
      <p>"Partnering with you at every step"</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚙️ Gemini API Key", expanded=not bool(st.session_state.api_key)):
        key_in = st.text_input("Key", type="password", value=st.session_state.api_key,
                               placeholder="AIza… — free at aistudio.google.com",
                               label_visibility="collapsed")
        if key_in:
            st.session_state.api_key = key_in

    st.markdown("<br>", unsafe_allow_html=True)

    prompt = st.text_area(
        "What's your idea?",
        placeholder=(
            "Describe anything freely.\n\n"
            "A dancing cat celebrating annual health checkups… "
            "a grandmother teaching her granddaughter yoga at sunrise… "
            "a 15-second Diwali reel… "
            "a family's morning wellness routine…"
        ),
        height=160,
    )

    # ── Video options (collapsible) ───────────────────────────────────────────
    with st.expander("🎬 Video generation options (if your idea is a video/reel/animation)"):
        st.markdown("<div class='video-options'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        video_model_label = c1.selectbox("Video model", list(VIDEO_MODELS.keys()), index=0)
        video_duration = c2.selectbox("Duration (seconds)", [4, 5, 6, 8, 10], index=1)
        st.caption("💡 `wan` and `wan-fast` work best for most ideas. `nova-reel` supports longer clips.")
        st.markdown("</div>", unsafe_allow_html=True)

    go = st.button("✨  Make it Prudential")

    if go:
        if not st.session_state.api_key:
            st.error("Add your Gemini API key above first.")
        elif not prompt.strip():
            st.warning("Type your idea first.")
        else:
            # Step 1 — Gemini writes the brief + generation prompt
            with st.spinner("Crafting your brand brief…"):
                try:
                    model = get_model(st.session_state.api_key)
                    raw = model.generate_content(prompt).text
                    brief, gen_prompt, prompt_type = extract_prompt(raw)
                    st.session_state.brief = brief
                    st.session_state.gen_prompt = gen_prompt
                    st.session_state.media_type = prompt_type
                    st.session_state.media_bytes = None
                    st.session_state.video_bytes = None
                    st.session_state.video_error = ""
                    st.session_state.history.insert(0, {
                        "prompt": prompt, "brief": brief,
                        "gen_prompt": gen_prompt, "kind": prompt_type,
                        "ts": datetime.now().strftime("%d %b, %H:%M"),
                    })
                except Exception as e:
                    st.error(f"Gemini error: {e}")
                    return

            # Step 2 — Always generate an image first (FLUX). For video ideas, also attempt video.
            if gen_prompt:
                with st.spinner("Generating image with FLUX via Pollinations.AI..."):
                    img = generate_image(gen_prompt)
                    if img:
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        st.session_state.media_bytes = buf.getvalue()
                if prompt_type == "video":
                    chosen_model = VIDEO_MODELS[video_model_label]
                    with st.spinner(f"Attempting video generation with {chosen_model}... (60-120s)"):
                        vid, err = generate_video(gen_prompt, model=chosen_model, duration=video_duration)
                        st.session_state.video_bytes = vid
                        st.session_state.video_error = err
                else:
                    st.session_state.video_bytes = None
                    st.session_state.video_error = ""

    # ── Output ────────────────────────────────────────────────────────────────
    if st.session_state.brief:
        kind = st.session_state.media_type or "image"
        badge_class = "video" if kind == "video" else "image"
        badge_icon = "🎬" if kind == "video" else "🖼️"
        badge_label = "VIDEO BRIEF" if kind == "video" else "IMAGE BRIEF"

        st.markdown(f"""
        <div class='media-badge {badge_class}'>
          {badge_icon} {badge_label} &nbsp;·&nbsp; Brand-aligned · Prudential Health India
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<div class='output-bubble'>{st.session_state.brief}</div>",
                    unsafe_allow_html=True)

        if st.session_state.gen_prompt:
            label = "🎬 Video prompt sent to Pollinations:" if kind == "video" else "🖼️ Image prompt sent to FLUX:"
            st.markdown(f"""
            <div class='gen-prompt-box'>
              <b>{label}</b><br>{st.session_state.gen_prompt}
            </div>""", unsafe_allow_html=True)

        # ── Rendered media ────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)

        # Always show the image
        if st.session_state.media_bytes:
            img = Image.open(io.BytesIO(st.session_state.media_bytes))
            st.image(img, use_container_width=True,
                     caption="Generated by FLUX via Pollinations.AI · Prudential brand-aligned")
            st.download_button(
                "⬇️ Download Image (.png)",
                data=st.session_state.media_bytes,
                file_name=f"prudential_image_{datetime.now().strftime('%Y%m%d_%H%M')}.png",
                mime="image/png",
                use_container_width=True,
            )

        # For video ideas — show video if it worked, else friendly message
        if kind == "video":
            vid_bytes = getattr(st.session_state, "video_bytes", None)
            if vid_bytes:
                st.markdown("<br>", unsafe_allow_html=True)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(vid_bytes)
                    tmp_path = tmp.name
                try:
                    st.video(tmp_path)
                except Exception:
                    pass
                finally:
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass
                st.download_button(
                    "⬇️ Download Video (.mp4)",
                    data=vid_bytes,
                    file_name=f"prudential_video_{datetime.now().strftime('%Y%m%d_%H%M')}.mp4",
                    mime="video/mp4",
                    use_container_width=True,
                )
            else:
                st.markdown(f"""
                <div style='background:#fff8f0;border-left:3px solid {BRAND["gold"]};
                            border-radius:8px;padding:0.9rem 1.1rem;margin-top:0.8rem;
                            font-size:0.85rem;color:#5a4200;'>
                  🎬 <b>Video could not be generated due to high demand — please try again later.</b><br>
                  <span style='font-size:0.78rem;'>The image above represents your concept.
                  You can also paste the prompt into
                  <a href='https://pollinations.ai' target='_blank'
                     style='color:{BRAND["red"]};'>pollinations.ai</a> directly.</span>
                </div>""", unsafe_allow_html=True)

        if "irdai" in (st.session_state.brief or "").lower() or \
           "insurance" in (st.session_state.brief or "").lower():
            st.markdown("""<div class='disclaimer'>
            Prudential HCL Health Insurance Limited has applied to IRDAI for registration
            as a Standalone Health Insurer; application under process.
            </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        c1.download_button("⬇️ Download Brief (.txt)",
            data=st.session_state.brief,
            file_name=f"prudential_brief_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain", use_container_width=True)
        if c2.button("✕ Clear", use_container_width=True):
            st.session_state.brief = None
            st.session_state.media_bytes = None
            st.session_state.gen_prompt = ""
            st.rerun()

    elif not go:
        st.markdown(f"""
        <div class='empty-state'>
          <div class='icon'>🎨</div>
          <div class='title'>Describe any media idea</div>
          <div class='sub'>
            Photo · Video · Reel · Animation · Mascot · Campaign · Social post<br>
            You get back the brand brief <i>and</i> a generated image or video —
            all in Prudential's world.
          </div>
          <div style='margin-top:1.2rem;display:flex;flex-wrap:wrap;gap:0.4rem;justify-content:center;'>
            {''.join([f"<span style='background:{BRAND['light']};color:{BRAND['red']};border-radius:20px;padding:0.2rem 0.7rem;font-size:0.75rem;font-weight:500;'>{t}</span>"
            for t in ["Dancing mascot 🐱", "Diwali reel 🪔", "Photo shoot 📸",
                       "Family wellness 🧘", "Instagram reel 📱", "Brand video 🎬"]])}
          </div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"📋 Recent ideas ({len(st.session_state.history)})"):
            for h in st.session_state.history[:6]:
                icon = "🎬" if h.get("kind") == "video" else "🖼️"
                st.markdown(f"""
                <div style='background:{BRAND["white"]};border-radius:8px;padding:0.8rem 1rem;
                            margin-bottom:0.5rem;border-left:3px solid {BRAND["red"]}55;font-size:0.85rem;'>
                  <span style='font-weight:600;color:{BRAND["charcoal"]};'>
                    {icon} {h["prompt"][:80]}{"…" if len(h["prompt"])>80 else ""}
                  </span><br>
                  <span style='font-size:0.72rem;color:{BRAND["grey"]};'>{h["ts"]}</span>
                </div>""", unsafe_allow_html=True)
            if st.button("Clear history"):
                st.session_state.history = []
                st.session_state.brief = None
                st.session_state.media_bytes = None
                st.rerun()

    st.markdown(f"""
    <div style='text-align:center;margin-top:3rem;padding-top:1rem;
                border-top:1px solid #e4d8d8;font-size:0.72rem;color:{BRAND["grey"]};'>
      Prudential HCL Health Insurance Limited · CIN: U65120MH2025FLC457866 · Internal use only<br>
      Image & video generation powered by
      <a href='https://pollinations.ai' style='color:{BRAND["red"]};text-decoration:none;'>Pollinations.AI</a>
      (FLUX · Wan · Seedance · Nova-Reel)
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()