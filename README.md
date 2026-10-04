# 🍲 Nani's Recipe Book

Turn a family member's **voice memos into a written recipe book**.
Record a recipe in Hindi or English, and the app transcribes it, lets you fix
mistakes, and formats it into a clean recipe card.

Built for **[Granny]** for the
[Hacktoberfest Weekend Challenge: Build for a Friend](https://dev.to/challenges/hacktoberfest-weekend-2026-10-01).

## Why

[2-3 lines: kiske liye banaya, unki recipes kyun important hain.]

## How it works

```
Voice memo → Whisper large-v3 (Groq) → editable transcript → Gemma 4 → recipe JSON → recipe book
```

| Part | Tool |
|---|---|
| Speech to text | Whisper large-v3 (open-weight), hosted on Groq |
| Recipe formatting | Gemma 4 31B (open-weight), via Google AI Studio API |
| UI | Streamlit + custom CSS |
| Storage | Local JSON files in `recipes/` |

The prompt tells the model to use **only what was said**, keep vague amounts like
"thoda sa" exactly as spoken, and never translate. The app retries and falls
back to a second Gemma model if the API returns an error.

## Setup

**Requirements:** Python 3.10+, a free [Google AI Studio](https://aistudio.google.com) key
and a free [Groq](https://console.groq.com) key.

```bash
git clone https://github.com/[YOUR-USERNAME]/[REPO-NAME].git
cd [REPO-NAME]

python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

Set your API keys (PowerShell):

```powershell
$env:GEMINI_API_KEY="your-google-key"
$env:GROQ_API_KEY="your-groq-key"
```

Mac/Linux:

```bash
export GEMINI_API_KEY="your-google-key"
export GROQ_API_KEY="your-groq-key"
```

Run:

```bash
streamlit run app.py
```

## Usage

1. Open `http://localhost:8501`
2. Upload a voice memo (`.m4a`, `.mp3`, `.wav`, `.ogg`, `.opus`)
3. Pick the language and click **Transcribe**
4. Fix any mistakes in the transcript
5. Click **Make recipe**, then **Save to recipe book**

Optional: put a photo named `nani.jpg` in the project folder to show it in the banner.

## Why open models?

Both models are open-weight. The same pipeline can run fully locally
(for example with Ollama and faster-whisper) by changing the two functions in
`core.py`, which would keep family audio on your own machine.
This version uses hosted APIs because [apni honest wajah, jaise: limited mobile data].

## Privacy

Audio and transcripts are sent to Groq and Google when using this version.
Do not commit family audio, photos, or API keys. See `.gitignore`.

## Next steps

- Fully local version (Ollama + faster-whisper)
- Printable recipe book (PDF)
- Read-aloud for each recipe

## License

MIT
