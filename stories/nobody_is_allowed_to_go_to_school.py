"""The scene file for \"In This Town, Nobody Is Allowed To Go To School\".
build() makes the cast and the sets once. Then one function per shot id (the ids in the .json),
called once per frame with t = seconds since the shot started and T = how long the shot lasts."""
import math
import rt_engine as E
from rt_engine import M, lerp, lerp3, ease, ease_out, ease_in, ramp, pop, wig, clamp

BR = (0, 300, 0)
LV = (0, 500, 0)


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

    looks = [
        ((146, 42, 46), (38, 42, 58), "short", (34, 26, 22), (232, 190, 160)),
        ((56, 104, 76), (66, 58, 50), "bun",   (188, 142, 66), (206, 160, 124)),
        ((198, 120, 46), (42, 48, 76), "long", (112, 40, 34), (232, 190, 160)),
    ]
    C.town = [Ch(f"t{i}", sh, pa, skin=sk, scale=0.96).hair(hs, hc, seed=i + 10) for i, (sh, pa, hs, hc, sk) in enumerate(looks)]

    C.cr = Ch("creature", (32, 38, 48), (24, 28, 36), skin=E.PALE, tall=True, shoes=(26, 26, 32), sole=(16, 16, 20))
    C.cr.jacket((18, 20, 26), zip_rgb=(90, 96, 112))

    fx = E.coll("fx"); C.props = []

    C.book = E.part("book", M("book_m", (40, 60, 120), rough=0.5), fx, (0.44, 0.09, 0.82), bevel=0.04)
    C.props.append(C.book)

    sx = E.coll("signs"); st = E.Static(sx)
    st.cyl(M("pole", (52, 54, 62)), 0.16, 7.0, (3.0, -10.6, 3.5))
    st.done("signpole")
    E.picture("custom_sign", "custom_sign", sx, 3.6, 3.6, (3.0, -10.5, 7.2), yaw=118, thick=0.2, back=(245, 245, 248))

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


def hook(C, t, T):
    E.mood("day"); C.street.day(); E.use("street", "signs", "hero", *C.always)
    h = C.hero; h.at(-10, 0, 0, yaw=-90); h.face("wired")
    k = ease_out(ramp(t, 0.14, 0.82))
    E.cam(lerp3((-15.4, 0.1, 4.3), (-47, -2.5, 19), k), lerp3((-10, 0, 3.75), (22, 0, 7.5), k), lerp(31, 58, k))


def rule(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.45)
    E.use("street", "signs", "creature", *C.always)
    cr = C.cr; cr.at(-2.0, -8.2, 0.25, yaw=82); cr.face("c_grin")
    light(C.L1, (0.5, -7.2, 6.8), (255, 224, 165), 260)
    k = ease(ramp(t, 0.0, T))
    E.cam(lerp3((13.5, -5.8, 3.4), (10.5, -6.5, 4.0), k), lerp3((1.0, -9.2, 5.2), (-0.5, -8.8, 5.4), k), lerp(52, 44, k))


def help(C, t, T):
    E.mood("day"); C.street.day(); E.use("street", "t0", "t1", *C.always)
    p0 = C.town[0]; p1 = C.town[1]
    p0.at(12.2, 8.2, 0.25, yaw=82); p0.face("happy", t)
    p1.at(15.6, 8.2, 0.25, yaw=-82); p1.face("scared")
    E.cam((13.6, -1.8, 3.8), (13.9, 8.2, 3.3), 54)


def rude(C, t, T):
    E.mood("day"); C.street.day(); E.use("street", "t0", "t1", *C.always)
    p1 = C.town[1]; p1.at(15.6, 8.2, 0.25, yaw=-65); p1.face("stern")
    E.cam((13.2, 0.2, 3.8), (14.6, 8.2, 3.6), 44)


def mom(C, t, T):
    E.mood("room"); C.liv.show(hide=("s",)); E.use("living", "mom", "hero", *C.always)
    m = C.mom; h = C.hero
    m.at(*V(-2.0, 0.6, 0), yaw=70); m.face("mom", t)
    h.at(*V(2.0, 0.6, 0), yaw=-70); h.face("stern")
    E.cam(V(0.0, -9.6, 4.2), V(0.0, 0.6, 3.3), 54)


