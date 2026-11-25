"""The scene file for "In This Town, Never Say Thank You".
build() makes the cast and the sets once. Then one function per shot id (the ids in the .json),
called once per frame with t = seconds since the shot started and T = how long the shot lasts."""
import math
import rt_engine as E
from rt_engine import M, lerp, lerp3, ease, ease_out, ease_in, ramp, pop, wig, clamp

BR = (0, 300, 0)   # bedroom origin
LV = (0, 500, 0)   # living room origin


class Ctx: pass


def build():
    C = Ctx()
    C.street = E.Street()
    C.bed = E.Room("bedroom", BR, wall=(112, 138, 168), floor=(142, 94, 58))
    C.blanket = C.bed.bed(); C.bed.nightstand(); C.bed.bedroom_bits()
    C.liv = E.Room("living", LV, wall=(184, 166, 138), floor=(124, 84, 54), yard=False)
    C.liv.living_bits()

    Ch = E.Char
    C.hero = Ch("hero", (26, 28, 34), (56, 60, 76), scale=0.88).hair("spiky", (196, 30, 44)).jacket((196, 30, 44))
    C.hero.extra("hood", (20, 22, 28), (1.5, 0.5, 0.5), (0, 0.42, 1.85), bevel=0.16, tex="fabric")

    C.mom = Ch("mom", (142, 54, 82), (38, 42, 58), skin=(206, 160, 124)).hair("long", (40, 28, 34), seed=3).jacket((228, 222, 210))
    C.dad = Ch("dad", (52, 74, 118), (38, 42, 52), skin=(206, 160, 124), shoes=(60, 48, 40), sole=(34, 28, 24)).hair("short", (52, 38, 30), seed=8).jacket((216, 216, 222))

    C.cop = Ch("cop", (28, 40, 82), (20, 26, 52), skin=(140, 96, 70), shoes=(20, 20, 24)).hair("copcap", (20, 26, 52), (236, 196, 60))
    C.cop.extra("badge2", (236, 196, 60), (0.4, 0.1, 0.45), (0.5, -0.5, 1.45))
    C.cop.extra("belt", (14, 14, 18), (2.04, 1.04, 0.28), (0, 0, 0.2), bevel=0.02)

    C.man = Ch("man", (222, 222, 228), (46, 44, 50), shoes=(38, 28, 24)).hair("short", (46, 34, 26), seed=5)
    C.man.extra("tie", (172, 34, 42), (0.34, 0.1, 1.3), (0, -0.5, 1.2))

    looks = [
        ((146, 42, 46), (38, 42, 58), "short", (34, 26, 22), (232, 190, 160)),
        ((56, 104, 76), (66, 58, 50), "bun",   (188, 142, 66), (206, 160, 124)),
        ((198, 120, 46), (42, 48, 76), "long", (112, 40, 34), (232, 190, 160)),
        ((86, 66, 142), (28, 28, 34), "spiky", (24, 24, 30), (140, 96, 70)),
        ((212, 212, 218), (48, 76, 124), "bun", (56, 38, 28), (110, 74, 56)),
        ((56, 114, 162), (74, 74, 84), "long", (206, 182, 104), (232, 190, 160)),
    ]
    C.town = [Ch(f"t{i}", sh, pa, skin=sk, scale=0.96 + 0.05 * (i % 2)).hair(hs, hc, seed=i + 10) for i, (sh, pa, hs, hc, sk) in enumerate(looks)]
    C.town[0].jacket((224, 224, 228)); C.town[3].jacket((204, 184, 58))

    # Tall pale stranger (dark slate coat, eerie pale blocky head)
    C.cr = Ch("creature", (32, 38, 48), (24, 28, 36), skin=E.PALE, tall=True, shoes=(26, 26, 32), sole=(16, 16, 20))
    C.cr.jacket((18, 20, 26), zip_rgb=(90, 96, 112))
    C.cr.extra("b1", (160, 164, 178), (0.18, 0.08, 0.18), (0.36, -0.49, 1.9), bevel=0.05)
    C.cr.extra("b2", (160, 164, 178), (0.18, 0.08, 0.18), (0.36, -0.49, 1.25), bevel=0.05)

    # Props in fx collection
    fx = E.coll("fx"); C.props = []

    # Smartphone prop
    C.phone = E.part("phone", M("phone_body", (24, 26, 32), rough=0.25), fx, (0.44, 0.09, 0.82), bevel=0.04)
    E.part("phone_scr", M("phone_scr", (110, 185, 255), emit=(110, 185, 255), emit_k=2.2), fx, (0.36, 0.02, 0.68), parent=C.phone, inner=(0, -0.045, 0), bevel=0.01)
    C.props.append(C.phone)

    # Dropped parcel box for help/rude joke
    C.box = E.part("parcel", M("parcel_m", (176, 126, 74), rough=0.75, tex="noise"), fx, (1.15, 0.95, 0.85), bevel=0.05)
    E.part("parcel_tape", M("parcel_t", (226, 198, 146)), fx, (1.18, 0.22, 0.88), parent=C.box, inner=(0, 0, 0), bevel=0.01)
    C.props.append(C.box)

    # Dinner plate with food for mom/awful joke
    C.plate = E.empty("plate", fx); C.props.append(C.plate)
    E.Mesher().cyl(0.95, 0.12, (0, 0, 0.06)).make("plate_dish", M("plate_w", (240, 240, 244), rough=0.2), fx, True, C.plate)
    E.Mesher().ball(0.38, (-0.22, 0.08, 0.28), (1.1, 0.9, 0.65)).make("plate_f1", M("food1", (166, 84, 46), rough=0.7), fx, True, C.plate)
    E.Mesher().ball(0.26, (0.32, -0.1, 0.24), (1.0, 1.0, 0.7)).make("plate_f2", M("food2", (76, 148, 62), rough=0.8), fx, True, C.plate)

    # Movable slam door prop for dad joke (pivots on left edge)
    C.door = E.empty("slam_door", fx); C.props.append(C.door)
    E.part("slam_door_leaf", M("slam_door_m", (118, 72, 46), rough=0.65, tex="noise"), fx, (2.4, 0.24, 4.5), parent=C.door, inner=(1.2, 0, 2.25), bevel=0.05)
    E.part("slam_door_knob", M("gold", (250, 205, 80), rough=0.3), fx, ball=0.16, parent=C.door, inner=(2.05, -0.18, 2.2))

    # NO THANK YOU street sign (placed on sidewalk)
    sx = E.coll("signs"); st = E.Static(sx)
    st.cyl(M("pole", (52, 54, 62)), 0.16, 7.0, (3.0, -10.6, 3.5))
    st.done("signpole")
    E.picture("nothankyou", "nothankyou", sx, 3.6, 3.6, (3.0, -10.5, 7.2), yaw=118, thick=0.2, back=(245, 245, 248))

    # Spare lights + moon
    L = E.coll("lights")
    C.L1 = E.point_light("L1", L, (0, 0, -100), (255, 255, 255), 0.0, radius=0.8)
    C.L2 = E.point_light("L2", L, (0, 0, -100), (255, 255, 255), 0.0, radius=0.8, shadow=False)
    C.moon = E.part("street_moon", M("moon", (255, 250, 225), emit=(255, 248, 215), emit_k=3.0), fx, ball=16.0)
    C.moon.visible_shadow = False; C.props.append(C.moon)
    C.always = ("fx", "lights")
    return C


