"""Pro Roblox Story Kit Director (powered by Gemini 3.8 Flash).
Includes the EXACT verified API signatures from rbx/core.py, rbx/story.py, rbx/world.py, rbx/world2.py
and real working shots from sneeze_teleport/shots.py so every generated shot renders cleanly on Pass 1!
"""
import os, re, ast, time
import requests

GEMINI_API_KEY  = os.environ["GEMINI_API_KEY"]
PRIMARY_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-3.5-flash-lite", "gemini-2.5-flash"]
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "engine")

EXACT_API_CHEATSHEET = """
=== EXACT VERIFIED API SIGNATURES (NEVER INVENT OR GUESS PARAMETERS!) ===
1. CAMERA (`cam = Cam()`):
   - `cam.push(t0, t1, target_xyz, d0, d1, yaw=0.0, pitch=8.0, lens=30, yaw1=None, pitch1=None, lens1=None, fstop=2.8, roll=0.0)`
     * IMPORTANT: `target_xyz` is a 3-tuple like `(x, y, 4.4)` (character head is at z~4.4!). `d0` and `d1` are DISTANCES (numbers like `7.0, 5.2`, NOT tuples!).
     * `yaw=0` puts the camera on the `-Y` side (DIRECTLY IN FRONT of a character with `rot=0`!). `yaw=180` is behind them.
     * NEVER use `d0 < 3.5` (closer than 3.5 clips inside the character's head/chest!). Use `d0=4.5..6.5` for close-ups, `7.5..11.0` for medium, `14.0..24.0` for wide!
   - `cam.orbit(t0, t1, target_xyz, dist, yaw0, yaw1, pitch=8.0, lens=30, fstop=2.8)`
   - `cam.crash(t, lens_from, lens_to, dur=0.12)`
   - `cam.whip(t0, t1, loc0, target0, loc1, target1)`
   - `cam.key(t, loc_xyz, target_xyz, lens=30, roll=0.0, focus=None, fstop=2.8)`
   - `cam.handheld(strength=1.0)`

2. CHARACTERS & ACTING:
   - Create character: `ch = story._live(chars.Char("Name", skin="#f0d5b8", shirt="#e0403a", pants="#2b3040", hair="spiky", hair_color="#3a2414", face="plain", sleeves="short"), t0, t1, "happy")`
     * Hair styles: `"spiky"`, `"short"`, `"long"`, `"bun"`, `"bob"`, `"slick"`, `"buzz"`, `"cap"`, `"tophat"`, `"pilot"`, `"bald"`
     * Faces: `"plain"`, `"girl"`, `"mustache"`
     * Built-in helpers: `eddie(t0, t1, expr)`, `leo(t0, t1, expr)`, `pickle(t0, t1, expr)`, `grandma(t0, t1, expr)`, `mayor(t0, t1, expr)`, `townie(i, t0, t1, expr)`
   - Pose & place: `ch.pose(t0, loc=(x, y, z), rot=deg)` (at `rot=0`, character faces `-Y`!).
   - Scale character (e.g. getting fat or shrinking!):
     * `ch.root.scale = (1.0, 1.0, 1.0); ch.root.keyframe_insert("scale", frame=F(t0))`
     * `ch.root.scale = (2.2, 2.2, 1.15); ch.root.keyframe_insert("scale", frame=F(t1))` (inflating fat!)
   - Gestures: `ch.act(t, gesture)` — valid gestures: `idle shock hands_head hands_face cheer point point_l shrug recoil lean slump think cross phone reach push hold wave fists facepalm brace`
   - Expressions: `ch.face(t, "shock")` — valid: `happy smile neutral smirk smug shock terror gasp scream angry determined sad cry squint side_eye`
   - Lip-sync: `lips(ch, t0, t1)`
   - Helper: `facing(from_xy, to_xy)` returns yaw degrees so a character faces another point; `up(pt, z)` adds z to a 3-tuple.

3. PROVEN SETS & SAFE COORDINATES (NEVER PUT CAMERAS INSIDE WALLS!):
   - `town_scene()` -> Open street is `x in [-30..30], y in [-35..-5], z=0`. Put characters at `(0, -14, 0)` to `(8, -18, 0)`, `rot=0`, camera `yaw=-20..+20`, `d0=6..14`.
   - `class_scene(t0, t1)` -> Builds lit classroom with desks & kids! Use `W.classroom_day()` + `W.seat_pos(desk)` / `W.sit(ch, t0, desk)` or place speaker at `(0, 5.5, 0)` facing `rot=0`, camera `yaw=-15..+15`, `d0=5.5..9.0`.
   - `W.comedy_club()` -> Stage is around `(0, 3.0, 1.0)`, character on stage at `(0, 3.0, 1.0), rot=0`, audience at `y=-4..-10`, camera at `yaw=-20..+20, d0=5.0..10.0`.
   - `W.tv_room()` -> Living room couch around `(0, 2.0, 0)`, characters at `(-1.5, 2.0, 0)` and `(1.5, 2.0, 0)`, `rot=0`, camera `yaw=-15..+15, d0=5.5..8.5`.
   - `W.hallway_day()` -> Corridor along Y, characters at `(0, 0, 0)`, `rot=0`, camera `yaw=-10..+10, d0=5.5..10.0`.
   - `W2.parking_lot((0, 0))` -> Open outdoor lot (call `W.sky(); W.sun()` first!), characters at `(0, 0, 0)`, camera `d0=7..16`.
   - `W2.flower_shop()` / `W2.pepper_jail()` -> Always call `world((0.8, 0.85, 0.9), 0.5)` for indoor ambient light!
   - Outdoor shots MUST call `town_scene()` or `W.sky(); W.sun()` so the scene is NEVER pitch black!

4. SFX (`sfx(t, "name", vol=1.0)`):
   Valid names: `alarm aww boing bonk boom buzzer cashier chat cheer click clink coin confetti crickets crowd ding door footsteps gasp glitch hammer jet kids_laugh meow paper pigeon place poof pop rimshot rise rocket rope sneeze snort sparkle splat stomp teleport thud whoosh wind window zombie`.
"""


