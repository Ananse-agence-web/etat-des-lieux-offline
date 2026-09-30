# Vidéo de démonstration

Génère `sortie/demo.mp4` (1920×1080, environ 80 s), entièrement en local, avec des **données fictives**.

```bash
pip install playwright imageio-ffmpeg pillow
# 1. dans le dossier de l'app : npx vite --port 5174
python 1_voix.py      # voix off (synthèse vocale Windows, voix française)
python 2_capture.py   # filme l'app au format téléphone (Edge piloté par Playwright)
python 3_montage.py   # montage : cartes + téléphone + voix -> sortie/demo.mp4
```

- **Texte et scénario** : `scenes.py`, qui est la source unique.
- **Mettre votre propre voix** : enregistrez `voix/<id>.perso.wav` (par exemple `voix/03_etats.perso.wav`), puis relancez les 3 scripts. Les durées se recalent automatiquement.
