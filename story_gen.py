"""Cinematic Fast-Paced Blender 5.2 Director for Telegram Bot.
Turns ANY user-provided TITLE + SCRIPT into:
  1) stories/<slug>.json  (exact user script split into rapid 1.0-1.3s beats, 60 fps)
  2) stories/<slug>.py    (fast-paced cinematic camera work: crash-zooms, Dutch tilts, shake, low/high angles, custom worlds & creatures)
  3) sign_text            (2-word sign text matching the story)
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
        "temperature": 0.72,
        "maxOutputTokens": 24576,
    }
    if model.startswith("gemini-3.8") or model.startswith("gemini-3"):
        gen_cfg["thinkingConfig"] = {"thinkingLevel": "high"}
    elif model.startswith("gemini-2.5"):
        gen_cfg["thinkingConfig"] = {"thinkingBudget": 2048}

    body = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": gen_cfg,
    }
    resp = requests.post(url, headers=headers, json=body, timeout=300)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def _validate_story(story_json: dict, story_py: str):
    tree = ast.parse(story_py)
    fn_names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    if "build" not in fn_names or "reset" not in fn_names:
        raise ValueError("Generated story_py missing build() or reset()")
    if "SHOTS" not in story_py:
        raise ValueError("Generated story_py missing SHOTS dict")
    if "E.cam(" not in story_py or "E.use(" not in story_py:
        raise ValueError("Generated story_py missing E.cam or E.use calls")
    missing = [s["id"] for s in story_json["shots"] if s["id"] not in fn_names]
    if missing:
        raise ValueError(f"Missing shot functions in story_py: {missing[:5]}")


def build_from_user_script(title: str, script: str, slug: str):
    ref_json, ref_py = _load_reference()
    words = len(script.split())
    target_seconds = max(18, min(60, int(round(words / 3.4)) + 1))

    system_prompt = f"""You are a top-tier viral Roblox/Blender 5.2 Shorts director and cinematographer using `rt_engine.py`.
The user wrote the exact Title and Script. Keep EVERY SINGLE WORD of their script verbatim, and direct it with HUMAN-GRADE, FAST-PACED, CINEMATIC 3D STORYTELLING!

Return ONLY a valid JSON object (no markdown fences) with 3 keys:
  "story_json": {{
    "title": "{title}",
    "voice": "en-US-AndrewNeural",
    "rate": "+18%",
    "seconds": {target_seconds},
    "fps": 60,
    "fx": {{"speed_lines": true, "flash_into": [<3 to 5 dramatic impact shot ids>]}},
    "shots": [{{"id": "s01", "line": "..."}}, ...]
  }},
  "story_py": string containing a complete, valid Python scene file using rt_engine.py,
  "sign_text": two short uppercase words separated by "|" for any world/street sign.

CINEMATIC PACING & CAMERA DIRECTION (TOP-NOTCH, FAST-PACED!):
1. RAPID-FIRE CUTTING (~0.9 to 1.3s PER SHOT):
   - Split the user's exact script into tight 3 to 6 word action beats so the visuals cut constantly with ZERO dead air! Joining all `"line"` fields MUST equal the user's exact script word-for-word.
   - EVERY shot must visually show the EXACT object, creature, or action being spoken in that beat (e.g. if the line mentions a knife, horn, basket, door, window, or sign, cut to a tight close-up of THAT exact prop/action!).
2. DYNAMIC HUMAN-STYLE CAMERA WORK (NEVER STATIC!):
   - Rotate through distinct cinema angles on EVERY cut — never repeat the same angle twice in a row:
     * **Crash-Zoom / Whip-In:** `fov` snaps `68 -> 30` in the first `0.2s` using `ease_out(ramp(t, 0, 0.22))` on shocking reveals!
     * **Low-Angle Power Shot:** Camera down at `z=1.2..1.8` looking UP at a towering creature, villain, or building.
     * **Dutch Tilt (`roll=-9..+9`):** Pass `roll=` to `E.cam(pos, target, fov, roll=...)` during dread, panic, or horror twists!
     * **Impact Camera Shake:** On slams, landings, roars, or jumpscares, add `sh = 0.28 * math.exp(-max(0, t-0.15)*9) * math.sin(t*68)` to camera `z` and `look_target`!
     * **Over-the-Shoulder (OTS):** Place camera right behind one character's shoulder looking toward the threat/other character.
     * **High Overhead / Bird's-Eye:** Dramatic top-down shot (`z=12..18`) for chases, swarms, or isolation.
     * **Macro Prop Close-Up:** Tight `fov=28..34` framing a key prop or character face filling the vertical 9:16 screen.
   - Use `pop(t, 0.05, 0.18)` for snappy, juicy Roblox-style pose transitions, and swap facial expressions mid-shot (`if t > T * 0.45:`) right on the punchline or scare!
3. FREE-BUILD CUSTOM WORLDS, CREATURES & CAST:
   - Procedurally build whatever world, buildings, landscapes, creatures, monsters, vehicles, and props the script describes using `E.Static(E.coll("world"))`, `E.Mesher` (`.box()`, `.cyl()`, `.ball()`, `.blob()`, `.prism()`, `.spike()`), `E.empty()`, `E.part()`, and textured `E.M(name, rgb, tex=...)` + glowing `emit` accents!
   - Always include a huge textured ground plane (`(400, 400, 1)` at `(0, 0, -0.5)`) so the camera NEVER sees empty void below.
   - Design a brand-new unique cast (`E.Char(..., scale=...)` — e.g. `0.35` for babies, `1.0` for adults, `tall=True` or `1.8` for giants/monsters) with rich/dark Roblox outfits, hair, and accessories. Never copy the reference red-haired hero!
4. ZERO BLUE-SCREEN GUARANTEES:
   - Always call `E.use(set_coll_name, *[c.name for c in visible_chars], *C.always)` using exact collection names created in `build()`.
   - Keep camera and actors in the EXACT same coordinate space (`(0,0,0)` for `"world"`/`"street"`, `B(...)` for `"bedroom"`, `V(...)` for `"living"`).
   - Characters face `-Y` at `yaw=0` (use `yaw=170..190` when camera is at `+Y` looking toward `-Y` so we ALWAYS see faces!).
   - Keep close-up point lights moderate (160..380W) so faces never blow out white.
   - Valid faces: `["happy","scared","sleepy","asleep","yawn","shock","smug","stern","blink","wired","c_tired","c_yawn","c_grin","c_asleep","dad_asleep","mom"]`.
   - Every shot ID in `story_json["shots"]` MUST have a matching function in `story_py` and be in `SHOTS`.

REFERENCE API USAGE (for rt_engine.py syntax only — build custom worlds, creatures, and dynamic shots matching the user's script!):
{ref_py}
"""
    user_prompt = f"TITLE: {title}\n\nEXACT SCRIPT (keep every word verbatim; direct with rapid ~1s cuts, crash-zooms, Dutch tilts, camera shake, and custom 3D worlds/creatures/props):\n{script}"
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

    _validate_story(story_json, story_py)
    return story_json, story_py, sign_text
