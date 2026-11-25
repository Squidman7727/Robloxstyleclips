"""Step 2. Draw the textures the 3D scene needs (plain Python + skia, about 1 second).
python rt_faces.py
Writes build/tex/faces.png (a 4x4 sheet of drawn faces, one cell per expression),
clock.png, nocoffee.png, alarm_*.png and posters.
The faces are flat drawings stuck on blocky heads, the same trick the real shorts use:
all the acting comes from swapping the face."""
import os, math, skia
HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(HERE, "build", "tex"); os.makedirs(TEX, exist_ok=True)
C = 512  # one face cell
# expression name -> cell index (row-major, row 0 at the TOP of the image)
FACES = ["happy", "scared", "sleepy", "asleep", "yawn", "shock", "smug", "stern",
         "blink", "wired", "c_tired", "c_yawn", "c_grin", "c_asleep", "dad_asleep", "mom"]
INK = skia.Color(22, 18, 28)
LID = [skia.Color(232, 190, 160)]  # eyelid colour = skin colour of whoever wears the face


def P(color, w=0, fill=True):
    p = skia.Paint(AntiAlias=True, Color=color)
    if not fill:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(w); p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def eye(c, x, y, r, iris, look=(0, 0), lid=0.0, pupil=0.5, bags=0, red=False, lash=False, low_lid=0.0, side=1):
    """A sharp anime-style eye (the style of Roblox face decals): tall oval, heavy upper lash line, big detailed iris.
    lid 0..1 closes from the top. pupil = iris size (small = shocked). bags = dark rings under the eye. side = -1 left, 1 right."""
    rx, ry = r * 0.86, r * 1.06
    if bags:
        for k in range(bags):
            path = skia.Path(); yy = y + ry * (1.02 + 0.3 * k)
            path.moveTo(x - rx * 0.95, yy - r * 0.1); path.quadTo(x, yy + r * 0.36, x + rx * 0.95, yy - r * 0.1)
            c.drawPath(path, P(skia.Color(96, 62, 120, 235), r * 0.1, False))
    oval = skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry)
    c.save(); clip = skia.Path(); clip.addOval(oval); c.clipPath(clip, doAntiAlias=True)
    c.drawPaint(P(skia.Color(250, 250, 252)))
    c.drawRect(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y - ry * 0.55), P(skia.Color(190, 196, 214)))   # shadow under the lash
    if red:
        for a in range(0, 360, 36):
            aa = math.radians(a + 13); pth = skia.Path()
            pth.moveTo(x + math.cos(aa) * rx * 1.05, y + math.sin(aa) * ry * 1.05)
            pth.quadTo(x + math.cos(aa + .35) * rx * .8, y + math.sin(aa + .35) * ry * .8, x + math.cos(aa - .1) * rx * .5, y + math.sin(aa - .1) * ry * .5)
            c.drawPath(pth, P(skia.Color(214, 48, 52), r * 0.04, False))
    ir = r * (0.3 + 0.52 * pupil); ix, iy = x + look[0] * rx * 0.4, y + look[1] * ry * 0.4 + r * 0.04
    dark = skia.Color(int(skia.ColorGetR(iris) * 0.45), int(skia.ColorGetG(iris) * 0.45), int(skia.ColorGetB(iris) * 0.5))
    c.drawCircle(ix, iy, ir, P(dark)); c.drawCircle(ix, iy + ir * 0.12, ir * 0.86, P(iris))
    lightc = skia.Color(min(255, skia.ColorGetR(iris) + 70), min(255, skia.ColorGetG(iris) + 60), min(255, skia.ColorGetB(iris) + 40))
    c.drawCircle(ix, iy + ir * 0.42, ir * 0.5, P(lightc))
    c.drawCircle(ix, iy, ir * 0.46, P(INK))
    c.drawCircle(ix - ir * 0.36, iy - ir * 0.4, ir * 0.3, P(skia.Color(255, 255, 255))); c.drawCircle(ix + ir * 0.34, iy + ir * 0.36, ir * 0.13, P(skia.Color(255, 255, 255, 230)))
    if lid > 0:
        yl = y - ry + 2 * ry * lid
        c.drawRect(skia.Rect.MakeLTRB(x - rx * 1.2, y - ry * 1.2, x + rx * 1.2, yl), P(LID[0])); c.drawLine(x - rx * 1.2, yl, x + rx * 1.2, yl, P(INK, r * 0.16, False))
    if low_lid > 0:
        yl = y + ry - 2 * ry * low_lid
        c.drawRect(skia.Rect.MakeLTRB(x - rx * 1.2, yl, x + rx * 1.2, y + ry * 1.2), P(LID[0])); c.drawLine(x - rx * 1.2, yl, x + rx * 1.2, yl, P(INK, r * 0.08, False))
    c.restore()
    c.drawOval(oval, P(INK, r * 0.07, False))
    if lid <= 0.02:   # heavy upper lash with a little wing on the outside
        lashp = skia.Path(); lashp.addArc(skia.Rect.MakeLTRB(x - rx * 1.03, y - ry * 1.04, x + rx * 1.03, y + ry * 1.0), 198, 144)
        c.drawPath(lashp, P(INK, r * 0.2, False))
        c.drawLine(x + side * rx * 0.92, y - ry * 0.42, x + side * rx * 1.28, y - ry * 0.74, P(INK, r * 0.14, False))
    if lash:
        for k in (0.55, 0.9): c.drawLine(x + side * rx * k, y - ry * (1.0 - 0.25 * k), x + side * rx * (k + 0.34), y - ry * (1.42 - 0.3 * k), P(INK, r * 0.1, False))


