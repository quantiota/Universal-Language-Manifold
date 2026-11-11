"""Lab 3: VR cube of one SKA run on one verse, in the learner's space (z, ż, P).

Fills vr/ska_vr_template.html (the Three.js template of the SKA-ECG cubes, two placeholders:
__DATA__ and __DESCRIPTION__) with results/ska_<verse>_h<h>_scale<s>.csv. A speech verse has no
fixed transitions, so the colours are the voiced stretches of the verse in order of time: a new
stretch starts after a gap of more than GAP_MS between two waves (a pause or a voiceless sound).
Colours run along one sequential ramp, early = dark, late = light.

  python build_verse_vr.py Gen.1.1 all 1   ->  vr/ska_Gen.1.1_hall_scale1_vr.html
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
GAP_MS = 20.0
TEXT = {                                   # the template's heartbeat wording -> the verse's
    "<title>Heartbeat Transition Probability VR</title>": "<title>Verse Learning Cube VR</title>",
    "The heartbeat in the learner's space (z, ż, P)": "One spoken verse in the learner's space (z, ż, P)",
    "highlight next transition": "highlight next stretch",
    "The five transitions of the heartbeat": "The voiced stretches of the verse, in order",
    "All transitions": "All stretches",
}


def main():
    verse, h, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
    name = f"ska_{verse}_h{h}_scale{scale:g}"
    d = pd.read_csv(HERE / "results" / f"{name}.csv")
    k = np.cumsum(d.delta_t.fillna(0).to_numpy() * 1000 > GAP_MS)      # stretch of each step
    d = d.assign(k=k).dropna(subset=["P", "zdot"]).reset_index(drop=True)
    ks = sorted(d.k.unique())
    ramp = matplotlib.colormaps["viridis"](np.linspace(0.15, 0.95, len(ks)))
    names = [f"{i + 1}: {g.t_s.iloc[0]:.2f}–{g.t_s.iloc[-1]:.2f} s, {len(g)} wave{"s" * (len(g) > 1)}"
             for i, (_, g) in enumerate(d.groupby("k"))]
    D = dict(z=d.knowledge.round(3).tolist(), zd=d.zdot.round(3).tolist(), p=d.P.round(4).tolist(),
             t=[ks.index(v) for v in d.k], names=names, colors=[matplotlib.colors.to_hex(c) for c in ramp],
             zmax=float(d.knowledge.max()), zdmax=float(d.zdot.max()))
    harm = "all 16 harmonics, u = Σ Re ċ_h" if h == "all" else f"harmonic {h}, u = Re ċ_{h}"
    desc = (f"{verse.replace('.', ' ', 1).replace('.', ':')} in Hebrew (Talking Bibles International, one narrator, "
            f"{d.t_s.iloc[0]:.2f}–{d.t_s.iloc[-1]:.2f} s of Genesis): {len(d)} waves (voice cycles) = steps of SKA "
            f"real-time learning, fresh learner. Input: {harm}, scale {scale:g}. Horizontal axes: z = ‖Z‖ and "
            f"ż = dz/dt (1/s); vertical axis: P = exp(−|ΔH/H|). Colours: the {len(ks)} voiced stretches "
            f"(split at gaps > {GAP_MS:g} ms), dark = early, light = late.")
    s = (HERE / "vr" / "ska_vr_template.html").read_text(encoding="utf-8")
    for a, b in TEXT.items():
        if a not in s:
            raise SystemExit(f"template text not found: {a}")
        s = s.replace(a, b)
    s = s.replace("__DATA__", json.dumps(D, separators=(",", ":"), ensure_ascii=False))
    s = s.replace("__DESCRIPTION__", desc)
    out = HERE / "vr" / f"{name}_vr.html"
    out.write_text(s, encoding="utf-8")
    print(f"wrote vr/{out.name}  ({len(d)} steps, {len(ks)} stretches)")


if __name__ == "__main__":
    main()
