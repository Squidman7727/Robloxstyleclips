import math
import rt_engine as E
from rt_engine import M, lerp, lerp3, ease, ease_out, ease_in, ramp, pop, wig, clamp

class Ctx: pass

def build():
    C = Ctx()
    
    # Huge ground plane for school courtyard
    C.ground = E.Static(E.coll("world"))
    C.ground.box(M("ground_m", (72, 82, 76), rough=0.85), (400, 400, 1), (0, 0, -0.5))
    C.ground.box(M("pave_m", (140, 145, 150), rough=0.6), (36, 120, 1.05), (0, 0, 0.0))
    C.ground.done("courtyard")

    # School building facade
    sw = E.coll("school")
    st = E.Static(sw)
    st.box(M("brick", (165, 88, 68), rough=0.8, tex="noise"), (48, 12, 28), (0, 32, 14))
    st.box(M("pillar_m", (220, 220, 225), rough=0.4), (3.2, 3.2, 18), (-8, 11, 9))
    st.box(M("pillar_m", (220, 220, 225), rough=0.4), (3.2, 3.2, 18), (8, 11, 9))
    st.box(M("arch_m", (110, 115, 125), rough=0.5), (14, 4.2, 14), (0, 11.2, 7))
    st.done("facade")

    # Giant Screen above entrance
    fx = E.coll("fx"); C.props = []
    C.screen = E.part("giant_screen", M("screen_body", (22, 24, 30), rough=0.2), fx, (18.0, 5.2, 22.0), bevel=0.1)
    C.scr_glow = E.part("screen_glass", M("screen_led", (30, 240, 90), emit=(30, 240, 90), emit_k=3.5), fx, (17.4, 2.2, 4.8), parent=C.screen, inner=(0, -0.05, 0), bevel=0.01)
    C.props.append(C.screen)

    # Bell Tower / Bell prop
    C.bell = E.empty("bell_tower", fx); C.props.append(C.bell)
    E.Mesher().cyl(2.2, 3.2, (0, 0, 0)).make("bell_body", M("brass", (230, 185, 60), rough=0.25), fx, True, C.bell)
    C.bell.location = (0, 18, 26)

    # Backpack prop
    C.bag = E.part("backpack", M("bag_m", (42, 92, 162), rough=0.7), fx, (1.2, 1.2, 1.2), bevel=0.08)
    C.props.append(C.bag)

    # Characters
    Ch = E.Char
    C.hero = Ch("hero", (45, 135, 95), (32, 38, 52), scale=0.88).hair("spiky", (220, 180, 50)).jacket((45, 135, 95))
    C.friend = Ch("friend", (210, 75, 45), (42, 44, 56), scale=0.9).hair("short", (60, 45, 35)).jacket((210, 75, 45))
    C.principal = Ch("principal", (20, 22, 28), (18, 20, 26), skin=(215, 175, 145), scale=1.05, tall=True, shoes=(15, 15, 18))
    C.principal.jacket((25, 28, 38), zip_rgb=(210, 185, 90))
    C.principal.extra("tie", (180, 30, 40), (0.35, 0.12, 1.4), (0, -0.52, 1.35))

    C.t1 = Ch("teacher1", (80, 40, 110), (35, 35, 45), skin=(200, 155, 125)).hair("bun", (40, 30, 25))
    C.t2 = Ch("teacher2", (50, 50, 60), (30, 30, 40), skin=(190, 145, 115)).hair("short", (20, 20, 20))

    C.crowd = [Ch(f"c{i}", (120 + i*15, 100, 140), (40, 40, 50), scale=0.92).hair("spiky", (30, 30, 30), seed=i+4) for i in range(5)]

    # Lights
    L = E.coll("lights")
    C.L1 = E.point_light("L1", L, (0, 0, -100), (255, 255, 255), 0.0, radius=1.0)
    C.L2 = E.point_light("L2", L, (0, 0, -100), (255, 255, 255), 0.0, radius=1.0, shadow=False)
    C.always = ("school", "fx", "lights")
    return C

def reset(C):
    for p in C.props: E.gone(p)
    for l in (C.L1, C.L2): l.data.energy = 0.0

def light(l, pos, rgb, watts):
    l.location = pos; l.data.color = E.lin(rgb)[:3]; l.data.energy = watts

def yaw_to(dx, dy): return math.degrees(math.atan2(dx, -dy))

