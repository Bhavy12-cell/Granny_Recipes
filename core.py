import json, os, re,  time
from google import genai
from groq import Groq

gem = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

GEMMA = "gemma-4-31b-it"# AI Studio mein dekh lo ki Gemma ka exact naam kya hai

def transcribe(path, language=None):
    with open(path, "rb") as f:
        kwargs = dict(file=(os.path.basename(path), f.read()), model="whisper-large-v3")
        if language:
            kwargs["language"] = language
        r = groq.audio.transcriptions.create(**kwargs)
    return r.text, language or "auto"

SYSTEM = """You turn a spoken family recipe transcript into a structured recipe.
Rules:
- Use ONLY information in the transcript. Never invent ingredients or amounts.
- If an amount is vague (like 'thoda sa' or 'a pinch'), keep the speaker's wording.
- Keep the original language of the speaker. Do not translate.
- Fix obvious speech-to-text mistakes only when clearly wrong.
- Reply with ONLY a JSON object, no other text, with keys: title,
  ingredients (list of strings), steps (list of strings),
  tips (list of strings), story (short personal remark, else "")."""

GEMMA_MODELS = ["gemma-4-31b-it", "gemma-4-26b-a4b-it"]

def to_recipe(transcript):
    prompt = SYSTEM + "\n\nTranscript:\n" + transcript
    last_err = None
    for model in GEMMA_MODELS:          # pehle bada model, phir chhota
        for attempt in range(3):        # har model ko 3 baar try karo
            try:
                r = gem.models.generate_content(model=model, contents=prompt)
                text = r.text
                start, end = text.find("{"), text.rfind("}")
                return json.loads(text[start:end + 1])
            except Exception as e:
                last_err = e
                time.sleep(2 * (attempt + 1))
    raise last_err