"""Lab 1: the speech wave surface w(n, phi).

The recording is read wave by wave: one wave = one voice cycle, found from the signal itself
(where the waveform best repeats), not from a fixed frame clock. Each wave keeps its own
duration, is placed on a common phase grid and stacked into the surface w(n, phi). As in the
ECG work (complex-events), each wave is read on its own circle: it gives a vector of 16 phasors
c_h, the Fourier coefficients of harmonics h = 1..16 (99 % of the wave's energy here), as the
ECG beat gives one phasor per event. The candidate learner input is c_dot = c_n - c_{n-1},
a vector of 16 complex numbers per wave.

The gaps between voiced runs stay in the stream as real time: they are where a real-time learner
catches up after a burst of waves. Each gap is stored with its start and duration, and labelled
silence or voiceless (sound without a voice cycle). The lab reports how much time a learner may
spend on each wave and still stay within a given delay behind the speech.

  python wave_surface.py                      # first 60 s of Genesis
  python wave_surface.py --start 0 --seconds 600
  python wave_surface.py --seconds 0          # the whole recording, read in 10-minute chunks
"""
import argparse
import subprocess
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DEFAULT_AUDIO = HERE.parents[1] / "scripture" / "hebrew" / "torah" / "genesis.mp3"
FS = 16000
PHI = 64                                  # points on the phase grid
HARMONICS = 16                            # phasors per wave
TMIN, TMAX = 0.0025, 0.012                # voice-cycle durations searched (s)
R_MIN = 0.6                               # minimum self-similarity of a voiced wave
LOUD = 0.05                               # loudness threshold, fraction of the maximum


def decode(path, start, seconds):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(seconds), "-i", str(path),
           "-f", "f32le", "-ac", "1", "-ar", str(FS), "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout,
                         np.float32).astype(float)


def best_period(x, m, lmin, lmax, prev=None):
    """Lag at which the waveform after m repeats itself, and the similarity there.

    Every lag whose similarity is a local maximum close to the best is a candidate; this
    avoids taking two waves for one (double lag) or a ripple inside the wave for a wave
    (half lag). Inside a voiced run the candidate closest to the previous wave's duration
    is kept; at the start of a run, the shortest one.
    """
    if m + 2 * lmax > len(x):
        return 0, 0.0
    a = x[m:m + lmax]
    B = np.lib.stride_tricks.sliding_window_view(x[m + lmin:m + 2 * lmax - 1], lmax)
    r = B @ a / np.sqrt((B * B).sum(1) * (a @ a) + 1e-12)
    peaks = np.flatnonzero((r[1:-1] >= r[:-2]) & (r[1:-1] >= r[2:])) + 1
    if len(peaks) == 0:
        return 0, 0.0
    best = r[peaks].max()
    if prev:
        cand = peaks[r[peaks] >= best - 0.15]
        k = cand[np.argmin(np.abs(np.log((cand + lmin) / prev)))]
    else:
        k = peaks[r[peaks] >= best - 0.05].min()
    return int(k + lmin), float(r[k])


def track_waves(x):
    """Wave starts and durations (samples) of the voiced stretches, with their similarity."""
    lmin, lmax = int(TMIN * FS), int(TMAX * FS)
    env = np.sqrt(np.convolve(x ** 2, np.ones(160) / 160, "same"))
    loud = env > LOUD * env.max()
    waves, m = [], 0
    while m < len(x) - 3 * lmax:
        if not loud[m]:
            m += lmin
            continue
        in_run = bool(waves) and waves[-1][0] + waves[-1][1] == m
        L, r = best_period(x, m, lmin, lmax, waves[-1][1] if in_run else None)
        if r < R_MIN:
            m += lmin
            continue
        if not in_run:                                          # new voiced run: start on the main peak
            m += int(np.argmax(x[m:m + L]))
            L, r = best_period(x, m, lmin, lmax)
            if r < R_MIN:
                m += lmin
                continue
        nxt = m + L - 3 + int(np.argmax(x[m + L - 3:m + L + 4]))   # next start on the matching peak
        waves.append((m, nxt - m, r))
        m = nxt
    return np.array([w[:2] for w in waves], int), np.array([w[2] for w in waves])


def gaps(x, waves):
    """Stretches between voiced runs: start and duration (samples), and the loud fraction inside."""
    env = np.sqrt(np.convolve(x ** 2, np.ones(160) / 160, "same"))
    loud = env > LOUD * env.max()
    ends = np.r_[0, waves[:, 0] + waves[:, 1]]
    starts = np.r_[waves[:, 0], len(x)]
    keep = starts > ends
    g = np.column_stack([ends[keep], starts[keep] - ends[keep]])
    frac = np.array([loud[s:s + n].mean() for s, n in g])
    return g, frac


def max_delay(waves, tau):
    """Largest delay behind the speech of a learner that spends tau samples on each wave."""
    done, worst = 0.0, 0.0
    for a in waves[:, 0] + waves[:, 1]:         # a wave can be read once it is complete
        done = max(a, done) + tau
        worst = max(worst, done - a)
    return worst


def budget(waves, delay):
    """Largest time per wave (samples) that keeps the learner within `delay` samples of the speech."""
    lo, hi = 0.0, float(waves[:, 0].max() + waves[:, 1].max())
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if max_delay(waves, mid) <= delay else (lo, mid)
    return lo


def surface(x, waves):
    phi = np.linspace(0, 1, PHI, endpoint=False)
    return np.array([np.interp(phi * n, np.arange(n + 1), x[s:s + n + 1]) for s, n in waves])