# ------------------------------------------------------------------ Shots
def s01(C, t, T):
    """At my school, the final bell doesn't mean everyone goes home."""
    E.mood("day"); E.use("courtyard", "hero", "friend", *C.always)
    C.hero.at(0, -6, 0, yaw=0); C.hero.face("stern"); C.hero.pose(aL=(12, 10), aR=(12, 10))
    C.friend.at(2.2, -5.5, 0, yaw=-15); C.friend.face("happy"); C.friend.pose(aL=(20, 15), aR=(20, 15))
    k = ease(ramp(t, 0, T))
    E.cam(lerp3((0, -22, 2.2), (0, -16, 8.5), k), lerp3((0, 2, 4.5), (0, 6, 6), k), lerp(52, 44, k))

def s02(C, t, T):
    """It means the school gets to choose."""
    E.mood("day"); E.use("courtyard", *C.always)
    z = ease_out(ramp(t, 0, T))
    E.cam((0, -2.5, 14.5), (0, 12, 15.5), lerp(68, 28, z))

def s03(C, t, T):
    """Every day at 3 PM, the bell rings once."""
    E.mood("day"); E.use("courtyard", *C.always)
    shake = 0.3 * math.exp(-t*8) * math.sin(t*55)
    E.cam((4.5 + shake, 12.5, 24 + shake), (0, 16, 26), 36)

def s04(C, t, T):
    """Then a name appears on the giant screen above the entrance."""
    E.mood("day"); E.use("courtyard", *C.always)
    flash = 1.0 if (t*8)%1 > 0.5 else 0.4
    light(C.L1, (0, 8, 20), (30, 255, 110), 400 * flash)
    E.cam((-6, -2, 15.2), (0, 10, 16.5), 40)

def s05(C, t, T):
    """That person gets to leave."""
    E.mood("day"); E.use("courtyard", "friend", *C.always)
    f = C.friend; f.at(0, lerp(-4, 14, t/T), 0, yaw=0); f.face("happy")
    ph = t * 18; s = math.sin(ph)
    f.pose(head=(0, 0, 0), aL=(-60*s, 15), aR=(60*s, 15), lL=50*s, lR=-50*s, bob=0.3*abs(math.cos(ph)))
    E.cam((-3.2, lerp(-8, 6, t/T), 3.5), (0, 5, 3.2), 50)

def s06(C, t, T):
    """Everyone else has to stay."""
    E.mood("day"); E.use("courtyard", "hero", *C.always)
    for i, cr in enumerate(C.crowd):
        cr.at(-6.0 + i*2.8, -8.2, 0, yaw=12)
        cr.face("scared" if i%2==0 else "stern")
        cr.pose(aL=(10, 10), aR=(10, 10))
    E.cam((5.2, -12, 5.5), (-2, -6, 2.5), 55, roll=-7)

def s07(C, t, T):
    """Yesterday, my best friend got picked."""
    E.mood("day"); E.use("courtyard", "hero", "friend", *C.always)
    C.hero.at(-1.5, -6, 0, yaw=25); C.hero.face("happy"); C.hero.pose(aL=(45, 20), aR=(10, 10))
    C.friend.at(1.5, -5.8, 0, yaw=-25); C.friend.face("happy"); C.friend.pose(aL=(10, 10), aR=(50, 20))
    E.cam((0, -9.5, 3.8), (0, -5, 3.0), 38)

def s08(C, t, T):
    """He celebrated, grabbed his backpack, and ran straight for the exit."""
    E.mood("day"); E.use("courtyard", "friend", *C.always)
    f = C.friend; f.at(0, lerp(-5, 10, t/T), 0, yaw=0); f.face("happy")
    E.put(C.bag, (0.4, lerp(-5.2, 9.8, t/T), 2.2), 1.0)
    ph = t * 22; s = math.sin(ph)
    f.pose(head=(0, 0, 0), aL=(-70*s, 10), aR=(70*s, 10), lL=55*s, lR=-55*s, bob=0.35*abs(math.cos(ph)))
    E.cam((8.2, 2.0, 4.5), (0, 6, 3.5), 48)

def s09(C, t, T):
    """But just before he reached the door..."""
    E.mood("day"); E.use("courtyard", "friend", *C.always)
    f = C.friend; f.at(0, 11.2, 0, yaw=180); f.face("shock")
    f.pose(head=(-12, 0, 0), aL=(45, 30), aR=(45, 30), lean=(-15, 0, 0))
    E.cam((0, 6.2, 2.1), (0, 11.2, 3.8), 32)

