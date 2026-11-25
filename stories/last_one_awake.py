"""The scene file for "In This Town, Never Be The Last One Awake".
build() makes the cast and the sets once. Then one function per shot id (the ids in the .json),
called once per frame with t = seconds since the shot started and T = how long the shot lasts.
Every shot sets: the lighting mood, who is on screen, where the camera is, and each character's pose and face."""
import math
import rt_engine as E
from rt_engine import M, lerp, lerp3, ease, ease_out, ease_in, ramp, pop, wig, clamp

BR = (0, 300, 0)   # bedroom origin
LV = (0, 500, 0)   # living room origin
HERO_HOUSE = 11    # which house on the street is ours


class Ctx: pass


def build():
    C = Ctx()
    C.street = E.Street()
    C.bed = E.Room("bedroom", BR, wall=(120, 150, 176), floor=(150, 100, 62)); C.blanket = C.bed.bed(); C.bed.nightstand(); C.bed.bedroom_bits()
    C.liv = E.Room("living", LV, wall=(188, 170, 140), floor=(128, 86, 56), yard=False); C.liv.living_bits()
    Ch = E.Char
    C.hero = Ch("hero", (26, 28, 34), (58, 62, 78), scale=0.88).hair("spiky", (196, 30, 44)).jacket((196, 30, 44))
    C.hero.extra("hood", (20, 22, 28), (1.5, 0.5, 0.5), (0, 0.42, 1.85), bevel=0.16, tex="fabric")
    C.mom = Ch("mom", (150, 60, 90), (40, 44, 60), skin=(206, 160, 124)).hair("long", (44, 30, 36), seed=3).jacket((232, 226, 214))
    C.dad = Ch("dad", (70, 98, 150), (70, 98, 150), skin=(206, 160, 124), shoes=(120, 90, 70), sole=(70, 50, 40)).hair("nightcap", (60, 84, 160), (230, 230, 236)).stripes((212, 216, 228))
    C.cop = Ch("cop", (30, 42, 84), (22, 28, 54), skin=(140, 96, 70), shoes=(20, 20, 24)).hair("copcap", (22, 28, 54), (236, 196, 60))
    C.cop.extra("badge2", (236, 196, 60), (0.4, 0.1, 0.45), (0.5, -0.5, 1.45)); C.cop.extra("belt", (14, 14, 18), (2.04, 1.04, 0.28), (0, 0, 0.2), bevel=0.02)
    C.man = Ch("man", (226, 226, 230), (50, 46, 52), shoes=(40, 30, 26)).hair("short", (50, 36, 28), seed=5); C.man.extra("tie", (176, 36, 44), (0.34, 0.1, 1.3), (0, -0.5, 1.2))
    looks = [((150, 40, 44), (40, 44, 60), "short", (36, 28, 24), (232, 190, 160)), ((60, 110, 80), (70, 60, 52), "bun", (196, 150, 70), (206, 160, 124)),
             ((210, 130, 50), (44, 50, 80), "long", (120, 44, 36), (232, 190, 160)), ((90, 70, 150), (28, 28, 34), "spiky", (24, 24, 30), (140, 96, 70)),
             ((220, 220, 224), (50, 80, 130), "bun", (60, 40, 30), (110, 74, 56)), ((60, 120, 170), (80, 80, 90), "long", (214, 190, 110), (232, 190, 160))]
    C.town = [Ch(f"t{i}", sh, pa, skin=sk, scale=0.96 + 0.05 * (i % 2)).hair(hs, hc, seed=i + 10) for i, (sh, pa, hs, hc, sk) in enumerate(looks)]
    C.town[0].jacket((230, 230, 230)); C.town[3].jacket((210, 190, 60))
    C.cr = Ch("creature", (40, 58, 70), (40, 58, 70), skin=E.PALE, tall=True, shoes=(188, 184, 210), sole=(150, 146, 176)).hair("nightcap", (40, 58, 70), (200, 200, 214))
    C.cr.extra("b1", (200, 200, 214), (0.2, 0.1, 0.2), (0, -0.48, 2.0), bevel=0.06); C.cr.extra("b2", (200, 200, 214), (0.2, 0.1, 0.2), (0, -0.48, 1.3), bevel=0.06)
    # props (always in the "fx" collection; parked far away when not used)
    fx = E.coll("fx"); C.props = []
    zin = M("z_in", (255, 255, 255), emit=(235, 242, 255), emit_k=1.0); zout = M("z_out", (20, 24, 40))
    C.zs = []
    for i in range(3):
        z = E.text3d(f"z{i}", "Z", zin, fx, size=1.0, depth=0.1); o = E.text3d(f"zo{i}", "Z", zout, fx, size=1.0, depth=0.06, parent=z)
        o.rotation_euler = (0, 0, 0); o.location = (0, 0, -0.07); o.data.offset = 0.07
        C.zs.append(z); C.props.append(z)
    C.bubble = E.part("bubble", M("bubble", (190, 232, 255), rough=0.08, emit=(170, 225, 255), emit_k=0.5), fx, ball=1.0); C.props.append(C.bubble)
    # book: two covers on a spine
    C.book = E.empty("book", fx); C.props.append(C.book); C.pages = []
    for sx in (-1, 1):
        hinge = E.empty(f"bookh{sx}", fx, C.book)
        E.part(f"bookc{sx}", M("bookcover", (140, 36, 44), tex="noise"), fx, (1.25, 0.12, 1.7), parent=hinge, inner=(sx * 0.62, 0, 0), bevel=0.04)
        E.part(f"bookp{sx}", M("bookpage", (255, 252, 240)), fx, (1.12, 0.14, 1.54), parent=hinge, inner=(sx * 0.6, -0.06, 0), bevel=0.03)
        C.pages.append((hinge, sx))
    # coffee cups
    def cup(name, parent):
        root = E.empty(name, parent.c, parent.hand_pos("R")); root.rotation_euler = (E.D(-90), 0, 0); root.location = (0, -0.75, 0.15)
        ms = E.Mesher().cyl(0.36, 1.0, (0, 0, 0.5), r2=0.46); ms.make(name + "_b", M("cup", (250, 250, 250)), parent.c, True, root)
        E.Mesher().cyl(0.44, 0.42, (0, 0, 0.5), r2=0.47).make(name + "_s", M("cupsleeve", (150, 100, 60)), parent.c, True, root)
        E.Mesher().cyl(0.5, 0.14, (0, 0, 1.05)).make(name + "_l", M("cuplid", (60, 50, 50)), parent.c, True, root)
        return root
    C.cup_man = cup("cup_man", C.man); C.cup_hero = cup("cup_hero", C.hero)
    # the NO COFFEE sign on the street
    sx = E.coll("signs"); st = E.Static(sx); st.cyl(M("pole", (52, 54, 62)), 0.16, 7.0, (3.0, -10.6, 3.5)); st.done("signpole")
    E.picture("nocoffee", "nocoffee", sx, 3.4, 3.4, (3.0, -10.5, 7.2), yaw=118, thick=0.2, back=(250, 250, 250))
    # spare lights + a moon for the street
    L = E.coll("lights")
    C.L1 = E.point_light("L1", L, (0, 0, -100), (255, 255, 255), 0.0, radius=0.8); C.L2 = E.point_light("L2", L, (0, 0, -100), (255, 255, 255), 0.0, radius=0.8, shadow=False)
    C.moon = E.part("street_moon", M("moon", (255, 250, 225), emit=(255, 248, 215), emit_k=3.0), fx, ball=16.0); C.moon.visible_shadow = False; C.props.append(C.moon)
    C.always = ("fx", "lights")
    return C


