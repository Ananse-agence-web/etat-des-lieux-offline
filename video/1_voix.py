"""Génère la voix off : voix/<id>.wav + voix/durees.json

Moteurs :
  - "edge"    (par défaut) : voix neuronale Microsoft fr-FR-DeniseNeural via edge-tts (naturelle ; envoie le texte du script au service de lecture d'Edge).
  - "windows" : synthèse vocale Windows, 100 % hors-ligne (plus robotique).
Usage : python 1_voix.py [edge|windows]
Une voix enregistrée à la main (voix/<id>.perso.wav) est toujours prioritaire.
"""
import asyncio
import json
import subprocess
import sys
import wave
from pathlib import Path

import imageio_ffmpeg

from scenes import SCENES

ICI = Path(__file__).parent
VOIX = ICI / "voix"
VOIX.mkdir(exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
MOTEUR = sys.argv[1] if len(sys.argv) > 1 else "edge"
VOIX_EDGE = "fr-FR-DeniseNeural"

PS = r"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -eq 'fr-FR' } | Select-Object -First 1
$s.SelectVoice($v.VoiceInfo.Name)
$s.Rate = 1
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(44100, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$s.SetOutputToWaveFile($args[0], $fmt)
$s.Speak([IO.File]::ReadAllText($args[1], [Text.Encoding]::UTF8))
$s.Dispose()
"""


def voix_windows(texte: str, wav: Path):
    script = VOIX / "_tts.ps1"
    script.write_text(PS, encoding="utf-8-sig")
    txt = VOIX / f"{wav.stem}.txt"
    txt.write_text(texte, encoding="utf-8")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), str(wav), str(txt)], check=True)


def voix_edge(texte: str, wav: Path):
    import edge_tts

    mp3 = wav.with_suffix(".mp3")
    asyncio.run(edge_tts.Communicate(texte, VOIX_EDGE, rate="+4%").save(str(mp3)))
    # Conversion en WAV 44,1 kHz mono + coupe du silence final
    subprocess.run([FF, "-loglevel", "error", "-y", "-i", str(mp3), "-af", "areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                    "-ar", "44100", "-ac", "1", str(wav)], check=True)
    mp3.unlink()


durees = {}
for sc in SCENES:
    wav = VOIX / f"{sc['id']}.wav"
    manuel = VOIX / f"{sc['id']}.perso.wav"
    if manuel.exists():
        wav = manuel
    elif MOTEUR == "windows":
        voix_windows(sc["voix"], wav)
    else:
        voix_edge(sc["voix"], wav)
    with wave.open(str(wav)) as w:
        durees[sc["id"]] = {"fichier": wav.name, "duree": w.getnframes() / w.getframerate()}
    print(f"{sc['id']}: {durees[sc['id']]['duree']:.1f} s")

(VOIX / "durees.json").write_text(json.dumps(durees, indent=2), encoding="utf-8")
print("Moteur :", MOTEUR, "| total voix :", round(sum(d["duree"] for d in durees.values()), 1), "s")
