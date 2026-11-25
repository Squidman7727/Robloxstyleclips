# In This Town kit

Makes a vertical "In This Town" story short in a Roblox-style look from one idea: blocky avatars, a town street, rooms, a free voice and word-by-word captions. Everything is code, so an AI agent can run it from start to finish.

Not affiliated with Roblox. The avatars are our own blocky look-alikes built in Blender, not Roblox's models or clothing.

## What you need

- Windows
- Python 3.10, then in this folder: `pip install -r requirements.txt`
- Blender 5.2 at `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` (or set the `BLENDER` environment variable to your blender.exe)
- ffmpeg on the PATH
- Internet for step 1 only (the free voice)

## Make the example clip

In this folder:

```bash
python make.py stories/last_one_awake.json
```

The video lands in `build\FINAL.mp4`. Add `--preview` for a half-size check first.

## The four steps (make.py runs them in order)

| Step | File | What it does |
|---|---|---|
| 1 | `rt_voice.py` | Speaks the lines with a free edge-tts voice, one sentence at a time, removes the dead air between sentences, speeds up until it fits the length. Writes `build\vo.wav` and `build\words.json` (start and end of every word). |
| 2 | `rt_faces.py` | Draws the face sheet (16 expressions), the clock face, signs and posters into `build\tex\`. |
| 3 | `rt_render.py` | Run by Blender. Builds the town and the cast from `rt_engine.py`, then calls the story's shot functions once per frame and renders to `build\frames\`. |
| 4 | `rt_finish.py` | Glow, contrast, vignette, speed lines on the hook, captions, then the mp4 with the voice. |

`rt_engine.py` is the 3D kit itself: materials with surface texture, the blocky avatar (`Char`), the street (`Street`), a room (`Room`), lighting moods and the camera. `rt_sheet.py` tiles check stills.

## Make a new clip from one idea

A story is two files with the same name in `stories\`.

**1. `stories\my_story.json`: the words.** One entry per shot. Each `line` is what the narrator says during that shot. Keep to the format the real shorts use:

- First line states the rule: "In this town, ..."
- Then two or three quick examples of how people live with the rule (the jokes)
- Then "I ..." and what happened to the narrator
- A last line that runs back into the first, so the video loops
- About 75 words for 20 seconds, one shot per phrase (a cut about every 1.2 seconds)

Settings in the same file: `voice`, `rate` (starting speed), `seconds`, `fps`, and `fx.flash_into` (shot ids that start with a white flash).

**2. `stories\my_story.py`: the pictures.** It needs:

- `build()`: make the sets and the cast once, return them in an object
- `reset(C)`: called before every frame, parks props and lights
- one function per shot id, `def my_shot(C, t, T)`, where `t` is seconds since the shot started and `T` its length
- `SHOTS = {...}` mapping ids to those functions

Inside a shot function you always set four things:

```python
E.mood("day")                              # day, dusk, night, room, room_dusk, room_night
E.use("street", "hero", *C.always)         # which sets and characters are on screen
hero.at(x, y, 0, yaw=90); hero.face("scared")
hero.pose(head=(nod, turn, tilt), aL=(swing, lift), aR=(swing, lift), lL=20, lR=-20)
E.cam((x, y, z), (look_x, look_y, look_z), fov)
```

Copy `stories\last_one_awake.py` and change the shots. `hero.walk(phase)` and `hero.run(phase)` give walk and run cycles. `pop(t, start)` gives the snappy pose change, `ease(...)` a smooth move.

**3. Check before the full render.** First make the voice and the textures (the stills need their timings and faces):

```bash
python rt_voice.py stories/my_story.json
python rt_faces.py
```

Then render three small stills per shot (about 15 seconds) and tile them:

```bash
"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b --factory-startup --python rt_render.py -- stories/my_story.json --stills --scale 50
python rt_sheet.py 9
```

Look at `build\stills\_sheet0.jpg` and fix what is wrong. Then run `make.py`.

## Rules that keep it looking like the real shorts

Measured on 13 real shorts:

- Roblox proportions: head about two thirds of the torso width. Big heads and huge round eyes look like a toddler show.
- Dark clothes and dark or strong-coloured hair. The frame needs real blacks.
- Every surface has texture (brick, siding, planks, fabric, grass). Flat pastel paint looks childish.
- Crisp block edges. Soft rounded edges look like a toy.
- One shot per phrase, about 1.2 seconds. Change the camera height and distance every shot.
- The face does the acting: swap the drawn face on the beat.
- Captions: two or three words, white with a black edge, the spoken word yellow, below the face.
- Voice only. No sound effects and no home-made music.

## Known limits

- The voice is edge-tts `en-US-AndrewNeural`, a free stand-in for testing. Record your own voice before you publish.
- `build\` is working output and can be deleted at any time; `make.py` rebuilds it.
