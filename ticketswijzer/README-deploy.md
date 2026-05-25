# TicketsWijzer — bouw- & deploy-handleiding

Statische vergelijkingssite voor ticketprijzen van attractieparken & dierentuinen.
Domein: **ticketswijzer.nl**. Alles wordt gegenereerd uit één databestand.

---

## Mappenstructuur

```
ticketswijzer/
├── data/attractions.json   ← DE bron: alle parken, prijzen, aanbieders
├── build.py                ← generator: leest de JSON, maakt de site
├── assets/
│   ├── style.css           ← styling (alle pagina's)
│   └── app.js              ← zoeken/filteren/sorteren op overzichtspagina's
├── site/                   ← GEGENEREERDE site (dit deploy je) — niet handmatig bewerken
└── README-deploy.md        ← dit bestand
```

> Bewerk nooit de bestanden in `site/` met de hand — die worden bij elke build overschreven. Pas `data/`, `assets/` of `build.py` aan.

---

## 1. Site (her)bouwen

Vereist Python 3 (geen extra packages nodig).

```bash
cd ticketswijzer
python3 build.py
```

Output: 17 pagina's (1 home + 4 categorieën + 12 detailpagina's) in `site/`.

## 2. Lokaal bekijken

```bash
cd site
python3 -m http.server 8000
# open http://localhost:8000 in je browser
```

## 3. Online zetten (hosting)

De site is volledig statisch, dus hosting is gratis of bijna gratis. Aanbevolen volgorde:

**Optie A — Cloudflare Pages of Netlify (aanbevolen, gratis):**
1. Maak een gratis account.
2. Sleep de map `site/` naar de "deploy" zone (of koppel een Git-repo en zet de output-map op `site`).
3. Je krijgt direct een live URL.
4. Koppel je domein: voeg `ticketswijzer.nl` toe als custom domain en volg de DNS-instructies (meestal een CNAME of de nameservers van Cloudflare overnemen).

**Optie B — hosting bij je domeinregistrar (TransIP/Versio):**
1. Open de webhosting/FTP van je `.nl`-pakket.
2. Upload de **inhoud** van `site/` naar de webroot (`public_html` / `www`).
3. Klaar — `ticketswijzer.nl` toont de site.

**DNS in het kort:** laat `ticketswijzer.nl` (en `www`) wijzen naar je host. Bij Cloudflare/Netlify krijg je exacte records; bij eigen hosting staat dit meestal al goed.

---

## 4. Een attractie toevoegen of wijzigen

1. Open `data/attractions.json`.
2. Voeg een object toe aan `"attractions"` (kopieer een bestaand blok):

```json
{
  "id": "phantasialand",
  "naam": "Phantasialand",
  "cat": "attractiepark",
  "plaats": "Brühl",
  "provincie": "Duitsland",
  "rating": 4.7,
  "kassa": 64.50,
  "omschrijving": "Topattractiepark net over de grens bij Keulen.",
  "offers": [
    { "v": "Kassa (park)", "p": 64.50, "t": "flexibel", "url": "#" },
    { "v": "Tiqets", "p": 57.00, "t": "datumticket", "url": "AFFILIATE_LINK_HIER" }
  ]
}
```

3. `id` = uniek, kleine letters, koppeltekens (wordt de URL: `attractie/<id>.html`).
4. `cat` = één van: `attractiepark`, `dierentuin`, `waterpark`, `indoor`.
5. Draai `python3 build.py`. De goedkoopste prijs en besparing worden automatisch berekend.

Een nieuwe **categorie** toevoegen? Voeg een blok toe aan `"categories"` (met `label`, `slug`, en twee kleuren `c1`/`c2`).

---

## 5. Affiliate-links koppelen (de verdienkant)

Nu staan alle `"url"`-velden op `"#"` (placeholder). Zo zet je ze live:

1. **Meld je aan bij Tiqets affiliate** — via Awin (±6%) of Travelpayouts (tot 8%). Tiqets is een Nederlands bedrijf met kant-en-klare links/widgets.
2. Meld je waar relevant ook aan bij andere partners (Tripper, Groupon, parken zelf).
3. Vervang per aanbieder de `"url": "#"` door jouw affiliate-link voor dat specifieke park.
4. Draai `python3 build.py`. De knoppen krijgen automatisch `rel="nofollow sponsored"` (correct voor affiliate, goed voor SEO).

---

## 6. Logische volgende stappen

1. Echte, geverifieerde prijzen invullen voor de eerste 20–30 NL-attracties (nu voorbeelddata).
2. Tiqets-affiliate regelen en links koppelen.
3. SEO-gidsen toevoegen ("Goedkoopste pretparken 2026", "Wanneer is de Efteling het goedkoopst") die naar de detailpagina's linken.
4. Automatische prijs-update-pipeline (kan als geplande taak draaien) zodat prijzen vers blijven.
5. Daarna uitbreiden: België → Duitsland (Europa-Park, Phantasialand) onder hetzelfde systeem.

---

*Voorbeelddata — prijzen ter illustratie, te verifiëren vóór lancering.*
