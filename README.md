# État des lieux Offline — site vitrine

Site de présentation et de vente de l'application **État des lieux Offline**, avec un blog pour le référencement. Construit avec **Hugo**, sans framework CSS, sans police externe, **sans cookie ni traceur**.

## Développer

```bash
hugo server            # http://localhost:1313/etat-des-lieux-offline/
hugo --gc --minify     # build dans public/
```

Hugo **extended 0.121.1** (même version dans le workflow GitHub).

## Où modifier quoi

| Quoi | Fichier |
|---|---|
| Nom, e-mail de contact, lien de démo, vidéo YouTube, **liens de paiement** | `hugo.toml` (section `[params]`) |
| Points forts | `data/atouts.yaml` |
| Offres et prix | `data/tarifs.yaml` |
| Questions fréquentes | `data/faq.yaml` |
| Page d'accueil (sections) | `layouts/index.html` |
| Styles | `assets/css/main.css` |
| Articles de blog | `content/blog/*.md` |
| Pages légales | `content/mentions-legales.md`, `cgv.md`, `confidentialite.md` |

## Brancher le paiement (Lemon Squeezy)

1. Créer un compte sur https://www.lemonsqueezy.com, puis une boutique.
2. Créer 3 produits :
   - **Particulier** : 5 €, abonnement annuel ;
   - **Particulier à vie** : 50 €, paiement unique ;
   - **Pro** : 5 €, abonnement mensuel.
3. Dans chaque produit, régler l'URL de redirection après achat sur `https://etat-des-lieux.ananse.fr/merci/`.
4. Copier le lien « Checkout » de chaque produit dans `hugo.toml`, sous `[params.paiement]` (`particulierAn`, `particulierVie`, `pro`).
   Tant qu'un lien est vide, le bouton ouvre un e-mail de commande.
   Dès qu'un lien est renseigné, le paiement s'ouvre en fenêtre intégrée au site (script `lemon.js`).
5. Compléter les `[À COMPLÉTER]` de `content/mentions-legales.md`, `content/cgv.md` et `content/confidentialite.md`.

## Publier

Chaque push sur `main` construit et publie le site sur GitHub Pages (`.github/workflows/hugo.yml`).

## Administration (Decap CMS)

https://etat-des-lieux.ananse.fr/admin/ : guides (blog), atouts, tarifs, FAQ, tous les textes de l'accueil (`data/accueil.yaml`, extraits des gabarits), coordonnées (`data/infos.yaml` : e-mail, SIRET, téléphone…) et pages légales. Connexion GitHub via le service commun de www.ananse.fr. Chaque enregistrement republie le site.
