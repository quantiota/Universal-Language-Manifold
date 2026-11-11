"""Lab 3: real-time replay of a verse cube, with the verse's sound.

Adds play / pause / speed / position to vr/<run>_vr.html (build_verse_vr.py). The points appear one
wave at a time at the recorded timing: 1x = the speed of the narrator, gaps included. The sound
of the verse (Lab 2 boundaries, cut from the recording, 16 kHz mono WAV) is embedded and plays
in step with the points. The cube stays one standalone file.
Adapted from the SKA-ECG replay (SKA-ECG-SDDB, add_replay.py).

  python add_replay.py Gen.1.1 all 1           ->  vr/ska_Gen.1.1_hall_scale1_vr_replay.html
  python add_replay.py Gen.1.1 all 1 entropy   ->  vr/ska_Gen.1.1_hall_scale1_entropy_vr_replay.html
"""
import base64
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf

HERE = Path(__file__).resolve().parent
AUDIO = HERE.parents[1] / "scripture" / "hebrew" / "torah" / "genesis.mp3"
VERSES = HERE.parent / "lab2-verse-alignment" / "genesis_verses.tsv"


def clip(t0, t1):
    with sf.SoundFile(str(AUDIO)) as f:
        f.seek(int(t0 * f.samplerate))
        x = f.read(int((t1 - t0) * f.samplerate), dtype="float32")
        buf = io.BytesIO()
        sf.write(buf, x, f.samplerate, format="WAV", subtype="PCM_16")
    return base64.b64encode(buf.getvalue()).decode()