def reset(C):
    """Called before every frame: park the props, switch the spare lights off, show all walls."""
    for p in C.props: E.gone(p)
    for l in (C.L1, C.L2): l.data.energy = 0.0
    C.bed.show(); C.liv.show(); C.bed.lamp_on(0.0)
    C.blanket.location = C.bed.P(0, 0.95, 2.8); C.blanket.rotation_euler = (0, 0, 0)
    C.cup_hero.scale = (0.001,) * 3; C.cup_man.scale = (1,) * 3


def light(l, pos, rgb, watts):
    l.location = pos; l.data.color = E.lin(rgb)[:3]; l.data.energy = watts


def zzz(C, t, base, drift=(1.6, 0.0, 2.4), yaw=0.0, size=1.0, period=1.1):
    """Three Z's floating up and growing, one after the other."""
    for i, z in enumerate(C.zs):
        u = ((t / period) + i / 3.0) % 1.0
        E.put(z, (base[0] + drift[0] * u + 0.25 * math.sin(u * 7 + i), base[1] + drift[1] * u, base[2] + drift[2] * u), size * (0.45 + 0.9 * u) * min(1.0, u * 8, (1 - u) * 6), (90, 12 * math.sin(u * 5), yaw))


def book(C, pos, yaw, open_k):
    E.put(C.book, pos, 1.0, (0, 0, yaw))
    for hinge, sx in C.pages: hinge.rotation_euler = (0, 0, E.D(-sx * 88 * (1 - open_k)))