def phasors(x, waves):
    """Fourier coefficients of harmonics 1..HARMONICS of each wave on its own circle."""
    h = np.arange(1, HARMONICS + 1)[:, None]
    return np.array([x[s:s + n] @ np.exp(2j * np.pi * h * np.arange(n) / n).T / n
                     for s, n in waves])


def plot(waves, W, c, out, at=11.0, count=400):
    T = waves[:, 1] / FS * 1000
    k0 = int(np.argmax(waves[:, 0] >= at * FS))
    sl = slice(k0, min(k0 + count, len(W)))
    cdot = np.diff(c, axis=0, prepend=c[:1])
    fig, ax = plt.subplots(4, 1, figsize=(12, 13), gridspec_kw={"height_ratios": [1, 2, 1.5, 1]})
    ax[0].plot(T, ".", ms=1)
    ax[0].set(xlabel="wave index n", ylabel="wave duration (ms)")
    ax[1].imshow(W[sl].T, aspect="auto", origin="lower", cmap="RdBu_r", vmin=-1, vmax=1,
                 extent=[sl.start, sl.stop, 0, 2 * np.pi])
    ax[1].set(ylabel="phase φ", title=f"wave surface w(n, φ), {sl.stop - sl.start} waves from {at:g} s")
    ax[2].imshow(np.abs(c[sl]).T, aspect="auto", origin="lower", cmap="magma",
                 extent=[sl.start, sl.stop, 0.5, HARMONICS + 0.5])
    ax[2].set(ylabel="harmonic h", title="|c_h|: the 16 phasors of each wave")
    ax[3].plot(np.arange(sl.start, sl.stop), np.linalg.norm(cdot[sl], axis=1), lw=0.7)
    ax[3].set(xlabel="wave index n", ylabel="|ċ| (16 harmonics)")
    fig.tight_layout()
    fig.savefig(out, dpi=80)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(path)], capture_output=True, text=True, check=True).stdout
    return float(out)


def read(path, start, seconds, chunk):
    """Track the recording chunk by chunk; positions are in samples from `start`."""
    parts, total = [], 0
    for s in np.arange(start, start + seconds, chunk):
        x = decode(path, s, min(chunk, start + seconds - s))
        waves, sim = track_waves(x)
        g, frac = gaps(x, waves)
        off = total
        parts.append((waves + [off, 0], sim, surface(x, waves).astype(np.float32),
                      phasors(x, waves).astype(np.complex64), g + [off, 0], frac * g[:, 1]))
        total += len(x)
        if seconds > chunk:
            print(f"  {s - start + len(x) / FS:7.0f} s read, {sum(len(q[0]) for q in parts)} waves", flush=True)
    waves, sim, W, c, g, loud = (np.concatenate(z) for z in zip(*parts))
    # a gap cut by a chunk boundary is joined again
    keep = np.r_[True, g[1:, 0] != g[:-1, 0] + g[:-1, 1]]
    grp = np.cumsum(keep) - 1
    g = np.column_stack([g[keep, 0], np.bincount(grp, g[:, 1])]).astype(int)
    frac = np.bincount(grp, loud) / g[:, 1]
    return waves, sim, W, c, g, frac, total


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", default=str(DEFAULT_AUDIO))
    p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--seconds", type=float, default=60.0, help="0 = to the end of the recording")
    p.add_argument("--chunk", type=float, default=600.0, help="seconds decoded at a time")
    a = p.parse_args()
    if a.seconds <= 0:
        a.seconds = duration(a.audio) - a.start

    waves, sim, W, c, g, frac, total = read(a.audio, a.start, a.seconds, a.chunk)
    voiceless = frac > 0.5
    T = waves[:, 1] / FS * 1000
    G = g[:, 1] / FS * 1000
    t = waves[:, 0] / FS
    peak = int((np.searchsorted(t, t + 1.0) - np.arange(len(t))).max())
    print(f"{len(waves)} waves covering {waves[:, 1].sum() / FS:.1f} s of {total / FS:.0f} s; "
          f"duration median {np.median(T):.2f} ms, p10-p90 {np.percentile(T, 10):.2f}-{np.percentile(T, 90):.2f} ms")
    print(f"{len(g)} gaps: {(~voiceless).sum()} silence ({G[~voiceless].sum() / 1000:.1f} s), "
          f"{voiceless.sum()} voiceless ({G[voiceless].sum() / 1000:.1f} s); median {np.median(G):.1f} ms, "
          f"longest {G.max():.0f} ms")
    print(f"rate {len(waves) / (total / FS):.0f} waves/s on average, {peak} in the busiest second")
    for d in (0.05, 0.2, 1.0):
        tau = budget(waves, d * FS)
        print(f"  to stay within {d * 1000:.0f} ms of the speech: at most {tau / FS * 1000:.2f} ms per wave")

    name = f"{Path(a.audio).stem}_{a.start:g}s_{a.seconds:.0f}s"
    (HERE / "data").mkdir(exist_ok=True)
    (HERE / "figures").mkdir(exist_ok=True)
    np.savez_compressed(HERE / "data" / f"{name}.npz", waves=waves, similarity=sim, W=W, c=c,
                        gaps=g, gap_loud=frac, gap_voiceless=voiceless, start=a.start, fs=FS)
    plot(waves, W, c, HERE / "figures" / f"{name}_surface.png")
    print(f"wrote data/{name}.npz and figures/{name}_surface.png")


if __name__ == "__main__":
    main()