def awful(C, t, T):
    E.mood("room"); C.liv.show(hide=("s",)); E.use("living", "mom", "hero", *C.always)
    h = C.hero; h.at(*V(2.0, 0.6, 0), yaw=-35); h.face("stern")
    E.cam(V(3.2, -4.2, 3.7), V(1.3, 0.8, 3.65), 36)


def dad(C, t, T):
    E.mood("day"); C.street.day(); E.use("street", "dad", *C.always)
    hx, hy, face = C.street.houses[5]
    dx, dy = hx - 3.2, hy + face * 5.65
    d = C.dad; d.at(dx + 1.0, dy + 1.2, 0.25, yaw=165); d.face("smug")
    E.cam((dx + 6.5, dy + 7.2, 3.8), (dx, dy + 1.8, 3.2), 46)


def dadface(C, t, T):
    E.mood("day"); C.street.day(); E.use("street", "dad", *C.always)
    hx, hy, face = C.street.houses[5]
    dx, dy = hx - 3.2, hy + face * 5.65
    d = C.dad; d.at(dx + 1.0, dy + 1.2, 0.25, yaw=172); d.face("smug")
    E.cam((dx + 1.6, dy + 5.6, 2.2), (dx + 1.0, dy + 1.2, 4.45), 36)


def polite(C, t, T):
    E.mood("day"); C.street.day(); E.use("street", "signs", "cop", *C.always)
    c = C.cop; c.at(0, -6.4, 0.0, yaw=84); c.face("stern")
    E.cam((10.5, -4.4, 3.0), (1.5, -8.6, 4.2), 52)


def slip(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.35, lamps=0.6)
    E.use("street", "hero", "creature", *C.always)
    h = C.hero; h.at(-5.2, -8.2, 0.25, yaw=102); h.face("scared")
    E.cam((-3.4, 2.4, 4.1), (-3.3, -8.2, 3.6), 56)


def said(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.35, lamps=0.55)
    E.use("street", "hero", *C.always)
    h = C.hero; h.at(-5.2, -8.2, 0.25, yaw=115); h.face("shock")
    E.cam((-1.2, -5.4, 3.75), (-5.2, -8.2, 3.7), 36)


def silent(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.15, lamps=0.75)
    E.use("street", "hero", "creature", *C.always)
    C.hero.at(-5.2, -8.2, 0.25, yaw=90); C.hero.face("scared")
    E.cam((-24, 1.5, 16), (2.0, -4.0, 3.0), 58)


def turn(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.45)
    E.use("street", "creature", *C.always)
    cr = C.cr; cr.at(-1.4, -8.2, 0.25, yaw=174); cr.face("c_grin")
    E.cam((1.4, -0.6, 4.8), (-1.4, -8.2, 5.2), 46)


def grin(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.35)
    E.use("street", "creature", *C.always)
    cr = C.cr; cr.at(-1.4, -8.2, 0.25, yaw=174); cr.face("c_grin")
    E.cam((-1.0, -2.2, 5.85), (-1.4, -8.2, 5.9), 34)


def welcome(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.0, lamps=0.4)
    E.use("street", "creature", *C.always)
    cr = C.cr; cr.at(-1.4, -8.2, 0.25, yaw=168); cr.face("c_grin")
    E.cam((0.8, -1.8, 5.0), (-1.4, -8.2, 5.4), 44)


HERO_RM = (-3.6, -3.4)
RM_CAM = ((-5.4, -8.8, 5.4), (-0.4, 4.0, 4.8), 52)


def _watching(C, t):
    E.mood("room_night", 1.5); C.bed.show(hide=("s", "w", "ceil"))
    E.use("bedroom", "hero", "creature", *C.always)
    cr = C.cr; cr.at(*B(0.6, 10.3, 0.0), yaw=0); cr.face("c_grin")
    h = C.hero; h.at(*B(HERO_RM[0], HERO_RM[1], 0), yaw=180); h.face("wired")
    return h


def since(C, t, T):
    _watching(C, t)
    E.cam(RM_CAM[0], RM_CAM[1], RM_CAM[2])


def loop(C, t, T):
    _watching(C, t + 1.0)
    E.cam(RM_CAM[0], RM_CAM[1], RM_CAM[2])


SHOTS = {f.__name__: f for f in (
    hook, rule, help, rude, mom, awful, dad, dadface, polite,
    slip, said, silent, turn, grin, welcome, since, loop
)}