def yaw_to(dx, dy): return math.degrees(math.atan2(dx, -dy))


def B(x, y, z=0.0): return (BR[0] + x, BR[1] + y, BR[2] + z)
def V(x, y, z=0.0): return (LV[0] + x, LV[1] + y, LV[2] + z)


# ------------------------------------------------------------------ the shots
def hook(C, t, T):
    """In this town,  -- starts tight on the hero's face, whips back to show the whole street."""
    E.mood("day"); C.street.day(); E.use("street", "signs", "hero", "t0", "t1", "t2", "t3", *C.always)
    h = C.hero; h.at(-10, 0, 0, yaw=-90); h.face("wired")
    a = pop(t, 0.06, 0.25)
    h.pose(head=(0, 0, wig(t, 7, 2.5)), aL=(0, 62 * a), aR=(0, 62 * a), bob=0.1 * abs(wig(t, 5)))
    for i, (x0, y, d) in enumerate(((6, 8.2, 1), (26, -8.0, -1), (44, 8.0, -1), (-4, -8.3, 1))):
        p = C.town[i]; x = x0 + d * 4.5 * t; p.at(x, y, 0.25, yaw=90 * d); p.walk(x * 1.3); p.face("happy", t + i)
    k = ease_out(ramp(t, 0.14, 0.82))
    E.cam(lerp3((-15.4, 0.1, 4.3), (-47, -2.5, 19), k), lerp3((-10, 0, 3.75), (22, 0, 7.5), k), lerp(31, 58, k))


def rule(C, t, T):
    """you must never be the last one awake.  -- one lit window in a dark street, and something tall waiting outside it."""
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.22, per={HERO_HOUSE: 1.0}); E.use("street", "creature", *C.always)
    E.put(C.moon, (-150, 330, 150), 0.7)
    cr = C.cr; cr.at(-10.0, 11.6, 0.0, yaw=176); cr.face("c_tired")
    cr.pose(head=(6, 0, wig(t, 0.5, 7)), lean=(3, 0, wig(t, 0.4, 2.5)), aL=(4, 5), aR=(4, 5))
    light(C.L1, (-12.8, 13.4, 3.4), (255, 200, 120), 420); light(C.L2, (-9, 6, 7), (120, 150, 255), 380)
    k = ease(ramp(t, 0.0, T))
    E.cam(lerp3((-9.5, -9.5, 2.2), (-10.6, -0.5, 2.9), k), lerp3((-12.6, 15.5, 5.6), (-11.4, 15.5, 4.7), k), lerp(52, 46, k))


def clock(C, t, T):
    """Every night at nine,  -- low under the town clock as the hand snaps to nine."""
    E.mood("dusk"); C.street.lights_set(windows=0.9, lamps=0.7); E.use("street", *C.always)
    snap = pop(t, 0.36, 0.2)
    C.street.clock_time(8.0 + (57 + 3 * snap) / 60.0 if snap < 1 else 9.0)
    sh = 0.35 * math.exp(-max(0, t - 0.4) * 7) * math.sin(t * 60) if t > 0.4 else 0
    k = ease_out(ramp(t, 0, T))
    E.cam((lerp(46, 55, k), 9.0, 2.4 + sh), (86.1, 0.0 + sh, lerp(24.5, 27.0, k)), lerp(48, 40, k))


