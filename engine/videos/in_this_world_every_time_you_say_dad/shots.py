from shotkit import *
from rbx import story
from rbx.story import *
import math, random
from mathutils import Vector

V = Video(__file__)
story.bind(V)

def protag(t0, t1, expr="neutral"):
    return story._live(chars.Char("Eddie", skin="#f4d0b6", shirt="#3478f6", pants="#283442", hair="messy", hair_color="#3a2212", face="boy", sleeves="long"), t0, t1, expr)

def dad_char(t0, t1, expr="smile"):
    return story._live(chars.Char("Dad", skin="#e8b896", shirt="#f2e8c4", pants="#485260", hair="short", hair_color="#523822", face="mustache", sleeves="long", extras=("glasses",)), t0, t1, expr)

def rick_char(t0, t1, expr="smirk"):
    return story._live(chars.Char("Rick", skin="#fbe3cb", shirt="#e83838", pants="#1c2028", hair="slick", hair_color="#181818", face="plain", sleeves="long", extras=("collar:#1c2028",)), t0, t1, expr)

@S(1, 0, 5, "Cafeteria: Eddie yells Dad across room")
def s01(t0, t1):
    W.classroom_day()
    E = protag(t0, t1, "shock")
    E.pose(t0, loc=(0, -2.0, 0), rot=0)
    E.act(t0, "point")
    cam = Cam()
    cam.push(t0, t1, (0, -6.0, 3.2), 4.5, 3.0, yaw=180, pitch=4, lens=28)
    cam.crash(t0, 28, 35, 0.08)
    cam.handheld(1.0)
    sfx(t0, "whoosh")

@S(2, 5, 9, "Instantly inflated like beach ball")
def s02(t0, t1):
    W.classroom_day()
    E = protag(t0, t1, "shock")
    E.pose(t0, loc=(0, -2.0, 0), rot=0)
    E.scale = (1.8, 1.8, 1.8)
    cam = Cam()
    cam.push(t0, t1, (0, -5.0, 3.5), 5.5, 4.0, yaw=180, pitch=6, lens=24)
    cam.crash(t0, 24, 32, 0.08)
    cam.handheld(1.2)
    sfx(t0, "poof")

@S(3, 9, 15, "Beach ball! Boing!")
def s03(t0, t1):
    W.classroom_day()
    E = protag(t0, t1, "terror")
    E.pose(t0, loc=(0, -2.0, 0), rot=0)
    E.scale = (2.2, 2.2, 2.2)
    tc = w(14)
    cam = Cam()
    cam.orbit(t0, t1, (0, -2.0, 3.5), 5.0, 4.0, yaw0=160, yaw1=200, pitch=10, lens=22)
    cam.crash(tc, 22, 32, 0.1)
    cam.handheld(1.2)
    sfx(tc, "boing")

@S(4, 15, 21, "Chair snaps in half! Boom!")
def s04(t0, t1):
    W.classroom_day()
    E = protag(t0, t1, "terror")
    E.pose(t0, loc=(0, -2.0, -0.5), rot=0)
    E.scale = (2.2, 2.2, 2.2)
    tb = w(21)
    cam = Cam()
    cam.whip(t0, t1, (2.0, -4.0, 2.8), (0, -2.0, 2.5), lens=25, roll=6)
    cam.crash(tb, 25, 34, 0.12)
    cam.handheld(1.5)
    sfx(tb, "boom")

@S(5, 21, 27, "World explanation: town overview")
def s05(t0, t1):
    W.town()
    cam = Cam()
    cam.track(t0, t1, (0, -20.0, 15.0), (0, -30.0, 2.0), lens=30, yaw=0, pitch=25)
    cam.handheld(1.0)
    sfx(t0, "wind")

@S(6, 27, 34, "Every time you say dad")
def s06(t0, t1):
    W.town()
    T = story._live(chars.Char("Townie", skin="#e9c7a6", shirt="#48a048", pants="#3a3e46", hair="short", hair_color="#2a1e14", face="plain"), t0, t1, "neutral")
    T.pose(t0, loc=(0, -25.0, 0), rot=0)
    cam = Cam()
    cam.push(t0, t1, (0, -28.0, 3.5), 4.0, 3.0, yaw=180, pitch=4, lens=35)
    cam.handheld(1.0)

