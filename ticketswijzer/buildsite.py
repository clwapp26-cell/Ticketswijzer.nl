#!/usr/bin/env python3
"""
TicketsWijzer static-site generator (runner copy of build.py).

Reads data/attractions.json and writes a deployable static site to site/:
  site/index.html                 homepage (search + category tiles + all attractions)
  site/categorie/<slug>.html      one page per category
  site/attractie/<id>.html        one detail page per attraction (price comparison)
  site/assets/                    copied css/js
  site/sitemap.xml + robots.txt   for search engines

Data workflow:  edit data/attractions.csv + data/offers.csv
                -> python3 ingest.py   (writes data/attractions.json)
                -> python3 build.py    (writes site/)
"""
import json, os, shutil, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "attractions.json")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "site")


def eur(n):
    return "€" + ("%.2f" % n).replace(".", ",")


def stars(r):
    full = int(round(r))
    return "★" * full + "☆" * (5 - full)


def esc(s):
    return html.escape(str(s), quote=True)


def derive(a):
    prices = [o["p"] for o in a["offers"]]
    a["cheapest"] = min(prices)
    a["savings"] = round(a["kassa"] - a["cheapest"], 2)
    a["save_pct"] = round(a["savings"] / a["kassa"] * 100) if a["kassa"] else 0
    return a


def grad(cat):
    return "linear-gradient(135deg,%s,%s)" % (cat["c1"], cat["c2"])


def head(title, desc, root, site):
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header><div class="wrap bar">
  <a class="logo" href="{root}index.html">
    <svg viewBox="0 0 24 24" fill="none"><path d="M3 9.5 12 4l9 5.5v9a1 1 0 0 1-1 1h-4v-6H8v6H4a1 1 0 0 1-1-1v-9Z" stroke="#0e8f7e" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="11" r="1.6" fill="#f4a52a"/></svg>
    Tickets<span class="dot">Wijzer</span></a>
  <nav class="nav-links">
    <a href="{root}categorie/attractieparken.html">Attractieparken</a>
    <a href="{root}categorie/dierentuinen.html">Dierentuinen</a>
    <a href="{root}categorie/waterparken.html">Waterparken</a>
    <a href="{root}categorie/indoor.html">Indoor</a>
  </nav>
</div></header>
"""


def foot(root, site):
    return f"""<footer><div class="wrap footer-flex">
  <div><strong>{esc(site['name'])}</strong> — vergelijk &amp; bespaar op dagjes uit in Nederland</div>
  <div>{esc(site['domain'])} · prijzen zijn richtprijzen, controleer altijd de actuele prijs bij de aanbieder</div>
</div></footer>
</body></html>"""


def card(a, cats, root):
    cat = cats[a["cat"]]
    save_badge = f'<span class="save">bespaar {eur(a["savings"])}</span>' if a["savings"] > 0 else ""
    strike = f'<span class="strike">{eur(a["kassa"])}</span>' if a["savings"] > 0 else ""
    return f"""<a class="card" href="{root}attractie/{esc(a['id'])}.html"
      data-cat="{esc(a['cat'])}" data-naam="{esc(a['naam'])}" data-plaats="{esc(a['plaats'])}"
      data-cheapest="{a['cheapest']}" data-savings="{a['savings']}" data-rating="{a['rating']}">
  <div class="thumb" style="background:{grad(cat)}">
    <span class="cat">{esc(cat['label'])}</span>{save_badge}
  </div>
  <div class="card-body">
    <h3>{esc(a['naam'])}</h3>
    <div class="loc">\U0001F4CD {esc(a['plaats'])}, {esc(a['provincie'])}</div>
    <div class="price-row"><span class="from">vanaf</span><span class="price">{eur(a['cheapest'])}</span>{strike}</div>
    <div class="meta">
      <span class="stars">{stars(a['rating'])} <span style="color:var(--ink-soft)">{a['rating']:.1f}</span></span>
      <span class="vendors-n">{len(a['offers'])} aanbieders</span>
    </div>
  </div>
</a>"""


def controls(cats, active="alle"):
    chips = f'<button class="chip{" active" if active=="alle" else ""}" data-cat="alle">Alles</button>'
    for key, c in cats.items():
        chips += f'<button class="chip{" active" if active==key else ""}" data-cat="{esc(key)}">{esc(c["label"])}</button>'
    return f"""<div class="controls">
  <div class="chips">{chips}</div>
  <div class="sort">Sorteer:
    <select id="sort">
      <option value="save">Hoogste besparing</option>
      <option value="price">Laagste prijs</option>
      <option value="rating">Best beoordeeld</option>
      <option value="name">Naam (A–Z)</option>
    </select>
  </div>
</div>"""


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)
    site, cats = data["site"], data["categories"]
    items = [derive(a) for a in data["attractions"]]

    # reset output
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree(ASSETS, os.path.join(OUT, "assets"))

    # ---- Homepage ----
    tiles = ""
    for key, c in cats.items():
        n = sum(1 for a in items if a["cat"] == key)
        tiles += f'<a class="cat-tile" style="background:{grad(c)}" href="categorie/{c["slug"]}.html">{esc(c["label"])}<small>{n} parken</small></a>'
    cards_html = "".join(card(a, cats, "") for a in items)
    home = head(f"{site['name']} — {site['tagline']}", site["intro"], "", site) + f"""
<section class="hero"><div class="wrap">
  <h1>{esc(site['tagline'])}</h1>
  <p>{esc(site['intro'])}</p>
  <div class="search"><input id="q" type="text" placeholder="Zoek een park of dierentuin…" autocomplete="off"><button type="button">Vergelijk</button></div>
  <div class="trust"><span>✓ Onafhankelijk &amp; gratis</span><span>✓ Officiële aanbieders</span><span>✓ Altijd actuele prijzen</span></div>
