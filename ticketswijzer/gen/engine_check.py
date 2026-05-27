#!/usr/bin/env python3
"""Clean build engine (full). Builds the site from gen/ inputs into an output dir."""
import json, os, shutil, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))           # gen/
PROJ = os.path.dirname(ROOT)                                 # ticketswijzer/
DATA = os.path.join(ROOT, "data.json")
HUBS_JSON = os.path.join(ROOT, "hubs.json")
HUBS_DIR = os.path.join(PROJ, "data", "hubs")
PAGES_JSON = os.path.join(ROOT, "pages.json")
PAGES_DIR = os.path.join(ROOT, "pages")
ASSETS = os.path.join(PROJ, "assets")

EXTRA_CSS = """<style>
.verified{margin-top:14px;font-size:13px;color:#0e8f7e;font-weight:600}
.gids{max-width:760px}
.gids h2{font-size:20px;margin:28px 0 8px}
.gids p{line-height:1.7;margin:12px 0}
.gids ul{line-height:1.7;margin:12px 0 12px 22px}
.gids li{margin:6px 0}
.gids a{color:#0e8f7e}
.gids-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin:18px 0}
.gids-card{display:block;padding:18px;border:1px solid var(--line);border-radius:12px;background:#fff;text-decoration:none;color:inherit;transition:box-shadow .15s}
.gids-card:hover{box-shadow:0 6px 18px rgba(0,0,0,.08)}
.gids-card h3{margin:0 0 6px;font-size:16px}
.gids-card p{margin:0;font-size:13px;color:var(--ink-soft);line-height:1.5}
.related{margin-top:30px;padding-top:18px;border-top:1px solid var(--line);font-size:14px}
.foot-links{font-size:13px}
.foot-links a{color:var(--ink-soft);text-decoration:none}
.foot-links a:hover{text-decoration:underline}
#cookiebar{position:fixed;left:0;right:0;bottom:0;background:#0f172a;color:#fff;padding:12px 16px;display:flex;gap:14px;align-items:center;justify-content:center;flex-wrap:wrap;font-size:13px;z-index:9999}
#cookiebar a{color:#7dd3fc}
#cookiebar button{border:0;border-radius:6px;padding:7px 14px;font-size:13px;cursor:pointer;margin-left:6px}
#cb-ok{background:#0e8f7e;color:#fff}
#cb-no{background:#334155;color:#fff}
.cb-btns{white-space:nowrap}
</style>"""

COOKIE_BAR = """<div id="cookiebar" style="display:none">
  <span>Wij gebruiken cookies voor een goede werking van de site en voor affiliate-links. <a href="__ROOT__cookiebeleid.html">Meer info</a>.</span>
  <span class="cb-btns"><button type="button" id="cb-ok">Akkoord</button><button type="button" id="cb-no">Weigeren</button></span>
</div>
<script>
(function(){try{if(!localStorage.getItem('tw_cookie')){var b=document.getElementById('cookiebar');b.style.display='flex';var c=function(v){try{localStorage.setItem('tw_cookie',v)}catch(e){}b.style.display='none'};document.getElementById('cb-ok').onclick=function(){c('akkoord')};document.getElementById('cb-no').onclick=function(){c('geweigerd')};}}catch(e){}})();
</script>"""


def eur(n): return "€" + ("%.2f" % n).replace(".", ",")
def stars(r):
    full = int(round(r)); return "★" * full + "☆" * (5 - full)
def esc(s): return html.escape(str(s), quote=True)
def base_url(site): return site.get("base_url", f"https://{site['domain']}").rstrip("/")
def grad(cat): return "linear-gradient(135deg,%s,%s)" % (cat["c1"], cat["c2"])


def derive(a):
    prices = [o["p"] for o in a["offers"]]
    a["cheapest"] = min(prices)
    a["savings"] = round(a["kassa"] - a["cheapest"], 2)
    a["save_pct"] = round(a["savings"] / a["kassa"] * 100) if a["kassa"] else 0
    return a


def load_hubs():
    if not os.path.exists(HUBS_JSON): return []
    hubs = json.load(open(HUBS_JSON, encoding="utf-8"))
    for h in hubs:
        h["body"] = open(os.path.join(HUBS_DIR, h["body_file"]), encoding="utf-8").read()
    return hubs


def load_pages():
    if not os.path.exists(PAGES_JSON): return []
    pages = json.load(open(PAGES_JSON, encoding="utf-8"))
    for p in pages:
        p["body"] = open(os.path.join(PAGES_DIR, p["body_file"]), encoding="utf-8").read()
    return pages


def ld_script(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "</script>"


def breadcrumb_ld(crumbs):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}


