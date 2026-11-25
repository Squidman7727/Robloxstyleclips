from shotkit import *
from rbx import story
from rbx.story import *
import math, random
from mathutils import Vector

V = Video(__file__)
story.bind(V)

# --- Custom Characters ---
def leo(t0, t1, expr="neutral"):
    ch = story._live(chars.Char("Leo", skin="#f0d5b8", shirt="#4a90e2", pants="#2b3040", hair="short", hair_color="#3a2414", face="plain", sleeves="short"), t0, t1, expr)
    return ch

def dad(t0, t1, expr="neutral"):
    ch = story._live(chars.Char("Dad", skin="#f0d5b8", shirt="#e0403a", pants="#3c3c3c", hair="slick", hair_color="#3a2414", face="plain", sleeves="short"), t0, t1, expr)
    return ch

def skinny_rick(t0, t1, expr="neutral"):
    ch = story._live(chars.Char("SkinnyRick", skin="#f0d5b8", shirt="#50e3c2", pants="#4a4a4a", hair="spiky", hair_color="#5a3d2e", face="plain", sleeves="short"), t0, t1, expr)
    return ch

def teacher(t0, t1, expr="neutral"):
    ch = story._live(chars.Char("Teacher", skin="#e0c0a0", shirt="#8b572a", pants="#2b3040", hair="bun", hair_color="#8a5a40", face="girl", sleeves="long"), t0, t1, expr)
    return ch

# --- Helper for character inflation ---
def inflate_char(ch, t_start, t_end, scale_factor=2.2, z_offset=0.2):
    ch.root.scale = (1.0, 1.0, 1.0)
    ch.root.keyframe_insert("scale", frame=F(t_start))
    ch.root.scale = (scale_factor, scale_factor, 1.0 + (scale_factor-1)*0.5) # Wider and slightly taller
    ch.root.loc[2] = z_offset # Push character up slightly to avoid clipping floor
    ch.root.keyframe_insert("scale", frame=F(t_end))
    ch.root.keyframe_insert("loc", index=2, frame=F(t_end))

# --- Scenes ---
def cafeteria_scene():
    W.sky(); W.sun()
    W.floor("wood")
    W.wall("wall_a", (0, 0, 0), (20, -20, 10), rot=0)
    W.wall("wall_a", (0, 0, 0), (-20, -20, 10), rot=0)
    W.wall("wall_a", (-20, 0, 0), (20, 20, 10), rot=90)
    W.table((0, -10, 0), (1.5, 3.0, 0.7))
    W.chair((-1.2, -10, 0), rot=0)
    W.chair((1.2, -10, 0), rot=180)
    W.table((5, -12, 0), (1.5, 3.0, 0.7))
    W.chair((3.8, -12, 0), rot=0)
    W.chair((6.2, -12, 0), rot=180)
    world((0.8, 0.85, 0.9), 0.5)

def talent_show_scene(t0, t1):
    W.comedy_club()
    # Add audience
    for i in range(5):
        story._live(chars.Char(f"Audience{i}", skin="#f0d5b8"), t0, t1, "neutral").pose(t0, loc=(-5 + i*2.5, -6, 0), rot=0)
    for i in range(5):
        story._live(chars.Char(f"Audience{i+5}", skin="#e0c0a0"), t0, t1, "neutral").pose(t0, loc=(-5 + i*2.5, -8, 0), rot=0)
    world((0.8, 0.85, 0.9), 0.5)

# --- Shots ---

@S(1, 0, 6, "Leo in cafeteria, yelling 'Dad!'")
def s01(t0, t1):
    cafeteria_scene()
    L = leo(t0, t1, "happy")
    L.pose(t0, loc=(0, -10, 0), rot=0)
    L.act(t0, "cheer")
    lips(L, t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, -10, 4.4), 6.0, 5.5, yaw=0, pitch=8, lens=35)
    cam.handheld(0.5)
    sfx(t0, "chat", 0.6)

