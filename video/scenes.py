"""Scénario de la vidéo de démonstration (source unique pour la voix, la capture et le montage).

type = "carte" : image fixe générée ; type = "app" : séquence filmée dans l'application.
Pour remplacer la voix de synthèse par la vôtre : déposez voix/<id>.wav (même nom) et relancez 3_montage.py.
"""

SCENES = [
    {
        "id": "01_intro", "type": "carte",
        "titre": "État des lieux Offline",
        "sous": "L'état des lieux dans votre poche,\nmême sans réseau.",
        "voix": "Voici État des lieux Offline : l'état des lieux sur votre téléphone, même sans réseau.",
    },
    {
        "id": "02_donnees", "type": "carte",
        "titre": "Rien n'est envoyé\nsur Internet",
        "sous": "Logements, locataires, photos, signatures :\ntout reste dans votre téléphone.",
        "voix": "Ici, aucune donnée n'est envoyée sur un serveur. Logements, locataires, photos et signatures restent uniquement dans votre téléphone.",
    },
    {
        "id": "03_etats", "type": "app",
        "titre": "Un geste\npar élément",
        "sous": "Très bon, Bon, Moyen,\nMauvais, Absent.",
        "voix": "Ouvrez une pièce. Pour chaque élément, un seul geste suffit : très bon, bon, moyen, mauvais ou absent.",
    },
    {
        "id": "04_photos", "type": "app",
        "titre": "Tout à « Bon »\nen un tap",
        "sous": "Photos avec la date\net l'heure incrustées.",
        "voix": "Tout est en bon état ? Un tap, et la pièce est remplie. Ajoutez une photo : la date et l'heure sont incrustées automatiquement.",
    },
    {
        "id": "05_sortie", "type": "app",
        "titre": "La sortie reprend\nl'entrée",
        "sous": "L'état d'entrée s'affiche\nà côté de chaque élément.",
        "voix": "Au départ du locataire, l'état des lieux de sortie reprend l'entrée. L'état d'origine s'affiche à côté de chaque élément.",
    },
    {
        "id": "06_ecarts", "type": "app",
        "titre": "Dégradations\ndétectées",
        "sous": "Et résumées dans une\nsynthèse claire.",
        "voix": "Une dégradation ? Elle est détectée tout de suite, puis résumée dans une synthèse claire.",
    },
    {
        "id": "07_signature", "type": "app",
        "titre": "Signature\nau doigt",
        "sous": "Heure et position GPS\nenregistrées.",
        "voix": "Bailleur et locataire signent au doigt. L'heure et la position sont enregistrées.",
    },
    {
        "id": "08_rapport", "type": "app",
        "titre": "Rapport PDF\nprêt à envoyer",
        "sous": "Photos, compteurs, clés,\nsynthèse et signatures.",
        "voix": "Le rapport PDF est prêt : photos, compteurs, clés, synthèse et signatures.",
    },
    {
        "id": "09_envoi", "type": "carte",
        "titre": "Envoyé aux deux parties",
        "sous": "Chacun répond « Bien reçu, OK ».\n10 jours pour demander un complément.",
        "voix": "Envoyez-le aux deux parties, directement depuis le téléphone : chacun répond, bien reçu, OK. Le locataire a ensuite dix jours pour demander un complément.",
    },
    {
        "id": "10_outro", "type": "carte",
        "titre": "État des lieux Offline",
        "sous": "50 € une fois, ou 5 € par an.\nSans compte. Sans cloud. Même sans réseau.",
        "voix": "État des lieux Offline. Cinquante euros une fois pour toutes, ou cinq euros l'année. Sans compte, sans cloud, et même sans réseau.",
    },
]

# Marge de silence après chaque phrase (secondes)
MARGE = 0.6
