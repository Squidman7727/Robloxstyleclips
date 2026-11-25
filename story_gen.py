"""Uses Gemini 3.8 Flash API to turn one line ('In this town, ...') into:
  1) stories/<slug>.json  (17-shot script, ~75 words, 20s, 60 fps)
  2) stories/<slug>.py    (complete Blender 5.2 scene file using rt_engine.py)
  3) sign_text            (2-word banned street sign text, e.g. 'THANK|YOU')
"""
import os, re, ast, json
import requests

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
HERE = os.path.dirname(os.path.abspath(__file__))


def _load_reference():
    ref_py = open(os.path.join(HERE, "stories", "never_say_thank_you.py"), encoding="utf-8").read()
    ref_json = open(os.path.join(HERE, "stories", "never_say_thank_you.json"), encoding="utf-8").read()
    return ref_json, ref_py


def generate_blender_story(idea: str, slug: str):
    ref_json, ref_py = _load_reference()
    system_prompt = f"""You write 20-second vertical "In This Town" shorts for the Blender 5.2 rt_engine.py kit.
Return ONLY a valid JSON object (no markdown fences) with 3 keys:
  "story_json": object matching stories/never_say_thank_you.json (15-17 shots, ~75 words, seconds: 20, fps: 60),
  "story_py": string containing a complete, valid Python scene file matching stories/never_say_thank_you.py,
  "sign_text": two short uppercase words separated by "|" for the banned street sign (e.g. "NO|BLINKING").

RULES FOR story_py:
- Must define build(), reset(C), one function per shot id in story_json["shots"], and SHOTS = {{...}}.
- Characters face -Y in rt_engine.py. When the camera is at +Y looking toward a character at -Y, set character yaw around 170..190 so we see their FACE.
- Keep close-up point lights moderate (160..400W) so pale faces are never blown out white.
- Valid faces: ["happy","scared","sleepy","asleep","yawn","shock","smug","stern","blink","wired","c_tired","c_yawn","c_grin","c_asleep","dad_asleep","mom"].
- Use texture name "custom_sign" for the banned street sign board.
- Vary camera height and distance on every shot.

REFERENCE JSON:
{ref_json}

REFERENCE PYTHON:
{ref_py}
"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body = {
        "contents": [{"role": "user", "parts": [{"text": f"Create the complete 17-shot Blender story for: {idea}"}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.75,
            "thinkingConfig": {"thinkingLevel": "low"},
        },
    }
    resp = requests.post(url, json=body, timeout=180)
    resp.raise_for_status()
    raw = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    data = json.loads(raw)

    story_json = data["story_json"]
    story_json["fps"] = 60
    story_json["seconds"] = 20
    story_py = data["story_py"]
    sign_text = data.get("sign_text", "NO|RULE")

    ast.parse(story_py)
    return story_json, story_py, sign_text