# Information rate as a cross-language invariant

**Status:** research lead, 2026-11-10. From the r/LanguageManifold archive (post of 2025-12-07), kept here before the archive is deleted. Not book text, not in the paper.

## The finding

Coupé, Oh, Dediu & Pellegrino (2019), *Different languages, similar encoding efficiency: Comparable information rates across the human communicative niche*, Science Advances 5(9), eaaw2594, doi:10.1126/sciadv.aaw2594.

Across 17 languages, speech carries information at about **39 bits per second**, nearly the same for all of them. Languages that pack more information into each syllable are spoken more slowly; languages that pack less are spoken faster. The rate is the product of the two, and it stays close to constant.

## Why it matters for the ULM

1. **A measurable prediction.** SKA's entropy is in bits, and the learner reads the speech in real time, one wave per step with the real time between waves. If languages are coordinate projections of one geometry, the learner's **entropy reduced per second** on the same verse should be about the same across languages, while the waves, their rate and the number of steps differ.
2. **It joins what is already built.** Lab 1 keeps the real time (wave durations and gaps); Lab 2 gives each verse its start and end; the learning-cost thread (Riemannian-Neural-Fields/notes/learning-cost) defines entropy along the geodesic per pass.
3. **First step.** Once the learner runs on Genesis, measure bits per second per verse for Hebrew: the first reference value, and its spread across verses.

## Cautions

- The paper measures an information rate in speech; it says nothing about consciousness. The archive's reading ("of human consciousness") goes beyond it.
- The paper's bits come from a syllable-level measure of text information; SKA's bits are the learner's entropy. They are different quantities: the prediction is that SKA's rate is also invariant, not that it equals 39.
- For the books: no comparison with other methods, and say "information rate", not the archive's wording.

Related: [meaning-as-geodesic.md](meaning-as-geodesic.md), Lab 1 (`../lab1-wave-surface`), Lab 2 (`../lab2-verse-alignment`).
