"""Synthèse Kokoro isolée (environnement Python séparé : kokoro-onnx embarque son propre phonémiseur).
Usage : python kokoro_synth.py modele.onnx voix.bin voix_kokoro vitesse sortie.wav < texte"""
import sys, soundfile as sf
from kokoro_onnx import Kokoro
m, vb, voix, vit, out = sys.argv[1:6]
a, sr = Kokoro(m, vb).create(sys.stdin.read(), voice=voix, speed=float(vit), lang="es")
sf.write(out, a, sr)