def race(C, t, T):
    """the whole town races to fall asleep.  -- from above: everyone sprinting for their own front door."""
    E.mood("dusk"); C.street.lights_set(windows=0.9, lamps=0.7); C.street.clock_time(9.0)
    E.use("street", "signs", "t0", "t1", "t2", "t3", "t4", "t5", "mom", "dad", *C.always)
    runs = [(C.town[0], (14, 2), 5, 0.0), (C.town[1], (22, -3), 13, 0.05), (C.town[2], (30, 3), 6, 0.1), (C.town[3], (8, -2), 12, 0.0),
            (C.town[4], (38, 0), 14, 0.12), (C.town[5], (25, 4), 5, 0.2), (C.mom, (4, 1), 4, 0.08), (C.dad, (18, -4), 12, 0.16)]
    for i, (p, (x0, y0), hi, d) in enumerate(runs):
        hx, hy, face = C.street.houses[hi]; tx, ty = hx - 3.2, hy + face * 4.6
        dist = math.hypot(tx - x0, ty - y0); go = clamp((t - d) * 9.0 / dist)
        x, y = lerp(x0, tx, go), lerp(y0, ty, go)
        p.at(x, y, 0.1, yaw=yaw_to(tx - x0, ty - y0)); p.run((t - d) * 19 + i, head=(-8, 0, 0)); p.face("shock" if i % 3 else "scared")
    k = ease(ramp(t, 0, T))
    E.cam((lerp(-8, -3, k), 0.5, lerp(27, 25, k)), (lerp(20, 23, k), 0, 0), 60)


MOM = (-3.7, 4.5, 62)   # x, y, yaw: mum stands at the left of the bed, turned to the boy and to us


def _mom(C, t, open_k, arms=16):
    m = C.mom; m.at(*B(MOM[0], MOM[1], 0), yaw=MOM[2]); m.face("mom", t + 0.6)
    m.pose(head=(12, 0, wig(t, 1.2, 3)), lean=(8, 0, 0), aL=(64, arms), aR=(64, arms), bob=0.06 * wig(t, 1.5))
    fx, fy = math.sin(math.radians(MOM[2])), -math.cos(math.radians(MOM[2]))
    book(C, B(MOM[0] + fx * 1.25, MOM[1] + fy * 1.25, 3.5), MOM[2], open_k)


def story(C, t, T):
    """Bedtime stories are one word.  -- from the foot of the bed: mum opens the book, he grins up at her."""
    E.mood("room_dusk"); C.bed.lamp_on(1.0); C.bed.show(hide=("s", "ceil")); E.use("bedroom", "hero", "mom", *C.always)
    h = C.hero; h.at(*B(-0.8, 1.2, 2.62), pitch=-90); h.face("happy", t + 0.5); h.pose(head=(0, 0, 16))
    _mom(C, t, pop(t, 0.12, 0.25))
    k = ease(ramp(t, 0, T))
    E.cam(B(-1.6, lerp(-2.2, -1.5, k), 6.9), B(-1.9, 4.6, 3.7), 60)


def end(C, t, T):
    """End.  -- book slams, he is out cold."""
    E.mood("room_dusk"); C.bed.lamp_on(1.0); C.bed.show(hide=("ceil",)); E.use("bedroom", "hero", "mom", *C.always)
    h = C.hero; h.at(*B(-0.8, 1.2, 2.62), pitch=-90); h.face("asleep"); h.pose(head=(0, 0, 8))
    _mom(C, 0.0, 1 - ease_out(ramp(t, 0.0, 0.09)), arms=20)
    E.put(C.zs[0], B(0.05, 6.0, 4.3 + 1.2 * t), 0.9 * pop(t, 0.05, 0.16), (0, 0, 10))
    E.cam(B(-0.4, lerp(4.6, 4.9, t / T), lerp(9.6, 9.0, t / T)), B(-0.5, 5.0, 3.0), 44)


def dad(C, t, T):
    """My dad sleeps standing up,  -- full body, swaying in the living room."""
    E.mood("room"); C.liv.show(hide=("s",)); E.use("living", "dad", *C.always)
    d = C.dad; sway = wig(t, 0.75, 6)
    d.at(*V(0.2, -0.6, 0), yaw=12, roll=sway * 0.5); d.face("dad_asleep")
    d.pose(head=(22 + wig(t, 1.5, 4), 0, sway), lean=(4, 0, sway * 0.6), aL=(4, 6 + sway * 0.4), aR=(4, 6 - sway * 0.4), bob=0.04 * wig(t, 1.5))
    zzz(C, t + 0.4, V(1.1, -1.2, 5.2), drift=(1.3, 0, 2.2), size=0.9, period=1.0)
    k = ease(ramp(t, 0, T))
    E.cam(V(lerp(-3.4, -2.6, k), -9.2, 4.3), V(0.5, -0.6, 3.75), lerp(50, 46, k))


