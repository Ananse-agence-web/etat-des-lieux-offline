// Paiement Stripe Checkout (Cloudflare Pages Function).
// Le formulaire « Acheter » de la section Tarifs envoie l'identifiant de l'offre ; on crée une session Stripe Checkout
// et on redirige le visiteur vers la page de paiement hébergée par Stripe.
// Montants et durées : /offres.json, généré par Hugo à partir de data/tarifs.yaml (champ « stripe »).
// Clé : variable Cloudflare STRIPE_SECRET_KEY (type Secret). Clé de test (sk_test_…) en préprod, jamais dans le code.

const texte = (t, status) => new Response(t, { status, headers: { "content-type": "text/plain; charset=utf-8" } });

export async function onRequestPost({ request, env }) {
  const origine = new URL(request.url).origin;
  if (!env.STRIPE_SECRET_KEY) return texte("Le paiement en ligne n'est pas encore activé. Écrivez-nous pour commander.", 503);

  const id = (await request.formData()).get("offre");
  const offres = await (await env.ASSETS.fetch(new URL("/offres.json", origine))).json();
  const o = offres[id];
  if (!o) return texte("Offre inconnue.", 400);

  const p = new URLSearchParams({
    mode: o.recurrence ? "subscription" : "payment",
    "line_items[0][quantity]": "1",
    "line_items[0][price_data][currency]": "eur",
    "line_items[0][price_data][unit_amount]": String(o.montant),
    "line_items[0][price_data][product_data][name]": o.nom,
    success_url: `${origine}/merci/?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origine}/#tarifs`,
    locale: "fr",
    billing_address_collection: "required",
    "metadata[offre]": id,
  });
  if (o.recurrence) {
    p.set("line_items[0][price_data][recurring][interval]", o.recurrence);
    p.set("subscription_data[metadata][offre]", id);
  } else {
    p.set("invoice_creation[enabled]", "true");
    p.set("customer_creation", "always");
  }

  const r = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}`, "Content-Type": "application/x-www-form-urlencoded" },
    body: p,
  });
  const s = await r.json();
  if (!r.ok || !s.url) {
    // Détail visible dans les journaux Cloudflare (Functions > Real-time logs) ; code court affiché pour le diagnostic.
    const e = s.error || {};
    console.error("Stripe", r.status, e.type, e.code, e.param, e.message);
    return texte(`Le paiement n'a pas pu démarrer. Réessayez dans un instant, ou écrivez-nous.
(code : ${r.status} ${e.type || ""} ${e.code || ""} ${e.param || ""})`, 502);
  }
  return Response.redirect(s.url, 303);
}
