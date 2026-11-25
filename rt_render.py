"""Step 3. Render the frames (run by Blender, not plain Python):
  blender -b --factory-startup --python rt_render.py -- stories/<story>.json [options]
options:
  --stills          one small picture per shot (3 moments each) into build/stills/ for checking
  --scale 50        render at 50% size (quick preview)
  --part 0/2        render only every 2nd frame, starting at 0 (run two Blenders side by side)
  --from 3.5 --to 5 only this time range, in seconds
Reads build/words.json for the timing: every shot starts just before its first spoken word."""
import sys, os, json, time, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
import rt_engine as E

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
story_path = os.path.join(HERE, argv[0]) if not os.path.isabs(argv[0]) else argv[0]
def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default
STILLS = "--stills" in argv; scale = int(opt("--scale", 100)); part = opt("--part", "0/1"); t_from = float(opt("--from", 0)); t_to = float(opt("--to", 1e9))
only = opt("--only")

story = json.load(open(story_path, encoding="utf-8"))
words = json.load(open(os.path.join(HERE, "build", "words.json"), encoding="utf-8"))["words"]
fps = int(story.get("fps", 30)); total = float(story.get("seconds", 20))
lead = float(story.get("cut_lead", 0.07))


def shot_times():
    out = []
    for i, s in enumerate(story["shots"]):
        ws = [w for w in words if w["shot"] == i]
        out.append([s["id"], max(0.0, ws[0]["t0"] - lead) if ws else None])
    out[0][1] = 0.0
    for i, o in enumerate(out):
        if o[1] is None: o[1] = out[i - 1][1]
    # snap to whole frames
    res = []
    for i, (sid, t0) in enumerate(out):
        t1 = out[i + 1][1] if i + 1 < len(out) else total
        res.append((sid, round(t0 * fps) / fps, round(t1 * fps) / fps))
    return res


TIMES = shot_times()
json.dump([{"id": a, "t0": b, "t1": c} for a, b, c in TIMES], open(os.path.join(HERE, "build", "shots.json"), "w"), indent=1)

spec = importlib.util.spec_from_file_location("scene_file", os.path.splitext(story_path)[0] + ".py")
scene_file = importlib.util.module_from_spec(spec); spec.loader.exec_module(scene_file)

t_build = time.time()
scn = E.new_scene(1080, 1920, fps, int(story.get("samples", 16)))
scn.render.resolution_percentage = scale
C = scene_file.build()
print(f"[rt] built scene in {time.time() - t_build:.1f}s; {len(TIMES)} shots, {fps} fps", flush=True)


def frame(t):
    for sid, a, b in TIMES:
        if a - 1e-6 <= t < b - 1e-6 or (sid == TIMES[-1][0] and t >= a):
            scene_file.reset(C); scene_file.SHOTS[sid](C, t - a, b - a); return sid
    return None


def render(path):
    scn.render.filepath = path; bpy.ops.render.render(write_still=True)


# warm-up: the first render after start comes out blank while shaders compile, so throw two away
for c in E.G.colls.values(): c.hide_render = False
E.mood("day"); E.cam((-40, -30, 30), (0, 0, 0), 60)
scn.render.resolution_percentage = 25; render(os.path.join(HERE, "build", "_warm.jpg")); render(os.path.join(HERE, "build", "_warm.jpg"))
scn.render.resolution_percentage = scale

t0 = time.time()
if STILLS:
    out = os.path.join(HERE, "build", "stills"); os.makedirs(out, exist_ok=True)
    for i, (sid, a, b) in enumerate(TIMES):
        if only and sid not in only.split(","): continue
        for j, fr in enumerate((0.0, 0.5, 0.96)):
            t = a + (b - a) * fr; frame(min(t, b - 1.0 / fps)); render(os.path.join(out, f"{i:02d}_{sid}_{j}.jpg"))
    print(f"[rt] stills done in {time.time() - t0:.1f}s", flush=True)
else:
    out = os.path.join(HERE, "build", "frames"); os.makedirs(out, exist_ok=True)
    k, n = [int(v) for v in part.split("/")]
    todo = [f for f in range(int(round(total * fps))) if f % n == k and t_from <= f / fps < t_to]
    for done, f in enumerate(todo):
        frame(f / fps); render(os.path.join(out, f"f_{f:05d}.jpg"))
        if done % 50 == 0: print(f"[rt] part {part}: {done}/{len(todo)} frames, {time.time() - t0:.0f}s", flush=True)
    print(f"[rt] part {part}: rendered {len(todo)} frames in {time.time() - t0:.1f}s ({(time.time() - t0) / max(1, len(todo)):.2f}s per frame)", flush=True)
