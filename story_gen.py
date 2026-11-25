"""Pro Roblox Story Kit Director (powered by Gemini 3.8 Flash).
Turns the user's exact TITLE + SCRIPT into `engine/videos/<slug>/shots.py` using
the full `roblox-story-kit` engine (Cam crash/whip/push/orbit/track/handheld,
layered faces + lip-sync talk + 20+ overshoot gestures, 15+ worlds, and 45+ real WAV SFX).
"""
import os, re, ast, time
import requests

GEMINI_API_KEY  = os.environ["GEMINI_API_KEY"]
PRIMARY_MODEL   = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = [PRIMARY_MODEL, "gemini-3.5-flash-lite", "gemini-2.5-flash"]
HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "engine")


def _load_refs():
    playbook = open(os.path.join(ENGINE, "PLAYBOOK.md"), encoding="utf-8").read()
    skill = open(os.path.join(HERE, "SKILL.md"), encoding="utf-8").read()
    ex_lines = open(os.path.join(ENGINE, "videos", "sneeze_teleport", "shots.py"), encoding="utf-8").read().splitlines()
    # First 240 lines show cast, helpers, and rich multi-location shot syntax
    ex_sample = "\n".join(ex_lines[:240])
    return playbook, skill, ex_sample


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
    return "".join(p.get("text", "") for p in parts if not p.get("thought"))


def _strip_fences(s: str) -> str:
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def build_pro_shots(title: str, script: str, slug: str):
    playbook, skill, ex_sample = _load_refs()
    words = [w for w in script.split() if w.strip()]
    word_index_map = " ".join(f"[{i}]{w}" for i, w in enumerate(words))

    system_prompt = f"""You are a master Roblox/Blender 5.2 director using the `roblox-story-kit` studio engine (`shotkit`, `rbx.story`, `rbx.core`, `rbx.chars`, `rbx.acting`, `rbx.world`, `rbx.world2`, `rbx.sets`, `rbx.locs`, `rbx.fx`).

Your job: write a COMPLETE, VALID, FAST-PACED `shots.py` file for the user's exact Title & Script.
Return ONLY raw valid Python code for `shots.py` (no markdown fences, no commentary).

CRITICAL RULES:
1. WORD-INDEX TIMING (`@S(shot_num, w0, w1, "label")`):
   - `w0` and `w1` are 0-based word indices into the user's script!
   - Shot 1 MUST start at `w0 = 0`. Every shot `k` MUST start at the previous shot's `w1` (zero gaps, zero overlaps!).
   - The FINAL shot MUST use `w1 = None` so it runs cleanly to the end of the voiceover!
   - Aim for **50-60 cuts/minute** (~4 to 7 words per shot, ~1.0-1.3s average)!
2. USE THE FULL PRO ENGINE (FAST-PACED, HUMAN-MADE QUALITY):
   - Always start with:
     ```python
     from shotkit import *
     from rbx import story
     from rbx.story import *
     import math, random
     from mathutils import Vector

     V = Video(__file__)
     story.bind(V)
     ```
   - Create a **BRAND-NEW UNIQUE CAST** for this story using `story._live(chars.Char(...), t0, t1, expr)` (varied skin, shirt, pants, hair, hair_color, face, sleeves, extras).
   - Use the rich built-in locations (`W.town()`, `W.classroom_day()`, `W.comedy_club()`, `W.cockpit()`, `W.tv_room()`, `W.hallway_day()`, `W2.cabin()`, `W2.flower_shop()`, `W2.parking_lot()`, `W2.pepper_jail()`, `sets.*`, `locs.*`) AND build any custom blocky props/creatures/vehicles needed using `box()`, `cyl()`, `sphere()`, `empty()`, `mat()`, `hexc()`.
   - Use **dynamic camera moves on EVERY shot**: `cam.crash(...)`, `cam.whip(...)`, `cam.push(...)`, `cam.orbit(...)`, `cam.track(...)`, `cam.handheld(...)`. NEVER leave a static camera!
   - Use **expressive acting**: `ch.face(t, "shock")` / `ch.act(t, "hands_head")` / `ch.act(t, "point")` / `ch.act(t, "recoil")` / `ch.jump(...)` / `ch.run(...)` / `ch.panic(...)` + `lips(ch, t0, t1)` when a character talks!
   - Put **`sfx(t, "name")`** on EVERY hit, whoosh, reveal, and punchline! Valid SFX names:
     `alarm aww boing bonk boom buzzer cashier chat cheer click clink coin confetti crickets crowd ding door footsteps gasp glitch hammer jet kids_laugh meow paper pigeon place poof pop rimshot rise rocket rope sneeze snort sparkle splat stomp teleport thud whoosh wind window zombie`.
3. AVOID ALL KNOWN TRAPS:
   - Ground cameras in `W.town()` MUST stay in the open street area (`x in -40..40, y in -55..10`) so cameras never clip inside a house!
   - Never attach custom attributes to `bpy` objects (`obj.head = ...` fails).
   - Never put props between the camera and a character's face.
   - Always call `W.sky()` + `W.sun()` (or `world(...)`) in outdoor shots so lighting is rich and vibrant.

STUDIO SKILL REFERENCE:
{skill}

WORKED EXAMPLE (`videos/sneeze_teleport/shots.py` excerpt):
{ex_sample}
"""

    user_prompt = (
        f"TITLE: {title}\n"
        f"TOTAL WORDS: {len(words)}\n\n"
        f"INDEXED SCRIPT (use these exact [index] numbers for @S(shot_num, w0, w1, label)):\n"
        f"{word_index_map}\n\n"
        f"Write the complete, fast-paced, SFX-rich `shots.py` now."
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
