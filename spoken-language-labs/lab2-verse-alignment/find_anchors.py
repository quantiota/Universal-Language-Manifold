"""Lab 2: chapter anchors. Whisper listens only to the chapter openings and locates the word פרק.

The narrator announces every chapter ("Perek" and its number) before its first verse. Around
the opening found by align_verses.py, a window of the recording is transcribed with word
timestamps; the time where פרק starts is the chapter's anchor. align_verses.py then forces each
chapter announcement to start at its anchor, so a slip cannot cross a chapter boundary. The
verse boundaries inside each chapter stay model-free.

  PYTHONPATH=<faster-whisper dir> python find_anchors.py --models-dir <cache>   ->  chapter_anchors.tsv
"""
import argparse
from pathlib import Path

from check_with_asr import clip, letters

HERE = Path(__file__).resolve().parent
BEFORE, AFTER = 15.0, 8.0          # window around the current start of each chapter's first verse (s)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="medium")
    p.add_argument("--models-dir", default=None)
    p.add_argument("--threads", type=int, default=40)
    a = p.parse_args()
    from faster_whisper import WhisperModel

    rows = [l.split("\t") for l in (HERE / "genesis_verses.tsv").read_text().split("\n")[1:] if l.strip()]
    firsts = [(int(r[0].split(".")[1]), float(r[2])) for r in rows if r[0].endswith(".1") and r[0] != "Gen.1.1"]
    model = WhisperModel(a.model, device="cpu", compute_type="int8", cpu_threads=a.threads,
                         download_root=a.models_dir)
    out = []
    for chapter, t in firsts:
        w0 = max(t - BEFORE, 0)
        segs, _ = model.transcribe(clip(w0, t + AFTER), language="he", beam_size=5, word_timestamps=True,
                                   condition_on_previous_text=False)
        hits = [w0 + w.start for s in segs for w in s.words if letters(w.word).startswith("פרק")]
        if hits:
            anchor = min(hits, key=lambda h: abs(h - t))           # the פרק closest to the expected opening
            out.append(f"{chapter}\t{anchor:.3f}\t{anchor - t:+.2f}\t{len(hits)}")
        else:
            out.append(f"{chapter}\t\t\t0")
        print(out[-1], flush=True)
    (HERE / "chapter_anchors.tsv").write_text("chapter\tanchor_s\tshift_from_previous_s\tperek_heard\n"
                                              + "\n".join(out) + "\n")
    print(f"{sum(1 for l in out if l.split(chr(9))[1])} of {len(out)} chapters anchored")


if __name__ == "__main__":
    main()
