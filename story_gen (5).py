"""Cinematic Fast-Paced Blender 5.2 Director for Telegram Bot.
Uses raw delimiter blocks (===SIGN=== / ===STORY_JSON=== / ===STORY_PY===) instead of escaping Python inside JSON,
so long 35-42 shot Python scene files NEVER fail with JSON escape errors!
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
    parts = resp.json()["candidates"][0]["content"]["parts"]
    # Join only non-thought text parts
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def _strip_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def _parse_blocks(raw: str):
    m_sign = re.search(r"===SIGN===\s*(.*?)\s*===STORY_JSON===", raw, re.S)
    m_json = re.search(r"===STORY_JSON===\s*(.*?)\s*===STORY_PY===", raw, re.S)
    m_py   = re.search(r"===STORY_PY===\s*(.*)", raw, re.S)
    if not (m_json and m_py):
        raise ValueError("Model output missing ===STORY_JSON=== or ===STORY_PY=== markers")
    sign_text = (m_sign.group(1).strip().splitlines()[0].strip() if m_sign else "NO|RULE")
    story_json = json.loads(_strip_fences(m_json.group(1)))
    story_py = _strip_fences(m_py.group(1))
    return story_json, story_py, sign_text


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

OUTPUT FORMAT (STRICT — use these exact 3 markers, NO extra commentary before or after):
===SIGN===
TWO|WORDS
===STORY_JSON===
{{
 "title": "{title}",
 "voice": "en-US-AndrewNeural",
 "rate": "+18%",
 "seconds": {target_seconds},
 "fps": 60,
 "fx": {{"speed_lines": true, "flash_into": ["s02", "s12"]}},
 "shots": [{{"id": "s01", "line": "..."}}, ...]
}}
===STORY_PY===
<raw, complete, valid Python 3 Blender scene file using rt_engine.py>

CINEMATIC PACING & CAMERA DIRECTION (TOP-NOTCH, FAST-PACED!):
1. RAPID-FIRE CUTTING (~0.9 to 1.3s PER SHOT):
   - Split the user's exact script into tight 3 to 6 word action beats so the visuals cut constantly with ZERO dead air! Joining all `"line"` fields MUST equal the user's exact script word-for-word.
   - EVERY shot must visually show the EXACT object, creature, or action being spoken in that beat (if the line mentions a knife, horn, basket, door, window, or sign, cut to a tight close-up of THAT exact prop/action!).
2. DYNAMIC HUMAN-STYLE CAMERA WORK (NEVER STATIC!):
   - Rotate through distinct cinema angles on EVERY cut — never repeat the same angle twice in a row:
     * **Crash-Zoom / Whip-In:** `fov` snaps `68 -> 30` in `0.2s` using `ease_out(ramp(t, 0, 0.22))` on shocking reveals!
     * **Low-Angle Power Shot:** Camera down at `z=1.2..1.8` looking UP at a towering creature, villain, or building.
     * **Dutch Tilt (`roll=-9..+9`):** Pass `roll=` to `E.cam(pos, target, fov, roll=...)` during dread, panic, or horror twists!
     * **Impact Camera Shake:** On slams, landings, roars, or jumpscares, add `sh = 0.28 * math.exp(-max(0, t-0.15)*9) * math.sin(t*68)` to camera `z` and `look_target`!
     * **Over-the-Shoulder (OTS):** Place camera right behind one character's shoulder looking toward the threat/other character.
     * **High Overhead / Bird's-Eye:** Dramatic top-down shot (`z=12..18`) for chases, swarms, or isolation.
     * **Macro Prop Close-Up:** Tight `fov=28..34` framing a key prop or character face filling the vertical 9:16 screen.
   - Use `pop(t, 0.05, 0.18)` for snappy Roblox-style poses, and swap faces mid-shot (`if t > T * 0.45:`) right on the punchline or scare!
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
                story_json, story_py, sign_text = _parse_blocks(raw)
                story_json["title"] = title
                story_json["fps"] = 60
                story_json["seconds"] = target_seconds
                _validate_story(story_json, story_py)
                return story_json, story_py, sign_text
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

    raise RuntimeError(f"Story generation failed ({last_err})")