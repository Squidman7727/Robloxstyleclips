"""Step 4. Finish: glow + colour, captions, the hook's speed lines, flashes on a few cuts, then the mp4 with the voice.
python rt_finish.py stories/<story>.json [--preview]
Reads build/frames/f_#####.jpg, build/words.json, build/shots.json, build/vo.wav. Writes build/FINAL.mp4.
Captions follow the real shorts: two or three words at a time, heavy white letters with a black edge,
the word being spoken turns yellow, sitting just under the middle of the screen."""
import sys, os, json, subprocess, re, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); BUILD = os.path.join(HERE, "build")
FONT = next((p for p in (r"C:\Windows\Fonts\seguibl.ttf", "/usr/share/fonts/opentype/inter/Inter-Black.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf") if os.path.exists(p)), "DejaVuSans-Bold.ttf")


def cards(words, max_words=3, max_chars=15):
    """Group words into caption cards: never across a shot or a sentence end."""
    out = []; cur = []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        text_len = sum(len(x["word"]) for x in cur) + len(cur) - 1
        end = (nxt is None or nxt["shot"] != w["shot"] or re.search(r"[.!?,…]$", w["word"]) or len(cur) >= max_words
               or text_len + 1 + len(nxt["word"]) > max_chars)
        if end: out.append(cur); cur = []
    return out


class Captions:
    def __init__(self, words, W, H, total):
        self.W, self.H = W, H; self.size = int(W * 0.074); self.font = ImageFont.truetype(FONT, self.size)
        self.cards = cards(words); self.cache = {}
        self.times = []
        for i, c in enumerate(self.cards):
            t0 = c[0]["t0"] - 0.03; t1 = self.cards[i + 1][0]["t0"] - 0.03 if i + 1 < len(self.cards) else total
            self.times.append((t0, min(t1, c[-1]["t1"] + 0.45)))

    def _render(self, ci, active):
        key = (ci, active)
        if key in self.cache: return self.cache[key]
        c = self.cards[ci]; f = self.font; pad = 40
        txt = [re.sub(r"[.,…]+$", "", w["word"]) for w in c]
        space = f.getlength(" "); widths = [f.getlength(t) for t in txt]
        # wrap onto two lines if too wide
        lines = [[]]; lw = 0
        for i, wd in enumerate(widths):
            if lines[-1] and lw + space + wd > self.W * 0.86: lines.append([]); lw = 0
            lines[-1].append(i); lw += wd + (space if len(lines[-1]) > 1 else 0)
        lh = int(self.size * 1.12); tw = int(max(sum(widths[i] for i in ln) + space * (len(ln) - 1) for ln in lines)) + pad * 2; th = lh * len(lines) + pad * 2
        img = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        sw = max(5, int(self.size * 0.09))
        for li, ln in enumerate(lines):
            x = (tw - (sum(widths[i] for i in ln) + space * (len(ln) - 1))) / 2; y = pad + li * lh - self.size * 0.12
            for i in ln:
                col = (255, 232, 30, 255) if i == active else (255, 255, 255, 255)
                d.text((x + 5, y + 7), txt[i], font=f, fill=(0, 0, 0, 150), stroke_width=sw, stroke_fill=(0, 0, 0, 150))
                d.text((x, y), txt[i], font=f, fill=col, stroke_width=sw, stroke_fill=(0, 0, 0, 255))
                x += widths[i] + space
        a = np.asarray(img).astype(np.float32) / 255.0
        self.cache[key] = a; return a

    def draw(self, frame, t):
        for ci, (t0, t1) in enumerate(self.times):
            if t0 <= t < t1:
                c = self.cards[ci]; active = -1
                for i, w in enumerate(c):
                    if t >= w["t0"] - 0.03: active = i
                a = self._render(ci, active)
                k = min(1.0, (t - t0) / 0.07); sc = 0.82 + 0.18 * (1 - (1 - k) ** 3) + 0.05 * math.sin(k * math.pi)
                if abs(sc - 1) > 0.004: a = cv2.resize(a, None, fx=sc, fy=sc, interpolation=cv2.INTER_LINEAR)
                h, w = a.shape[:2]; cx, cy = self.W // 2, int(self.H * 0.68)
                x0, y0 = cx - w // 2, cy - h // 2
                x1, y1 = max(0, x0), max(0, y0); x2, y2 = min(self.W, x0 + w), min(self.H, y0 + h)
                sub = a[y1 - y0:y2 - y0, x1 - x0:x2 - x0]
                reg = frame[y1:y2, x1:x2]; al = sub[..., 3:4]
                reg[:] = reg * (1 - al) + sub[..., 2::-1] * 255.0 * al
                return


