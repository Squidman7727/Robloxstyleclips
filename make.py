"""One command for the whole clip:   python make.py stories/<story>.json [--preview] [--keep-voice]
Runs the four steps in order and prints how long each took (also saved to build/timings.json).
  1 rt_voice.py   voice + word timings        (skipped if --keep-voice and build/vo.wav exists)
  2 rt_faces.py   drawn textures              (plain Python)
  3 rt_render.py  the frames                  (Blender, two copies side by side)
  4 rt_finish.py  captions, glow, mp4         (plain Python + ffmpeg)
--preview renders at half size (about a quarter of the time)."""
import sys, os, json, time, subprocess, glob, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
BLENDER = os.environ.get("BLENDER") or shutil.which("blender") or r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"


def run(name, cmd, timings):
    t = time.time(); print(f"--- {name}", flush=True)
    subprocess.check_call(cmd, cwd=HERE); timings[name] = round(time.time() - t, 1); print(f"    {timings[name]} s", flush=True)


def main():
    story = sys.argv[1]; preview = "--preview" in sys.argv; keep_voice = "--keep-voice" in sys.argv; timings = {}
    vo_exists = os.path.exists(os.path.join(HERE, "build", "vo.wav")) and os.path.exists(os.path.join(HERE, "build", "words.json"))
    if keep_voice and vo_exists:
        print("--- 1 voice (using existing build/vo.wav + build/words.json)", flush=True)
    else:
        run("1 voice", [sys.executable, "rt_voice.py", story], timings)
    run("2 textures", [sys.executable, "rt_faces.py"], timings)
    for f in glob.glob(os.path.join(HERE, "build", "frames", "f_*.jpg")): os.remove(f)
    t = time.time(); print("--- 3 render", flush=True)
    base = [BLENDER, "-b", "--factory-startup", "--python", "rt_render.py", "--", story]
    if os.name != "nt" and shutil.which("xvfb-run") and not os.environ.get("DISPLAY"):
        base = ["xvfb-run", "-a"] + base
    if preview: procs = [subprocess.Popen(base + ["--scale", "50"], cwd=HERE, stdout=subprocess.DEVNULL)]
    else: procs = [subprocess.Popen(base + ["--part", f"{k}/2"], cwd=HERE, stdout=subprocess.DEVNULL) for k in range(2)]
    for p in procs:
        if p.wait() != 0: raise SystemExit("Blender failed; run the rt_render.py command by hand to see why")
    timings["3 render"] = round(time.time() - t, 1); print(f"    {timings['3 render']} s", flush=True)
    run("4 finish", [sys.executable, "rt_finish.py", story] + (["--preview"] if preview else []), timings)
    json.dump(timings, open(os.path.join(HERE, "build", "timings.json"), "w"), indent=1)
    print("done:", os.path.join(HERE, "build", "preview.mp4" if preview else "FINAL.mp4"))


if __name__ == "__main__":
    main()
