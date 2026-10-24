#!/usr/bin/env python3
"""Habillage sonore original (100 % synthétisé, libre de droits) pour un Reel Avialog.
Usage : sound_reel.py sortie.wav durée_s "t_plan1,t_plan2,..." "t_clic1,..." t_logo"""
import sys, numpy as np, wave

SR = 44100
out, dur = sys.argv[1], float(sys.argv[2])
cuts = [float(x) for x in sys.argv[3].split(",") if x]
ticks = [float(x) for x in sys.argv[4].split(",") if x]
logo = float(sys.argv[5])
n = int(SR * dur); t = np.arange(n) / SR
mix = np.zeros(n)
rng = np.random.default_rng(7)

def add(sig, at, gain=1.0):
    i = int(at * SR); j = min(n, i + len(sig))
    if i < n: mix[i:j] += gain * sig[: j - i]

# Nappe grave (la mineur), qui monte doucement
pad = sum(np.sin(2 * np.pi * f * t + p) for f, p in [(55, 0), (110, .3), (164.8, .7), (220, 1.1)])
pad *= 0.06 * np.clip(t / 2, 0, 1) * (1 + 0.3 * np.sin(2 * np.pi * 0.25 * t))
mix += pad

# Pulsation type kick à 100 bpm
bpm_dt = 60 / 100
kt = np.arange(int(0.25 * SR)) / SR
kick = np.sin(2 * np.pi * (45 + 80 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 14)
hat_t = np.arange(int(0.05 * SR)) / SR
hat = rng.standard_normal(len(hat_t)) * np.exp(-hat_t * 90)
hat = np.diff(hat, prepend=0)  # filtre passe-haut simple
b = 0.0
while b < dur - 0.3:
    if b >= 2.6 and b < logo:  # la pulsation démarre après l'accroche
        add(kick, b, 0.55)
        add(hat, b + bpm_dt / 2, 0.12)
    b += bpm_dt

# Souffle (whoosh) à chaque changement de plan
wl = int(0.45 * SR); wt = np.arange(wl) / SR
noise = rng.standard_normal(wl)
env = np.sin(np.pi * wt / wt[-1]) ** 2
whoosh = np.convolve(noise, np.ones(30) / 30, mode="same") * env
for c in cuts:
    add(whoosh, max(0, c - 0.2), 0.35)

# Clic net à chaque case cochée
cl = np.arange(int(0.12 * SR)) / SR
click = (np.sin(2 * np.pi * 1760 * cl) + 0.5 * np.sin(2 * np.pi * 2640 * cl)) * np.exp(-cl * 45)
for k in ticks:
    add(click, k, 0.35)

# Impact + accord final sur le logo
it = np.arange(int(2.5 * SR)) / SR
impact = np.sin(2 * np.pi * (40 + 60 * np.exp(-it * 12)) * it) * np.exp(-it * 3)
chord = sum(np.sin(2 * np.pi * f * it) for f in (220, 277.2, 329.6, 440)) * np.exp(-it * 1.2) * 0.12
add(impact * 0.8 + chord, logo)

# Fondu de fin, normalisation
fade = int(0.6 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.85
stereo = np.stack([mix, mix], axis=1)
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype(np.int16).tobytes())
print(out)
