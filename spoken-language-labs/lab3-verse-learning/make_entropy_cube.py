"""Lab 3: entropy cube (z, ż, H) of a verse run.

The verse cube vr/<run>_vr.html (build_verse_vr.py, read unchanged) with its vertical axis replaced
by the same run's entropy H, scaled to [min H, max H], as the SKA-ECG entropy cubes
(make_entropy_cubes.py). Add the replay with: python add_replay.py <verse> <h> <scale> entropy

  python make_entropy_cube.py Gen.1.1 all 1   ->  vr/ska_Gen.1.1_hall_scale1_entropy_vr.html
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def swap(s, a, b):
    assert s.count(a) == 1, a
    return s.replace(a, b)


def main():
    verse, h, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
    name = f"ska_{verse}_h{h}_scale{scale:g}"
    s = (HERE / "vr" / f"{name}_vr.html").read_text(encoding="utf-8")
    m = re.search(r"const D = (\{.*?\});\n", s, re.S)
    D = json.loads(m.group(1))
    d = pd.read_csv(HERE / "results" / f"{name}.csv").dropna(subset=["P", "zdot"]).reset_index(drop=True)
    assert len(d) == len(D["z"]) and np.allclose(d.knowledge.round(3), D["z"])   # same run as the cube
    H = d.entropy.round(5)
    D.update(p=H.tolist(), ymin=float(H.min()), ymax=float(H.max()))
    s = s.replace(m.group(0), f"const D = {json.dumps(D, separators=(',', ':'), ensure_ascii=False)};\n")
    s = swap(s, "in the learner's space (z, ż, P)</h1>", "in the learner's space (z, ż, H)</h1>")
    s = swap(s, "const toY = v => v * SIZE;", "const toY = v => (v - D.ymin) / (D.ymax - D.ymin) * SIZE;")
    s = swap(s, "lab('P', -SIZE/2", "lab('H', -SIZE/2")
    s = swap(s, "lab(p.toFixed(2), -SIZE/2 - 0.12,", "lab((D.ymin + p * (D.ymax - D.ymin)).toFixed(2), -SIZE/2 - 0.12,")
    s = swap(s, "vertical axis: P = exp(−|ΔH/H|).", "vertical axis: H, the entropy (bits).")
    s = swap(s, "<title>Verse Learning Cube VR</title>", "<title>Verse Entropy Cube VR</title>")
    out = HERE / "vr" / f"{name}_entropy_vr.html"
    out.write_text(s, encoding="utf-8")
    print(f"wrote vr/{out.name}  ({len(d)} steps, H {D['ymin']:.3f} .. {D['ymax']:.3g})")


if __name__ == "__main__":
    main()