@S(2, 6, 13, "Leo instantly inflates like a beach ball")
def s02(t0, t1):
    cafeteria_scene()
    L = leo(t0, t1, "shock")
    L.pose(t0, loc=(0, -10, 0), rot=0)
    L.act(t0, "shock")
    inflate_char(L, t0 + 0.1, t1 - 0.1, scale_factor=2.2, z_offset=0.2) # First inflation
    cam = Cam()
    cam.push(t0, t1, (0, -10, 4.4), 5.5, 5.0, yaw=0, pitch=8, lens=30, lens1=25)
    cam.handheld(0.8)

@S(3, 13, 14, "Boing! Sound effect for inflation")
def s03(t0, t1):
    cafeteria_scene()
    L = leo(t0, t1, "shock")
    L.pose(t0, loc=(0, -10, 0.2), rot=0) # Already slightly up
    L.root.scale = (2.2, 2.2, 1.5) # Fully inflated
    L.act(t0, "shock")
    cam = Cam()
    cam.push(t0, t1, (0, -10, 4.4), 5.0, 5.0, yaw=0, pitch=8, lens=25)
    cam.handheld(1.0)
    sfx(t0, "boing")

@S(4, 14, 21, "My chair snapped straight in half! Boom!")
def s04(t0, t1):
    cafeteria_scene()
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(0, -10, 0.2), rot=0)
    L.root.scale = (2.2, 2.2, 1.5) # Fully inflated
    ch = W.chair((-1.2, -10, 0), rot=0)
    ch.scale = (1.0, 1.0, 1.0)
    ch.keyframe_insert("scale", frame=F(t0))
    ch.scale = (1.0, 1.0, 0.5) # Break chair
    ch.keyframe_insert("scale", frame=F(t0 + 0.3))
    ch.rotation_euler[2] = math.radians(10)
    ch.keyframe_insert("rotation_euler", index=2, frame=F(t0 + 0.3))
    cam = Cam()
    cam.push(t0, t1, (-1.2, -10, 3.4), 5.0, 4.5, yaw=10, pitch=15, lens=30)
    cam.handheld(1.2)
    sfx(t0 + 0.3, "boom", 0.8)

@S(5, 21, 27, "Leo explains the rule, still fat")
def s05(t0, t1):
    cafeteria_scene()
    L = leo(t0, t1, "sad")
    L.pose(t0, loc=(0, -10, 0.2), rot=0)
    L.root.scale = (2.2, 2.2, 1.5) # Fully inflated
    lips(L, t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, -10, 4.4), 6.0, 5.5, yaw=0, pitch=8, lens=30)
    cam.handheld(0.6)

@S(6, 27, 33, "Graphic or visual representation of 'dad' -> weight gain")
def s06(t0, t1):
    W.sky(); W.sun()
    W.floor("concrete")
    # Placeholder for a visual effect: a character on a scale or a text overlay
    ch_generic = story._live(chars.Char("Generic", skin="#f0d5b8", shirt="#90ee90", pants="#808080", hair="short", hair_color="#3a2414"), t0, t1, "neutral")
    ch_generic.pose(t0, loc=(0, 0, 0), rot=0)
    inflate_char(ch_generic, t0 + 0.1, t1 - 0.1, scale_factor=1.8, z_offset=0.15)
    cam = Cam()
    cam.push(t0, t1, (0, 0, 4.4), 7.0, 6.0, yaw=0, pitch=8, lens=35)
    cam.handheld(0.5)
    sfx(t0 + 0.1, "boing", 0.5)

