"""Lab 2: Genesis aligned verse by verse, from the waves of Lab 1 and the Hebrew text.

No frames and no speech model. Each verse is expected to last a number of waves proportional
to its number of letters (WLC text); the verse boundaries are chosen among the silences of the
recording by dynamic programming, so that every segment's wave count matches its verse.

  - candidate boundaries: silences of at least MIN_PAUSE (Lab 1 gaps not labelled voiceless);
  - cost of a verse: (log of waves found / waves expected)^2, minus a small reward for ending
    on a long pause;
  - the narrator announces every chapter ("Perek" and its number, e.g. פרק יא) before its first
    verse: each announcement is an item of its own, expected to last as many waves as its letters;
    the book opens with a longer announcement (at most MAX_BOOK_INTRO waves);
  - the narrator also announces each weekly portion ("Parashat" and its name, e.g. פרשת לך לך):
    with the chapter announcement when the portion opens a chapter, as an item of its own when it
    opens in the middle of a chapter.

  python align_verses.py      ->  genesis_verses.tsv, figures/
"""
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
LABS = HERE.parent
WAVES = LABS / "lab1-wave-surface" / "data" / "genesis_0s_16542s.npz"
TEXT = LABS.parent / "scripture" / "hebrew" / "text" / "gen_lengths.tsv"
FS = 16000
MIN_PAUSE = 0.25          # s
PAUSE_REWARD = 0.05       # per log(pause / MIN_PAUSE)
MAX_BOOK_INTRO = 1500     # waves, book announcement
INTRO_COST = 0.3
RATIO = (0.3, 3.0)        # admissible waves found / waves expected


def load():
    d = np.load(WAVES)
    waves, gaps, voiceless = d["waves"], d["gaps"], d["gap_voiceless"]
    rows = [l.split("\t") for l in TEXT.read_text().split("\n")[1:] if l.strip()]
    verses = [(r[0], int(r[1]), int(r[2])) for r in rows]
    return waves, gaps[~voiceless], verses


def candidates(waves, sil):
    """Boundary candidates: position in waves (index of the first wave after the pause) and pause length."""
    sil = sil[sil[:, 1] >= MIN_PAUSE * FS]
    pos = np.searchsorted(waves[:, 0], sil[:, 0])
    keep = (pos > 0) & (pos < len(waves))
    pos, dur = pos[keep], sil[keep, 1] / FS
    pos = np.r_[0, pos, len(waves)]                    # start and end of the recording
    dur = np.r_[10.0, dur, 10.0]
    return pos, dur


# weekly portions of Genesis after the first: opening verse (WLC numbering) and name
PARASHOT = {"Gen.6.9": "נח", "Gen.12.1": "לך לך", "Gen.18.1": "וירא", "Gen.23.1": "חיי שרה",
            "Gen.25.19": "תולדת", "Gen.28.10": "ויצא", "Gen.32.4": "וישלח", "Gen.37.1": "וישב",
            "Gen.41.1": "מקץ", "Gen.44.18": "ויגש", "Gen.47.28": "ויחי"}


def numeral(n):
    """Chapter number in Hebrew letters (1-50; 15 and 16 written טו, טז)."""
    if n in (15, 16):
        return "ט" + "וז"[n - 15]
    tens, units = divmod(n, 10)
    return ("יכלמנ"[tens - 1] if tens else "") + ("אבגדהוזחט"[units - 1] if units else "")


def anchor_index(waves, pos, anchors):
    """Candidate boundary of each anchored chapter: the pause boundary nearest to where פרק is heard."""
    t = waves[np.minimum(pos, len(waves) - 1), 0] / FS        # start of the first wave after each pause
    return {c: int(np.argmin(np.abs(t - s))) for c, s in anchors.items()}


def load_anchors():
    f = HERE / "chapter_anchors.tsv"
    if not f.exists():
        return {}
    rows = [l.split("\t") for l in f.read_text().split("\n")[1:] if l.strip()]
    return {int(r[0]): float(r[1]) for r in rows if r[1]}


