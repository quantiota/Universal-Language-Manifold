"""Lab 3: figures of one SKA run on one verse and one harmonic (results/ska_<verse>_h<h>_scale<s>.csv).

Left: the input x, the entropy H and the transition probability P = exp(-|dH / H|) against the time
in the recording; steps after a gap (more than GAP_MS between two waves) are marked. Right: the
learner's space (z, z-dot, P), coloured by time.

  python plot_verse.py Gen.1.1 1 25     ->  figures/ska_Gen.1.1_h1_scale25.png
  python plot_verse.py Gen.1.1 all 25   ->  figures/ska_Gen.1.1_hall_scale25.png  (all 16 harmonics)
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
GAP_MS = 20.0


def main():
    verse, h, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
    name = f"ska_{verse}_h{h}_scale{scale:g}"
    d = pd.read_csv(HERE / "results" / f"{name}.csv")
    gap = d.delta_t.fillna(0) * 1000 > GAP_MS
    fig = plt.figure(figsize=(15, 8))
    rows = [("x_input", "input x"), ("entropy", "entropy H (bits)"), ("P", "P")]
    ax0 = None
    for i, (col, label) in enumerate(rows):
        ax = fig.add_subplot(3, 2, 2 * i + 1, sharex=ax0)
        ax0 = ax0 or ax
        ax.plot(d.t_s, d[col], lw=0.7, color="#2a78d6")
        ax.plot(d.t_s[gap], d[col][gap], "o", ms=3, color="#e8730c", label=f"after a gap > {GAP_MS:g} ms")
        ax.set_ylabel(label)
        if i == 0:
            ax.legend(loc="upper right", fontsize=8)
    ax.set_xlabel("time in the recording (s)")
    ax3 = fig.add_subplot(1, 2, 2, projection="3d")
    s = ax3.scatter(d.knowledge, d.zdot, d.P, c=d.t_s, cmap="viridis", s=6)
    ax3.set(xlabel="z", ylabel="ż (1/s)", zlabel="P")
    fig.colorbar(s, ax=ax3, shrink=0.6, label="time (s)")
    fig.suptitle(f"{verse}, {"all 16 harmonics" if h == "all" else f"harmonic {h}"}, scale {scale:g}: fresh learner, {len(d)} waves, "
                 f"{d.t_s.iloc[0]:.2f}-{d.t_s.iloc[-1]:.2f} s; median P {d.P.median():.3f}", x=0.01, ha="left")
    fig.tight_layout()
    (HERE / "figures").mkdir(exist_ok=True)
    fig.savefig(HERE / "figures" / f"{name}.png", dpi=90)
    print(f"wrote figures/{name}.png")


if __name__ == "__main__":
    main()