def s10(C, t, T):
    """The screen changed."""
    E.mood("day"); E.use("courtyard", *C.always)
    flicker = 1.0 if (t*12)%1 > 0.4 else 0.1
    light(C.L1, (0, 8, 20), (255, 40, 40), 600 * flicker)
    E.cam((4.0, 1.0, 13.5), (0, 12, 15.0), 45)

def s11(C, t, T):
    """His name disappeared."""
    E.mood("day"); E.use("courtyard", *C.always)
    fade = 1.0 - ramp(t, 0, T)
    light(C.L1, (0, 8, 20), (255, 255, 255), 300 * fade)
    E.cam((-2.0, 6.0, 16.2), (0, 11.5, 15.8), 34)

def s12(C, t, T):
    """And someone else's name appeared."""
    E.mood("day"); E.use("courtyard", *C.always)
    p = pop(t, 0.1, 0.3)
    light(C.L1, (0, 8, 20), (255, 50, 50), 700 * p)
    E.cam((2.0, 5.0, 15.5), (0, 11.5, 15.8), 38)

def s13(C, t, T):
    """Nobody said a word."""
    E.mood("day"); E.use("courtyard", "hero", "friend", *C.always)
    C.hero.at(-1, -7, 0, yaw=10); C.hero.face("scared"); C.hero.pose(aL=(10,10), aR=(10,10))
    C.friend.at(1, 10.5, 0, yaw=170); C.friend.face("shock"); C.friend.pose(aL=(15,15), aR=(15,15))
    E.cam((-10.5, 2.0, 5.2), (0, 4, 3.5), 52, roll=5)

def s14(C, t, T):
    """The teachers just dragged him back to class like nothing happened."""
    E.mood("day"); E.use("courtyard", "friend", "teacher1", "teacher2", *C.always)
    f = C.friend; f.at(0, lerp(9, 2, t/T), 0, yaw=0); f.face("scared")
    C.t1.at(-1.2, lerp(8.5, 1.8, t/T), 0, yaw=20); C.t1.face("stern"); C.t1.pose(aL=(65, 20), aR=(10, 10))
    C.t2.at(1.2, lerp(8.5, 1.8, t/T), 0, yaw=-20); C.t2.face("stern"); C.t2.pose(aL=(10, 10), aR=(65, 20))
    E.cam((6.5, 4.0, 4.8), (0, 5, 3.2), 46)

def s15(C, t, T):
    """Then today, something weird happened."""
    E.mood("day"); E.use("courtyard", "hero", *C.always)
    h = C.hero; h.at(0, -6, 0, yaw=0); h.face("shock")
    h.pose(head=(4, 0, wig(t, 8, 4)), aL=(25, 15), aR=(25, 15), bob=0.08*wig(t, 6))
    E.cam((0, -10.5, 3.9), (0, -6, 3.5), 42)

def s16(C, t, T):
    """The screen showed MY name."""
    E.mood("day"); E.use("courtyard", *C.always)
    z = ease_out(ramp(t, 0.05, 0.35))
    light(C.L1, (0, 8, 20), (50, 255, 120), 800)
    E.cam((0, lerp(-4, 2, z), lerp(14, 12, z)), (0, 12, 15.5), lerp(60, 26, z))

def s17(C, t, T):
    """I couldn't believe it."""
    E.mood("day"); E.use("courtyard", "hero", *C.always)
    h = C.hero; h.at(0, -6, 0, yaw=0); h.face("scared")
    h.pose(head=(-8, 0, 0), aL=(35, 20), aR=(35, 20))
    E.cam((0, -7.8, 4.1), (0, -6, 3.8), 30)

def s18(C, t, T):
    """I grabbed my bag and sprinted towards the entrance."""
    E.mood("day"); E.use("courtyard", "hero", *C.always)
    h = C.hero; h.at(0, lerp(-6, 9, t/T), 0, yaw=0); h.face("wired")
    E.put(C.bag, (0.3, lerp(-6.2, 8.8, t/T), 2.3), 1.0)
    ph = t * 24; s = math.sin(ph)
    h.pose(head=(0, 0, 0), aL=(-75*s, 10), aR=(75*s, 10), lL=60*s, lR=-60*s, bob=0.4*abs(math.cos(ph)))
    E.cam((-7.2, 1.5, 4.0), (0, 4, 3.0), 50)