def main():
    verse, h, scale = sys.argv[1], sys.argv[2], float(sys.argv[3])
    name = f"ska_{verse}_h{h}_scale{scale:g}" + (f"_{sys.argv[4]}" if len(sys.argv) > 4 else "")
    src, out = HERE / "vr" / f"{name}_vr.html", HERE / "vr" / f"{name}_vr_replay.html"
    v = pd.read_csv(VERSES, sep="\t").set_index("verse").loc[verse]
    t0, t1 = float(v.start_s), float(v.end_s)
    d = pd.read_csv(HERE / "results" / f"ska_{verse}_h{h}_scale{scale:g}.csv").dropna(subset=["P", "zdot"]).reset_index(drop=True)
    s = src.read_text(encoding="utf-8")

    # 1. timing into the data object: time of every point from the start of the verse
    i = s.find("const D ="); e = s.find("};", i) + 1
    D = json.loads(s[i + 9:e])
    assert len(D["p"]) == len(d) and np.allclose(D["z"], d.knowledge.round(3)), "cube and run differ"
    D["tv"] = (d.t_s - t0).round(5).tolist()
    D["tend"] = round(t1 - t0, 5)
    s = s[:i] + "const D = " + json.dumps(D, separators=(",", ":"), ensure_ascii=False) + ";" + s[e + 1:]

    # 2. player style + markup (the sound is embedded)
    css = """  #player { position:absolute; left:50%; transform:translateX(-50%); bottom:72px; display:flex; align-items:center; gap:8px; background:rgba(18,19,23,.9); border:1px solid var(--line); border-radius:10px; padding:8px 12px; font-size:12px; width:min(680px, calc(100% - 32px)); box-sizing:border-box; }
  #player button, #player select { background:#22232a; color:var(--ink); border:1px solid var(--line); border-radius:6px; padding:4px 8px; font-size:12px; cursor:pointer; }
  #player input[type=range] { flex:1; min-width:60px; accent-color:#e87ba4; }
  #player .clock { color:var(--ink2); white-space:nowrap; font-variant-numeric:tabular-nums; min-width:230px; text-align:right; }
  #hint { bottom:128px !important; }
"""
    s = s.replace("</style>", css + "</style>", 1)
    player = f"""<div id="player">
  <button id="restart" title="Start again">⏮</button>
  <button id="play" title="Play / pause">▶ Play</button>
  <select id="speed" title="Replay speed"><option value="0.1">0.1×</option><option value="0.25">0.25×</option><option value="0.5">0.5×</option><option value="1" selected>1× (real time)</option></select>
  <input id="pos" type="range" min="1" max="1" value="1" title="Position in the verse">
  <span class="clock" id="clock"></span>
  <audio id="snd" preload="auto" src="data:audio/wav;base64,{clip(t0, t1)}"></audio>
</div>
"""
    assert '<div id="hint">' in s
    s = s.replace('<div id="hint">', player + '<div id="hint">', 1)
    s = s.replace("Desktop: drag to rotate",
                  "Replay: ▶ plays the verse with its sound, one wave at a time at the narrator's pace "
                  "(1× = real time). Desktop: drag to rotate", 1)

    # 3. replay logic: the clock follows the sound when it plays
    js = """
// ---- real-time replay: the points appear wave by wave, at the recorded timing, with the sound ----
const TV = D.tv, TEND = D.tend, snd = document.getElementById('snd');
snd.preservesPitch = true;
let shownN = N, playing = false, simT = TEND, last = performance.now();
const head = new THREE.Mesh(new THREE.SphereGeometry(0.018, 16, 12), new THREE.MeshBasicMaterial({ color: 0xffffff }));
head.visible = false; plot.add(head);
const posEl = document.getElementById('pos'), playEl = document.getElementById('play'),
      speedEl = document.getElementById('speed'), clockEl = document.getElementById('clock');
posEl.max = N; posEl.value = N;
function upto(t) { let k = 0; while (k < N && TV[k] <= t) k++; return k; }
function setShown(n) {
  shownN = Math.max(0, Math.min(N, n));
  geo.setDrawRange(0, shownN);
  const j = Math.max(shownN - 1, 0);
  head.position.set(pos[3*j], toY(D.p[j]), pos[3*j+2]); head.visible = shownN > 0 && (shownN < N || playing);
  posEl.value = Math.max(shownN, 1);
  clockEl.innerHTML = `${simT.toFixed(2)} / ${TEND.toFixed(2)} s · wave ${shownN} / ${N}` +
    (shownN ? ` · <b style="color:${D.colors[D.t[j]]}">stretch ${D.t[j] + 1}</b>` : '');
}
function setPlaying(v) {
  playing = v; playEl.textContent = v ? '❚❚ Pause' : '▶ Play'; last = performance.now();
  snd.playbackRate = +speedEl.value;
  if (v) { snd.currentTime = Math.min(simT, TEND); snd.play().catch(() => {}); } else snd.pause();
}
playEl.onclick = () => {
  if (!playing && shownN >= N) { simT = 0; setShown(0); }          // finished: play again from the start
  setPlaying(!playing);
};
document.getElementById('restart').onclick = () => { simT = 0; setShown(0); setPlaying(true); };
speedEl.onchange = () => { snd.playbackRate = +speedEl.value; };
posEl.oninput = () => { setPlaying(false); simT = TV[+posEl.value - 1]; setShown(+posEl.value); };
function tick() {
  const now = performance.now(), dt = (now - last) / 1000; last = now;
  if (!playing) return;
  simT = (!snd.paused && !snd.ended) ? snd.currentTime : simT + dt * +speedEl.value;
  setShown(upto(simT));
  if (simT >= TEND) { simT = TEND; setShown(N); setPlaying(false); head.visible = false; }
}
setShown(N);
"""
    anchor = "recolor();\naddEventListener('resize'"
    assert anchor in s
    s = s.replace(anchor, js + anchor, 1)
    loop = "renderer.setAnimationLoop(() => { controls.update();"
    assert loop in s
    s = s.replace(loop, "renderer.setAnimationLoop(() => { tick(); controls.update();", 1)
    s = s.replace(" Cube VR</title>", " Cube Replay</title>", 1)
    out.write_text(s, encoding="utf-8")
    print(f"wrote vr/{out.name}  ({len(d)} waves, {t1 - t0:.2f} s with sound)")


if __name__ == "__main__":
    main()