def closed(c, x, y, r, up=True, w=None):
    path = skia.Path(); s = -1 if up else 1
    path.moveTo(x - r, y); path.quadTo(x, y + s * r * 0.8, x + r, y)
    c.drawPath(path, P(INK, w or r * 0.2, False))


def brow(c, x, y, r, tilt, w=0.16):
    """A tapered brow: thick inside, thin outside."""
    path = skia.Path(); path.moveTo(x - r, y + tilt * r); path.quadTo(x, y - r * 0.12, x + r, y - tilt * r)
    c.drawPath(path, P(INK, r * w, False))


def mouth_arc(c, x, y, w, h, wd=10):
    path = skia.Path(); path.moveTo(x - w, y); path.quadTo(x, y + h, x + w, y)
    c.drawPath(path, P(INK, wd, False))


def mouth_open(c, x, y, w, h, tongue=True, teeth=False):
    r = skia.Rect.MakeLTRB(x - w, y - h, x + w, y + h)
    c.drawOval(r, P(skia.Color(96, 22, 36)))
    c.save(); clip = skia.Path(); clip.addOval(r); c.clipPath(clip, doAntiAlias=True)
    if tongue: c.drawCircle(x, y + h * 1.0, w * 0.8, P(skia.Color(226, 96, 110)))
    if teeth: c.drawRect(skia.Rect.MakeLTRB(x - w, y - h, x + w, y - h * 0.5), P(skia.Color(250, 250, 250)))
    c.restore()
    c.drawOval(r, P(INK, 9, False))


def grin(c, x, y, w, h):
    path = skia.Path(); path.moveTo(x - w, y - h * 0.2); path.quadTo(x, y + h * 0.2, x + w, y - h * 0.2)
    path.quadTo(x, y + h * 1.9, x - w, y - h * 0.2); path.close()
    c.drawPath(path, P(skia.Color(250, 250, 250))); c.drawPath(path, P(INK, 9, False))


