// Menu mobile
const bouton = document.querySelector('.menu-bouton');
const nav = document.getElementById('nav-principale');
if (bouton && nav) {
  bouton.addEventListener('click', () => {
    const ouvert = nav.classList.toggle('ouvert');
    bouton.setAttribute('aria-expanded', String(ouvert));
  });
  nav.addEventListener('click', (e) => {
    if (e.target.closest('a')) {
      nav.classList.remove('ouvert');
      bouton.setAttribute('aria-expanded', 'false');
    }
  });
}

// Mini-démo de l'application dans la maquette de téléphone
const RANG = { TB: 4, B: 3, M: 2, KO: 1, ABS: 0 };
const cartes = [...document.querySelectorAll('[data-element]')];
const barre = document.querySelector('[data-progression]');
const texte = document.querySelector('[data-progression-texte]');

function majProgression() {
  const faits = cartes.filter((c) => c.querySelector('.actif')).length;
  if (barre) barre.style.width = (faits / cartes.length) * 100 + '%';
  if (texte) texte.textContent = `${faits}/${cartes.length} éléments renseignés`;
}

function majCarte(carte) {
  const actif = carte.querySelector('.actif');
  const alerte = carte.querySelector('.app-alerte');
  const avant = carte.dataset.entree;
  const apres = actif?.textContent;
  // Dégradation = baisse vers M, KO ou ABS (TB -> B = usure normale)
  const degrade = apres && RANG[apres] < RANG[avant] && RANG[apres] <= RANG.M;
  carte.classList.toggle('rempli', !!apres && !degrade);
  carte.classList.toggle('degrade', !!degrade);
  if (alerte) {
    alerte.hidden = !degrade;
    alerte.textContent = degrade ? `⚠ Dégradation : ${avant} → ${apres}` : '';
  }
}

cartes.forEach((carte) => {
  majCarte(carte);
  carte.querySelectorAll('.app-etats button').forEach((b) => {
    b.addEventListener('click', () => {
      const deja = b.classList.contains('actif');
      carte.querySelectorAll('.app-etats button').forEach((x) => x.classList.remove('actif', 'e-TB', 'e-B', 'e-M', 'e-KO', 'e-ABS'));
      if (!deja) b.classList.add('actif', 'e-' + b.textContent);
      majCarte(carte);
      majProgression();
    });
  });
});
majProgression();

// Vidéo YouTube chargée uniquement au clic (aucun cookie avant)
document.querySelectorAll('[data-youtube]').forEach((b) => {
  b.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${encodeURIComponent(b.dataset.youtube)}?autoplay=1&rel=0`;
    f.title = 'Vidéo de démonstration';
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    b.replaceWith(f);
  });
});