def head(title, desc, root, site, path="", jsonld="", og_type="website"):
    base = base_url(site)
    canonical = base + "/" + path if path else base + "/"
    return f"""<!DOCTYPE html>
<html lang="nl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="63563a671fb0df5" content="0b8482ff6a6f147677542ed9695b90cf" />
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{esc(site['name'])}">
<meta property="og:locale" content="nl_NL">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canonical)}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{root}assets/style.css">
{EXTRA_CSS}
{jsonld}
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
    <a href="{root}categorie/musea.html">Musea</a>
    <a href="{root}gids/index.html">Gidsen</a>
  </nav>
</div></header>
"""


def foot(root, site):
    return f"""<footer><div class="wrap footer-flex">
  <div><strong>{esc(site['name'])}</strong> — vergelijk &amp; bespaar op dagjes uit in Nederland</div>
  <div class="foot-links"><a href="{root}over-ons.html">Over ons</a> · <a href="{root}contact.html">Contact</a> · <a href="{root}privacybeleid.html">Privacybeleid</a> · <a href="{root}cookiebeleid.html">Cookiebeleid</a></div>
  <div>{esc(site['domain'])} · richtprijzen, controleer bij de aanbieder · bevat affiliate-links</div>
</div></footer>
{COOKIE_BAR.replace("__ROOT__", root)}
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


def hub_card(h, root):
    return (f'<a class="gids-card" href="{root}gids/{esc(h["slug"])}.html">'
            f'<h3>{esc(h["h1"])}</h3><p>{esc(h["description"])}</p></a>')


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
    open(path, "w", encoding="utf-8").write(content)


def build(out):
    data = json.load(open(DATA, encoding="utf-8"))
    site, cats = data["site"], data["categories"]
    items = [derive(a) for a in data["attractions"]]
    hubs = load_hubs()
    base = base_url(site)
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(out)
    shutil.copytree(ASSETS, os.path.join(out, "assets"))

    tiles = ""
    for key, c in cats.items():
        n = sum(1 for a in items if a["cat"] == key)
        tiles += f'<a class="cat-tile" style="background:{grad(c)}" href="categorie/{c["slug"]}.html">{esc(c["label"])}<small>{n} parken</small></a>'
    guides_section = ""
    if hubs:
        guides_section = f'  <h2 class="section-title">Slim besparen — onze gidsen</h2>\n  <div class="gids-grid">{"".join(hub_card(h, "") for h in hubs)}</div>\n'
    cards_html = "".join(card(a, cats, "") for a in items)
    home_ld = ld_script({"@context": "https://schema.org", "@type": "WebSite", "name": site["name"], "url": base + "/"})
    home_ld += ld_script({"@context": "https://schema.org", "@type": "Organization", "name": site["name"], "url": base + "/"})
    home = head(f"{site['name']} — {site['tagline']}", site["intro"], "", site, path="", jsonld=home_ld) + f"""
<section class="hero"><div class="wrap">
  <h1>{esc(site['tagline'])}</h1>
  <p>{esc(site['intro'])}</p>
  <div class="search"><input id="q" type="text" placeholder="Zoek een park of dierentuin…" autocomplete="off"><button type="button">Vergelijk</button></div>
  <div class="trust"><span>✓ Onafhankelijk &amp; gratis</span><span>✓ Officiële aanbieders</span><span>✓ Altijd actuele prijzen</span></div>
</div></section>
<main class="wrap">
  <h2 class="section-title">Categorieën</h2>
  <div class="cat-tiles">{tiles}</div>
{guides_section}  <h2 class="section-title">Alle attracties</h2>
  {controls(cats)}
  <div class="grid" id="grid">{cards_html}<div class="empty" id="empty" style="display:none">Geen resultaten gevonden.</div></div>