@S(7, 33, 40, "Show a generic character quickly gaining fifty pounds")
def s07(t0, t1):
    W.sky(); W.sun()
    W.floor("concrete")
    ch_generic = story._live(chars.Char("Generic2", skin="#e0c0a0", shirt="#ff69b4", pants="#808080", hair="bob", hair_color="#8a5a40"), t0, t1, "shock")
    ch_generic.pose(t0, loc=(0, 0, 0), rot=0)
    inflate_char(ch_generic, t0 + 0.05, t1 - 0.05, scale_factor=2.0, z_offset=0.18)
    cam = Cam()
    cam.push(t0, t1, (0, 0, 4.4), 6.5, 5.5, yaw=0, pitch=8, lens=30)
    cam.handheld(0.7)
    sfx(t0 + 0.05, "boing", 0.6)

@S(8, 40, 50, "Kids in school avoiding eye contact, looking nervous")
def s08(t0, t1):
    town_scene()
    k1 = townie(1, t0, t1, "neutral")
    k1.pose(t0, loc=(-3, -14, 0), rot=-15)
    k2 = townie(2, t0, t1, "neutral")
    k2.pose(t0, loc=(3, -16, 0), rot=15)
    k1.face(t0, "side_eye")
    k2.face(t0, "squint")
    cam = Cam()
    cam.push(t0, t1, (0, -15, 4.4), 10.0, 8.0, yaw=0, pitch=8, lens=35)
    cam.handheld(0.5)

@S(9, 50, 59, "Kids whispering 'tall guy at home'")
def s09(t0, t1):
    town_scene()
    k1 = townie(1, t0, t1, "neutral")
    k1.pose(t0, loc=(-1, -14, 0), rot=-15)
    k2 = townie(2, t0, t1, "neutral")
    k2.pose(t0, loc=(1.5, -14.5, 0), rot=15)
    k1.act(t0, "think")
    k2.act(t0, "think")
    cam = Cam()
    cam.push(t0, t1, (0, -14, 4.4), 7.0, 6.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.6)

@S(10, 59, 67, "Classroom scene, neighbor calling teacher 'dad'")
def s10(t0, t1):
    class_scene(t0, t1)
    T = teacher(t0, t1, "neutral")
    T.pose(t0, loc=(0, 5.5, 0), rot=0)
    N = story._live(chars.Char("Neighbor", skin="#f0d5b8", shirt="#6a0dad", pants="#3c3c3c", hair="spiky", hair_color="#3a2414"), t0, t1, "neutral")
    W.sit(N, t0, "desk_0")
    N.pose(t0, loc=up(W.seat_pos("desk_0"), 0.2), rot=facing(W.seat_pos("desk_0"), (0, 5.5)))
    N.act(t0 + 0.2, "point")
    lips(N, t0 + 0.2, t1)
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 4.4), 8.0, 7.0, yaw=0, pitch=10, lens=30)
    cam.handheld(0.7)

@S(11, 67, 73, "Neighbor inflates rapidly")
def s11(t0, t1):
    class_scene(t0, t1)
    T = teacher(t0, t1, "shock")
    T.pose(t0, loc=(0, 5.5, 0), rot=0)
    N = story._live(chars.Char("Neighbor", skin="#f0d5b8", shirt="#6a0dad", pants="#3c3c3c", hair="spiky", hair_color="#3a2414"), t0, t1, "terror")
    N.pose(t0, loc=up(W.seat_pos("desk_0"), 0.2), rot=facing(W.seat_pos("desk_0"), (0, 5.5)))
    N.act(t0 + 0.1, "shock")
    inflate_char(N, t0 + 0.1, t1 - 0.1, scale_factor=2.5, z_offset=0.3)
    cam = Cam()
    cam.push(t0, t1, up(W.seat_pos("desk_0"), 4.4), 6.0, 5.0, yaw=facing(W.seat_pos("desk_0"), (0, 5.5)), pitch=10, lens=28)
    cam.handheld(1.0)
    sfx(t0 + 0.1, "boing")

