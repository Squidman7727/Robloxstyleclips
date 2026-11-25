"""Turns a user-provided TITLE + SCRIPT into:
  1) stories/<slug>.json  (exact user script split into crisp phrase shots, auto-timed 20-60s, 60 fps)
  2) stories/<slug>.py    (complete Blender 5.2 scene file animating every single shot)
  3) sign_text            (2-word street sign text matching the story)
"""
import os, re, ast, json, time
import requests

GEMINI_API_KEY  = os.environ["GEMINI_API_KEY"]
PRIMARY_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-3.5-flash-lite", "gemini-2.5-flash"]
HERE = os.path.dirname(os.path.abspath(__file__))


def _load_reference():
    ref_py = open(os.path.join(HERE, "stories", "never_say_thank_you.py"), encoding="utf-8").read()
    ref_json = open(os.path.join(HERE, "stories", "never_say_thank_you.json"), encoding="utf-8").read()
    return ref_json, ref_py


def _call_gemini(model: str, system_prompt: str, user_prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    gen_cfg = {
        "responseMimeType": "application/json",
        "temperature": 0.7,
        "maxOutputTokens": 16384,
    }
    if model.startswith("gemini-3.8") or model.startswith("gemini-3"):
        gen_cfg["thinkingConfig"] = {"thinkingLevel": "low"}
    elif model.startswith("gemini-2.5"):
        gen_cfg["thinkingConfig"] = {"thinkingBudget": 0}

    body = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": gen_cfg,
    }
    resp = requests.post(url, headers=headers, json=body, timeout=240)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def build_from_user_script(title: str, script: str, slug: str):
    ref_json, ref_py = _load_reference()
    words = len(script.split())
    # Auto-calculate duration from word count (~3.3 words/sec for punchy Shorts narration, clamped 18..60s)
    target_seconds = max(18, min(60, int(round(words / 3.3)) + 2))

    system_prompt = f"""You are a Blender 5.2 director for the "In This Town" rt_engine.py kit.
The user has ALREADY written the exact Title and Script.
DO NOT rewrite, summarize, or drop ANY words from the user's script!

Your job is to return ONLY a valid JSON object (no markdown fences) with 3 keys:
  "story_json": {{
    "title": "{title}",
    "voice": "en-US-AndrewNeural",
    "rate": "+16%",
    "seconds": {target_seconds},
    "fps": 60,
    "fx": {{"speed_lines": true, "flash_into": [<2 or 3 dramatic shot ids>]}},
    "shots": [{{"id": "s01", "line": "..."}}, ...]
  }},
  "story_py": string containing a complete, valid Python scene file matching stories/never_say_thank_you.py,
  "sign_text": two short uppercase words separated by "|" for the street sign (e.g. "NO|TALKING").

STRICT RULES:
1. EXACT SCRIPT FIDELITY: Split the user's exact script into natural phrase-by-phrase shots (~5-8 words per shot). Joining all shot "line" fields in order MUST match the user's exact script word-for-word.
2. MATCHING BLENDER SCENES: In story_py, define build(), reset(C), one concise function (5-10 lines) per shot id in story_json["shots"], and SHOTS = {{...}} mapping every shot id to its function.
3. CAMERA & ACTING QUALITY:
   - Characters face -Y in rt_engine.py. When the camera is at +Y looking toward a character at -Y, set character yaw around 170..190 so we see their FACE, never the back of their head!
   - Keep close-up point lights moderate (160..400W) so pale faces are never blown out white.
   - Use varied faces from FACE_NAMES: ["happy","scared","sleepy","asleep","yawn","shock","smug","stern","blink","wired","c_tired","c_yawn","c_grin","c_asleep","dad_asleep","mom"], with mid-shot face swaps (`if t > T * 0.5:`) on dramatic beats!
   - Use texture name "custom_sign" for the street sign board.
   - Change camera height, FOV, and distance on EVERY consecutive shot (alternate wide/medium/close-up) so every scene matches what the narrator is saying.

REFERENCE JSON:
{ref_json}

REFERENCE PYTHON:
{ref_py}
"""
    user_prompt = f"TITLE: {title}\n\nEXACT SCRIPT (keep every word verbatim):\n{script}"
    models = list(dict.fromkeys(FALLBACK_MODELS))
    last_err = None
    raw = None
    for model in models:
        for attempt in range(2):
            try:
                raw = _call_gemini(model, system_prompt, user_prompt)
                break
            except requests.HTTPError as e:
                last_err = e
                code = e.response.status_code if e.response is not None else 0
                if code in (429, 500, 502, 503, 504):
                    time.sleep(3 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_err = e
                time.sleep(2)
        if raw is not None:
            break

    if raw is None:
        raise RuntimeError(f"All Gemini models busy/failed ({last_err})")

    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    data = json.loads(raw)

    story_json = data["story_json"]
    story_json["title"] = title
    story_json["fps"] = 60
    story_json["seconds"] = target_seconds
    story_py = data["story_py"]
    sign_text = data.get("sign_text", "NO|RULE")

    ast.parse(story_py)
    return story_json, story_py, sign_text
