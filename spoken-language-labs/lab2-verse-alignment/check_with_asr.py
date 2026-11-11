"""Lab 2 check: does each aligned segment contain its verse?

Verification only: the alignment itself (align_verses.py) uses no speech model. Here a sample of
aligned segments is cut from the recording and transcribed with Whisper (faster-whisper, CPU),
and each transcript is compared, letters only, with the WLC text of its verse and of the two
verses on each side. A segment is correct when its own verse matches best.

  PYTHONPATH=<faster-whisper dir> python check_with_asr.py --model medium --models-dir <cache>
"""
import argparse
import subprocess
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AUDIO = HERE.parents[1] / "scripture" / "hebrew" / "torah" / "genesis.mp3"
TEXT = HERE.parents[1] / "scripture" / "hebrew" / "text" / "Gen.xml"
VERSES = HERE / "genesis_verses.tsv"
FINALS = str.maketrans("ךםןףץ", "כמנפצ")
OSIS = "{http://www.bibletechnologies.net/2003/OSIS/namespace}"


def letters(s):
    return "".join(ch for ch in s if "HEBREW LETTER" in unicodedata.name(ch, "")).translate(FINALS)


def wlc():
    root = ET.parse(TEXT).getroot()
    return {v.get("osisID"): letters("".join("".join(w.itertext()) for w in v.iter(OSIS + "w")))
            for v in root.iter(OSIS + "verse")}


def distance(a, b):
    """Levenshtein distance."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(hyp, ref):
    return distance(hyp, ref) / max(len(ref), 1)


def clip(t0, t1):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(AUDIO),
           "-f", "f32le", "-ac", "1", "-ar", "16000", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)


def sample(rows, n_random, seed=0):
    ids = [r[0] for r in rows]
    waves = np.array([int(r[6]) for r in rows])
    rng = np.random.default_rng(seed)
    pick = set(rng.choice(len(rows), n_random, replace=False).tolist())
    pick |= set(np.argsort(waves)[-10:].tolist())                       # the 10 longest
    firsts = [i for i, v in enumerate(ids) if v.endswith(".1") and not v.endswith(".1.1")]
    pick |= set(firsts)                                                 # every chapter opening
    return sorted(pick)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="medium")
    p.add_argument("--models-dir", default=None)
    p.add_argument("--random", type=int, default=40)  # plus the 10 longest verses and all chapter openings
    p.add_argument("--threads", type=int, default=40)
    a = p.parse_args()
    from faster_whisper import WhisperModel

    rows = [l.split("\t") for l in VERSES.read_text().split("\n")[1:] if l.strip()]
    ids = [r[0] for r in rows]
    text = wlc()
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=a.threads,
                         download_root=a.models_dir)
    out, ok = [], 0
    for i in sample(rows, a.random):
        vid, t0, t1 = rows[i][0], float(rows[i][2]), float(rows[i][3])
        segs, _ = model.transcribe(clip(max(t0 - 0.05, 0), t1 + 0.05), language="he", beam_size=5,
                                   condition_on_previous_text=False, vad_filter=False)
        hyp = letters(" ".join(s.text for s in segs))
        own = cer(hyp, text[vid])
        nb = {ids[k]: cer(hyp, text[ids[k]]) for k in (i - 2, i - 1, i + 1, i + 2) if 0 <= k < len(ids)}
        best = min(nb.values()) if nb else 9.9
        good = own < best
        ok += good
        # does the transcript start with the end of the previous verse or run into the next one?
        out.append(f"{vid}\t{t1 - t0:.1f}\t{len(text[vid])}\t{len(hyp)}\t{own:.2f}\t{best:.2f}\t{'yes' if good else 'NO'}\t{hyp}")
        print(out[-1][:120], flush=True)
    (HERE / "asr_check.tsv").write_text(
        "verse\tseconds\tletters_text\tletters_heard\tcer_own\tcer_best_neighbour\tcorrect\ttranscript\n"
        + "\n".join(out) + "\n")
    own = np.array([float(l.split("\t")[4]) for l in out])
    print(f"\n{ok} of {len(out)} segments match their own verse best; "
          f"letter error rate against own verse: median {np.median(own):.2f}")


if __name__ == "__main__":
    main()