@S(12, 73, 81, "Fat neighbor being rolled out of the classroom door")
def s12(t0, t1):
    W.hallway_day()
    N = story._live(chars.Char("Neighbor", skin="#f0d5b8", shirt="#6a0dad", pants="#3c3c3c", hair="spiky", hair_color="#3a2414"), t0, t1, "terror")
    N.root.scale = (2.5, 2.5, 1.75) # Fully inflated
    N.pose(t0, loc=(0, -2, 0.3), rot=90)
    N.pose(t1, loc=(0, 5, 0.3), rot=90)
    cam = Cam()
    cam.push(t0, t1, (0, 0, 4.4), 8.0, 7.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.8)
    sfx(t0, "thud", 0.5)

@S(13, 81, 90, "Mayor at a podium, gavel bang, 'BANNED' sign")
def s13(t0, t1):
    W.sky(); W.sun()
    W.floor("carpet")
    W.wall("wall_a", (0, 0, 0), (20, -20, 10), rot=0)
    W.wall("wall_a", (0, 0, 0), (-20, -20, 10), rot=0)
    M = mayor(t0, t1, "determined")
    M.pose(t0, loc=(0, 4.0, 0), rot=0)
    M.act(t0 + 0.2, "point")
    # Simulate a podium/desk
    W.table((0, 3.0, 0), (2.0, 1.0, 1.0), "wood")
    cam = Cam()
    cam.push(t0, t1, (0, 4.0, 4.4), 6.0, 5.0, yaw=0, pitch=8, lens=35)
    cam.handheld(0.7)
    sfx(t0 + 0.3, "bonk", 0.7) # Gavel sound

@S(14, 90, 97, "Close-up on someone biting their tongue, looking stressed")
def s14(t0, t1):
    world((0.8, 0.85, 0.9), 0.5)
    ch = story._live(chars.Char("Stressed", skin="#f0d5b8", hair="bun", hair_color="#8a5a40"), t0, t1, "sad")
    ch.pose(t0, loc=(0, 0, 0), rot=0)
    ch.face(t0, "sad")
    ch.face(t0 + 0.2, "squint", 0.8)
    cam = Cam()
    cam.push(t0, t1, (0, 0, 4.4), 5.0, 4.5, yaw=0, pitch=8, lens=40)
    cam.handheld(0.8)

@S(15, 97, 108, "Wide shot of a stage, 'Talent Show' banner")
def s15(t0, t1):
    talent_show_scene(t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, -8, 4.4), 18.0, 16.0, yaw=0, pitch=10, lens=24)
    cam.handheld(0.5)
    sfx(t0, "cheer", 0.4)

@S(16, 108, 114, "Leo backstage, nervous")
def s16(t0, t1):
    world((0.6, 0.6, 0.65), 0.3)
    W.wall("wall_a", (0, 0, 0), (10, 0, 10), rot=90)
    W.floor("wood")
    L = leo(t0, t1, "gasp")
    L.pose(t0, loc=(0, 0, 0), rot=0)
    L.act(t0, "think")
    L.face(t0, "gasp")
    cam = Cam()
    cam.push(t0, t1, (0, 0, 4.4), 6.0, 5.5, yaw=0, pitch=8, lens=30)
    cam.handheld(0.7)

@S(17, 114, 124, "Dad enters the front row with a sign")
def s17(t0, t1):
    talent_show_scene(t0, t1)
    D = dad(t0, t1, "happy")
    D.pose(t0, loc=(-2, -6, 0), rot=0)
    D.act(t0 + 0.2, "wave")
    sign = W.prop_named("sign", "sign", (0, 0, 0), scale=(0.8, 0.8, 0.8))
    sign.parent = D.handR
    sign.loc = (0.2, -0.2, 0.1)
    sign.rotation_euler = (math.radians(90), 0, math.radians(-90))
    cam = Cam()
    cam.push(t0, t1, (-2, -6, 4.4), 7.0, 6.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.6)

