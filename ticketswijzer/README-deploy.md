# TicketsWijzer — bouw- & deploy-handleiding

Statische vergelijkingssite voor ticketprijzen van attractieparken & dierentuinen.
Domein: **ticketswijzer.nl**. Alles wordt gegenereerd uit één databestand.

---

## Mappenstructuur

```
ticketswijzer/
├── data/attractions.csv    ← BEWERK HIER: één rij per park
├── data/offers.csv         ← BEWERK HIER: één rij per prijs (gekoppeld via id); url = affiliate-link
├── data/site.json          ← config: naam/domein/base_url + categorieën
├── data/hubs.json          ← index van de gids-/SEO-pagina's
├── data/hubs/*.html        ← de gids-artikelen (handgeschreven content)
├── data/attractions.json   ← GEGENEREERD door ingest.py — niet handmatig bewerken
├── ingest.py               ← CSV → attractions.json
├── build.py                ← startpunt: roept de generator aan (python3 build.py)
├── sitegen_core.py         ← de generator-engine (HTML + canonical + Open Graph + JSON-LD)
├── assets/
│   ├── style.css           ← styling (alle pagina's)
│   └── app.js              ← zoeken/filteren/sorteren op overzichtspagina's
├── site/                   ← GEGENEREERDE site (dit deploy je) — niet handmatig bewerken
└── README-deploy.md        ← dit bestand
```

> Bewerk de twee CSV's (openen prima in Excel/Google Sheets). Bewerk nooit `site/` of `attractions.json` met de hand — die worden bij elke build overschreven.

---

## 1. Site (her)bouwen

Vereist Python 3 (geen extra packages nodig).

```bash
cd ticketswijzer
python3 ingest.py   # CSV's → data/attractions.json
python3 build.py    # JSON → site/
```

Output: 17 pagina's (1 home + 4 categorieën + 12 detailpagina's) in `site/`, plus `sitemap.xml` en `robots.txt`.

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

1. Open `data/attractions.csv` en voeg een rij toe (kolommen: `id,naam,cat,plaats,provincie,rating,kassa,verified,bron,omschrijving`):

```
phantasialand,Phantasialand,attractiepark,Brühl,Duitsland,4.7,64.50,2026-05-26,phantasialand.de,"Topattractiepark net over de grens bij Keulen."
```

2. Open `data/offers.csv` en voeg één rij per prijs toe (kolommen: `id,v,p,t,url`), met dezelfde `id`:

```
phantasialand,Aan de poort,64.50,flexibel,https://www.phantasialand.de/nl/tickets
phantasialand,Tiqets,57.00,datumticket,AFFILIATE_LINK_HIER
```

3. `id` = uniek, kleine letters, koppeltekens (wordt de URL: `attractie/<id>.html`).
4. `cat` = één van: `attractiepark`, `dierentuin`, `waterpark`, `indoor`.
5. Draai `python3 ingest.py` en daarna `python3 build.py`. Goedkoopste prijs en besparing worden automatisch berekend. `verified` (datum) en `bron` verschijnen op de detailpagina.

Een nieuwe **categorie** toevoegen? Voeg een blok toe aan `"categories"` in `data/site.json` (met `label`, `slug`, en twee kleuren `c1`/`c2`).

---

## 4b. Een gids-/SEO-pagina toevoegen

De gidsen onder `site/gids/` trekken zoekverkeer op concrete vragen ("wanneer is de Efteling het goedkoopst") en linken door naar de detailpagina's.

1. Schrijf het artikel als los HTML-fragment (alleen de inhoud: `<p>`, `<h2>`, `<ul>`, en interne links als `<a href="../attractie/efteling.html">`). Sla het op in `data/hubs/<slug>.html`.
2. Voeg een blok toe aan `data/hubs.json`:

```json
{
  "slug": "walibi-goedkoopste-dag",
  "title": "Wanneer is Walibi het goedkoopst? | titel voor Google",
  "description": "Meta-omschrijving voor de zoekresultaten (±155 tekens).",
  "h1": "Wanneer is Walibi Holland het goedkoopst?",
  "lead": "Korte intro-alinea bovenaan de pagina.",
  "body_file": "walibi-goedkoopste-dag.html"
}
```

3. Draai `python3 build.py`. De pagina verschijnt op `gids/<slug>.html`, met automatisch een plek in het menu, op de homepage en in de sitemap. Mik op 500+ woorden echte, unieke inhoud per gids (dun gekopieerde content straft Google af).

---

## 5. Affiliate-links koppelen (de verdienkant)

De `url`-kolom in `offers.csv` wijst nu naar echte officiële ticket-/Tripper-pagina's (werkend, maar nog géén affiliate = nog geen commissie). Zo zet je ze om naar verdienende links:

1. **Meld je aan bij de affiliate-netwerken** — voor NL vooral **Daisycon** en **TradeTracker** (leisure/tickets), plus **Awin** / **Travelpayouts** (Tiqets ±6–8%, GetYourGuide). De productfeeds van die netwerken zijn later óók je live prijsbron.
2. Meld je waar relevant ook aan bij specifieke partners (Tripper, parken zelf).
3. Vervang per aanbieder de `url` in `offers.csv` door jouw affiliate-deeplink voor dat specifieke park.
4. Draai `python3 ingest.py` en `python3 build.py`. De knoppen krijgen automatisch `rel="nofollow sponsored"` (correct voor affiliate, goed voor SEO).

---

## 6. Logische volgende stappen

1. Dataset uitbreiden van 12 → 20–30 NL-attracties (rijen toevoegen aan de CSV's). Overweeg de twee zwakke entries (Monkey Town, Tikibad) te vervangen.
2. Affiliate regelen (Daisycon/TradeTracker/Awin/Travelpayouts) en de `url`-kolom omzetten naar deeplinks.
3. Meer SEO-gidsen toevoegen (zie 4b). Canonical, Open Graph en JSON-LD (Product/AggregateOffer, BreadcrumbList, ItemList, Article) zitten al automatisch op elke pagina via `sitegen_core.py`. Tip: controleer een pagina met Google's Rich Results Test na livegang.
4. Automatische prijs-update-pipeline op basis van de affiliate-productfeeds (kan als geplande taak draaien) zodat prijzen vers blijven — die feeds schrijven dezelfde twee CSV's.
5. Daarna uitbreiden: België → Duitsland (Europa-Park, Phantasialand) onder hetzelfde systeem.

---

*Prijzen zijn richtprijzen, geverifieerd 26 mei 2026. Parken hanteren dynamische prijzen — controleer de actuele prijs bij de aanbieder.*