@S(7, 34, 41, "Gain fifty pounds on the spot")
def s07(t0, t1):
    W.town()
    T = story._live(chars.Char("Townie", skin="#e9c7a6", shirt="#48a048", pants="#3a3e46", hair="short", hair_color="#2a1e14", face="plain"), t0, t1, "shock")
    T.pose(t0, loc=(0, -25.0, 0), rot=0)
    T.scale = (1.6, 1.6, 1.6)
    tt = w(35)
    cam = Cam()
    cam.push(t0, t1, (0, -27.0, 3.2), 4.5, 3.5, yaw=180, pitch=5, lens=28)
    cam.crash(tt, 28, 36, 0.08)
    cam.handheld(1.2)
    sfx(tt, "thud")

@S(8, 41, 51, "Nobody at school talks about parents")
def s08(t0, t1):
    W.hallway_day()
    cam = Cam()
    cam.orbit(t0, t1, (-2.0, -15.0, 3.0), 6.0, 4.0, yaw0=140, yaw1=220, pitch=8, lens=32)
    cam.handheld(1.0)

@S(9, 51, 60, "Kids call them the tall guy at home")
def s09(t0, t1):
    W.classroom_day()
    K = story._live(chars.Char("Kid", skin="#f2dbc6", shirt="#d868a0", pants="#3a3a44", hair="bob", hair_color="#905030", face="girl"), t0, t1, "smile")
    K.pose(t0, loc=(1.2, -3.0, 0), rot=160)
    cam = Cam()
    cam.push(t0, t1, (1.2, -5.5, 3.2), 4.0, 3.0, yaw=165, pitch=4, lens=26)
    cam.handheld(1.0)

@S(10, 60, 73, "Neighbor called teacher dad in front of class")
def s10(t0, t1):
    W.classroom_day()
    N = story._live(chars.Char("Neighbor", skin="#d8a07c", shirt="#e8b838", pants="#2e3844", hair="messy", hair_color="#442818", face="boy"), t0, t1, "shock")
    N.pose(t0, loc=(-1.0, -2.5, 0), rot=20)
    cam = Cam()
    cam.whip(t0, t1, (-3.0, -6.0, 3.5), (-1.0, -2.5, 2.5), lens=25, roll=-4)
    cam.handheld(1.2)

@S(11, 73, 82, "Had to roll him out the door")
def s11(t0, t1):
    W.classroom_day()
    N = story._live(chars.Char("Neighbor", skin="#d8a07c", shirt="#e8b838", pants="#2e3844", hair="messy", hair_color="#442818", face="boy"), t0, t1, "terror")
    N.pose(t0, loc=(-1.0, -2.5, 0), rot=20)
    N.scale = (2.0, 2.0, 2.0)
    ts = w(77)
    cam = Cam()
    cam.track(t0, t1, (-2.0, -4.0, 3.0), (-1.0, -2.5, 2.0), lens=24, yaw=190, pitch=6)
    cam.handheld(1.3)
    sfx(ts, "stomp")

@S(12, 82, 91, "Father's Day banned by mayor")
def s12(t0, t1):
    W.town()
    M = story._live(chars.Char("Mayor", skin="#f0dcc3", shirt="#1e2a4a", pants="#1e2a4a", hair="slick", hair_color="#cccccc", face="mustache", extras=("collar:#ffffff",)), t0, t1, "determined")
    M.pose(t0, loc=(0, -22.0, 0), rot=0)
    cam = Cam()
    cam.push(t0, t1, (0, -26.0, 3.2), 4.5, 3.5, yaw=180, pitch=5, lens=32)
    cam.handheld(1.0)

@S(13, 91, 98, "Survive by biting tongue")
def s13(t0, t1):
    W.hallway_day()
    cam = Cam()
    cam.handheld(1.5)
    cam.orbit(t0, t1, (0.0, -12.0, 3.0), 5.0, 4.0, yaw0=170, yaw1=190, pitch=6, lens=28)

@S(14, 98, 109, "Biggest school talent show of the year")
def s14(t0, t1):
    W.comedy_club()
    cam = Cam()
    cam.orbit(t0, t1, (0, -5.0, 4.0), 7.0, 5.0, yaw0=150, yaw1=210, pitch=12, lens=25)
    cam.handheld(1.1)
    sfx(t0, "cheer")

@S(15, 109, 125, "Dad walked into front row holding giant sign")
def s15(t0, t1):
    W.comedy_club()
    D = dad_char(t0, t1, "smile")
    D.pose(t0, loc=(0, -4.0, 0), rot=180)
    td = w(122)
    cam = Cam()
    cam.push(t0, t1, (0, -8.0, 3.5), 6.0, 4.5, yaw=180, pitch=5, lens=26)
    cam.crash(td, 26, 34, 0.08)
    cam.handheld(1.2)
    sfx(td, "ding")