@S(18, 124, 132, "Leo on stage, sees dad, panics, yells 'Dad!'. Starts inflating.")
def s18(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(0, 3.0, 1.0), rot=0)
    L.act(t0, "shock")
    lips(L, t0 + 0.1, t1 - 0.2)
    inflate_char(L, t0 + 0.5, t1 - 0.1, scale_factor=2.0, z_offset=0.18)
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 6.0, 5.0, yaw=0, pitch=8, lens=30)
    cam.handheld(1.0)
    sfx(t1 - 0.1, "boing")

@S(19, 132, 140, "Close up on Leo's shirt buttons popping. Pop! Pop!")
def s19(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.18), rot=0)
    L.root.scale = (2.0, 2.0, 1.3) # Already inflated
    L.act(t0, "recoil")
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 4.0), 4.5, 4.0, yaw=0, pitch=20, lens=45)
    cam.handheld(1.2)
    sfx(t0 + 0.1, "pop")
    sfx(t0 + 0.3, "pop")

@S(20, 140, 142, "Wide shot of audience gasping")
def s20(t0, t1):
    talent_show_scene(t0, t1)
    for i in range(5):
        audience_ch = story._live(chars.Char(f"Audience{i}", skin="#f0d5b8"), t0, t1, "gasp")
        audience_ch.pose(t0, loc=(-5 + i*2.5, -6, 0), rot=0)
        audience_ch.face(t0, "gasp")
    cam = Cam()
    cam.push(t0, t1, (0, -8, 4.4), 18.0, 17.0, yaw=0, pitch=10, lens=24)
    cam.handheld(0.5)
    sfx(t0, "gasp", 0.7)

@S(21, 142, 152, "Skinny Rick pointing and laughing from the audience")
def s21(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "smirk")
    R.pose(t0, loc=(3, -6, 0), rot=0)
    R.act(t0, "point")
    R.face(t0, "smirk")
    cam = Cam()
    cam.push(t0, t1, (3, -6, 4.4), 7.0, 6.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.7)
    sfx(t0 + 0.2, "kids_laugh", 0.6)

@S(22, 152, 157, "Leo (fat) looking sad/angry")
def s22(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "angry")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.18), rot=0)
    L.root.scale = (2.0, 2.0, 1.3) # Inflated
    L.face(t0, "angry")
    lips(L, t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 5.5, 5.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.8)

@S(23, 157, 165, "Rick smirking, looking towards the front row")
def s23(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "smirk")
    R.pose(t0, loc=(3, -6, 0), rot=0)
    R.face(t0, "smirk")
    R.look(t0, 0, -10) # Look towards the front row
    cam = Cam()
    cam.push(t0, t1, (3, -6, 4.4), 6.5, 5.5, yaw=0, pitch=8, lens=30)
    cam.handheld(0.6)

@S(24, 165, 173, "Leo slips up again: 'That's my dad!'")
def s24(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.18), rot=0)
    L.root.scale = (2.0, 2.0, 1.3) # Inflated
    L.act(t0, "shock")
    lips(L, t0 + 0.1, t1 - 0.2)
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 5.0, 4.5, yaw=0, pitch=8, lens=30)
    cam.handheld(1.0)

@S(25, 173, 175, "Boing! Boom! Double inflation")
def s25(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.18), rot=0)
    L.root.scale = (2.0, 2.0, 1.3) # Initial inflation
    inflate_char(L, t0, t1, scale_factor=3.0, z_offset=0.4) # Second inflation
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 4.5, 4.0, yaw=0, pitch=8, lens=25)
    cam.handheld(1.5)
    sfx(t0, "boing")
    sfx(t0 + 0.2, "boom")

@S(26, 175, 183, "Now Leo was rounder than a wrecking ball!")
def s26(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.4), rot=0)
    L.root.scale = (3.0, 3.0, 2.0) # Fully inflated
    L.act(t0, "hands_head")
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 6.0, 5.0, yaw=0, pitch=8, lens=20)
    cam.handheld(1.0)