def reset(C):
    for p in C.props: E.gone(p)
    for l in (C.L1, C.L2): l.data.energy = 0.0
    C.bed.show(); C.liv.show(); C.bed.lamp_on(0.0)
    C.blanket.location = C.bed.P(0, 0.95, 2.8); C.blanket.rotation_euler = (0, 0, 0)


def light(l, pos, rgb, watts):
    l.location = pos; l.data.color = E.lin(rgb)[:3]; l.data.energy = watts


def yaw_to(dx, dy): return math.degrees(math.atan2(dx, -dy))
def B(x, y, z=0.0): return (BR[0] + x, BR[1] + y, BR[2] + z)
def V(x, y, z=0.0): return (LV[0] + x, LV[1] + y, LV[2] + z)


# ------------------------------------------------------------------ the shots
def hook(C, t, T):
    """In this town, -- starts tight on the hero's wired face, whips back to show the street."""
    E.mood("day"); C.street.day(); E.use("street", "signs", "hero", "t0", "t1", "t2", "t3", *C.always)
    h = C.hero; h.at(-10, 0, 0, yaw=-90); h.face("wired")
    a = pop(t, 0.06, 0.25)
    h.pose(head=(0, 0, wig(t, 7, 2.5)), aL=(0, 62 * a), aR=(0, 62 * a), bob=0.1 * abs(wig(t, 5)))
    for i, (x0, y, d) in enumerate(((6, 8.2, 1), (26, -8.0, -1), (44, 8.0, -1), (-4, -8.3, 1))):
        p = C.town[i]; x = x0 + d * 4.5 * t; p.at(x, y, 0.25, yaw=90 * d); p.walk(x * 1.3); p.face("happy", t + i)
    k = ease_out(ramp(t, 0.14, 0.82))
    E.cam(lerp3((-15.4, 0.1, 4.3), (-47, -2.5, 19), k), lerp3((-10, 0, 3.75), (22, 0, 7.5), k), lerp(31, 58, k))