</div></section>
<main class="wrap">
  <h2 class="section-title">Categorieën</h2>
  <div class="cat-tiles">{tiles}</div>
  <h2 class="section-title">Alle attracties</h2>
  {controls(cats)}
  <div class="grid" id="grid">{cards_html}<div class="empty" id="empty" style="display:none">Geen resultaten gevonden.</div></div>
</main>
<script src="assets/app.js"></script>
""" + foot("", site)
    write(os.path.join(OUT, "index.html"), home)

    # ---- Category pages ----
    for key, c in cats.items():
        sub = [a for a in items if a["cat"] == key]
        cards_html = "".join(card(a, cats, "../") for a in sub) or ""
        page = head(f"{c['label']} vergelijken | {site['name']}",
                    f"Vergelijk ticketprijzen van {c['label'].lower()} in Nederland.", "../", site) + f"""
<section class="hero slim"><div class="wrap">
  <div class="crumb"><a href="../index.html">Home</a> › {esc(c['label'])}</div>
  <h1>{esc(c['label'])} vergelijken</h1>
  <div class="search"><input id="q" type="text" placeholder="Zoek binnen {esc(c['label'].lower())}…" autocomplete="off"><button type="button">Zoek</button></div>
</div></section>
<main class="wrap">
  {controls(cats, active=key)}
  <div class="grid" id="grid">{cards_html}<div class="empty" id="empty" style="display:none">Geen resultaten gevonden.</div></div>
</main>
<script src="../assets/app.js"></script>
""" + foot("../", site)
        write(os.path.join(OUT, "categorie", f"{c['slug']}.html"), page)

    # ---- Detail pages ----
    for a in items:
        cat = cats[a["cat"]]
        offers = sorted(a["offers"], key=lambda o: o["p"])
        best = offers[0]["p"]
        rows = ""
        for o in offers:
            is_best = o["p"] == best
            badge = '<span class="best-badge">goedkoopst</span>' if is_best else ""
            rows += f"""<tr class="{'best' if is_best else ''}">
  <td><span class="vendor-name">{esc(o['v'])}</span><span class="tag">{esc(o['t'])}</span>{badge}</td>
  <td class="vprice">{eur(o['p'])}</td>
  <td style="text-align:right"><a class="buy" href="{esc(o['url'])}" rel="nofollow sponsored" target="_blank">Naar ticket →</a></td>
</tr>"""
        verified_line = ""
        if a.get("verified"):
            src = f" · bron: {esc(a['bron'])}" if a.get("bron") else ""
            verified_line = f'<div class="verified">✓ Prijzen geverifieerd op {esc(a["verified"])}{src}</div>'
        page = head(f"{a['naam']} tickets vergelijken | {site['name']}",
                    f"Vergelijk ticketprijzen voor {a['naam']} in {a['plaats']}. Bespaar tot {eur(a['savings'])}.",
                    "../", site) + f"""
<section class="detail-hero" style="background:{grad(cat)}"><div class="wrap">
  <div class="crumb"><a href="../index.html">Home</a> › <a href="../categorie/{cat['slug']}.html">{esc(cat['label'])}</a> › {esc(a['naam'])}</div>
  <span class="cat">{esc(cat['label'])}</span>
  <h1>{esc(a['naam'])}</h1>
  <div class="sub">\U0001F4CD {esc(a['plaats'])}, {esc(a['provincie'])} · {stars(a['rating'])} {a['rating']:.1f}</div>
</div></section>
<main class="wrap detail-body">
  <p class="lead">{esc(a['omschrijving'])}</p>
  <div class="savings-box">Goedkoopste ticket: <strong>{eur(a['cheapest'])}</strong> — je bespaart tot <strong>{eur(a['savings'])} ({a['save_pct']}%)</strong> t.o.v. de kassaprijs van {eur(a['kassa'])}.</div>
  <h2 class="section-title">Prijsvergelijking</h2>
  <table class="cmp"><thead><tr><th>Aanbieder</th><th>Prijs (volw.)</th><th></th></tr></thead><tbody>{rows}</tbody></table>
  {verified_line}
  <div class="disclaimer">\U0001F4A1 Prijzen zijn richtprijzen en kunnen per bezoekdatum verschillen (veel parken hanteren dynamische prijzen). Controleer altijd de actuele prijs bij de aanbieder voordat je boekt.</div>
</main>
""" + foot("../", site)
        write(os.path.join(OUT, "attractie", f"{a['id']}.html"), page)

    # ---- sitemap.xml + robots.txt ----
    base = site.get("base_url", f"https://{site['domain']}").rstrip("/")
    urls = [f"{base}/"]
    urls += [f"{base}/categorie/{c['slug']}.html" for c in cats.values()]
    urls += [f"{base}/attractie/{a['id']}.html" for a in items]
    today = datetime.date.today().isoformat()
    body = "".join(
        f"  <url><loc>{esc(u)}</loc><lastmod>{today}</lastmod></url>\n" for u in urls
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}</urlset>\n"
    )
    write(os.path.join(OUT, "sitemap.xml"), sitemap)
    robots = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
    write(os.path.join(OUT, "robots.txt"), robots)

    pages = 1 + len(cats) + len(items)
    print(f"Built {pages} pages: 1 home + {len(cats)} categories + {len(items)} detail pages -> {OUT}")
    print(f"Wrote sitemap.xml ({len(urls)} urls) + robots.txt (base: {base})")


if __name__ == "__main__":
    build()