@S(27, 183, 192, "Rick kept laughing and stepped onstage to steal my trophy.")
def s27(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "angry")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.4), rot=0)
    L.root.scale = (3.0, 3.0, 2.0) # Fully inflated
    R = skinny_rick(t0, t1, "smirk")
    R.pose(t0, loc=(3, -6, 0), rot=0)
    R.pose(t1, loc=(1.5, 3.0, 1.0), rot=0) # Move to stage
    R.act(t0, "cheer")
    R.face(t0, "smirk")
    W.prop_named("trophy", "trophy", (0, 3.0, 1.0))
    cam = Cam()
    cam.push(t0, t1, (0, 0, 4.4), 10.0, 8.0, yaw=0, pitch=10, lens=28)
    cam.handheld(0.7)
    sfx(t0, "kids_laugh", 0.6)

@S(28, 192, 204, "Then I noticed something. Rick was holding the microphone—and he loved bragging.")
def s28(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "smirk")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.4), rot=0)
    L.root.scale = (3.0, 3.0, 2.0) # Fully inflated
    R = skinny_rick(t0, t1, "smirk")
    R.pose(t0, loc=(1.5, 3.0, 1.0), rot=0)
    mic = W.prop_named("mic", "mic", (0, 0, 0))
    mic.parent = R.handR
    mic.loc = (0.2, 0, 0.1)
    mic.rotation_euler = (math.radians(90), 0, math.radians(-90))
    R.act(t0, "hold")
    cam = Cam()
    cam.push(t0, t1, (1.5, 3.0, 5.4), 6.0, 5.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.8)

@S(29, 204, 218, "Leo grinned and yelled, 'Hey Rick, who taught you how to dance like that?'")
def s29(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "smirk")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.4), rot=0)
    L.root.scale = (3.0, 3.0, 2.0) # Fully inflated
    L.face(t0, "smirk")
    L.act(t0, "point")
    lips(L, t0 + 0.2, t1)
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 6.0, 5.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.9)

@S(30, 218, 223, "Rick puffed his chest out.")
def s30(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "smug")
    R.pose(t0, loc=(1.5, 3.0, 1.0), rot=0)
    mic = W.prop_named("mic", "mic", (0, 0, 0))
    mic.parent = R.handR
    mic.loc = (0.2, 0, 0.1)
    mic.rotation_euler = (math.radians(90), 0, math.radians(-90))
    R.act(t0, "fists")
    R.face(t0, "smug")
    cam = Cam()
    cam.push(t0, t1, (1.5, 3.0, 5.4), 5.5, 5.0, yaw=0, pitch=8, lens=35)
    cam.handheld(0.7)

@S(31, 223, 233, "'My dad! My dad's a pro! Everyone loves my dad!'")
def s31(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "smug")
    R.pose(t0, loc=(1.5, 3.0, 1.0), rot=0)
    mic = W.prop_named("mic", "mic", (0, 0, 0))
    mic.parent = R.handR
    mic.loc = (0.2, 0, 0.1)
    mic.rotation_euler = (math.radians(90), 0, math.radians(-90))
    R.act(t0, "cheer")
    lips(R, t0 + 0.1, t1 - 0.1)
    cam = Cam()
    cam.push(t0, t1, (1.5, 3.0, 5.4), 5.0, 4.5, yaw=0, pitch=8, lens=30)
    cam.handheld(0.9)

@S(32, 233, 237, "Boing! Boing! Boing! Rapid inflation for Rick")
def s32(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "terror")
    R.pose(t0, loc=(1.5, 3.0, 1.0), rot=0)
    mic = W.prop_named("mic", "mic", (0, 0, 0))
    mic.parent = R.handR
    mic.loc = (0.2, 0, 0.1)
    mic.rotation_euler = (math.radians(90), 0, math.radians(-90))
    inflate_char(R, t0, t1, scale_factor=2.0, z_offset=0.18)
    cam = Cam()
    cam.push(t0, t1, (1.5, 3.0, 5.4), 5.0, 4.5, yaw=0, pitch=8, lens=25)
    cam.handheld(1.5)
    sfx(t0, "boing")
    sfx(t0 + 0.15, "boing")
    sfx(t0 + 0.3, "boing")