def rule(C, t, T):
    """you must never say thank you. -- night street: NO THANK YOU sign in foreground, tall stranger under streetlamp behind."""
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.45)
    E.use("street", "signs", "creature", *C.always)
    E.put(C.moon, (280, -120, 140), 0.75)
    cr = C.cr; cr.at(-2.0, -8.2, 0.25, yaw=82); cr.face("c_grin")
    cr.pose(head=(6, 0, wig(t, 0.5, 6)), lean=(4, 0, wig(t, 0.4, 2.0)), aL=(4, 6), aR=(4, 6))
    light(C.L1, (0.5, -7.2, 6.8), (255, 224, 165), 260)
    light(C.L2, (5.5, -7.6, 6.2), (160, 185, 255), 220)
    k = ease(ramp(t, 0.0, T))
    E.cam(lerp3((13.5, -5.8, 3.4), (10.5, -6.5, 4.0), k), lerp3((1.0, -9.2, 5.2), (-0.5, -8.8, 5.4), k), lerp(52, 44, k))


def help(C, t, T):
    """If someone helps you, -- daytime sidewalk: neighbor politely hands a dropped parcel to another."""
    E.mood("day"); C.street.day(); E.use("street", "t0", "t1", *C.always)
    p0 = C.town[0]; p1 = C.town[1]
    p0.at(12.2, 8.2, 0.25, yaw=82); p0.face("happy", t)
    reach = pop(t, 0.1, 0.3)
    p0.pose(head=(6, 0, 0), lean=(8 * reach, 0, 0), aL=(72 * reach, 8), aR=(72 * reach, 8))
    p1.at(15.6, 8.2, 0.25, yaw=-82); p1.face("scared")
    p1.pose(head=(-4, 0, 0), aL=(12, 10), aR=(12, 10))
    E.put(C.box, (13.6 + 0.3 * reach, 8.0, 3.05 + 0.1 * reach), 1.0, (0, 0, 15))
    k = ease(ramp(t, 0, T))
    E.cam((lerp(13.6, 14.2, k), -1.8, 3.8), (13.9, 8.2, 3.3), lerp(54, 48, k))


def rude(C, t, T):
    """you have to be rude back. -- tight cut: p1 glares and smacks the parcel flying!"""
    E.mood("day"); C.street.day(); E.use("street", "t0", "t1", *C.always)
    p0 = C.town[0]; p1 = C.town[1]
    hit = ease_out(ramp(t, 0.18, 0.38))
    p1.at(15.6, 8.2, 0.25, yaw=-65); p1.face("stern")
    p1.pose(head=(4, -8 * hit, -6), lean=(12 * hit, -18 * hit, 0), aL=(18, 14), aR=(86 * hit, 45 * hit))
    p0.at(12.2, 8.2, 0.25, yaw=82); p0.face("happy")
    p0.pose(head=(-6, 0, 6), aL=(20, 12), aR=(20, 12))
    fly = ramp(t, 0.22, T)
    E.put(C.box, (13.9 - 5.2 * fly, 8.0 - 3.0 * fly, 3.15 + 3.2 * fly - 5.5 * fly * fly), 1.0, (240 * fly, 180 * fly, 40 * fly))
    E.cam((lerp(13.2, 12.6, t / T), 0.2, 3.8), (14.6, 8.2, 3.6), 44)


