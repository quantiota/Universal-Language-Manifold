# Lab 2 — Genesis verse by verse

Each of the 1,533 verses of Genesis given its place in the recording, from the waves of Lab 1 and the number of letters of each verse (text: `../../scripture/hebrew/text/`).

- `align_verses.py` → `genesis_verses.tsv`: start and end time and wave range of each verse; `figures/genesis_alignment.png`
- `find_anchors.py` → `chapter_anchors.tsv`: the chapter anchors (Whisper, chapter openings only)
- `check_with_asr.py` → `asr_check.tsv`: the verification on a sample of 97 segments

```bash
python align_verses.py                                                 # about 4 min, needs the Lab 1 data
PYTHONPATH=<faster-whisper> python check_with_asr.py --models-dir <cache>
```

Method and results: [Lab 2 in the main README](../README.md#lab-2--genesis-verse-by-verse-lab2-verse-alignment).