VIG = {}


def grade(f, glow=0.34, sat=0.97, contrast=1.1, lift=0.9):
    """Roblox-style finish: soft bloom on bright parts, a firmer contrast curve, a slight dark vignette and a hint of colour fringing at the edges."""
    f = 255.0 * (f / 255.0) ** lift           # open the shadows a little (night shots)
    small = cv2.resize(f, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    lum = small.max(axis=2, keepdims=True); bright = small * np.clip((lum - 185.0) / 60.0, 0, 1)
    b = cv2.GaussianBlur(bright, (0, 0), 9) * 0.6 + cv2.GaussianBlur(bright, (0, 0), 26) * 0.6
    f = f + cv2.resize(b, (f.shape[1], f.shape[0]), interpolation=cv2.INTER_LINEAR) * glow
    g = f.mean(axis=2, keepdims=True); f = g + (f - g) * sat
    f = (f - 122.0) * contrast + 126.0
    h, w = f.shape[:2]
    if (h, w) not in VIG:
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2) / 1.414
        VIG[(h, w)] = (1.0 - 0.2 * np.clip(r - 0.45, 0, 1) ** 1.5 * 2.2)[..., None]
    f = f * VIG[(h, w)]
    s = max(1, int(w * 0.0016))   # tiny red/blue split, strongest feel at the edges
    f[..., 2] = np.roll(f[..., 2], s, axis=1); f[..., 0] = np.roll(f[..., 0], -s, axis=1)
    return f


def speed_lines(W, H, seed, n=46):
    rng = np.random.default_rng(seed); img = Image.new("L", (W, H), 0); d = ImageDraw.Draw(img); cx, cy = W / 2, H * 0.42
    for i in range(n):
        a = rng.uniform(0, 2 * math.pi); r0 = rng.uniform(0.36, 0.62) * H; r1 = H * 1.3; wd = rng.uniform(0.005, 0.016)
        p = [(cx + math.cos(a - wd) * r1, cy + math.sin(a - wd) * r1), (cx + math.cos(a + wd) * r1, cy + math.sin(a + wd) * r1), (cx + math.cos(a) * r0, cy + math.sin(a) * r0)]
        d.polygon(p, fill=255)
    return np.asarray(img).astype(np.float32)[..., None] / 255.0


def main(story_path, preview=False):
    story = json.load(open(story_path, encoding="utf-8")); fps = int(story.get("fps", 30)); total = float(story.get("seconds", 20))
    words = json.load(open(os.path.join(BUILD, "words.json"), encoding="utf-8"))["words"]
    shots = json.load(open(os.path.join(BUILD, "shots.json")))
    fx = story.get("fx", {})
    first = cv2.imread(os.path.join(BUILD, "frames", "f_00000.jpg")); H, W = first.shape[:2]
    caps = Captions(words, W, H, total)
    n = int(round(total * fps)); out = os.path.join(BUILD, "preview.mp4" if preview else "FINAL.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-i", os.path.join(BUILD, "vo.wav"),
           "-c:v", "libx264", "-preset", "medium" if not preview else "veryfast", "-crf", "16" if not preview else "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-af", f"apad=whole_dur={total}", "-t", str(total), "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hook_end = shots[1]["t0"] if len(shots) > 1 else 0.8
    flashes = [s["t0"] for s in shots if s["id"] in fx.get("flash_into", [])]
    lines = [speed_lines(W, H, i) for i in range(3)]
    last = None; missing = 0
    for i in range(n):
        t = i / fps; fp = os.path.join(BUILD, "frames", f"f_{i:05d}.jpg")
        fr = cv2.imread(fp)
        if fr is None: fr = last; missing += 1
        last = fr
        f = grade(fr.astype(np.float32))
        if fx.get("speed_lines", True) and t < hook_end:
            k = 1.0 - max(0.0, (t - hook_end * 0.55) / (hook_end * 0.45)); f = f * (1 - lines[(i // max(1, fps // 15)) % 3] * 0.85 * k) + 255.0 * lines[(i // max(1, fps // 15)) % 3] * 0.85 * k
        for ft in flashes:
            if 0 <= t - ft < 0.1: f = f + (255.0 - f) * 0.75 * (1 - (t - ft) / 0.1)
        caps.draw(f, t)
        p.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    p.stdin.close(); p.wait()
    print(f"wrote {out}  ({n} frames, {missing} missing)")


if __name__ == "__main__":
    main(os.path.join(HERE, sys.argv[1]) if not os.path.isabs(sys.argv[1]) else sys.argv[1], "--preview" in sys.argv)