def mom(C, t, T):
    """My mom serves me dinner, -- living room: mom holds out a dinner plate with a warm smile."""
    E.mood("room"); C.liv.show(hide=("s",)); E.use("living", "mom", "hero", *C.always)
    m = C.mom; h = C.hero
    m.at(*V(-2.0, 0.6, 0), yaw=70); m.face("mom", t)
    s = pop(t, 0.08, 0.28)
    m.pose(head=(8, 0, wig(t, 1.2, 3)), lean=(6 * s, 0, 0), aL=(68 * s, 8), aR=(68 * s, 8))
    h.at(*V(2.0, 0.6, 0), yaw=-70); h.face("stern")
    h.pose(head=(0, 0, 0), aL=(10, 8), aR=(10, 8))
    E.put(C.plate, V(-0.55 + 0.35 * s, 0.35, 3.05), 1.0)
    k = ease(ramp(t, 0, T))
    E.cam(V(lerp(-0.3, 0.2, k), -9.6, 4.2), V(0.0, 0.6, 3.3), lerp(54, 50, k))


def awful(C, t, T):
    """and I call it trash. -- close-up on hero shoving/pointing down in disgust while mom beams behind."""
    E.mood("room"); C.liv.show(hide=("s",)); E.use("living", "mom", "hero", *C.always)
    h = C.hero; m = C.mom
    p = pop(t, 0.08, 0.2)
    h.at(*V(2.0, 0.6, 0), yaw=-35); h.face("stern")
    h.pose(head=(8, 6, -8 * p), lean=(10 * p, 0, 0), aL=(78 * p, 24), aR=(64 * p, 18), bob=0.08 * wig(t, 6))
    m.at(*V(-1.8, 2.2, 0), yaw=28); m.face("happy")
    m.pose(head=(0, 0, 6), aL=(10, 26), aR=(10, 26))
    E.put(C.plate, V(0.5, -0.3, 0.12), 1.0, (0, 0, 20))
    E.cam(V(lerp(3.2, 2.8, t / T), -4.2, 3.7), V(1.3, 0.8, 3.65), 36)


def dad(C, t, T):
    """My dad slams doors on everyone, -- outside a house porch: dad slams the door shut on a shocked neighbor."""
    E.mood("day"); C.street.day(); E.use("street", "dad", "t2", *C.always)
    hx, hy, face = C.street.houses[5]
    dx, dy = hx - 3.2, hy + face * 5.65
    slam = ease_in(ramp(t, 0.25, 0.52))
    ang = lerp(-75, 0, slam)
    E.put(C.door, (dx - 1.2, dy + 0.15, 0.4), 1.0, (0, 0, ang))
    d = C.dad; d.at(dx + 1.0, dy + 1.2, 0.25, yaw=165); d.face("smug")
    d.pose(head=(4, -10, 0), lean=(8 * slam, 0, 0), aL=(70, 12), aR=(20, 10))
    n = C.town[2]; n.at(dx - 0.3, dy + 3.4, 0.1, yaw=0); n.face("shock" if t > 0.35 else "happy")
    n.pose(head=(-8 * slam, 0, 0), aL=(0, 52 * slam), aR=(0, 52 * slam), lean=(-10 * slam, 0, 0))
    sh = 0.25 * math.exp(-max(0, t - 0.52) * 10) * math.sin(t * 70) if t > 0.52 else 0
    E.cam((dx + 6.5, dy + 7.2 + sh, 3.8 + sh), (dx, dy + 1.8, 3.2), 46)