def s19(C, t, T):
    """But when I reached the door, the principal was standing there."""
    E.mood("day"); E.use("courtyard", "hero", "principal", *C.always)
    pr = C.principal; pr.at(0, 11.0, 0, yaw=180); pr.face("stern")
    pr.pose(head=(0, 0, 0), aL=(15, 12), aR=(15, 12))
    C.hero.at(0, 7.5, 0, yaw=0); C.hero.face("shock")
    E.cam((0, 3.5, 2.5), (0, 10.5, 4.2), 40)

def s20(C, t, T):
    """He looked at me and whispered..."""
    E.mood("day"); E.use("courtyard", "hero", "principal", *C.always)
    pr = C.principal; pr.at(0, 11.0, 0, yaw=180); pr.face("stern")
    pr.pose(head=(-4, 0, 0), aL=(10, 10), aR=(10, 10))
    E.cam((-1.2, 9.2, 4.5), (0, 11.0, 4.3), 48)

def s21(C, t, T):
    """\"You're not supposed to be here.\""""
    E.mood("day"); E.use("courtyard", "principal", *C.always)
    pr = C.principal; pr.at(0, 11.0, 0, yaw=180); pr.face("stern")
    pr.pose(head=(-6, 0, wig(t, 4, 2)), aL=(12, 10), aR=(12, 10))
    light(C.L1, (0, 10, 6), (255, 230, 200), 220)
    E.cam((0.2, 9.6, 4.4), (0, 11.0, 4.4), 28)

def s22(C, t, T):
    """I turned around."""
    E.mood("day"); E.use("courtyard", "hero", *C.always)
    h = C.hero; spin = lerp(0, 180, ease(t/T))
    h.at(0, 7.5, 0, yaw=spin); h.face("shock")
    h.pose(head=(0, 0, 0), aL=(30, 20), aR=(30, 20))
    E.cam((3.5, 5.0, 4.2), (0, 7.5, 3.8), 44)

def s23(C, t, T):
    """The entire school was empty."""
    E.mood("day"); E.use("courtyard", "hero", *C.always)
    C.hero.at(0, 5, 0, yaw=180); C.hero.face("scared"); C.hero.pose(aL=(10,10), aR=(10,10))
    E.cam((0, -12, 28), (0, 10, 5), 62)

def s24(C, t, T):
    """Then the bell rang again."""
    E.mood("day"); E.use("courtyard", *C.always)
    shake = 0.35 * math.exp(-t*6) * math.sin(t*65)
    E.cam((8.5 + shake, -4.5 + shake, 5.2), (0, 12, 16), 36)

def s25(C, t, T):
    """And the screen displayed one final name."""
    E.mood("day"); E.use("courtyard", *C.always)
    light(C.L1, (0, 8, 20), (255, 30, 30), 900)
    E.cam((-4.5, 2.0, 14.5), (0, 12, 16), 42)

def s26(C, t, T):
    """THE PRINCIPAL."""
    E.mood("day"); E.use("courtyard", *C.always)
    flash = 1.0 if (t*10)%1 > 0.5 else 0.5
    light(C.L1, (0, 8, 20), (255, 255, 255), 1000 * flash)
    E.cam((0, 6.0, 16.0), (0, 11.5, 15.8), 32)

def s27(C, t, T):
    """He slowly looked up at it..."""
    E.mood("day"); E.use("courtyard", "principal", *C.always)
    pr = C.principal; pr.at(0, 11.0, 0, yaw=180); pr.face("shock")
    look = lerp(-10, -35, ease(t/T))
    pr.pose(head=(look, 0, 0), aL=(20, 15), aR=(20, 15))
    E.cam((0, 7.2, 3.2), (0, 11.0, 4.8), 38)

def s28(C, t, T):
    """And started running."""
    E.mood("day"); E.use("courtyard", "principal", *C.always)
    pr = C.principal; pr.at(0, lerp(11, -8, t/T), 0, yaw=180); pr.face("scared")
    ph = t * 26; s = math.sin(ph)
    pr.pose(head=(-20, 0, 0), aL=(-80*s, 15), aR=(80*s, 15), lL=65*s, lR=-65*s, bob=0.45*abs(math.cos(ph)))
    E.cam((6.5, -2.0, 4.5), (0, 4, 3.0), 54)

SHOTS = {f.__name__: f for f in (
    s01, s02, s03, s04, s05, s06, s07, s08, s09, s10,
    s11, s12, s13, s14, s15, s16, s17, s18, s19, s20,
    s21, s22, s23, s24, s25, s26, s27, s28
)}