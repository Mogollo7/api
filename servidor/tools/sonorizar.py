#!/usr/bin/env python3
# [CLAUDE-CONSTRUCTOR] Banda sonora sintetizada (propia, sin licencias de terceros): base rítmica al pulso del video y un «whoosh» en cada corte. Se mezcla bajo, sin picos.
"""python servidor/tools/sonorizar.py video.mp4 [--bpm 120] [--cortes 2.5,5,8.1] [-o salida.mp4]
El motor la llama solo cuando el Markdown del video trae `musica: si` en la cabecera (usa los cortes reales de las escenas)."""
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 44100


def _env(n, a=0.005, r=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)


def kick(n=int(SR * .35)):
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, .002, .16)


def hat(rng, n=int(SR * .06)):
    x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))                 # pasa-altos simple
    return x * _env(n, .001, .018) * .35


def bass(freq, n):
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * freq * t)) * .3 + np.sin(2 * np.pi * freq * t) * .7
    return x * _env(n, .01, .25)


def pad(freqs, n):
    t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs) / len(freqs)
    att = np.minimum(1, t / .4)
    rel = np.minimum(1, (n / SR - t) / .4)
    return x * att * rel * .18


def whoosh(rng, n=int(SR * .55)):
    x = rng.standard_normal(n)
    k = np.linspace(.02, .6, n)                            # filtro que se abre: barrido de ruido
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc += k[i] * (x[i] - acc)
        y[i] = acc
    t = np.arange(n) / SR
    env = np.sin(np.pi * t / t[-1]) ** 2
    return y * env * .5


def banda(dur, bpm=120, cortes=(), seed=7):
    rng = np.random.default_rng(seed)
    n = int(dur * SR) + SR
    mus = np.zeros(n)
    fx = np.zeros(n)
    beat = 60 / bpm
    prog = [(55.0, (220, 277.18, 329.63)), (43.65, (174.61, 220, 261.63)), (65.41, (261.63, 329.63, 392)), (49.0, (196, 246.94, 293.66))]   # Am F C G
    side = np.ones(n)
    b = 0
    while b * beat < dur:
        i = int(b * beat * SR)
        k = kick()
        mus[i:i + len(k)] += k[:max(0, min(len(k), n - i))] * .9
        side[i:i + int(SR * .18)] = np.minimum(side[i:i + int(SR * .18)], np.linspace(.35, 1, len(side[i:i + int(SR * .18)])))
        j = int((b + .5) * beat * SR)
        h = hat(rng)
        if j + len(h) < n:
            mus[j:j + len(h)] += h
        if b % 4 == 0:
            root, chord = prog[(b // 4) % len(prog)]
            m = int(beat * 4 * SR)
            if i + m < n:
                mus[i:i + m] += pad(chord, m) * side[i:i + m]
        root = prog[(b // 4) % len(prog)][0]
        m = int(beat * .9 * SR)
        if i + m < n:
            mus[i:i + m] += bass(root * (2 if b % 2 else 1), m) * .35
        b += 1
    for c in cortes:
        w = whoosh(rng)
        i = max(0, int((c - .3) * SR))
        fx[i:i + len(w)] += w[:max(0, min(len(w), n - i))]
    # fade final y mezcla: efectos por debajo de la música, techo -1 dB
    t = np.arange(n) / SR
    fade = np.clip((dur - t) / 1.5, 0, 1) * np.clip(t / .3, 0, 1)
    mix = (mus * .55 + fx * .35) * fade
    mix = np.tanh(mix * 1.2) * .85
    return mix[:int(dur * SR)]


def escribir_wav(x, ruta):
    s = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(ruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(s.tobytes())


def sonorizar(video, bpm=120, cortes=(), salida=None):
    video = Path(video)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip())
    wav = video.with_suffix(".banda.wav")
    escribir_wav(banda(dur, bpm, cortes), wav)
    out = Path(salida) if salida else video.with_name(video.stem + "_con_audio.mp4")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(video), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)],
                       capture_output=True, text=True)
    wav.unlink(missing_ok=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    else:
        opt = lambda k, d: a[a.index(k) + 1] if k in a else d      # noqa: E731
        cortes = [float(x) for x in opt("--cortes", "").split(",") if x]
        print(sonorizar(a[0], float(opt("--bpm", 120)), cortes, opt("-o", None)))