def draw_face(c, name):
    LID[0] = skia.Color(188, 184, 210) if name.startswith("c_") else skia.Color(232, 190, 160)
    L, R, EY, r = 168, 344, 236, 64  # eye centres
    blue = skia.Color(60, 150, 235); brown = skia.Color(130, 82, 46); green = skia.Color(60, 170, 110); violet = skia.Color(160, 120, 235)
    def eyes(col=blue, rr=1.0, **kw):
        eye(c, L, EY, r * rr, col, side=-1, **kw); eye(c, R, EY, r * rr, col, side=1, **kw)
    if name == "happy":
        eyes(); brow(c, L, EY - 100, 46, 0.12); brow(c, R, EY - 100, 46, -0.12); grin(c, 256, 378, 70, 36)
    elif name == "mom":
        eyes(green, 0.95, lash=True); brow(c, L, EY - 100, 44, 0.16, .12); brow(c, R, EY - 100, 44, -0.16, .12); mouth_arc(c, 256, 380, 46, 30)
    elif name == "blink":
        closed(c, L, EY + 12, r * .8, up=False, w=11); closed(c, R, EY + 12, r * .8, up=False, w=11); mouth_arc(c, 256, 380, 44, 26)
    elif name == "scared":
        eyes(blue, 1.1, pupil=0.12); brow(c, L, EY - 112, 50, -0.34); brow(c, R, EY - 112, 50, 0.34)
        path = skia.Path(); path.moveTo(196, 392)
        for i in range(6): path.lineTo(196 + (i + 1) * 20, 392 + (11 if i % 2 == 0 else -11))
        c.drawPath(path, P(INK, 9, False))
        for k in range(3): c.drawLine(96 + k * 16, 150 + k * 4, 96 + k * 16, 196 + k * 6, P(skia.Color(70, 90, 160, 200), 5, False))
    elif name == "sleepy":
        eyes(blue, 1.0, lid=0.5, look=(0, .3), bags=1); c.drawLine(226, 388, 290, 388, P(INK, 10, False))
    elif name == "asleep":
        closed(c, L, EY + 8, r * .8, w=11); closed(c, R, EY + 8, r * .8, w=11)
        c.drawOval(skia.Rect.MakeLTRB(238, 366, 276, 410), P(skia.Color(96, 22, 36))); c.drawOval(skia.Rect.MakeLTRB(238, 366, 276, 410), P(INK, 8, False))
    elif name == "dad_asleep":
        closed(c, L, EY + 4, r * .8, w=11); closed(c, R, EY + 4, r * .8, w=11); brow(c, L, EY - 84, 50, 0.1, .22); brow(c, R, EY - 84, 50, -0.1, .22)
        c.drawOval(skia.Rect.MakeLTRB(236, 398, 276, 446), P(skia.Color(96, 22, 36))); c.drawOval(skia.Rect.MakeLTRB(236, 398, 276, 446), P(INK, 8, False))
        m = skia.Path(); m.moveTo(256, 352); m.cubicTo(214, 326, 150, 346, 128, 396); m.cubicTo(170, 378, 220, 386, 256, 374)
        m.cubicTo(292, 386, 342, 378, 384, 396); m.cubicTo(362, 346, 298, 326, 256, 352); m.close()
        c.drawPath(m, P(skia.Color(70, 44, 28))); c.drawPath(m, P(INK, 7, False))
    elif name == "yawn":
        closed(c, L, EY, r * .76, up=False, w=14); closed(c, R, EY, r * .76, up=False, w=14)
        brow(c, L, EY - 84, 46, 0.25); brow(c, R, EY - 84, 46, -0.25); mouth_open(c, 256, 384, 58, 70)
    elif name == "shock":
        eyes(blue, 1.16, pupil=0.06); brow(c, L, EY - 122, 50, -0.38); brow(c, R, EY - 122, 50, 0.38); mouth_open(c, 256, 404, 44, 50, tongue=True)
        for k in range(3): c.drawLine(92 + k * 16, 140 + k * 4, 92 + k * 16, 190 + k * 6, P(skia.Color(70, 90, 160, 200), 5, False))
    elif name == "smug":
        eyes(blue, 1.0, lid=0.36, look=(.5, .1)); brow(c, L, EY - 92, 46, 0.2); brow(c, R, EY - 100, 46, 0.1)
        path = skia.Path(); path.moveTo(208, 384); path.quadTo(266, 414, 312, 368); c.drawPath(path, P(INK, 10, False))
    elif name == "stern":
        eyes(brown, 0.94, lid=0.26, pupil=.36); brow(c, L, EY - 74, 58, -0.44, .3); brow(c, R, EY - 74, 58, 0.44, .3); mouth_arc(c, 256, 408, 50, -30)
    elif name == "wired":
        eyes(blue, 1.14, pupil=0.1, bags=2, red=True); brow(c, L, EY - 118, 48, -0.2); brow(c, R, EY - 118, 48, 0.2)
        path = skia.Path(); path.moveTo(218, 418)
        for i in range(4): path.lineTo(218 + (i + 1) * 19, 418 + (8 if i % 2 == 0 else -8))
        c.drawPath(path, P(INK, 9, False))
    elif name == "c_tired":
        eye(c, L, EY, r * 1.08, violet, lid=0.56, look=(0, .45), pupil=.3, bags=3, red=True, side=-1); eye(c, R, EY, r * 1.08, violet, lid=0.62, look=(0, .45), pupil=.3, bags=3, red=True)
        brow(c, L, EY - 96, 50, -0.3, .12); brow(c, R, EY - 96, 50, 0.3, .12); mouth_arc(c, 256, 440, 44, -22, 9)
    elif name == "c_yawn":
        closed(c, L, EY, r * .9, up=False, w=14); closed(c, R, EY, r * .9, up=False, w=14)
        for k in range(3):
            for X in (L, R):
                p2 = skia.Path(); yy = EY + 44 + 20 * k; p2.moveTo(X - 58, yy - 6); p2.quadTo(X, yy + 22, X + 58, yy - 6)
                c.drawPath(p2, P(skia.Color(96, 62, 120), 8, False))
        mouth_open(c, 256, 418, 62, 72, teeth=True)
    elif name == "c_grin":
        eye(c, L, EY, r * 1.08, violet, lid=0.42, look=(0, .2), pupil=.3, bags=3, red=True, side=-1); eye(c, R, EY, r * 1.08, violet, lid=0.42, look=(0, .2), pupil=.3, bags=3, red=True)
        grin(c, 256, 420, 104, 34)
        for i in range(1, 7): c.drawLine(152 + i * 30, 414, 152 + i * 30, 462, P(INK, 5, False))
    elif name == "c_asleep":
        closed(c, L, EY + 8, r * .9, w=12); closed(c, R, EY + 8, r * .9, w=12)
        for X in (L, R):
            p2 = skia.Path(); yy = EY + 50; p2.moveTo(X - 58, yy - 6); p2.quadTo(X, yy + 22, X + 58, yy - 6)
            c.drawPath(p2, P(skia.Color(96, 62, 120), 8, False))
        mouth_arc(c, 256, 410, 56, 36, 9)