@S(16, 125, 132, "I panicked and blurted out, Hey, Dad!")
def s16(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "shock")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.act(t0, "hands_head")
    cam = Cam()
    cam.push(t0, t1, (0, -4.5, 3.2), 4.0, 3.0, yaw=180, pitch=4, lens=30)
    cam.handheld(1.2)

@S(17, 132, 139, "Shirt buttons popped like bullets")
def s17(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "terror")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (1.5, 1.5, 1.5)
    tb = w(132)
    cam = Cam()
    cam.push(t0, t1, (0, -4.0, 3.0), 3.8, 2.8, yaw=180, pitch=5, lens=24)
    cam.crash(tb, 24, 32, 0.1)
    cam.handheld(1.3)
    sfx(tb, "boing")

@S(18, 139, 143, "Pop! Pop! Everyone gasped!")
def s18(t0, t1):
    W.comedy_club()
    tp = w(139)
    tg = w(142)
    cam = Cam()
    cam.whip(t0, t1, (2.0, -3.0, 3.2), (0, -1.5, 2.5), lens=22, roll=8)
    cam.crash(tp, 22, 30, 0.08)
    cam.crash(tg, 30, 38, 0.08)
    cam.handheld(1.4)
    sfx(tp, "pop")
    sfx(tg, "gasp")

