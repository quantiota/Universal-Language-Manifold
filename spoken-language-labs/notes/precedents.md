# Precedents for the wave-by-wave construction

**Status:** research note, 2026-11-10. Where the tools of Lab 1 come from, to be cited when Part IV introduces them. Bibliographic details are from memory: check each one against the publication before it goes into the book.

## The wave surface

- **W. B. Kleijn**, *Encoding speech using prototype waveforms*, IEEE Transactions on Speech and Audio Processing 1(4), 386–399, 1993.
- **W. B. Kleijn and J. Haagen**, *Waveform interpolation for coding and synthesis*, in W. B. Kleijn and K. K. Paliwal (eds.), *Speech Coding and Synthesis*, Elsevier, 1995, 175–207.
- **W. B. Kleijn and J. Haagen**, *A speech coder based on decomposition of characteristic waveforms*, Proc. ICASSP 1995.

Waveform interpolation extracts one voice cycle at a time, aligns it on a common phase axis and stacks the cycles into a two-dimensional *characteristic waveform surface*, with axes time and phase: essentially the surface w(n, φ) of Lab 1, found here independently. Kleijn splits it into a slowly evolving waveform (the voiced sound) and a rapidly evolving waveform (noise, voiceless sounds). That split is a known route for the voiceless gaps, which Lab 1 does not model yet.

## The pieces

| Lab 1 | Precedent |
|---|---|
| one step per voice cycle (pitch-synchronous analysis) | E. Moulines and F. Charpentier, *Pitch-synchronous waveform processing techniques for text-to-speech synthesis using diphones*, Speech Communication 9, 453–467, 1990 (PSOLA) |
| a wave described by its harmonics (16 phasors) | D. W. Griffin and J. S. Lim, *Multiband excitation vocoder*, IEEE Trans. Acoustics, Speech, and Signal Processing 36(8), 1223–1235, 1988; Y. Stylianou, harmonic plus noise model (2001) |
| the period found where the waveform repeats itself | J. C. R. Licklider, *A duplex theory of pitch perception*, Experientia 7, 128–134, 1951 (autocorrelation account of pitch) |
| a wave predicted from the previous one | the long-term (pitch) predictor of CELP speech codecs |

## What is not in these precedents

1. The voice cycle as the **time step of a learner**, with the real time between waves.
2. The **gaps kept as time**, where a real-time learner catches up.
3. The **change between successive phasor vectors** as the learner's input, carried over from the SKA-ECG work.

For the books: citing where a tool comes from is not a comparison of methods.

Related: [information-rate.md](information-rate.md), [meaning-as-geodesic.md](meaning-as-geodesic.md), Lab 1 (`../lab1-wave-surface`).
