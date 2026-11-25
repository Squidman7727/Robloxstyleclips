"""Print the comma-separated shot IDs assigned to parallel runner `part` of `total`.
Usage: python tools/split_shots.py <slug> <part_0_based> <total_parts>
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
slug, part, total = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
txt = open(os.path.join(STUDIO, "videos", slug, "shots.py"), encoding="utf-8").read()
ids = sorted({int(m) for m in re.findall(r"@S\(\s*(\d+)\s*,", txt)})
mine = [str(sid) for idx, sid in enumerate(ids) if idx % total == part]
print(",".join(mine))