def dadface(C, t, T):
    """just in case.  -- low angle on his face; the snore bubble pops and he jolts."""
    E.mood("room"); C.liv.show(hide=("s",)); E.use("living", "dad", *C.always)
    d = C.dad; popt = 0.5; jolt = math.exp(-max(0, t - popt) * 9) if t > popt else 0
    d.at(*V(0.2, -0.6, 0), yaw=12); d.face("shock" if popt < t < popt + 0.16 else "dad_asleep")
    d.pose(head=(20 - 34 * jolt, 0, 4), lean=(4 - 8 * jolt, 0, 0), aL=(4, 6 + 40 * jolt), aR=(4, 6 + 40 * jolt), bob=0.5 * jolt)
    if t < popt:
        r = 0.1 + 0.26 * ease_out(t / popt) + 0.015 * wig(t, 9)
        E.put(C.bubble, V(0.2 + 0.42, -1.55 - r * 0.8, 4.0 - r * 0.3), r)
    k = ease(ramp(t, 0, T))
    E.cam(V(lerp(2.4, 2.0, k), -5.4, 1.9), V(0.2, -0.9, 4.45), lerp(42, 38, k))


def coffee(C, t, T):
    """Coffee is illegal.  -- a man bolts with his cup, the officer right behind him."""
    E.mood("day"); C.street.day(); E.use("street", "signs", "man", "cop", "t1", *C.always)
    x = -9 + 13.5 * t
    m = C.man; m.at(x, -8.3, 0.25, yaw=90); m.face("scared"); ph = t * 21
    s = math.sin(ph)
    m.pose(head=(-6, 14, 0), lean=(20, 0, 0), aL=(-70 * s, 10), aR=(78 + 8 * s, 6), lL=62 * s, lR=-62 * s, bob=0.35 * abs(math.cos(ph)))
    c = C.cop; c.at(x - 4.6 + 1.2 * t, -6.4, 0.0, yaw=84); c.face("stern"); s2 = math.sin(ph + 1.3)
    c.pose(head=(-10, 0, 0), lean=(26, 0, 0), aL=(96, 8), aR=(-70 * s2, 10), lL=62 * s2, lR=-62 * s2, bob=0.35 * abs(math.cos(ph + 1.3)))
    p = C.town[1]; p.at(-2, -12.5, 0.0, yaw=60); p.face("shock"); p.pose(aL=(0, 50), aR=(0, 50))
    E.cam((10.5, -4.4, 3.0), (lerp(-6, 1.5, ease(t / T)), -8.6, lerp(4.6, 4.2, t / T)), 52)


def awake(C, t, T):
    """But last night, I couldn't sleep.  -- straight down on the bed, eyes wide."""
    E.mood("room_night", 1.8); C.bed.show(hide=("ceil",)); E.use("bedroom", "hero", *C.always)
    h = C.hero; h.at(*B(0, 1.2, 2.62), pitch=-90)
    look = -1 if (t % 0.7) < 0.35 else 1
    h.face("scared"); h.pose(head=(0, 0, 13 * look * ease(ramp(t % 0.35, 0, 0.1))))
    C.blanket.location = B(0, 0.95 + 0.55 * pop(t, 0.25, 0.2), 2.8)
    light(C.L1, B(3.9, 4.6, 3.6), (255, 70, 60), 220); light(C.L2, B(0, 4, 9), (150, 175, 255), 900)
    k = ease(ramp(t, 0, T))
    E.cam(B(0.3, lerp(2.2, 3.6, k), lerp(14.5, 10.2, k)), B(0.3, lerp(2.6, 4.2, k), 2.5), 44, roll=lerp(-9, 5, k))


def lights(C, t, T):
    """One by one, every light on my street went out.  -- from his roof: the windows die from the far end towards us."""
    E.mood("night"); E.use("street", "signs", *C.always)
    E.put(C.moon, (360, -70, 185), 0.8); C.street.clock_time(11.9)
    order = sorted(range(len(C.street.houses)), key=lambda i: -C.street.houses[i][0])
    per = {}
    for rank, i in enumerate(order):
        off = 0.18 + rank * (T - 0.55) / len(order)
        per[i] = 1.0 if t < off else 0.0
    C.street.lights_set(windows=1.0, lamps=lerp(0.9, 0.12, ease(ramp(t, T - 0.5, T - 0.1))), per=per)
    k = ease(ramp(t, 0, T))
    E.cam((lerp(-15, -20, k), 1.5, lerp(10.5, 12.5, k)), (40, 0.0, lerp(5, 6.5, k)), 60)