</main>
<script src="assets/app.js"></script>
""" + foot("", site)
    write(os.path.join(out, "index.html"), home)

    for key, c in cats.items():
        sub = [a for a in items if a["cat"] == key]
        cards_html = "".join(card(a, cats, "../") for a in sub) or ""
        cat_path = f"categorie/{c['slug']}.html"
        bc = breadcrumb_ld([("Home", base + "/"), (c["label"], base + "/" + cat_path)])
        il = {"@context": "https://schema.org", "@type": "ItemList",
              "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": base + f"/attractie/{a['id']}.html", "name": a["naam"]} for i, a in enumerate(sub)]}
        page = head(f"{c['label']} vergelijken | {site['name']}", f"Vergelijk ticketprijzen van {c['label'].lower()} in Nederland.", "../", site,
                    path=cat_path, jsonld=ld_script(bc) + ld_script(il)) + f"""
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
        write(os.path.join(out, "categorie", f"{c['slug']}.html"), page)

    for a in items:
        cat = cats[a["cat"]]
        offers = sorted(a["offers"], key=lambda o: o["p"])
        best = offers[0]["p"]
        rows = ""
        for o in offers:
            badge = '<span class="best-badge">goedkoopst</span>' if o["p"] == best else ""
            rows += f"""<tr class="{'best' if o['p'] == best else ''}">
  <td><span class="vendor-name">{esc(o['v'])}</span><span class="tag">{esc(o['t'])}</span>{badge}</td>
  <td class="vprice">{eur(o['p'])}</td>
  <td style="text-align:right"><a class="buy" href="{esc(o['url'])}" rel="nofollow sponsored" target="_blank">Naar ticket →</a></td>
</tr>"""
        verified_line = ""
        if a.get("verified"):
            src = f" · bron: {esc(a['bron'])}" if a.get("bron") else ""
            verified_line = f'<div class="verified">✓ Prijzen geverifieerd op {esc(a["verified"])}{src}</div>'
        if a["savings"] > 0:
            savings_html = f'<div class="savings-box">Goedkoopste ticket: <strong>{eur(a["cheapest"])}</strong> — je bespaart tot <strong>{eur(a["savings"])} ({a["save_pct"]}%)</strong> t.o.v. de kassaprijs van {eur(a["kassa"])}.</div>'
        else:
            savings_html = f'<div class="savings-box">Prijs: <strong>{eur(a["cheapest"])}</strong> — bij alle aanbieders gelijk. Kies hieronder waar je het liefst boekt.</div>'
        det_path = f"attractie/{a['id']}.html"
        canonical = base + "/" + det_path
        prod_ld = {"@context": "https://schema.org", "@type": "Product", "name": f"{a['naam']} ticket",
                   "description": a["omschrijving"], "category": cat["label"], "url": canonical,
                   "offers": {"@type": "AggregateOffer", "priceCurrency": "EUR", "lowPrice": a["cheapest"], "highPrice": a["kassa"], "offerCount": len(offers), "availability": "https://schema.org/InStock"}}
        bc = breadcrumb_ld([("Home", base + "/"), (cat["label"], base + f"/categorie/{cat['slug']}.html"), (a["naam"], canonical)])
        page = head(f"{a['naam']} tickets vergelijken | {site['name']}", f"Vergelijk ticketprijzen voor {a['naam']} in {a['plaats']}. Bespaar tot {eur(a['savings'])}.",
                    "../", site, path=det_path, jsonld=ld_script(prod_ld) + ld_script(bc), og_type="product") + f"""
<section class="detail-hero" style="background:{grad(cat)}"><div class="wrap">
  <div class="crumb"><a href="../index.html">Home</a> › <a href="../categorie/{cat['slug']}.html">{esc(cat['label'])}</a> › {esc(a['naam'])}</div>
  <span class="cat">{esc(cat['label'])}</span>
  <h1>{esc(a['naam'])}</h1>
  <div class="sub">\U0001F4CD {esc(a['plaats'])}, {esc(a['provincie'])} · {stars(a['rating'])} {a['rating']:.1f}</div>
</div></section>
<main class="wrap detail-body">
  <p class="lead">{esc(a['omschrijving'])}</p>
  {savings_html}
  <h2 class="section-title">Prijsvergelijking</h2>
  <table class="cmp"><thead><tr><th>Aanbieder</th><th>Prijs (volw.)</th><th></th></tr></thead><tbody>{rows}</tbody></table>
  {verified_line}
  <div class="disclaimer">\U0001F4A1 Prijzen zijn richtprijzen en kunnen per bezoekdatum verschillen (veel parken hanteren dynamische prijzen). Controleer altijd de actuele prijs bij de aanbieder voordat je boekt.</div>
</main>
""" + foot("../", site)
        write(os.path.join(out, "attractie", f"{a['id']}.html"), page)

    today = datetime.date.today().isoformat()
    for h in hubs:
        hub_path = f"gids/{h['slug']}.html"
        canonical = base + "/" + hub_path
        art = {"@context": "https://schema.org", "@type": "Article", "headline": h["h1"], "description": h["description"],
               "datePublished": today, "dateModified": today,
               "author": {"@type": "Organization", "name": site["name"]}, "publisher": {"@type": "Organization", "name": site["name"]},
               "mainEntityOfPage": canonical}
        bc = breadcrumb_ld([("Home", base + "/"), ("Gidsen", base + "/gids/index.html"), (h["h1"], canonical)])
        related = '<div class="related">Vergelijk verder: <a href="../index.html">alle attracties</a> · <a href="../gids/index.html">meer gidsen</a></div>'
        page = head(h["title"], h["description"], "../", site, path=hub_path, jsonld=ld_script(art) + ld_script(bc), og_type="article") + f"""
<section class="hero slim"><div class="wrap">
  <div class="crumb"><a href="../index.html">Home</a> › <a href="../gids/index.html">Gidsen</a> › {esc(h['h1'])}</div>
  <h1>{esc(h['h1'])}</h1>
</div></section>
<main class="wrap detail-body">
  <article class="gids