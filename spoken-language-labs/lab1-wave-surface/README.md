# Lab 1 — the wave surface

Genesis read wave by wave: one wave = one voice cycle, 16 phasors per wave (harmonics 1–16), and the gaps (silence or voiceless) kept as real time.

- `wave_surface.py`: the waves, their surface w(n, φ), their phasors and the gaps → `data/` (not in git) and `figures/`
- `plot_waves.py`: the waves rebuilt from their 16 phasors, drawn on the real audio
- `figures/`: the surface of the first 60 s and of the whole recording; the waves on the audio at 11 s

```bash
python wave_surface.py                 # first 60 s
python wave_surface.py --seconds 0     # whole recording (about 13 min), output in data/ (551 MB)
python plot_waves.py --at 11 --span 0.4
```

Method and results: [Lab 1 in the main README](../README.md#lab-1--the-wave-surface-lab1-wave-surface).
