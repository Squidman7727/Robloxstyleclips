# Instructions for the AI agent

This folder is a kit that makes a 20-second vertical "In This Town" story short in a Roblox-style look. Read `README.md` first: it explains every file and the story format.

## When the user gives you an idea

The user types one line, usually starting with "In this town". Turn it into a finished short:

1. **Write the words** in `stories/<short_name>.json`, in the same shape as `stories/last_one_awake.json`.
   - Line 1 states the rule: "In this town, you must never ...".
   - Then two or three quick examples of how people live with the rule. These are the jokes.
   - Then it turns personal with "I ...", something goes wrong, and there's a twist.
   - The last line runs straight back into the first, so the short loops.
   - About 75 words for 20 seconds. One shot per phrase, so 15 to 18 shots.
   - Show the user the lines before you build the pictures.
2. **Write the pictures** in `stories/<short_name>.py` by copying `stories/last_one_awake.py`. Then change the cast, the sets and every shot function.
   - Every shot sets the mood, who is on screen, each character's position, pose and face, and the camera.
   - Change the camera height and distance on every shot. Avoid two wide shots in a row: every joke gets its own close cut.
   - Swap the face on the beat, because the face does the acting. The faces are listed in `FACE_NAMES` in `rt_engine.py`.
   - If the story needs a new sign, poster or prop texture, draw it in `rt_faces.py` the same way the existing signs are drawn.
3. **Make the voice and textures:** `python rt_voice.py stories/<short_name>.json`, then `python rt_faces.py`.
4. **Check pictures first, before any full render.** This is where a bad camera angle gets caught cheaply.
   - Render: `"%BLENDER%" -b --factory-startup --python rt_render.py -- stories/<short_name>.json --stills --scale 50`. If `BLENDER` isn't set, use `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
   - Run `python rt_sheet.py 9`.
   - Open `build/stills/_sheet0.jpg` (and `_sheet1.jpg` if it exists) and look at every shot. Is each character whole? Can you read each face? Does each shot show what its line says? Is any camera inside a wall?
   - Fix the shots and repeat until every shot is right.
   - Show the user the sheet.
5. **Preview:** `python make.py stories/<short_name>.json --preview`. It makes `build/preview.mp4` at half size.
6. **Final:** `python make.py stories/<short_name>.json` makes `build/FINAL.mp4`.

## Keep the look right

- Use Roblox proportions: dark clothes, dark or strong-coloured hair, and texture on every surface. Big heads and pastel colours look like a toddler show.
- Use only the voice. Add no sound effects and no music.
- Keep `rt_engine.py` story-free. Put story-specific things in the story's own `.py` file.
