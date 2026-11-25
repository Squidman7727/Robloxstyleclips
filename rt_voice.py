"""Step 1. Voice + word timings.
python rt_voice.py stories/<story>.json
Speaks the story with a free edge-tts voice, one sentence at a time, cuts the dead air between
sentences (the real shorts never pause), speeds up until it fits the story's "seconds",
and writes build/vo.wav + build/words.json (every word with start/end and the shot it belongs to)."""
import sys, os, json, asyncio, subprocess, re, time
import numpy as np, edge_tts
HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build"); SR = 48000


async def speak(text, voice, rate, out):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(out, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]])
    return words


def pcm(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


norm = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("’", "'"))


def build(story, voice, rate, gap):
    # sentences = runs of shot lines up to . ! ? or ...
    sents = []; cur = []
    for si, s in enumerate(story["shots"]):
        line = (s.get("line") or "").strip()
        if not line: continue
        cur.append((si, line))
        if re.search(r"[.!?…]$", line): sents.append(cur); cur = []
    if cur: sents.append(cur)
    audio = []; out = []; t = 0.0
    for k, sent in enumerate(sents):
        text = " ".join(l for _, l in sent)
        mp3 = os.path.join(BUILD, f"_s{k}.mp3")
        for attempt in range(6):  # the free service drops a request now and then
            try:
                wb = asyncio.run(speak(text, voice, rate, mp3)); break
            except Exception as e:
                if attempt == 5: raise
                time.sleep(2 + 2 * attempt)
        a = pcm(mp3).copy(); os.remove(mp3)
        idx = np.nonzero(np.abs(a) > 0.012)[0]
        lead = max(0, idx[0] - int(0.015 * SR)); tail = min(len(a), idx[-1] + int(0.05 * SR))
        a = a[lead:tail]; lead_s = lead / SR
        owners = [(si, w) for si, l in sent for w in l.split() if norm(w)]
        j = 0
        for st, en, tx in wb:
            pieces = [p for p in tx.split() if norm(p)] or [tx]
            for q in range(len(pieces)):
                si, shown = owners[min(j, len(owners) - 1)]; j += 1
                b0 = st + (en - st) * q / len(pieces); b1 = st + (en - st) * (q + 1) / len(pieces)
                out.append({"t0": round(max(0, b0 - lead_s) + t, 3), "t1": round(min(len(a) / SR, b1 - lead_s) + t, 3), "word": shown, "shot": si})
        if j != len(owners): print("  ! word count mismatch in:", text, j, len(owners))
        fade = int(0.008 * SR); a[:fade] *= np.linspace(0, 1, fade); a[-fade:] *= np.linspace(1, 0, fade)
        audio.append(a); t += len(a) / SR
        if k < len(sents) - 1:
            audio.append(np.zeros(int(gap * SR), np.float32)); t += gap
    return np.concatenate(audio), out


def main(story_path):
    story = json.load(open(story_path, encoding="utf-8"))
    voice = story.get("voice", "en-US-AndrewNeural")
    lead = story.get("lead", 0.1)
    target = story.get("seconds", 20) - story.get("tail", 0.25) - lead
    gap = story.get("gap", 0.09)
    os.makedirs(BUILD, exist_ok=True)
    for pct in range(int(str(story.get("rate", "+10%")).strip("+%")), 60, 3):
        audio, words = build(story, voice, f"+{pct}%", gap)
        d = len(audio) / SR
        print(f"{voice} +{pct}%: {d:.2f}s (target {target:.2f}s)")
        if d <= target: break
    audio = np.concatenate([np.zeros(int(lead * SR), np.float32), audio])
    for w in words: w["t0"] = round(w["t0"] + lead, 3); w["t1"] = round(w["t1"] + lead, 3)
    audio = audio / max(1e-6, np.abs(audio).max()) * 0.89
    wav = os.path.join(BUILD, "vo.wav")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", wav], stdin=subprocess.PIPE)
    p.communicate(audio.astype(np.float32).tobytes())
    json.dump({"voice": voice, "rate": f"+{pct}%", "duration": len(audio) / SR, "words": words},
              open(os.path.join(BUILD, "words.json"), "w", encoding="utf-8"), indent=1)
    wps = len(words) / (words[-1]["t1"] - words[0]["t0"])
    print(f"wrote vo.wav {len(audio)/SR:.2f}s, {len(words)} words, {wps:.2f} words/s")
    for si, s in enumerate(story["shots"]):
        ws = [w for w in words if w["shot"] == si]
        if ws: print(f"  {ws[0]['t0']:6.2f}-{ws[-1]['t1']:6.2f}  {s['id']:8s} {s['line']}")


if __name__ == "__main__":
    main(sys.argv[1])