def dadface(C, t, T):
    """just in case. -- low-angle tight close-up on dad's smug face."""
    E.mood("day"); C.street.day(); E.use("street", "dad", *C.always)
    hx, hy, face = C.street.houses[5]
    dx, dy = hx - 3.2, hy + face * 5.65
    d = C.dad; d.at(dx + 1.0, dy + 1.2, 0.25, yaw=172); d.face("smug")
    nod = 10 * math.sin(ramp(t, 0.15, 0.65) * math.pi)
    d.pose(head=(6 + nod, 0, 4), aL=(12, 10), aR=(12, 10))
    E.cam((dx + 1.6, dy + 5.6, 2.2), (dx + 1.0, dy + 1.2, 4.45), lerp(36, 30, ease(t / T)))


def polite(C, t, T):
    """Manners are illegal. -- a polite guy bolts past the NO THANK YOU sign, cop right behind him."""
    E.mood("day"); C.street.day(); E.use("street", "signs", "man", "cop", "t1", *C.always)
    x = -9 + 14.0 * t
    m = C.man; m.at(x, -8.3, 0.25, yaw=90); m.face("scared"); ph = t * 21
    s = math.sin(ph)
    m.pose(head=(-6, 14, 0), lean=(20, 0, 0), aL=(-70 * s, 10), aR=(70 * s, 10), lL=62 * s, lR=-62 * s, bob=0.35 * abs(math.cos(ph)))
    c = C.cop; c.at(x - 4.5 + 1.1 * t, -6.4, 0.0, yaw=84); c.face("stern"); s2 = math.sin(ph + 1.3)
    c.pose(head=(-10, 0, 0), lean=(26, 0, 0), aL=(96, 8), aR=(-70 * s2, 10), lL=62 * s2, lR=-62 * s2, bob=0.35 * abs(math.cos(ph + 1.3)))
    p = C.town[1]; p.at(-2, -12.5, 0.0, yaw=60); p.face("shock"); p.pose(aL=(0, 50), aR=(0, 50))
    E.cam((10.5, -4.4, 3.0), (lerp(-6, 1.5, ease(t / T)), -8.6, lerp(4.6, 4.2, t / T)), 52)


def slip(C, t, T):
    """But last night, someone caught my phone. -- night sidewalk: hero stumbles, tall stranger catches his phone."""
    E.mood("night"); C.street.lights_set(windows=0.35, lamps=0.6)
    E.use("street", "hero", "creature", *C.always)
    h = C.hero; cr = C.cr
    h.at(-5.2, -8.2, 0.25, yaw=102); h.face("scared")
    h.pose(head=(10, 0, 0), lean=(16, 0, 0), aL=(48, 16), aR=(64, 10))
    cr.at(-1.4, -8.2, 0.25, yaw=-102); cr.face("c_tired")
    catch = pop(t, 0.22, 0.24)
    cr.pose(head=(14, 0, -4), lean=(10 * catch, 0, 0), aL=(4, 6), aR=(74 * catch, 8))
    drop = ease_out(ramp(t, 0.0, 0.28))
    E.put(C.phone, (lerp(-3.9, -2.55, drop), -7.9, lerp(3.8, 3.25, drop)), 1.15, (0, 25 * (1 - drop), 90))
    light(C.L1, (-3.0, -5.8, 6.8), (255, 224, 155), 360)
    light(C.L2, (-4.0, -2.0, 5.0), (150, 175, 255), 220)
    k = ease(ramp(t, 0, T))
    E.cam((lerp(-3.4, -3.1, k), 2.4, 4.1), (-3.3, -8.2, 3.6), lerp(56, 50, k))


def said(C, t, T):
    """By habit, I said thank you. -- tight close-up on hero: innocent smile snaps to horror."""
    E.mood("night"); C.street.lights_set(windows=0.35, lamps=0.55)
    E.use("street", "hero", *C.always)
    h = C.hero; h.at(-5.2, -8.2, 0.25, yaw=115)
    realize = t > T * 0.52
    h.face("shock" if realize else "happy")
    jolt = pop(t, T * 0.52, 0.16) if realize else 0.0
    h.pose(head=(-4 * jolt, 0, wig(t, 12, 3) * jolt if realize else 4), aL=(24, 18 * (1 + jolt)), aR=(24, 18 * (1 + jolt)), bob=0.14 * jolt)
    light(C.L1, (-2.5, -5.8, 5.2), (255, 228, 180), 260)
    E.cam((-1.2, -5.4, 3.75), (-5.2, -8.2, 3.7), lerp(36, 28, ease(ramp(t, T * 0.45, T))))


