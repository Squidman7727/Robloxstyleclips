"""Free edge-tts voice + silence trimmer + word timestamps for roblox-story-kit.
Writes videos/<slug>/audio/voice.wav and videos/<slug>/audio/words.json
in the exact schema expected by shotkit.py, mix.py, and finish.py.
Usage:
  python tools/free_voice.py <slug> [--voice en-US-AndrewNeural] [--rate +24%]
"""
import asyncio, json, os, re, subprocess, sys, time
import numpy as np
import edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
SR = 44100


async def speak(text, voice, rate, out_mp3):
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]])
    return words


def pcm(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def norm(s):
    return re.sub(r"[^a-z0-9']", "", s.lower().replace("’", "'"))


def main():
    slug = sys.argv[1]
    voice = "en-US-AndrewNeural"
    rate = "+24%"
    if "--voice" in sys.argv:
        voice = sys.argv[sys.argv.index("--voice") + 1]
    if "--rate" in sys.argv:
        rate = sys.argv[sys.argv.index("--rate") + 1]

    vdir = os.path.join(STUDIO, "videos", slug)
    adir = os.path.join(vdir, "audio")
    os.makedirs(adir, exist_ok=True)

    # Skip if pre-processed voice already exists (e.g. sneeze_teleport / laugh_float)
    if os.path.exists(os.path.join(adir, "voice.wav")) and os.path.exists(os.path.join(adir, "words.json")):
        print(f"[free_voice] using existing voice.wav + words.json for {slug}")
        return

    script_p = os.path.join(vdir, "script.txt")
    raw_lines = [l.strip() for l in open(script_p, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    full_text = " ".join(raw_lines)
    # Split into sentences so dead air between sentences is tightly trimmed (0.14s gap)
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", full_text) if s.strip()]

    audio_chunks = []
    words_out = []
    t = 0.0
    gap = 0.14

    for k, sent in enumerate(sents):
        mp3 = os.path.join(adir, f"_tmp_{k}.mp3")
        for attempt in range(6):
            try:
                wb = asyncio.run(speak(sent, voice, rate, mp3))
                break
            except Exception:
                if attempt == 5:
                    raise
                time.sleep(2 + 2 * attempt)

        a = pcm(mp3).copy()
        os.remove(mp3)
        nz = np.nonzero(np.abs(a) > 0.012)[0]
        if len(nz) == 0:
            continue
        lead = max(0, nz[0] - int(0.015 * SR))
        tail = min(len(a), nz[-1] + int(0.045 * SR))
        a = a[lead:tail]
        lead_s = lead / SR
        dur_s = len(a) / SR

        owners = [w for w in sent.split() if norm(w)]
        j = 0
        for st, en, tx in wb:
            pieces = [p for p in tx.split() if norm(p)] or [tx]
            for q in range(len(pieces)):
                shown = owners[min(j, len(owners) - 1)] if owners else tx
                j += 1
                b0 = st + (en - st) * q / len(pieces)
                b1 = st + (en - st) * (q + 1) / len(pieces)
                words_out.append({
                    "word": shown,
                    "start": round(max(0.0, b0 - lead_s) + t, 3),
                    "end": round(min(dur_s, b1 - lead_s) + t, 3),
                })

        fade = min(int(0.008 * SR), len(a) // 4)
        if fade > 0:
            a[:fade] *= np.linspace(0, 1, fade)
            a[-fade:] *= np.linspace(1, 0, fade)
        audio_chunks.append(a)
        t += dur_s
        if k < len(sents) - 1:
            audio_chunks.append(np.zeros(int(gap * SR), np.float32))
            t += gap

    final_a = np.concatenate(audio_chunks)
    final_a = final_a / max(1e-6, np.abs(final_a).max()) * 0.89
    wav_p = os.path.join(adir, "voice.wav")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", wav_p], stdin=subprocess.PIPE)
    p.communicate(final_a.astype(np.float32).tobytes())

    json.dump(words_out, open(os.path.join(adir, "words.json"), "w", encoding="utf-8"), indent=1)
    print(f"[free_voice] wrote {wav_p} ({len(final_a)/SR:.2f}s, {len(words_out)} words)")


if __name__ == "__main__":
    main()
