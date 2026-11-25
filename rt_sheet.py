"""Tile build/stills into contact sheets for a quick look. python rt_sheet.py [cols]"""
import os, sys, glob, cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); d = os.path.join(HERE, "build", "stills")
files = sorted(glob.glob(os.path.join(d, "[0-9]*.jpg"))); cols = int(sys.argv[1]) if len(sys.argv) > 1 else 9; w = 300
tiles = []
for f in files:
    im = cv2.imread(f); im = cv2.resize(im, (w, int(im.shape[0] * w / im.shape[1])), interpolation=cv2.INTER_AREA)
    cv2.rectangle(im, (0, 0), (w, 22), (0, 0, 0), -1); cv2.putText(im, os.path.basename(f)[:-4], (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1); tiles.append(im)
n = 0
for i in range(0, len(tiles), cols * 2):
    chunk = tiles[i:i + cols * 2]
    while len(chunk) % cols: chunk.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(chunk[r:r + cols]) for r in range(0, len(chunk), cols)])
    cv2.imwrite(os.path.join(d, f"_sheet{n}.jpg"), sheet, [cv2.IMWRITE_JPEG_QUALITY, 88]); n += 1
print(n, "sheets")