def _load_examples():
    ex_lines = open(os.path.join(ENGINE, "videos", "sneeze_teleport", "shots.py"), encoding="utf-8").read().splitlines()
    # Lines 220..360 show real working shots with Cam.push, Cam.orbit, Cam.crash, Cam.whip, town_scene, comedy_club, etc.
    return "\n".join(ex_lines[220:360])


def _call_gemini(model: str, system_prompt: str, user_prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }
    gen_cfg = {
        "temperature": 0.65,
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
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def _strip_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def build_pro_shots(title: str, script: str, slug: str):
    ex_shots = _load_examples()
    words = [w for w in script.split() if w.strip()]
    word_index_map = " ".join(f"[{i}]{w}" for i, w in enumerate(words))

    system_prompt = f"""You are a master Roblox/Blender 5.2 director using the `roblox-story-kit` studio engine.
Write a COMPLETE, 100% CRASH-FREE, FAST-PACED `shots.py` for the user's exact Title & Script.
Return ONLY raw valid Python code for `shots.py` (no markdown fences, no prose).

HEADER (copy verbatim):
```python
from shotkit import *
from rbx import story
from rbx.story import *
import math, random
from mathutils import Vector

V = Video(__file__)
story.bind(V)
```

CRITICAL RULES:
1. ZERO CRASHES: Use ONLY the exact function names & signatures in the API Cheat Sheet below! Never invent parameters or call nonexistent methods.
2. WORD-INDEX TIMING (`@S(shot_num, w0, w1, "desc")`):
   - Shot 1 MUST start at `w0 = 0`. Every shot `k` MUST start at the previous shot's `w1`.
   - The FINAL shot MUST use `w1 = None`.
   - Cut every 4 to 7 words (~40-55 fast shots for a 1-minute script, ~1.1s average!).
3. BRIGHT, CLEAN, READABLE FRAMING (LIKE `sneeze_teleport`!):
   - ALWAYS light every scene (`town_scene()` or `W.sky(); W.sun()` outdoors; `world((0.8, 0.85, 0.9), 0.5)` indoors). NEVER render a black frame!
   - ALWAYS keep camera distance `d0 >= 4.5` from character head `(x, y, 4.4)` so you NEVER clip into a character's chin, shirt, or wall!
   - Design a fresh unique cast for this story and animate them expressively (`face`, `act`, `lips`, `ch.root.scale` for growing/shrinking/inflating, `W2.poof`, `sfx`).
   - Add `sfx(t, "name")` on every impact, pop, boing, boom, gasp, whoosh, cheer!

{EXACT_API_CHEATSHEET}

PROVEN WORKING SHOT EXAMPLES (from `sneeze_teleport/shots.py` — copy this exact coding style!):
{ex_shots}
"""

    user_prompt = (
        f"TITLE: {title}\n"
        f"TOTAL WORDS: {len(words)}\n\n"
        f"INDEXED SCRIPT (use these exact [index] numbers for @S(shot_num, w0, w1, desc)):\n"
        f"{word_index_map}\n\n"
        f"Write the complete, crash-free, brightly-lit, fast-paced `shots.py` now."
    )

    models = list(dict.fromkeys(FALLBACK_MODELS))
    last_err = None
    for model in models:
        for attempt in range(2):
            try:
                raw = _call_gemini(model, system_prompt, user_prompt)
                code = _strip_fences(raw)
                ast.parse(code)
                if "@S(" not in code or "Video(__file__)" not in code:
                    raise ValueError("Generated shots.py missing @S() decorators or Video(__file__)")
                return code
            except requests.HTTPError as e:
                last_err = e
                code_num = e.response.status_code if e.response is not None else 0
                if code_num in (429, 500, 502, 503, 504):
                    time.sleep(3 * (attempt + 1))
                    continue
                break
            except Exception as e:
                last_err = e
                time.sleep(2)

    raise RuntimeError(f"Failed to generate shots.py ({last_err})")