def _night_room(C, hero_yaw=0.0, face="scared", lamp=0.0):
    E.mood("room_night", 1.6); E.use("bedroom", "hero", "creature", *C.always)
    h = C.hero; h.at(*B(0, 3.0, 0.5), yaw=hero_yaw); h.face(face)
    light(C.L2, B(0, -2, 8), (190, 200, 255), 1000)
    return h


def knock(C, t, T):
    """Then something knocked on my window.  -- he sits up facing us; behind him it slides into the window and knocks."""
    h = _night_room(C); C.bed.show(hide=("s", "ceil")); h.at(*B(-1.3, 3.0, 0.5), yaw=0)
    kn = t > 0.5
    h.face("shock" if kn else "scared"); h.pose(head=(0, wig(t, 5, 20) if kn and t < 0.9 else 0, 0), aL=(18, 14), aR=(18, 14), bob=0.12 * pop(t, 0.5, 0.15) if kn else 0)
    cr = C.cr; x = lerp(8.0, 1.5, ease_out(ramp(t, 0.0, 0.45)))
    cr.at(*B(x, 10.3, 0), yaw=0); cr.face("c_tired")
    cr.pose(head=(10, 0, -6), lean=(8, 0, 0), aL=(4, 5), aR=(84 + (wig(t, 6.5, 16) if kn else 0), 4) if t > 0.38 else (4, 5))
    light(C.L1, B(1.5, 7.0, 6.9), (150, 170, 255), 420)
    k = ease(ramp(t, 0, T))
    E.cam(B(0.2, lerp(-7.4, -6.2, k), 4.9), B(0.2, 6, lerp(5.5, 5.8, k)), lerp(54, 50, k))


def tired(C, t, T):
    """It looked exhausted.  -- its face, close, framed by the window."""
    h = _night_room(C); C.bed.show(hide=("ceil",))
    cr = C.cr; cr.at(*B(0.5, 10.3, 0), yaw=0); cr.face("c_asleep" if 0.42 < t < 0.56 else "c_tired")
    cr.pose(head=(12 + 6 * ease(ramp(t, 0.35, 0.6)), 0, 7 + wig(t, 0.8, 2)), lean=(10, 0, 0), aL=(4, 5), aR=(4, 5), bob=-0.2 * ease(ramp(t, 0.35, 0.6)))
    light(C.L1, B(0.8, 7.2, 6.4), (200, 205, 255), 420)
    k = ease(ramp(t, 0, T))
    E.cam(B(lerp(1.5, 1.1, k), lerp(3.2, 4.4, k), 6.2), B(0.5, 10.3, 6.0), lerp(36, 32, k))


def yawn(C, t, T):
    """It yawned and said,  -- over the boy's shoulder: a huge stretching yawn."""
    h = _night_room(C, hero_yaw=180, face="scared"); C.bed.show(hide=("s", "ceil")); h.pose(aL=(10, 12), aR=(10, 12))
    k = ease(ramp(t, 0.0, 0.34)) * (1 - 0.5 * ease(ramp(t, T - 0.22, T)))
    cr = C.cr; cr.at(*B(0.5, 10.3, 0), yaw=0); cr.face("c_yawn" if t < T - 0.12 else "c_tired")
    cr.pose(head=(-18 * k, 0, 4), lean=(-9 * k, 0, 0), aL=(10 * k, 150 * k + 5), aR=(10 * k, 138 * k + 5), bob=0.35 * k)
    light(C.L1, B(0.8, 8.5, 7.0), (200, 205, 255), 300)
    E.cam(B(-0.9, lerp(1.6, 2.2, t / T), 6.45), B(0.8, 10.3, 6.25), 37)


