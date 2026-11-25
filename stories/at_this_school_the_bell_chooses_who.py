"""The scene file for \"At This School, The Bell Chooses Who Goes Home\"."""
import math
import rt_engine as E
from rt_engine import M, lerp, lerp3, ease, ease_out, ease_in, ramp, pop, wig, clamp

SCH = (0, 300, 0)

class Ctx: pass

def build():
    C = Ctx()
    C.street = E.Street()
    C.sch = E.Room("school", SCH, wall=(210, 215, 225), floor=(120, 110, 100))
    C.sch.living_bits()
    Ch = E.Char
    C.hero = Ch("hero", (40, 50, 90), (60, 60, 70), scale=0.88).hair("spiky", (40, 30, 20)).jacket((50, 60, 110))
    C.friend = Ch("friend", (180, 50, 50), (50, 50, 60)).hair("short", (30, 20, 10)).jacket((200, 60, 60))
    C.princ = Ch("princ", (30, 30, 35), (40, 40, 40), skin=(230, 190, 160), tall=True).hair("copcap", (20, 20, 20))
    C.princ.extra("tie", (180, 20, 20), (0.3, 0.1, 1.2), (0, -0.4, 1.2))
    fx = E.coll("fx"); C.props = []
    C.bag = E.part("bag", M("bag_m", (40, 80, 140), rough=0.6), fx, (0.4, 0.0, 0.8), bevel=0.05)
    C.props.append(C.bag)
    L = E.coll("lights")
    C.L1 = E.point_light("L1", L, (0, 0, -100), (255, 255, 255), 0.0, radius=0.8)
    C.L2 = E.point_light("L2", L, (0, 0, -100), (255, 255, 255), 0.0, radius=0.8, shadow=False)
    C.always = ("fx", "lights")
    return C

def reset(C):
    for p in C.props: E.gone(p)
    for l in (C.L1, C.L2): l.data.energy = 0.0
    C.sch.show()

def light(l, pos, rgb, watts):
    l.location = pos; l.data.color = E.lin(rgb)[:3]; l.data.energy = watts

def yaw_to(dx, dy): return math.degrees(math.atan2(dx, -dy))
def S(x, y, z=0.0): return (SCH[0] + x, SCH[1] + y, SCH[2] + z)

def hook(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(-2, -4, 0)); h.face("stern"); h.pose(aL=(10,10), aR=(10,10))
    E.cam(S(0, -12, 4), S(0, 0, 3), 50)

def choose(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(-4, -8, 6), S(0, 0, 3), 44)

def daily(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(4, -6, 5), S(0, 0, 3), 48)

def screen(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(0, -9, 7), S(0, 4, 5), 36)

def leave(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "friend", *C.always)
    f = C.friend; f.at(*S(0, -2, 0)); f.face("happy"); f.pose(aL=(40,20), aR=(40,20))
    E.cam(S(0, -7, 3.5), S(0, -2, 3), 52)

def stay(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(2, -3, 0)); h.face("scared"); h.pose(aL=(10,10), aR=(10,10))
    E.cam(S(2, -7, 3.5), S(2, -3, 3), 45)

def friend(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "friend", *C.always)
    f = C.friend; f.at(*S(0, -4, 0)); f.face("happy"); f.pose(aL=(60,30), aR=(60,30))
    E.cam(S(-2, -8, 4), S(0, -4, 3), 50)

def run(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "friend", *C.always)
    f = C.friend; f.at(*S(0, lerp(-4, 4, t/T), 0)); f.face("happy"); f.pose(aL=(70,20), aR=(70,20), lL=40, lR=-40)
    E.cam(S(3, -6, 3), S(0, 0, 3), 55)

def reach(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "friend", *C.always)
    f = C.friend; f.at(*S(0, 4, 0)); f.face("shock"); f.pose(aL=(20,40), aR=(20,40))
    E.cam(S(-2, 1, 3.2), S(0, 4, 3), 40)

def changed(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(0, -8, 6), S(0, 4, 5), 35)

def disappear(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(0, -10, 7), S(0, 4, 5), 40)