@S(19, 143, 153, "Skinny Rick pointed and laughed")
def s19(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smirk")
    R.pose(t0, loc=(-1.5, -2.5, 0), rot=10)
    R.act(t0, "point")
    tl = w(152)
    cam = Cam()
    cam.push(t0, t1, (-1.5, -5.5, 3.2), 4.5, 3.5, yaw=190, pitch=5, lens=28)
    cam.handheld(1.0)
    sfx(tl, "kids_laugh")

@S(20, 153, 157, "Nice belly, balloon boy!")
def s20(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smirk")
    R.pose(t0, loc=(-1.5, -2.5, 0), rot=10)
    cam = Cam()
    cam.orbit(t0, t1, (-1.5, -2.5, 3.2), 3.5, 2.8, yaw0=180, yaw1=210, pitch=4, lens=32)
    cam.handheld(1.0)

@S(21, 157, 166, "Wait—who's that in the front row?")
def s21(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "shock")
    R.pose(t0, loc=(-1.5, -2.5, 0), rot=10)
    cam = Cam()
    cam.push(t0, t1, (-1.5, -5.0, 3.2), 4.0, 3.0, yaw=185, pitch=4, lens=28)
    cam.handheld(1.1)

@S(22, 166, 173, "I slipped up again. That's my dad!")
def s22(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "terror")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (1.8, 1.8, 1.8)
    tc = w(172)
    cam = Cam()
    cam.push(t0, t1, (0, -4.5, 3.2), 4.5, 3.2, yaw=180, pitch=5, lens=22)
    cam.crash(tc, 22, 32, 0.1)
    cam.handheld(1.3)
    sfx(tc, "boing")

@S(23, 173, 183, "Rounder than a wrecking ball!")
def s23(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "terror")
    E.pose(t0, loc=(0, -1.5, -0.5), rot=0)
    E.scale = (2.5, 2.5, 2.5)
    tb = w(174)
    cam = Cam()
    cam.push(t0, t1, (0, -5.0, 3.5), 5.5, 4.0, yaw=180, pitch=6, lens=20)
    cam.crash(tb, 20, 30, 0.12)
    cam.handheld(1.4)
    sfx(w(173), "boing")
    sfx(tb, "boom")

@S(24, 183, 193, "Rick kept laughing and stepped onstage to steal trophy")
def s24(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smirk")
    R.pose(t0, loc=(1.0, -3.0, 0), rot=170)
    R.act(t0, "run")
    cam = Cam()
    cam.track(t0, t1, (1.0, -6.0, 3.2), (0, -2.0, 2.5), lens=26, yaw=170, pitch=5)
    cam.handheld(1.2)

@S(25, 193, 197, "Then I noticed something")
def s25(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "shock")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (2.5, 2.5, 2.5)
    cam = Cam()
    cam.push(t0, t1, (0, -4.5, 3.2), 4.0, 3.0, yaw=180, pitch=4, lens=28)
    cam.handheld(1.1)

@S(26, 197, 205, "Rick holding microphone and loved bragging")
def s26(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smile")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    cam = Cam()
    cam.orbit(t0, t1, (0, -2.0, 3.2), 4.5, 3.5, yaw0=160, yaw1=200, pitch=6, lens=30)
    cam.handheld(1.0)

@S(27, 205, 212, "I grinned and yelled, Hey Rick, who")
def s27(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "smile")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (2.5, 2.5, 2.5)
    cam = Cam()
    cam.push(t0, t1, (0, -5.0, 3.2), 4.5, 3.5, yaw=180, pitch=5, lens=28)
    cam.handheld(1.1)

@S(28, 212, 219, "taught you how to dance like that?")
def s28(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "smile")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (2.5, 2.5, 2.5)
    cam = Cam()
    cam.crash(t0, 28, 35, 0.08)
    cam.handheld(1.2)

@S(29, 219, 224, "Rick puffed his chest out")
def s29(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smile")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    R.act(t0, "cheer")
    cam = Cam()
    cam.push(t0, t1, (0, -5.0, 3.2), 4.2, 3.2, yaw=180, pitch=4, lens=30)
    cam.handheld(1.1)

@S(30, 224, 230, "My dad! My dad's a pro!")
def s30(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smile")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    cam = Cam()
    cam.orbit(t0, t1, (0, -2.0, 3.2), 4.0, 3.0, yaw0=170, yaw1=190, pitch=5, lens=32)
    cam.handheld(1.1)

@S(31, 230, 234, "Everyone loves my dad!")
def s31(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "smile")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    cam = Cam()
    cam.crash(t0, 32, 40, 0.08)
    cam.handheld(1.2)

@S(32, 234, 237, "Boing! Boing! Boing!")
def s32(t0, t1):
    W.comedy_club()
    tb = w(234)
    cam = Cam()
    cam.whip(t0, t1, (-2.0, -4.0, 3.5), (0, -2.0, 2.5), lens=24, roll=10)
    cam.crash(tb, 24, 32, 0.1)
    cam.handheld(1.4)
    sfx(tb, "boing")

@S(33, 237, 244, "In three seconds, Skinny Rick blew up")
def s33(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "terror")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    R.scale = (1.8, 1.8, 1.8)
    cam = Cam()
    cam.push(t0, t1, (0, -5.5, 3.5), 5.0, 3.8, yaw=180, pitch=6, lens=22)
    cam.crash(t0, 22, 30, 0.08)
    cam.handheld(1.3)
    sfx(w(242), "whoosh")

@S(34, 244, 250, "Bigger than the entire stage and")
def s34(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "terror")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    R.scale = (2.8, 2.8, 2.8)
    cam = Cam()
    cam.push(t0, t1, (0, -6.5, 4.0), 6.0, 4.5, yaw=180, pitch=8, lens=18)
    cam.handheld(1.4)

@S(35, 250, 257, "Rolled straight out into the parking lot!")
def s35(t0, t1):
    W.comedy_club()
    R = rick_char(t0, t1, "terror")
    R.pose(t0, loc=(0, -2.0, 0), rot=180)
    R.scale = (3.2, 3.2, 3.2)
    ts = w(250)
    cam = Cam()
    cam.track(t0, t1, (0, -8.0, 4.0), (0, -2.0, 3.0), lens=20, yaw=180, pitch=6)
    cam.handheld(1.5)
    sfx(ts, "stomp")

@S(36, 257, 262, "Boom! The crowd went wild!")
def s36(t0, t1):
    W.comedy_club()
    tb = w(257)
    tc = w(261)
    cam = Cam()
    cam.whip(t0, t1, (0, -4.0, 3.5), (0, -2.0, 2.5), lens=25, roll=-6)
    cam.crash(tb, 25, 34, 0.1)
    cam.handheld(1.3)
    sfx(tb, "boom")
    sfx(tc, "cheer")

@S(37, 262, 269, "I waddled over, grabbed my trophy, and")
def s37(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "smile")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (2.0, 2.0, 2.0)
    cam = Cam()
    cam.push(t0, t1, (0, -4.5, 3.2), 4.2, 3.2, yaw=180, pitch=4, lens=28)
    cam.handheld(1.1)

@S(38, 269, 274, "Smiled at the front row.")
def s38(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "smile")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (2.0, 2.0, 2.0)
    cam = Cam()
    cam.orbit(t0, t1, (0, -1.5, 3.2), 3.8, 3.0, yaw0=170, yaw1=190, pitch=4, lens=30)
    cam.handheld(1.0)

@S(39, 274, None, "Thanks, tall guy at home!")
def s39(t0, t1):
    W.comedy_club()
    E = protag(t0, t1, "smile")
    E.pose(t0, loc=(0, -1.5, 0), rot=0)
    E.scale = (2.0, 2.0, 2.0)
    td = t0 + 0.1
    cam = Cam()
    cam.push(t0, t1, (0, -4.0, 3.2), 3.8, 2.8, yaw=180, pitch=4, lens=32)
    cam.crash(td, 32, 40, 0.08)
    cam.handheld(1.2)
    sfx(td, "ding")