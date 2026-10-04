import json, re, time, html, tempfile, pathlib
import streamlit as st
from core import transcribe, to_recipe

RECIPES = pathlib.Path("recipes")
RECIPES.mkdir(exist_ok=True)

st.set_page_config(page_title="Nani's Recipe Book", page_icon="🍲", layout="centered")

# ---------- STYLE ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&display=swap');

html, body, [class*="css"], .stApp { font-family: 'Baloo 2', 'Segoe UI', sans-serif; }

.stApp {
  background: linear-gradient(135deg, #fff1eb 0%, #ffe3f1 40%, #e3f6ff 100%);
}
#MainMenu, footer, header {visibility: hidden;}

.hero {
  background: linear-gradient(120deg, #ff9a3c, #ff5f6d, #c850c0);
  border-radius: 28px; padding: 28px 24px; text-align: center; color: white;
  box-shadow: 0 10px 30px rgba(255, 95, 109, 0.35); margin-bottom: 18px;
}
.hero h1 { color: white; font-size: 2.6rem; margin: 0; font-weight: 800; }
.hero p { font-size: 1.15rem; margin: 6px 0 10px 0; opacity: .95; }
.hero .emojis { font-size: 2.2rem; letter-spacing: 8px; }

/* Tabs */
button[data-baseweb="tab"] { font-size: 1.1rem; font-weight: 700; }
button[data-baseweb="tab"][aria-selected="true"] { color: #ff5f6d; }

/* Buttons */
div.stButton > button {
  background: linear-gradient(90deg, #ff9a3c, #ff5f6d);
  color: white; border: none; border-radius: 999px;
  padding: 10px 26px; font-weight: 700; font-size: 1.05rem;
  box-shadow: 0 6px 16px rgba(255, 95, 109, 0.3); transition: transform .15s;
}
div.stButton > button:hover { transform: scale(1.05); color: white; }

/* Upload box and text area */
[data-testid="stFileUploader"] section {
  background: rgba(255,255,255,0.7); border: 2px dashed #ff9a3c; border-radius: 20px;
}
textarea { border-radius: 16px !important; border: 2px solid #ffb3c6 !important; }

/* Recipe card */
.card {
  background: white; border-radius: 24px; padding: 22px; margin: 14px 0;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08); border-top: 8px solid #ff5f6d;
}
.card h2 { margin: 0 0 6px 0; color: #c2185b; font-size: 1.8rem; }
.story { background: #fff6d6; border-radius: 14px; padding: 10px 14px; margin: 8px 0; color: #7a5b00; font-style: italic; }
.sec { font-weight: 800; font-size: 1.2rem; margin: 14px 0 6px 0; color: #2b2b2b; }
.chip {
  display: inline-block; padding: 6px 14px; margin: 4px 6px 4px 0; border-radius: 999px;
  color: white; font-weight: 600; font-size: .98rem;
}
.step { display: flex; gap: 12px; align-items: flex-start; margin: 8px 0; color: #2b2b2b; }
.num {
  min-width: 32px; height: 32px; border-radius: 50%; color: white; font-weight: 800;
  background: linear-gradient(135deg, #36d1dc, #5b86e5); display: flex;
  align-items: center; justify-content: center;
}
.tip { background: #e6fff3; border-left: 6px solid #2ecc71; border-radius: 10px; padding: 8px 12px; margin: 6px 0; color: #145a32; }
</style>
""", unsafe_allow_html=True)

COLORS = ["#ff6b6b", "#ff9f43", "#feca57", "#1dd1a1", "#48dbfb", "#5f27cd", "#ff6bcb", "#10ac84"]

def recipe_card(r):
    e = lambda x: html.escape(str(x))
    parts = ['<div class="card">', f'<h2>🍽️ {e(r.get("title", "Untitled"))}</h2>']
    if r.get("story"):
        parts.append(f'<div class="story">💬 {e(r["story"])}</div>')
    parts.append('<div class="sec">🥕 Ingredients</div>')
    for i, ing in enumerate(r.get("ingredients", [])):
        parts.append(f'<span class="chip" style="background:{COLORS[i % len(COLORS)]}">{e(ing)}</span>')
    parts.append('<div class="sec">👩‍🍳 Steps</div>')
    for n, s in enumerate(r.get("steps", []), 1):
        parts.append(f'<div class="step"><div class="num">{n}</div><div>{e(s)}</div></div>')
    if r.get("tips"):
        parts.append('<div class="sec">💡 Tips</div>')
        for t in r["tips"]:
            parts.append(f'<div class="tip">{e(t)}</div>')
    parts.append('</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div class="hero">
  <div class="emojis">🍲 🥘 🍛 🫓 🍵</div>
  <h1>Nani's Recipe Book</h1>
  <p>Nani ki awaaz se likhi hui recipes, hamesha ke liye ❤️</p>
</div>
""", unsafe_allow_html=True)

# Optional: Nani ki photo. Project folder mein nani.jpg rakho to yahan dikhegi
if pathlib.Path("nani.jpg").exists():
    st.image("nani.jpg", width=160, caption="Nani ❤️")

tab1, tab2 = st.tabs(["🎙️ Add a recipe", "📖 Our recipe book"])

# ---------- TAB 1 ----------
with tab1:
    audio = st.file_uploader("🎧 Voice memo upload karo", type=["mp3", "m4a", "wav", "ogg", "opus"])
    lang = st.selectbox("🗣️ Language", ["Auto", "Hindi", "English"])
    if audio and st.button("✨ Transcribe"):
        with tempfile.NamedTemporaryFile(suffix=pathlib.Path(audio.name).suffix, delete=False) as f:
            f.write(audio.read())
        code = {"Auto": None, "Hindi": "hi", "English": "en"}[lang]
        with st.spinner("Sun rahe hain... 👂"):
            st.session_state.text, _ = transcribe(f.name, code)
        st.session_state.pop("recipe", None)

    if "text" in st.session_state:
        st.session_state.text = st.text_area("📝 Transcript (galti ho to theek karo)",
                                             st.session_state.text, height=180)
        if st.button("🍳 Make recipe"):
            with st.spinner("Recipe likh rahe hain... ✍️"):
                st.session_state.recipe = to_recipe(st.session_state.text)

    if "recipe" in st.session_state:
        r = st.session_state.recipe
        recipe_card(r)
        if st.button("💾 Save to recipe book"):
            slug = re.sub(r"\W+", "-", r.get("title", "recipe")).strip("-").lower() or "recipe"
            path = RECIPES / f"{slug}-{int(time.time())}.json"
            path.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
            st.balloons()
            st.success("Recipe book mein save ho gayi! 🎉")

# ---------- TAB 2 ----------
with tab2:
    files = sorted(RECIPES.glob("*.json"))
    if not files:
        st.info("Abhi koi recipe nahi hai. Pehle tab mein ek add karo 🍲")
    else:
        st.markdown(f"### 📚 {len(files)} recipes")
    for p in files:
        recipe_card(json.loads(p.read_text(encoding="utf-8")))