def faces():
    s = skia.Surface(C * 4, C * 4); c = s.getCanvas(); c.clear(skia.Color(0, 0, 0, 0))
    for i, n in enumerate(FACES):
        c.save(); c.translate((i % 4) * C, (i // 4) * C); c.clipRect(skia.Rect.MakeWH(C, C)); draw_face(c, n); c.restore()
    s.makeImageSnapshot().save(os.path.join(TEX, "faces.png"), skia.kPNG)


def font(size, name="Arial Black"):
    import os
    for fp in ("/usr/share/fonts/opentype/inter/Inter-Black.otf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(fp):
            return skia.Font(skia.Typeface.MakeFromFile(fp), size)
    return skia.Font(skia.Typeface(name, skia.FontStyle.Bold()), size)


def clock():
    S = 1024; s = skia.Surface(S, S); c = s.getCanvas(); c.clear(skia.Color(250, 244, 228))
    c.drawCircle(S / 2, S / 2, S / 2 - 14, P(INK, 28, False))
    f = font(120)
    for h in range(1, 13):
        a = math.radians(h * 30 - 90); x = S / 2 + math.cos(a) * 385; y = S / 2 + math.sin(a) * 385
        t = str(h); w = f.measureText(t); c.drawString(t, x - w / 2, y + 42, f, P(INK))
    for m in range(60):
        if m % 5:
            a = math.radians(m * 6); c.drawLine(S / 2 + math.cos(a) * 478, S / 2 + math.sin(a) * 478, S / 2 + math.cos(a) * 458, S / 2 + math.sin(a) * 458, P(INK, 6, False))
    s.makeImageSnapshot().save(os.path.join(TEX, "clock.png"), skia.kPNG)


def sign(name, lines, bg, fg, w=1024, h=512, ban=False, size=150):
    s = skia.Surface(w, h); c = s.getCanvas(); c.clear(bg)
    c.drawRect(skia.Rect.MakeLTRB(14, 14, w - 14, h - 14), P(fg, 20, False))
    f = font(size); y0 = h / 2 - (len(lines) - 1) * size * 0.55 + size * 0.36
    for i, t in enumerate(lines):
        tw = f.measureText(t); c.drawString(t, w / 2 - tw / 2, y0 + i * size * 1.1, f, P(fg))
    if ban:
        c.drawCircle(w / 2, h / 2, h * 0.42, P(skia.Color(230, 30, 40), 44, False))
        c.drawLine(w / 2 - h * 0.3, h / 2 - h * 0.3, w / 2 + h * 0.3, h / 2 + h * 0.3, P(skia.Color(230, 30, 40), 44, False))
    s.makeImageSnapshot().save(os.path.join(TEX, name + ".png"), skia.kPNG)


def cup_sign():
    S = 1024; s = skia.Surface(S, S); c = s.getCanvas(); c.clear(skia.Color(255, 255, 255))
    cup = skia.Path(); cup.moveTo(330, 330); cup.lineTo(690, 330); cup.lineTo(640, 760); cup.lineTo(380, 760); cup.close()
    c.drawPath(cup, P(skia.Color(120, 78, 48))); c.drawPath(cup, P(INK, 26, False))
    c.drawRoundRect(skia.Rect.MakeLTRB(300, 270, 720, 340), 24, 24, P(skia.Color(245, 245, 245))); c.drawRoundRect(skia.Rect.MakeLTRB(300, 270, 720, 340), 24, 24, P(INK, 26, False))
    for x in (430, 510, 590):
        p = skia.Path(); p.moveTo(x, 235); p.cubicTo(x - 40, 190, x + 40, 160, x, 110); c.drawPath(p, P(INK, 20, False))
    red = skia.Color(232, 28, 40)
    c.drawCircle(S / 2, S / 2, 440, P(red, 90, False)); c.drawLine(S / 2 - 310, S / 2 - 310, S / 2 + 310, S / 2 + 310, P(red, 90, False))
    s.makeImageSnapshot().save(os.path.join(TEX, "nocoffee.png"), skia.kPNG)


def alarm(name, text):
    s = skia.Surface(512, 256); c = s.getCanvas(); c.clear(skia.Color(12, 10, 14))
    f = font(170); tw = f.measureText(text); c.drawString(text, 256 - tw / 2, 188, f, P(skia.Color(255, 60, 50)))
    s.makeImageSnapshot().save(os.path.join(TEX, name + ".png"), skia.kPNG)


def poster(name, bg, kind):
    s = skia.Surface(512, 720); c = s.getCanvas(); c.clear(bg)
    if kind == "rocket":
        for (x, y, r) in [(90, 120, 9), (400, 90, 7), (430, 560, 10), (70, 600, 6), (250, 60, 5), (140, 330, 6), (420, 300, 8)]: c.drawCircle(x, y, r, P(skia.Color(255, 255, 255)))
        b = skia.Path(); b.moveTo(256, 150); b.cubicTo(350, 260, 340, 430, 320, 520); b.lineTo(192, 520); b.cubicTo(172, 430, 162, 260, 256, 150); b.close()
        c.drawPath(b, P(skia.Color(245, 245, 250))); c.drawPath(b, P(INK, 14, False)); c.drawCircle(256, 330, 42, P(skia.Color(80, 180, 255))); c.drawCircle(256, 330, 42, P(INK, 12, False))
        for sgn in (-1, 1):
            fin = skia.Path(); fin.moveTo(256 + sgn * 64, 440); fin.lineTo(256 + sgn * 130, 560); fin.lineTo(256 + sgn * 64, 520); fin.close(); c.drawPath(fin, P(skia.Color(240, 70, 60))); c.drawPath(fin, P(INK, 12, False))
        fl = skia.Path(); fl.moveTo(210, 525); fl.lineTo(256, 660); fl.lineTo(302, 525); fl.close(); c.drawPath(fl, P(skia.Color(255, 180, 40))); c.drawPath(fl, P(INK, 12, False))
    else:
        c.drawCircle(256, 300, 150, P(skia.Color(255, 214, 80))); c.drawCircle(256, 300, 150, P(INK, 14, False))
        closed(c, 200, 280, 34); closed(c, 312, 280, 34); mouth_arc(c, 256, 340, 50, 40)
        f = font(74); t = "SLEEP!"; tw = f.measureText(t); c.drawString(t, 256 - tw / 2, 600, f, P(skia.Color(255, 255, 255)))
    c.drawRect(skia.Rect.MakeLTRB(8, 8, 504, 712), P(skia.Color(255, 255, 255), 16, False))
    s.makeImageSnapshot().save(os.path.join(TEX, name + ".png"), skia.kPNG)


if __name__ == "__main__":
    faces(); clock(); cup_sign()
    alarm("alarm_late", "2:47"); alarm("alarm_nine", "9:00")
    sign("lightsout", ["LIGHTS OUT", "9:00"], skia.Color(25, 40, 95), skia.Color(255, 225, 90), size=140)
    sign("nothankyou", ["THANK", "YOU"], skia.Color(250, 250, 252), INK, w=1024, h=1024, ban=True, size=220)
    _cs = [p.strip() for p in os.environ.get("CUSTOM_SIGN_TEXT", "THANK|YOU").split("|") if p.strip()] or ["NO", "RULE"]
    sign("custom_sign", _cs, skia.Color(250, 250, 252), INK, w=1024, h=1024, ban=True, size=210)
    poster("poster_rocket", skia.Color(40, 50, 120), "rocket"); poster("poster_sleep", skia.Color(90, 60, 170), "moon")
    print("textures in", TEX)