@S(33, 237, 249, "Skinny Rick blew up bigger than the entire stage")
def s33(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "terror")
    R.pose(t0, loc=(1.5, 3.0, 1.0 + 0.18), rot=0)
    R.root.scale = (2.0, 2.0, 1.3) # Initial inflation
    inflate_char(R, t0, t1, scale_factor=4.0, z_offset=0.8) # Massive inflation
    cam = Cam()
    cam.push(t0, t1, (1.5, 3.0, 5.4), 6.0, 5.0, yaw=0, pitch=8, lens=20, lens1=15)
    cam.handheld(1.8)

@S(34, 249, 256, "And rolled straight out into the parking lot!")
def s34(t0, t1):
    talent_show_scene(t0, t1)
    R = skinny_rick(t0, t1, "terror")
    R.pose(t0, loc=(1.5, 3.0, 1.0 + 0.8), rot=0)
    R.root.scale = (4.0, 4.0, 2.5) # Fully massive
    R.pose(t0, loc=(1.5, 3.0, 1.0 + 0.8), rot=0)
    R.pose(t1, loc=(10, -5, 0.8), rot=45) # Rolling off stage
    cam = Cam()
    cam.push(t0, t1, (1.5, 3.0, 5.4), 10.0, 15.0, yaw=0, pitch=10, lens=18)
    cam.handheld(1.5)

@S(35, 256, 258, "Boom! Sound effect for Rick rolling away")
def s35(t0, t1):
    W2.parking_lot((0, 0))
    W.sky(); W.sun()
    R = skinny_rick(t0, t1, "terror")
    R.root.scale = (4.0, 4.0, 2.5) # Fully massive
    R.pose(t0, loc=(10, -5, 0.8), rot=45)
    cam = Cam()
    cam.push(t0, t1, (10, -5, 4.4), 12.0, 10.0, yaw=0, pitch=8, lens=20)
    cam.handheld(1.0)
    sfx(t0, "boom", 0.9)

@S(36, 258, 262, "The crowd went wild!")
def s36(t0, t1):
    talent_show_scene(t0, t1)
    for i in range(5):
        audience_ch = story._live(chars.Char(f"Audience{i}", skin="#f0d5b8"), t0, t1, "cheer")
        audience_ch.pose(t0, loc=(-5 + i*2.5, -6, 0), rot=0)
        audience_ch.act(t0, "cheer")
    cam = Cam()
    cam.push(t0, t1, (0, -8, 4.4), 18.0, 17.0, yaw=0, pitch=10, lens=24)
    cam.handheld(0.5)
    sfx(t0, "cheer", 1.0)

@S(37, 262, None, "Leo waddled over, grabbed my trophy, and smiled at the front row. 'Thanks, tall guy at home!'")
def s37(t0, t1):
    talent_show_scene(t0, t1)
    L = leo(t0, t1, "happy")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.4), rot=0)
    L.root.scale = (3.0, 3.0, 2.0) # Fully inflated
    L.face(t0, "smirk")
    L.pose(t0, loc=(0, 3.0, 1.0 + 0.4))
    L.pose(t0 + 0.5, loc=(-0.5, 3.0, 1.0 + 0.4), rot=-15) # Waddling
    L.act(t0 + 0.8, "hold")
    W.prop_named("trophy", "trophy", (0, 3.0, 1.0))
    trophy = W.prop_named("trophy", "trophy", (0, 3.0, 1.0))
    trophy.parent = L.handR
    trophy.loc = (0.2, -0.2, 0.1)
    trophy.rotation_euler = (math.radians(90), 0, math.radians(-90))
    lips(L, t0 + 1.0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, 3.0, 5.4), 6.0, 5.0, yaw=0, pitch=8, lens=30)
    cam.handheld(0.8)