# Hebrew text

- `Gen.xml`: Genesis, Westminster Leningrad Codex (WLC 4.20) in OSIS XML, from the Open Scriptures Hebrew Bible Project, <https://github.com/openscriptures/morphhb> (`wlc/Gen.xml`, commit 3d15126fb1ef, downloaded 2026-11-10).
  - The WLC text is in the public domain. The lemma and morphology tags are licensed under CC BY 4.0: credit the Open Scriptures Hebrew Bible Project.
- `gen_lengths.tsv`: one row per verse (1,533), with the number of words and of consonant letters (vowel points and cantillation marks not counted). Genesis: 20,629 words, 78,143 letters; median 49 letters per verse, longest Gen 43:18 with 116.

Used to check verse lengths against the audio: the narrator of `../torah/genesis.mp3` spends about 19 waves per letter, so the longest verse is about 2,200 waves (Lab 1, `spoken-language-labs/lab1-wave-surface`).
