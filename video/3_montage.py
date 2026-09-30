"""Montage final : cartes + séquences filmées dans un cadre de téléphone + voix off -> sortie/demo.mp4 (1920x1080)."""
import json
import subprocess
import textwrap
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from scenes import MARGE, SCENES

ICI = Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30
TMP = ICI / "sortie" / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
DUREES = json.loads((ICI / "voix" / "durees.json").read_text(encoding="utf-8"))
SEGMENTS = json.loads((ICI / "capture" / "segments.json").read_text(encoding="utf-8"))
LOGO = ICI.parent / "static" / "images" / "icon-512.png"

F = "C:/Windows/Fonts/"
def police(nom, taille):
    return ImageFont.truetype(F + nom, taille)
GRAS, SEMI, NORMAL = "segoeuib.ttf", "seguisb.ttf", "segoeui.ttf"

BLEU, VERT, ROUGE = (29, 111, 184), (31, 157, 85), (217, 67, 47)

# Téléphone : écran 390x844 mis à l'échelle
ECH = 1.07
EW, EH = int(390 * ECH), int(844 * ECH)
BORD = 14
EX, EY = 400, (H - EH) // 2


def fond():
    """Dégradé bleu nuit + halos."""
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(9 + 6 * t), int(22 + 40 * t), int(40 + 70 * t)))
    halo = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo).ellipse([1100, -300, 2300, 700], fill=90)
    halo = halo.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(Image.new("RGB", (W, H), (40, 130, 210)), im, halo)
    halo2 = Image.new("L", (W, H), 0)
    ImageDraw.Draw(halo2).ellipse([-400, 600, 700, 1500], fill=60)
    halo2 = halo2.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB", (W, H), (31, 157, 85)), im, halo2)


def marque(im, x=70, y=56, taille=44):
    logo = Image.open(LOGO).convert("RGBA").resize((taille, taille))
    im.paste(logo, (x, y), logo)
    d = ImageDraw.Draw(im)
    f1, f2 = police(NORMAL, int(taille * 0.62)), police(GRAS, int(taille * 0.62))
    d.text((x + taille + 14, y + taille / 2), "État des lieux ", font=f1, fill="white", anchor="lm")
    w = d.textlength("État des lieux ", font=f1)
    d.text((x + taille + 14 + w, y + taille / 2), "Offline", font=f2, fill=(95, 168, 236), anchor="lm")


def texte_multi(d, xy, txt, f, fill, interligne=1.2, anchor="la"):
    x, y = xy
    for ligne in txt.split("\n"):
        d.text((x, y), ligne, font=f, fill=fill, anchor=anchor)
        y += int(f.size * interligne)
    return y


def fond_app(sc):
    """Fond d'une scène filmée : textes à droite + ombre du téléphone."""
    im = fond()
    ombre = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ombre).rounded_rectangle([EX - BORD + 20, EY - BORD + 40, EX + EW + BORD + 20, EY + EH + BORD + 40], 60, fill=150)
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, ombre.filter(ImageFilter.GaussianBlur(40)))
    marque(im)
    d = ImageDraw.Draw(im)
    x = 1010
    y = texte_multi(d, (x, 300), sc["titre"], police(GRAS, 84), "white", 1.12)
    d.rounded_rectangle([x, y + 24, x + 110, y + 32], 4, fill=VERT)
    y = texte_multi(d, (x, y + 70), sc["sous"], police(SEMI, 42), (159, 208, 255), 1.3)
    voix = "\n".join(textwrap.wrap("« " + sc["voix"] + " »", 52))
    texte_multi(d, (x, max(y + 60, 800)), voix, police(NORMAL, 27), (170, 190, 210), 1.35)
    return im