def align(pos, dur, verses, rate, anchored=None):
    """Dynamic programming over (item, candidate). Items: the book announcement, then for each chapter its
    announcement and its verses. `anchored` maps a chapter to the candidate where its announcement must start."""
    anchored = anchored or {}
    items = []
    for i, (vid, _, letters) in enumerate(verses):
        portion = 4 + len(PARASHOT[vid].replace(" ", "")) if vid in PARASHOT else 0     # פרשת + name
        if vid.endswith(".1"):
            if i == 0:
                items.append(("intro", vid, MAX_BOOK_INTRO, None))
            else:
                chapter = int(vid.split(".")[1])
                items.append(("chapter", vid, (portion + 3 + len(numeral(chapter))) * rate, chapter))  # פרק + number
        elif portion:
            items.append(("portion", vid, portion * rate, None))
        items.append(("verse", vid, letters * rate, None))
    C = len(pos)
    reward = PAUSE_REWARD * np.log(dur / MIN_PAUSE)
    INF = np.inf
    cost = np.full(C, INF)
    cost[0] = 0.0
    back = []
    for kind, vid, x, chapter in items:
        if chapter in anchored:                          # the announcement must start at its anchor
            keep = np.full(C, INF)
            keep[anchored[chapter]] = cost[anchored[chapter]]
            cost = keep
        new = np.full(C, INF)
        arg = np.full(C, -1)
        if kind == "intro" or (kind == "chapter" and chapter not in anchored):
            new[:] = cost                               # no announcement heard: stay on the same boundary
            arg[:] = np.arange(C)
        lo_len, hi_len = (1, x) if kind == "intro" else (RATIO[0] * x, RATIO[1] * x)
        # for every end k, the starts j with pos[k] - pos[j] in [lo_len, hi_len]
        jlo = np.searchsorted(pos, pos - hi_len, "left")
        jhi = np.searchsorted(pos, pos - lo_len, "right")
        for k in range(1, C):
            a, b = jlo[k], min(jhi[k], k)
            if a >= b:
                continue
            j = np.arange(a, b)
            n = pos[k] - pos[j]
            c = cost[j] + (INTRO_COST if kind == "intro" else np.log(n / x) ** 2) - reward[k]
            m = int(np.argmin(c))
            if c[m] < new[k]:
                new[k], arg[k] = c[m], j[m]
        cost = new
        back.append(arg)
    # trace back from the end of the recording
    k, path = C - 1, []
    for (kind, vid, x, _), arg in zip(items[::-1], back[::-1]):
        j = arg[k]
        path.append((kind, vid, x, j, k))
        k = j
    return path[::-1], cost[C - 1]


def main():
    waves, sil, verses = load()
    letters = sum(v[2] for v in verses)
    pos, dur = candidates(waves, sil)
    rate = len(waves) / letters                      # first estimate, refined from the first pass
    anchored = anchor_index(waves, pos, load_anchors())
    for _ in range(2):
        path, total = align(pos, dur, verses, rate, anchored)
        vs = [(x, pos[k] - pos[j]) for kind, _, x, j, k in path if kind == "verse"]
        rate *= np.median([n / x for x, n in vs])
    print(f"{len(pos) - 2} candidate pauses >= {MIN_PAUSE} s; {len(anchored)} chapters anchored; "
          f"rate {rate:.2f} waves per letter; total cost {total:.1f}")

    rows, ratios, intros = [], [], []
    for kind, vid, x, j, k in path:
        a, b = pos[j], pos[k]
        if kind != "verse":
            if b > a:
                intros.append((vid, b - a))
            continue
        t0 = waves[a, 0] / FS
        t1 = (waves[b - 1, 0] + waves[b - 1, 1]) / FS
        ratios.append((b - a) / x)
        rows.append(f"{vid}\t{int(round(x / rate))}\t{t0:.3f}\t{t1:.3f}\t{a}\t{b}\t{b - a}\t{(b - a) / x:.2f}")
    out = HERE / "genesis_verses.tsv"
    out.write_text("verse\tletters\tstart_s\tend_s\tfirst_wave\tend_wave\twaves\tratio\n" + "\n".join(rows) + "\n")
    r = np.array(ratios)
    print(f"{len(rows)} verses aligned; waves found / expected: median {np.median(r):.2f}, "
          f"within 0.67-1.5: {((r > 0.67) & (r < 1.5)).mean() * 100:.1f} %")
    print(f"announcements (book, chapters, portions): {len(intros)} of 56 "
          f"(median {np.median([n for _, n in intros]) if intros else 0:.0f} waves)")
    w = np.array([int(l.split('\t')[6]) for l in rows])
    print(f"longest aligned verse: {rows[int(np.argmax(w))].split(chr(9))[0]} with {w.max()} waves")

    (HERE / "figures").mkdir(exist_ok=True)
    x = np.array([float(l.split("\t")[1]) for l in rows])
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].loglog(x, w, ".", ms=3)
    ax[0].plot([x.min(), x.max()], [x.min() * rate, x.max() * rate], "r-", lw=1)
    ax[0].set(xlabel="letters in the verse (WLC)", ylabel="waves in the aligned segment",
              title=f"Genesis, {len(rows)} verses: rate {rate:.1f} waves per letter")
    ax[1].hist(np.log2(r), bins=60)
    ax[1].set(xlabel="log2(waves found / waves expected)", ylabel="verses", title="match per verse")
    fig.tight_layout()
    fig.savefig(HERE / "figures" / "genesis_alignment.png", dpi=90)
    print(f"wrote {out.name} and figures/genesis_alignment.png")


if __name__ == "__main__":
    main()
