"""Lab 1: the detected waves drawn on the real audio.

Grey: the raw recording. Coloured: each wave rebuilt from its 16 phasors on its own circle,
drawn over its own span, so the two can be compared wave by wave. Vertical lines: wave starts.
Shaded: gaps (silence or voiceless).

  python plot_waves.py                       # 11.0-11.4 s of Genesis, with a zoom
  python plot_waves.py --at 30 --span 0.5
"""
import argparse
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from wave_surface import DEFAULT_AUDIO, FS, HARMONICS, decode

HERE = Path(__file__).resolve().parent


def rebuild(c, n):
    """A wave of n samples from its phasors c_h, h = 1..HARMONICS."""
    h = np.arange(1, HARMONICS + 1)[:, None]
    return 2 * np.real(c @ np.exp(-2j * np.pi * h * np.arange(n) / n))


def panel(ax, x, t0, a, b, waves, c, gaps, voiceless):
    t = lambda k: (k / FS + t0) * 1000                     # sample index -> ms in the recording
    for (s, n), v in zip(gaps, voiceless):
        if s + n > a and s < b:
            ax.axvspan(t(max(s, a)), t(min(s + n, b)), color="tab:orange" if v else "0.85", alpha=0.3, lw=0)
    ax.plot(t(np.arange(a, b)), x[a:b], color="0.45", lw=0.9, label="real audio")
    first = True
    for (s, n), ck in zip(waves, c):
        if s + n > a and s < b:
            ax.plot(t(np.arange(s, s + n)), rebuild(ck, n), color="tab:blue", lw=1.1,
                    label="wave (16 harmonics)" if first else None)
            ax.axvline(t(s), color="tab:red", lw=0.5)
            first = False
    ax.set(xlim=(t(a), t(b)), xlabel="time (ms)", ylabel="amplitude")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=str(HERE / "data" / "genesis_0s_60s.npz"))
    p.add_argument("--at", type=float, default=11.0, help="start, seconds in the recording")
    p.add_argument("--span", type=float, default=0.4, help="seconds shown")
    p.add_argument("--zoom", type=float, default=0.06, help="seconds in the zoomed panel")
    a = p.parse_args()

    d = np.load(a.data)
    t0 = float(d["start"])
    x = decode(DEFAULT_AUDIO, t0, a.at - t0 + a.span + 0.1)
    waves, c, gaps, voiceless = d["waves"], d["c"], d["gaps"], d["gap_voiceless"]
    i0 = int((a.at - t0) * FS)
    i1 = i0 + int(a.span * FS)
    # zoom on the middle of the busiest voiced run in the window
    inside = (waves[:, 0] >= i0) & (waves[:, 0] < i1)
    mid = int(np.median(waves[inside, 0])) if inside.any() else (i0 + i1) // 2
    z0, z1 = mid - int(a.zoom * FS / 2), mid + int(a.zoom * FS / 2)

    fig, ax = plt.subplots(2, 1, figsize=(13, 8))
    panel(ax[0], x, t0, i0, i1, waves, c, gaps, voiceless)
    ax[0].set_title(f"Genesis, {a.at:g}-{a.at + a.span:g} s: real audio (grey), waves rebuilt from 16 harmonics (blue), "
                    f"wave starts (red); gaps: silence (grey), voiceless (orange)", fontsize=9)
    ax[0].axvspan((z0 / FS + t0) * 1000, (z1 / FS + t0) * 1000, color="tab:green", alpha=0.08, lw=0)
    ax[0].legend(loc="upper right", fontsize=8)
    panel(ax[1], x, t0, z0, z1, waves, c, gaps, voiceless)
    ax[1].set_title(f"zoom, {a.zoom * 1000:.0f} ms (green band above)", fontsize=9)
    fig.tight_layout()
    out = HERE / "figures" / f"waves_on_audio_{a.at:g}s.png"
    fig.savefig(out, dpi=90)
    print(f"wrote figures/{out.name}")


if __name__ == "__main__":
    main()