def appear(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(0, -10, 7), S(0, 4, 5), 40)

def silent(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(0, 0, 0)); h.face("stern"); h.pose(aL=(0,0), aR=(0,0))
    E.cam(S(0, -6, 3.5), S(0, 0, 3), 50)

def drag(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "friend", *C.always)
    f = C.friend; f.at(*S(0, lerp(4, -2, t/T), 0)); f.face("scared"); f.pose(aL=(10,10), aR=(10,10))
    E.cam(S(4, -2, 4), S(0, 0, 3), 52)

def today(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(0, -3, 0)); h.face("wired"); h.pose(aL=(10,10), aR=(10,10))
    E.cam(S(0, -8, 4), S(0, -3, 3), 45)

def myname(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(0, -10, 7), S(0, 4, 5), 38)

def believe(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(0, -3, 0)); h.face("shock"); h.pose(aL=(30,30), aR=(30,30))
    E.cam(S(0, -6, 3.5), S(0, -3, 3), 42)

def sprint(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(0, lerp(-4, 4, t/T), 0)); h.face("happy"); h.pose(aL=(70,20), aR=(70,20), lL=40, lR=-40)
    E.cam(S(-3, -2, 3), S(0, 2, 3), 55)

def principal(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", "princ", *C.always)
    p = C.princ; p.at(*S(0, 5, 0)); p.face("stern"); p.pose(aL=(10,10), aR=(10,10))
    h = C.hero; h.at(*S(0, 3, 0)); h.face("shock"); h.pose(aL=(20,10), aR=(20,10))
    E.cam(S(0, 1, 3.2), S(0, 4, 3), 45)

def whisper(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "princ", *C.always)
    p = C.princ; p.at(*S(0, 5, 0)); p.face("stern"); p.pose(aL=(10,10), aR=(10,10))
    E.cam(S(0, 3, 3.2), S(0, 5, 3.2), 32)

def not_(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "princ", *C.always)
    p = C.princ; p.at(*S(0, 5, 0)); p.face("stern"); p.pose(aL=(20,10), aR=(20,10))
    E.cam(S(0, 3, 3.2), S(0, 5, 3.2), 30)

def turn(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", "hero", *C.always)
    h = C.hero; h.at(*S(0, 3, 0)); h.face("scared"); h.pose(aL=(10,10), aR=(10,10))
    E.cam(S(0, 6, 3.5), S(0, 3, 3), 50)

def empty(C, t, T):
    E.mood("day"); C.street.day(); E.use("school", *C.always)
    E.cam(S(0, -4, 6), S(0, 2, 3), 55)

def bell(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.1, lamps=0.5); E.use("school", *C.always)
    E.cam(S(-3, -6, 5), S(0, 0, 3), 48)

def final(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.1, lamps=0.5); E.use("school", *C.always)
    E.cam(S(0, -10, 7), S(0, 4, 5), 36)

def boss(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.1, lamps=0.5); E.use("school", *C.always)
    E.cam(S(0, -10, 7), S(0, 4, 5), 34)

def up(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.1, lamps=0.5); E.use("school", "princ", *C.always)
    p = C.princ; p.at(*S(0, 3, 0)); p.face("scared"); p.pose(aL=(10,10), aR=(10,10))
    E.cam(S(0, 1, 3.2), S(0, 3, 3.2), 38)

def loop(C, t, T):
    E.mood("night"); C.street.lights_set(windows=0.1, lamps=0.5); E.use("school", "princ", *C.always)
    p = C.princ; p.at(*S(0, lerp(3, 8, t/T), 0)); p.face("scared"); p.pose(aL=(70,20), aR=(70,20), lL=40, lR=-40)
    E.cam(S(0, -2, 3), S(0, 4, 3), 55)

SHOTS = {f.__name__: f for f in (
    hook, choose, daily, screen, leave, stay, friend, run, reach,
    changed, disappear, appear, silent, drag, today, myname, believe,
    sprint, principal, whisper, not_, turn, empty, bell, final, boss, up, loop
)}
