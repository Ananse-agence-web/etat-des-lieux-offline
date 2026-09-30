"""Filme l'application (serveur de dev local) au format téléphone, calé sur la durée de la voix.

Prérequis : l'app tourne sur http://localhost:5174/Etats-des-lieux-appartements/ (npx vite --port 5174 dans le dossier de l'app).
Produit : capture/capture.webm + capture/segments.json (début/fin de chaque scène dans la vidéo).
Toutes les données sont fictives.
"""
import json
import shutil
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from playwright.sync_api import sync_playwright

from scenes import MARGE, SCENES

ICI = Path(__file__).parent
URL = "http://localhost:5174/Etats-des-lieux-appartements/"
MOD = "/Etats-des-lieux-appartements/src/"
SORTIE = ICI / "capture"
PROFIL = SORTIE / "profil"
DUREES = json.loads((ICI / "voix" / "durees.json").read_text(encoding="utf-8"))
duree = lambda sid: DUREES[sid]["duree"] + MARGE

# Indicateur visuel des « taps »
TAP_JS = """
addEventListener('pointerdown', (e) => {
  const d = document.createElement('div');
  d.style.cssText = `position:fixed;left:${e.clientX-22}px;top:${e.clientY-22}px;width:44px;height:44px;border-radius:50%;
    background:rgba(255,255,255,.45);border:3px solid rgba(255,255,255,.9);pointer-events:none;z-index:99999;
    transition:transform .45s ease-out, opacity .45s ease-out;`;
  document.documentElement.appendChild(d);
  requestAnimationFrame(() => { d.style.transform = 'scale(1.6)'; d.style.opacity = '0'; });
  setTimeout(() => d.remove(), 500);
}, true);
"""


def photo_mur(chemin: Path):
    """Photo fictive : mur peint avec une fissure."""
    im = Image.new("RGB", (1600, 1200), (226, 214, 196))
    d = ImageDraw.Draw(im)
    for y in range(0, 1200, 6):  # léger grain de peinture
        d.line([(0, y), (1600, y)], fill=(222 + (y * 7) % 9, 210 + (y * 5) % 8, 192 + (y * 3) % 7))
    d.rectangle([0, 1010, 1600, 1200], fill=(245, 245, 240))  # plinthe
    d.line([(0, 1010), (1600, 1010)], fill=(200, 200, 195), width=6)
    pts = [(700, 180), (730, 300), (705, 420), (760, 540), (740, 650), (800, 780), (785, 900)]
    d.line(pts, fill=(95, 85, 75), width=7, joint="curve")
    d.line([(760, 540), (860, 600), (900, 700)], fill=(110, 100, 90), width=4, joint="curve")
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    im.save(chemin, quality=90)