def cadre_telephone():
    """Calque RGBA : corps du téléphone avec l'écran transparent."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([EX - BORD, EY - BORD, EX + EW + BORD, EY + EH + BORD], 58, fill=(17, 24, 39, 255), outline=(60, 72, 92, 255), width=2)
    d.rounded_rectangle([EX, EY, EX + EW, EY + EH], 44, fill=(0, 0, 0, 0))
    return im


def icone_tel(d, cx, cy, h, coul):
    w = h * 0.55
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], h * 0.12, outline=coul, width=max(4, int(h / 18)))
    d.line([cx - w * 0.15, cy + h * 0.36, cx + w * 0.15, cy + h * 0.36], fill=coul, width=max(4, int(h / 18)))


def carte(sc):
    im = fond()
    d = ImageDraw.Draw(im)
    cx = W // 2
    if sc["id"] in ("01_intro", "10_outro"):
        logo = Image.open(LOGO).convert("RGBA").resize((190, 190))
        im.paste(logo, (cx - 95, 190), logo)
        f1, f2 = police(NORMAL, 96), police(GRAS, 96)
        w1, w2 = d.textlength("État des lieux ", font=f1), d.textlength("Offline", font=f2)
        x = cx - (w1 + w2) / 2
        d.text((x, 470), "État des lieux ", font=f1, fill="white")
        d.text((x + w1, 470), "Offline", font=f2, fill=(95, 168, 236))
        texte_multi(d, (cx, 640), sc["sous"], police(SEMI, 50), (190, 222, 250), 1.35, anchor="ma")
        if sc["id"] == "10_outro":
            d.rounded_rectangle([cx - 330, 850, cx + 330, 940], 45, fill=BLEU)
            d.text((cx, 895), "Installez-la sur votre téléphone", font=police(GRAS, 38), fill="white", anchor="mm")
        return im
    marque(im)
    texte_multi(d, (cx, 150), sc["titre"], police(GRAS, 78), "white", 1.12, anchor="ma")
    if sc["id"] == "02_donnees":
        y = 560
        d.rounded_rectangle([cx - 520, y - 150, cx - 200, y + 150], 30, fill=(20, 40, 60), outline=VERT, width=5)
        icone_tel(d, cx - 360, y - 30, 130, VERT)
        d.text((cx - 360, y + 85), "Votre téléphone", font=police(GRAS, 34), fill="white", anchor="mm")
        d.rounded_rectangle([cx + 200, y - 150, cx + 520, y + 150], 30, fill=(20, 30, 45), outline=(90, 105, 125), width=4)
        for i in range(3):
            d.rounded_rectangle([cx + 290, y - 95 + i * 45, cx + 430, y - 60 + i * 45], 6, outline=(120, 135, 155), width=4)
        d.text((cx + 360, y + 85), "Serveur / cloud", font=police(GRAS, 34), fill=(150, 165, 185), anchor="mm")
        for x in range(cx - 190, cx + 190, 26):
            d.line([x, y, x + 14, y], fill=(90, 105, 125), width=5)
        d.ellipse([cx - 55, y - 55, cx + 55, y + 55], fill=ROUGE)
        d.line([cx - 24, y - 24, cx + 24, y + 24], fill="white", width=10)
        d.line([cx - 24, y + 24, cx + 24, y - 24], fill="white", width=10)
        texte_multi(d, (cx, 780), sc["sous"], police(SEMI, 44), (190, 222, 250), 1.35, anchor="ma")
    elif sc["id"] == "09_envoi":
        for i, (qui, x0) in enumerate([("Le bailleur", cx - 620), ("Le locataire", cx + 40)]):
            d.rounded_rectangle([x0, 330, x0 + 580, 620], 22, fill=(245, 248, 252))
            d.rectangle([x0, 330 + 22, x0 + 580, 400], fill=(228, 236, 246))
            d.rounded_rectangle([x0, 330, x0 + 580, 400], 22, fill=(228, 236, 246))
            d.text((x0 + 28, 365), "Re : État des lieux de sortie", font=police(GRAS, 30), fill=(20, 32, 46), anchor="lm")
            d.text((x0 + 28, 440), qui, font=police(SEMI, 26), fill=(82, 96, 109))
            d.text((x0 + 28, 490), "Bien reçu, OK, je confirme", font=police(NORMAL, 36), fill=(20, 32, 46))
            d.text((x0 + 28, 540), "l'état des lieux.", font=police(NORMAL, 36), fill=(20, 32, 46))
            d.ellipse([x0 + 500, 530, x0 + 556, 586], fill=VERT)
            d.line([x0 + 514, 558, x0 + 526, 570, x0 + 544, 546], fill="white", width=7)
        texte_multi(d, (cx, 720), sc["sous"], police(SEMI, 46), (190, 222, 250), 1.4, anchor="ma")
    return im


def encoder(args, sortie):
    subprocess.run([FF, "-loglevel", "error", "-y", *args, "-r", str(FPS), "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", str(sortie)], check=True)


def main():
    cadre = TMP / "cadre.png"
    cadre_telephone().save(cadre)
    capture = ICI / "capture" / "capture.webm"
    parties = []
    for sc in SCENES:
        sid = sc["id"]
        wav = ICI / "voix" / DUREES[sid]["fichier"]
        out = TMP / f"{sid}.mp4"
        if sc["type"] == "carte":
            d = DUREES[sid]["duree"] + MARGE + 0.5
            img = TMP / f"{sid}.png"
            carte(sc).save(img)
            n = int(d * FPS)
            vf = (f"scale=2304:1296,zoompan=z='min(zoom+0.0006,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
                  f"fade=t=in:st=0:d=0.4,fade=t=out:st={d - 0.4:.2f}:d=0.4")
            encoder(["-loop", "1", "-i", str(img), "-i", str(wav), "-filter_complex",
                     f"[0:v]{vf}[v];[1:a]adelay=250|250,apad[a]", "-map", "[v]", "-map", "[a]", "-t", f"{d:.2f}"], out)
        else:
            seg = SEGMENTS[sid]
            d = seg["fin"] - seg["debut"]
            img = TMP / f"{sid}.png"
            fond_app(sc).save(img)
            fc = (f"[1:v]trim=start={seg['debut']:.3f}:end={seg['fin']:.3f},setpts=PTS-STARTPTS,fps={FPS},scale={EW}:{EH}:flags=lanczos[app];"
                  f"[0:v][app]overlay={EX}:{EY}[a1];[a1][2:v]overlay=0:0,fade=t=in:st=0:d=0.3,fade=t=out:st={d - 0.3:.2f}:d=0.3[v];"
                  f"[3:a]adelay=150|150,apad[a]")
            encoder(["-loop", "1", "-i", str(img), "-i", str(capture), "-loop", "1", "-i", str(cadre), "-i", str(wav),
                     "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{d:.2f}"], out)
        parties.append(out)
        print("ok", sid, f"{d:.1f}s")

    liste = TMP / "liste.txt"
    liste.write_text("".join(f"file '{p.as_posix()}'\n" for p in parties), encoding="utf-8")
    final = ICI / "sortie" / "demo.mp4"
    subprocess.run([FF, "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(liste), "-c", "copy",
                    "-movflags", "+faststart", str(final)], check=True)
    print("Vidéo :", final, f"({final.stat().st_size / 1e6:.1f} Mo)")


if __name__ == "__main__":
    main()
