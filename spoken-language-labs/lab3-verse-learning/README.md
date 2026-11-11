# Lab 3 — learning one verse

One verse, one fresh SKA learner: one step per wave (Lab 1) inside the verse (Lab 2), with the real time between waves; the learner reads the change of the 16 phasors of each wave. Verses so far: Gen 1:1 and Gen 1:2.

**Cubes** (scale 1): each opens in the browser (GitHub Pages), or in a headset (WebXR); the files are in `vr/`. The replays play the verse with the narrator's voice, the points appearing wave by wave as they are spoken.

| verse | | cube | replay with the voice |
|---|---|---|---|
| Gen 1:1 | (z, ż, P) | [`ska_Gen.1.1_hall_scale1_vr.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_vr.html) | [`ska_Gen.1.1_hall_scale1_vr_replay.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_vr_replay.html) |
| Gen 1:1 | (z, ż, H) | [`ska_Gen.1.1_hall_scale1_entropy_vr.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_entropy_vr.html) | [`ska_Gen.1.1_hall_scale1_entropy_vr_replay.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.1_hall_scale1_entropy_vr_replay.html) |
| Gen 1:2 | (z, ż, P) | [`ska_Gen.1.2_hall_scale1_vr.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.2_hall_scale1_vr.html) | [`ska_Gen.1.2_hall_scale1_vr_replay.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.2_hall_scale1_vr_replay.html) |
| Gen 1:2 | (z, ż, H) | [`ska_Gen.1.2_hall_scale1_entropy_vr.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.2_hall_scale1_entropy_vr.html) | [`ska_Gen.1.2_hall_scale1_entropy_vr_replay.html`](https://quantiota.github.io/Universal-Language-Manifold/spoken-language-labs/lab3-verse-learning/vr/ska_Gen.1.2_hall_scale1_entropy_vr_replay.html) |

- `results/`: one CSV per run (verse, harmonics, scale), one row per step
- `figures/`: one figure per run
- `vr/`: the cubes, the replays and the template
- `plot_verse.py`, `build_verse_vr.py`, `make_entropy_cube.py`, `add_replay.py`: figures, cubes and replays from the CSV files

Input, columns of the CSV files and how to reproduce: [Lab 3 in the main README](../README.md#lab-3--learning-one-verse-lab3-verse-learning).
