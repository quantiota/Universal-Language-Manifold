# Spoken-language labs

The spoken input of the Universal Language Manifold: raw speech read wave by wave, as the SKA learner will read it. The labs follow the SKA-ECG pipeline ([SKA-ECG-Heart-Rate-Variability](https://github.com/quantiota/SKA-ECG-Heart-Rate-Variability), `complex-events/`): one step per wave, the real time between steps, and the change of each wave's phasor as the learner's input.

Corpus so far: Genesis in Hebrew, one narrator (`../scripture/hebrew/torah/genesis.mp3`, 4.6 h, 16 kHz mono, Talking Bibles International), and its text (`../scripture/hebrew/text/`, Westminster Leningrad Codex).

## Lab 1 — the wave surface (`lab1-wave-surface/`)

One wave is one voice cycle, found where the waveform repeats itself; each keeps its own duration, so the clock comes from the signal, not from fixed frames.

- `wave_surface.py`: the waves, their surface w(n, φ) on a 64-point phase grid, 16 phasors per wave (harmonics 1–16, 99 % of the wave's energy), and the gaps (silence or voiceless), kept as real time. Reports the time a real-time learner may spend per wave.
- `plot_waves.py`: the waves rebuilt from their 16 phasors, drawn on the real audio.

Genesis: 1,486,239 waves (median 5.7 ms) covering 52 % of the recording; 87,530 gaps; 90 waves per second on average, 237 in the busiest second. To stay within 50 ms / 200 ms / 1 s of the speech, a learner may spend 3.1 / 4.5 / 6.9 ms per wave.

```bash
python wave_surface.py                 # first 60 s
python wave_surface.py --seconds 0     # whole recording (about 13 min), output in data/ (not in git)
python plot_waves.py --at 11 --span 0.4
```

## Lab 2 — Genesis verse by verse (`lab2-verse-alignment/`)

Each verse is given its place in the recording, from the waves of Lab 1 and the number of letters of each verse: verse boundaries are chosen among the pauses so that every segment's length matches its verse (18.8 waves per letter). The narrator announces each chapter (פרק) and each weekly portion (פרשת); these announcements are modelled, and 46 chapters are anchored where the announcement is heard.

- `align_verses.py` → `genesis_verses.tsv`: 1,533 verses, start and end time, wave range.
- `find_anchors.py` → `chapter_anchors.tsv`: chapter anchors (Whisper, chapter openings only).
- `check_with_asr.py` → `asr_check.tsv`: verification. A sample of 97 segments (40 random, the 10 longest, all chapter openings) transcribed with Whisper and compared, letters only, with the text: 97 of 97 match their own verse better than the two verses on each side; median letter error 0.15.

The alignment itself uses no speech model; Whisper only places the chapter anchors and checks the result. Longest verse: Gen 43:18, 2,477 waves, within one 3,500-step loop.

```bash
python align_verses.py                                                 # about 4 min
PYTHONPATH=<faster-whisper> python check_with_asr.py --models-dir <cache>
```

## Lab 3 — learning one verse (`lab3-verse-learning/`)

One verse, one fresh learner: the SKA learner reads the waves of the verse (Lab 1) inside its boundaries (Lab 2), one step per wave, with the real time between waves, silences included. For each wave n and harmonic h, the return is ċ_h,n = c_h,n − c_h,n−1, and the learner reads

$$
u_n = \sum_{h=1}^{16} \mathrm{Re}\,\dot c_{h,n}, \qquad x_n = \frac{1}{1 + e^{-s\,u_n}}
$$

all 16 harmonics together, with s the scale (`h1` in a file name: harmonic 1 alone, u_n = Re ċ_1,n). The learner's space is (z, ż, P), as in the SKA-ECG work: z = ‖Z‖ the knowledge, ż = dz/dt, P = exp(−|ΔH/H|) with H the entropy.

First verse: Gen 1:1, 4.77 s of the recording (11.16–15.93 s), 554 waves.

| scale | figure | results |
|---|---|---|
| 1 | [`ska_Gen.1.1_hall_scale1.png`](lab3-verse-learning/figures/ska_Gen.1.1_hall_scale1.png) | [`ska_Gen.1.1_hall_scale1.csv`](lab3-verse-learning/results/ska_Gen.1.1_hall_scale1.csv) |
| 10 | [`ska_Gen.1.1_hall_scale10.png`](lab3-verse-learning/figures/ska_Gen.1.1_hall_scale10.png) | [`ska_Gen.1.1_hall_scale10.csv`](lab3-verse-learning/results/ska_Gen.1.1_hall_scale10.csv) |
| 25 | [`ska_Gen.1.1_hall_scale25.png`](lab3-verse-learning/figures/ska_Gen.1.1_hall_scale25.png) | [`ska_Gen.1.1_hall_scale25.csv`](lab3-verse-learning/results/ska_Gen.1.1_hall_scale25.csv) |
| 100 | [`ska_Gen.1.1_hall_scale100.png`](lab3-verse-learning/figures/ska_Gen.1.1_hall_scale100.png) | [`ska_Gen.1.1_hall_scale100.csv`](lab3-verse-learning/results/ska_Gen.1.1_hall_scale100.csv) |
| 25, harmonic 1 | [`ska_Gen.1.1_h1_scale25.png`](lab3-verse-learning/figures/ska_Gen.1.1_h1_scale25.png) | [`ska_Gen.1.1_h1_scale25.csv`](lab3-verse-learning/results/ska_Gen.1.1_h1_scale25.csv) |

**Cubes** (scale 1). Each is one standalone HTML file: download it and open it in a browser, or in a headset (WebXR). Colours: the voiced stretches of the verse, split at gaps of more than 20 ms, dark = early, light = late. The replays play the verse with the narrator's voice; the points appear wave by wave at the time they are spoken (1× = real time).

| | cube | replay with the voice |
|---|---|---|
| (z, ż, P) | [`ska_Gen.1.1_hall_scale1_vr.html`](lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_vr.html) | [`ska_Gen.1.1_hall_scale1_vr_replay.html`](lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_vr_replay.html) |
| (z, ż, H) | [`ska_Gen.1.1_hall_scale1_entropy_vr.html`](lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_entropy_vr.html) | [`ska_Gen.1.1_hall_scale1_entropy_vr_replay.html`](lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_entropy_vr_replay.html) |

- `plot_verse.py`: the figure of a run (x, H and P against time, and the space (z, ż, P)).
- `build_verse_vr.py`: the cube (z, ż, P), from `vr/ska_vr_template.html`, the template of the SKA-ECG cubes.
- `make_entropy_cube.py`: the same cube with the entropy H as the vertical axis.
- `add_replay.py`: the replay, with the sound of the verse cut from the recording.

The SKA engine is not published; its results are in `results/`, one row per step:

| column | |
|---|---|
| `verse`, `harmonic` | the verse, and the harmonic read (`all` = the 16 together) |
| `step_index`, `wave` | the step (1 = the second wave of the verse, the first has no return) and its wave index in the Lab 1 data |
| `t_s`, `duration_ms` | the start of the wave in the recording (s) and its duration |
| `c_cos`, `c_sin` | the phasor of the wave (for `all`: the sum of its 16 phasors) |
| `ret`, `x_input` | the input u_n and x_n = σ(s·u_n) |
| `knowledge`, `entropy`, `matrix_size` | the learner's output: z = ‖Z‖, H, and the size of its matrix |
| `delta_t` | the time since the previous wave (s), gaps included |
| `P`, `zdot` | P = exp(−\|ΔH/H\|) and ż = dz/dt |

**Reproduce.** From the public recording and these CSV files:

1. Build the Lab 1 data (`lab1-wave-surface/data/`, not in git, 551 MB): `python wave_surface.py --seconds 0` in `lab1-wave-surface/` (about 13 min, needs ffmpeg).
2. Check the learner's input against it (run in `spoken-language-labs/`): every row's `ret` and `x_input` follow from the phasors of its wave and of the wave before it.

   ```python
   import numpy as np, pandas as pd
   r = pd.read_csv("lab3-verse-learning/results/ska_Gen.1.1_hall_scale1.csv")
   c = np.load("lab1-wave-surface/data/genesis_0s_16542s.npz")["c"].astype(complex).sum(1)   # all 16 harmonics
   u = np.real(c[r.wave] - c[r.wave - 1])
   x = 1 / (1 + np.exp(-1 * u))                                                              # scale 1
   print(np.abs(u - r.ret).max(), np.abs(x - r.x_input).max())                              # ~5e-9: float32 storage
   ```

   The verse boundaries are in `lab2-verse-alignment/genesis_verses.tsv` (`first_wave`, `end_wave`); the times in `t_s` are the wave starts of the Lab 1 data.
3. Draw the figures, the cubes and the replays from the CSV files (the commands below, in `lab3-verse-learning/`). They read only `results/`, the template, `genesis_verses.tsv` and, for the replays, the recording `scripture/hebrew/torah/genesis.mp3` of this repository; they do not need the Lab 1 data.

```bash
python plot_verse.py Gen.1.1 all 1
python build_verse_vr.py Gen.1.1 all 1
python make_entropy_cube.py Gen.1.1 all 1
python add_replay.py Gen.1.1 all 1             # replay of the (z, ż, P) cube
python add_replay.py Gen.1.1 all 1 entropy     # replay of the (z, ż, H) cube
```

## Notes (`notes/`)

- `meaning-as-geodesic.md`: the meaning of an utterance defined as its geodesic.
- `information-rate.md`: speech carries about 39 bits/s in every language studied (Coupé et al. 2019); the learner's entropy reduced per second as a cross-language prediction.
- `precedents.md`: where the tools come from (waveform interpolation, pitch-synchronous analysis, harmonic models), and what is new here.

## Next

The next verses of Genesis, one fresh learner each.

Python: `/opt/venv` (numpy, scipy, matplotlib, pandas) and ffmpeg. The Whisper checks need `faster-whisper`; the replays need `soundfile`.