def turn(C, t, T):
    """Finally. Your turn.  -- it grins and points; smash zoom on the boy."""
    cut = 0.52
    if t < cut:
        h = _night_room(C, hero_yaw=180); C.bed.show(hide=("ceil",))
        cr = C.cr; cr.at(*B(0.5, 10.3, 0), yaw=0); cr.face("c_grin"); p = pop(t, 0.04, 0.2)
        cr.pose(head=(14, 0, -8), lean=(16 * p, 0, 0), aL=(4, 5), aR=(86 * p, 3))
        light(C.L1, B(0.9, 7.0, 6.2), (200, 205, 255), 520)
        E.cam(B(1.9, lerp(5.0, 5.6, t / cut), 5.5), B(0.4, 10.0, 5.8), 44)
    else:
        u = t - cut; h = _night_room(C, hero_yaw=180, face="shock"); C.bed.show(hide=("ceil",))
        C.cr.at(*B(0.5, 10.3, 0), yaw=0); C.cr.pose(aR=(86, 3), lean=(16, 0, 0))
        h.pose(head=(-6, 0, wig(u, 11, 3) * math.exp(-u * 4)), aL=(0, 34 * pop(u, 0, 0.15)), aR=(0, 34 * pop(u, 0, 0.15)), lean=(-8, 0, 0))
        light(C.L1, B(0.2, 6.6, 5.6), (170, 190, 255), 260)
        z = ease_out(ramp(u, 0.0, 0.22))
        E.cam(B(0.5, lerp(7.1, 6.7, z), 4.8), B(0, 3.0, 4.2), lerp(72, 46, z))


HERO_AM = (-5.1, -4.6)            # where he stands in the morning
AM_CAM = ((-6.8, -9.6, 6.6), (-0.8, 2.0, 3.2), 50)


def _morning(C, t):
    E.mood("room", 1.05); C.bed.show(hide=("s", "w", "ceil")); E.use("bedroom", "hero", "creature", *C.always)
    cr = C.cr; cr.at(*B(0.3, 4.9, -1.06), yaw=8); cr.face("c_asleep")
    br = wig(t, 0.55, 1.0)
    cr.pose(head=(10 + 3 * br, 0, 20), lean=(-8, 0, 5), aL=(34, 16), aR=(30, 14), bob=0.05 * br)
    C.blanket.location = B(0.2, 0.75, 2.86); C.blanket.rotation_euler = (0, 0, E.D(5))
    zzz(C, t + 0.5, B(1.5, 4.4, 6.3), drift=(1.3, -0.3, 2.0), yaw=-25, size=1.2, period=0.9)
    h = C.hero; h.at(*B(HERO_AM[0], HERO_AM[1], 0), yaw=yaw_to(AM_CAM[0][0] - HERO_AM[0], AM_CAM[0][1] - HERO_AM[1])); h.face("wired"); C.cup_hero.scale = (1,) * 3
    tw = 1 if (t * 6) % 1 < 0.5 else 0
    h.pose(head=(-4, 0, 3 * tw), aL=(0, 8), aR=(78 + 4 * wig(t, 9), 4), bob=0.03 * wig(t, 9))
    return h


def since(C, t, T):
    """I haven't slept since.  -- morning: he stands in front, wired, with a cup of the illegal stuff; behind him it sleeps in HIS bed."""
    _morning(C, t)
    k = ease(ramp(t, 0, T))
    E.cam(B(AM_CAM[0][0] + 0.3 * k, AM_CAM[0][1] + 0.5 * k, AM_CAM[0][2]), B(*AM_CAM[1]), AM_CAM[2])


def loop(C, t, T):
    """Because...  -- fast push into his eyes, which is where the video starts again."""
    _morning(C, t + 1.0)
    k = ease_in(ramp(t, 0.0, T * 0.8)) * 0.35 + ease_out(ramp(t, 0.0, T * 0.8)) * 0.65
    p0 = (AM_CAM[0][0] + 0.3, AM_CAM[0][1] + 0.5, AM_CAM[0][2])
    dx, dy = AM_CAM[0][0] - HERO_AM[0], AM_CAM[0][1] - HERO_AM[1]; n = math.hypot(dx, dy)
    p1 = (HERO_AM[0] + dx / n * 4.4, HERO_AM[1] + dy / n * 4.4, 4.9); tg1 = (HERO_AM[0], HERO_AM[1], 3.7)
    E.cam(B(*lerp3(p0, p1, k)), B(*lerp3(AM_CAM[1], tg1, k)), lerp(AM_CAM[2], 31, k))


SHOTS = {f.__name__: f for f in (hook, rule, clock, race, story, end, dad, dadface, coffee, awake, lights, knock, tired, yawn, turn, since, loop)}