def silent(C, t, T):
    """The whole street froze. -- high wide shot: everyone on the street frozen mid-stride staring at hero."""
    E.mood("night"); C.street.lights_set(windows=0.15, lamps=0.75)
    E.use("street", "hero", "creature", "t0", "t1", "t2", "t3", "t4", *C.always)
    E.put(C.moon, (340, -60, 175), 0.8)
    C.hero.at(-5.2, -8.2, 0.25, yaw=90); C.hero.face("scared"); C.hero.pose(aL=(14, 14), aR=(14, 14))
    C.cr.at(-1.4, -8.2, 0.25, yaw=-90); C.cr.face("c_tired"); C.cr.pose(aL=(4, 5), aR=(4, 5))
    frozen = [(-18, -8.1), (10, -8.3), (-12, 8.2), (6, 8.0), (22, 8.2)]
    for i, (fx, fy) in enumerate(frozen):
        p = C.town[i]; p.at(fx, fy, 0.25, yaw=yaw_to(-5.2 - fx, -8.2 - fy))
        p.face("shock" if i % 2 == 0 else "scared")
        p.pose(head=(0, 0, 0), aL=(18, 12), aR=(-14, 12), lL=22, lR=-22)
    k = ease(ramp(t, 0, T))
    E.cam((lerp(-24, -21, k), 1.5, lerp(16, 14, k)), (2.0, -4.0, 3.0), 58)


def turn(C, t, T):
    """The stranger slowly turned around. -- medium shot under streetlamp: tall stranger slowly turns to face camera (+Y)."""
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.45)
    E.use("street", "creature", *C.always)
    cr = C.cr; k = ease(ramp(t, 0.05, T * 0.88))
    cr.at(-1.4, -8.2, 0.25, yaw=lerp(35, 174, k)); cr.face("c_tired" if k < 0.78 else "c_grin")
    cr.pose(head=(8, 0, lerp(0, -10, k)), lean=(6, 0, 0), aL=(4, 5), aR=(4, 5))
    light(C.L1, (-0.8, -5.2, 7.2), (255, 224, 165), 240)
    light(C.L2, (1.5, -2.5, 5.5), (150, 175, 255), 180)
    E.cam((lerp(1.4, 0.2, k), lerp(-0.6, -1.8, k), 4.8), (-1.4, -8.2, 5.2), lerp(46, 38, k))


def grin(C, t, T):
    """He grinned and said, -- tight eerie close-up on the stranger's wide toothy grin."""
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.35)
    E.use("street", "creature", *C.always)
    cr = C.cr; cr.at(-1.4, -8.2, 0.25, yaw=174); cr.face("c_grin")
    k = ease(ramp(t, 0, T))
    cr.pose(head=(10 + 4 * k, 0, -10 + wig(t, 1.2, 2)), lean=(8, 0, 0), aL=(4, 5), aR=(4, 5))
    light(C.L1, (-1.0, -5.4, 5.8), (210, 220, 255), 160)
    E.cam((-1.0, lerp(-2.2, -3.2, k), 5.85), (-1.4, -8.2, 5.9), lerp(34, 27, k))