def main():
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    photo = SORTIE / "photo-mur.jpg"
    photo_mur(photo)

    options = dict(
        channel="msedge", headless=True, viewport={"width": 390, "height": 844}, device_scale_factor=2,
        color_scheme="dark", locale="fr-FR", geolocation={"latitude": 48.8566, "longitude": 2.3522}, permissions=["geolocation"],
    )
    with sync_playwright() as p:
        # ---- 1. Préparation des données (non filmée) ----
        ctx = p.chromium.launch_persistent_context(str(PROFIL), **options)
        page = ctx.pages[0]
        page.goto(URL)
        page.wait_for_selector("h1")
        ids = page.evaluate(
            """async (m) => {
              const f = await import(m + 'model/factory.ts');
              const db = await import(m + 'storage/db.ts');
              const { MODELES_PIECES } = await import(m + 'data/modeles.ts');
              await db.enregistrerReglages({ bailleur: { nom: 'SCI Exemple', adresse: '' }, faitA: 'Paris', mentions: (await db.chargerReglages()).mentions });
              const lg = f.nouveauLogement('Studio centre-ville', '12 rue de l\\'Exemple, 75000 Paris', 'Studio de 25 m²');
              await db.enregistrerLogement(lg);
              const e = f.nouvelEdl(lg, await db.chargerReglages());
              e.date = '2026-09-01';
              for (const id of ['entree', 'cuisine', 'sejour', 'sdb']) e.pieces.push(f.pieceDepuisModele(MODELES_PIECES.find((x) => x.id === id)));
              e.locataire.nom = 'Camille Martin'; e.signatures.locataire.nom = 'Camille Martin';
              e.compteurs[0].index = '1284'; e.compteurs[1].index = '20417';
              await db.enregistrerEdl(e);
              return { entree: e.id, cuisine: e.pieces[1].id };
            }""",
            MOD,
        )
        ctx.close()

        # ---- 2. Tournage ----
        ctx = p.chromium.launch_persistent_context(
            str(PROFIL), record_video_dir=str(SORTIE), record_video_size={"width": 390, "height": 844}, **options
        )
        ctx.add_init_script(TAP_JS)
        page = ctx.pages[0]
        t0 = time.monotonic()
        segments = {}
        horloge = lambda: time.monotonic() - t0
        attendre = lambda s: page.wait_for_timeout(int(s * 1000))

        def scene(sid, actions):
            debut = horloge()
            actions()
            reste = duree(sid) - (horloge() - debut)
            if reste > 0:
                attendre(reste)
            segments[sid] = {"debut": debut, "fin": horloge()}
            print(f"{sid}: {debut:.1f} → {segments[sid]['fin']:.1f}")

        def aller(hash_):
            page.goto(URL + "#/" + hash_)
            page.wait_for_load_state("networkidle")
            attendre(0.6)

        def etat(i, code):
            carte = page.locator("article.element").nth(i)
            carte.scroll_into_view_if_needed()
            carte.locator(".etats button", has_text=code).first.click()

        aller(f"edl/{ids['entree']}")

        def s03():
            attendre(0.9)
            page.locator("a.tuile", has_text="Cuisine").click()
            attendre(1.3)
            for i, c in enumerate(["TB", "B", "B", "M"]):
                etat(i, c)
                attendre(0.9)
        scene("03_etats", s03)

        def s04():
            attendre(0.5)
            page.get_by_role("button", name="Tout le reste à « B »").click()
            attendre(1.6)
            carte = page.locator("article.element").nth(2)
            carte.scroll_into_view_if_needed()
            attendre(0.4)
            carte.locator("input[type=file][multiple]").set_input_files(str(photo))
            carte.locator(".miniature img").wait_for()
            attendre(1.2)
            carte.locator(".miniature").first.click()
            attendre(2.6)
            page.locator(".visionneuse .barre button", has_text="✕").click()
        scene("04_photos", s04)

        # Entrée complète + création de la sortie (hors champ)
        sortie = page.evaluate(
            """async ([m, id]) => {
              const f = await import(m + 'model/factory.ts');
              const db = await import(m + 'storage/db.ts');
              const e = await db.chargerEdl(id);
              for (const p of e.pieces) for (const el of p.elements) el.etat ??= 'B';
              for (const c of e.cles) c.etat ??= 'TB';
              await db.enregistrerEdl(e);
              const s = f.creerSortie(e);
              s.date = '2026-09-28';
              s.compteurs[0].index = '1391'; s.compteurs[1].index = '22980';
              await db.enregistrerEdl(s);
              return { id: s.id, cuisine: s.pieces[1].id };
            }""",
            [MOD, ids["entree"]],
        )
        aller(f"edl/{sortie['id']}/piece/{sortie['cuisine']}")

        def s05():
            attendre(1.2)
            for i in range(2):
                etat(i, "B")
                attendre(1.0)
            page.mouse.wheel(0, 120)
            attendre(1.0)
        scene("05_sortie", s05)

        def s06():
            attendre(0.4)
            etat(2, "KO")
            attendre(2.2)
            page.goto(URL + f"#/edl/{sortie['id']}/synthese")
            page.wait_for_selector("h2")
        scene("06_ecarts", s06)

        # Tout le reste de la sortie = état d'entrée, pour une synthèse réaliste
        page.evaluate(
            """async ([m, id]) => {
              const db = await import(m + 'storage/db.ts');
              const s = await db.chargerEdl(id);
              for (const p of s.pieces) for (const el of p.elements) el.etat ??= el.entree?.etat;
              for (const c of s.cles) c.etat ??= c.entree?.etat;
              await db.enregistrerEdl(s);
            }""",
            [MOD, sortie["id"]],
        )
        aller(f"edl/{sortie['id']}/signatures")

        def signer(n):
            page.get_by_role("button", name="✍️ Signer").first.click()
            toile = page.locator(".pad-signature canvas")
            b = toile.bounding_box()
            x, y, w, h = b["x"], b["y"], b["width"], b["height"]
            trace = [(0.12, 0.62), (0.22, 0.3), (0.3, 0.7), (0.4, 0.35), (0.48, 0.66), (0.58, 0.4), (0.66, 0.62), (0.8, 0.45), (0.9, 0.55)]
            if n:
                trace = [(a, 1 - c) for a, c in trace]
            page.mouse.move(x + w * trace[0][0], y + h * trace[0][1])
            page.mouse.down()
            for a, c in trace[1:]:
                page.mouse.move(x + w * a, y + h * c, steps=6)
            page.mouse.up()
            attendre(0.3)
            page.get_by_role("button", name="Valider").click()
            attendre(0.5)

        def s07():
            attendre(0.4)
            signer(0)
            page.mouse.wheel(0, 380)
            attendre(0.4)
            signer(1)
        scene("07_signature", s07)

        aller(f"edl/{sortie['id']}/rapport")

        def s08():
            attendre(0.8)
            for _ in range(24):
                page.mouse.wheel(0, 90)
                attendre(0.18)
        scene("08_rapport", s08)

        video = page.video
        ctx.close()
        chemin = Path(video.path())
        chemin.rename(SORTIE / "capture.webm")
        (SORTIE / "segments.json").write_text(json.dumps(segments, indent=2), encoding="utf-8")
        shutil.rmtree(PROFIL, ignore_errors=True)
        print("OK :", SORTIE / "capture.webm")


if __name__ == "__main__":
    main()
