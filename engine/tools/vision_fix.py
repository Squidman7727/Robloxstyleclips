"""Automatic Vision + Error Self-Fixer for roblox-story-kit (runs inside GitHub Actions prepare job).
Reads:
  - videos/<slug>/render_log_preview.txt  (any crashed shots / tracebacks)
  - videos/<slug>/full.jpg                (rendered contact sheet image)
  - videos/<slug>/shots.py                (current shot code)
Sends them to Gemini 3.8 Flash Vision so it literally SEES black/clipped/crashed tiles and rewrites
the broken shots automatically BEFORE the 20 parallel runners render final!
"""
import ast, base64, os, re, sys, requests

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.8-flash")


def strip_fences(s):
    s = s.strip()
    s = re.sub(r"^```[a-zA-Z]*\s*", "", s)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()


def main():
    slug = sys.argv[1]
    if slug in ("sneeze_teleport", "laugh_float"):
        print("[vision_fix] skipping built-in demo")
        return
    if not GEMINI_API_KEY:
        print("[vision_fix] GEMINI_API_KEY secret not set in GitHub Actions; skipping auto-fix")
        return

    vdir = os.path.join(STUDIO, "videos", slug)
    shots_p = os.path.join(vdir, "shots.py")
    log_p = os.path.join(vdir, "render_log_preview.txt")
    img_p = os.path.join(vdir, "full.jpg")

    shots_code = open(shots_p, encoding="utf-8").read()
    log_txt = open(log_p, encoding="utf-8").read()[-8000:] if os.path.exists(log_p) else ""

    parts = []
    if os.path.exists(img_p):
        b64 = base64.b64encode(open(img_p, "rb").read()).decode("ascii")
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64}})

    prompt = f"""You are QA-fixing a Blender 5.2 `shots.py` file for `roblox-story-kit`.
Look closely at the attached preview contact sheet (`full.jpg`) AND the render log below!

FIX EVERY PROBLEM YOU SEE:
1. Any shot that printed `FAILED` in the log: fix the Python bug / wrong argument signature so it renders cleanly!
2. Any tile in `full.jpg` that is **pitch black** -> add `W.sky(); W.sun()` (outdoors) or `world((0.8, 0.85, 0.9), 0.5)` (indoors) and pull the camera out of any wall!
3. Any tile in `full.jpg` that is **just a solid wall, too close to a chin/chest, or empty** -> fix `cam.push(t0, t1, target_xyz, d0, d1, yaw=..., pitch=..., lens=...)` using `d0=5.5..10.0`, `target=(x, y, 4.4)`, `yaw=-20..+20` so the character's FULL FACE and action are clearly framed!

Return ONLY the complete, fixed, valid Python `shots.py` file (no markdown fences, no commentary).

RENDER LOG (errors/tracebacks):
{log_txt}

CURRENT shots.py:
{shots_code}
"""
    parts.append({"text": prompt})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    headers = {"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY}
    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 24576, "thinkingConfig": {"thinkingLevel": "medium"}},
    }
    r = requests.post(url, headers=headers, json=body, timeout=240)
    r.raise_for_status()
    out_parts = r.json()["candidates"][0]["content"]["parts"]
    fixed = strip_fences("".join(p.get("text", "") for p in out_parts if not p.get("thought")))
    ast.parse(fixed)
    if "@S(" not in fixed:
        raise ValueError("Vision fix returned invalid shots.py")
    open(shots_p, "w", encoding="utf-8").write(fixed)
    print(f"[vision_fix] rewrote {shots_p} cleanly!")


if __name__ == "__main__":
    main()