def welcome(C, t, T):
    """You're welcome. Now you're mine. -- stranger leans and points; smash zoom on terrified hero."""
    cut = T * 0.52
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.4)
    if t < cut:
        E.use("street", "creature", *C.always)
        cr = C.cr; cr.at(-1.4, -8.2, 0.25, yaw=168); cr.face("c_grin")
        p = pop(t, 0.04, 0.2)
        cr.pose(head=(12, 0, -8), lean=(14 * p, 0, 0), aL=(4, 5), aR=(86 * p, 4))
        light(C.L1, (-0.5, -4.8, 5.8), (210, 220, 255), 190)
        E.cam((0.8, lerp(-1.8, -2.8, t / cut), 5.0), (-1.4, -8.2, 5.4), 44)
    else:
        u = t - cut
        E.use("street", "hero", *C.always)
        h = C.hero; h.at(-5.2, -8.2, 0.25, yaw=192); h.face("shock")
        h.pose(head=(-6, 0, wig(u, 11, 3) * math.exp(-u * 4)), aL=(0, 38 * pop(u, 0, 0.15)), aR=(0, 38 * pop(u, 0, 0.15)), lean=(-10, 0, 0))
        light(C.L1, (-4.6, -5.0, 5.0), (195, 210, 255), 220)
        z = ease_out(ramp(u, 0.0, 0.22))
        E.cam((-4.6, lerp(-2.2, -3.4, z), 4.1), (-5.2, -8.2, 3.85), lerp(64, 40, z))


HERO_RM = (-3.6, -3.4)
RM_CAM = ((-5.4, -8.8, 5.4), (-0.4, 4.0, 4.8), 52)


def _watching(C, t):
    E.mood("room_night", 1.5); C.bed.show(hide=("s", "w", "ceil"))
    E.use("bedroom", "hero", "creature", *C.always)
    # Stranger standing right outside the bedroom window, grinning and waving slowly
    cr = C.cr; cr.at(*B(0.6, 10.3, 0.0), yaw=0); cr.face("c_grin")
    cr.pose(head=(10, 0, -8 + wig(t, 0.7, 4)), lean=(10, 0, 0), aL=(4, 5), aR=(128, 22 + wig(t, 1.4, 14)))
    light(C.L1, B(0.8, 7.6, 6.4), (175, 195, 255), 240)
    light(C.L2, B(-2.5, -2.5, 7.2), (170, 185, 240), 750)
    h = C.hero
    h.at(*B(HERO_RM[0], HERO_RM[1], 0), yaw=yaw_to(RM_CAM[0][0] - HERO_RM[0], RM_CAM[0][1] - HERO_RM[1]))
    h.face("wired")
    tw = 1 if (t * 6) % 1 < 0.5 else 0
    h.pose(head=(-4, 0, 3 * tw), aL=(12, 10), aR=(62, 10), bob=0.03 * wig(t, 9))
    E.put(C.phone, B(HERO_RM[0] - 0.65, HERO_RM[1] - 0.85, 2.75), 1.0, (0, 0, 25))
    return h


def since(C, t, T):
    """He's been watching me ever since. -- bedroom at night: wired hero in front, grinning stranger outside the window."""
    _watching(C, t)
    k = ease(ramp(t, 0, T))
    E.cam(B(RM_CAM[0][0] + 0.3 * k, RM_CAM[0][1] + 0.5 * k, RM_CAM[0][2]), B(*RM_CAM[1]), RM_CAM[2])


def loop(C, t, T):
    """Because... -- fast push into hero's wired eyes, looping straight back into shot 1."""
    _watching(C, t + 1.0)
    k = ease_in(ramp(t, 0.0, T * 0.8)) * 0.35 + ease_out(ramp(t, 0.0, T * 0.8)) * 0.65
    p0 = (RM_CAM[0][0] + 0.3, RM_CAM[0][1] + 0.5, RM_CAM[0][2])
    dx, dy = RM_CAM[0][0] - HERO_RM[0], RM_CAM[0][1] - HERO_RM[1]; n = math.hypot(dx, dy)
    p1 = (HERO_RM[0] + dx / n * 4.4, HERO_RM[1] + dy / n * 4.4, 4.3)
    tg1 = (HERO_RM[0], HERO_RM[1], 3.7)
    E.cam(B(*lerp3(p0, p1, k)), B(*lerp3(RM_CAM[1], tg1, k)), lerp(RM_CAM[2], 31, k))


SHOTS = {f.__name__: f for f in (
    hook, rule, help, rude, mom, awful, dad, dadface, polite,
    slip, said, silent, turn, grin, welcome, since, loop
)}
