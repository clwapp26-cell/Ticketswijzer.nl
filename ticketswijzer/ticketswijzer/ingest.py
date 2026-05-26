#!/usr/bin/env python3
"""
TicketsWijzer data ingest.

Combines the editable source files into data/attractions.json (which build.py reads):

  data/site.json          site info + categories (config)
  data/attractions.csv    one row per attraction
  data/offers.csv         one row per price offer (linked by 'id')
        |
        v
  data/attractions.json   generated -- do NOT edit by hand

Workflow:  edit the CSV's  ->  python3 ingest.py  ->  python3 build.py

This keeps the data maintainable in Excel/Google Sheets today, and gives us a
single drop-in point later: an affiliate-feed importer just needs to write the
same two CSV's (or attractions.json directly) and the rest of the pipeline is
unchanged.
"""
import csv, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(DATA, "site.json")
ATTR_CSV = os.path.join(DATA, "attractions.csv")
OFFERS_CSV = os.path.join(DATA, "offers.csv")
OUT = os.path.join(DATA, "attractions.json")


def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def num(v, field, ctx):
    try:
        return float(str(v).replace(",", ".").strip())
    except (ValueError, AttributeError):
        sys.exit(f"FOUT: ongeldig getal '{v}' in {field} bij '{ctx}'")


def main():
    with open(SITE, encoding="utf-8") as f:
        config = json.load(f)
    cats = config["categories"]

    attr_rows = read_csv(ATTR_CSV)
    offer_rows = read_csv(OFFERS_CSV)

    # group offers by attraction id
    offers_by_id = {}
    for o in offer_rows:
        aid = o["id"].strip()
        offers_by_id.setdefault(aid, []).append({
            "v": o["v"].strip(),
            "p": num(o["p"], "p (prijs)", o.get("v", aid)),
            "t": o["t"].strip(),
            "url": o["url"].strip(),
        })

    attractions = []
    seen = set()
    for r in attr_rows:
        aid = r["id"].strip()
        if aid in seen:
            sys.exit(f"FOUT: dubbele id '{aid}' in attractions.csv")
        seen.add(aid)
        if r["cat"].strip() not in cats:
            sys.exit(f"FOUT: onbekende categorie '{r['cat']}' bij '{aid}' (zie site.json)")
        offers = offers_by_id.get(aid)
        if not offers:
            sys.exit(f"FOUT: geen offers gevonden voor '{aid}' in offers.csv")
        attractions.append({
            "id": aid,
            "naam": r["naam"].strip(),
            "cat": r["cat"].strip(),
            "plaats": r["plaats"].strip(),
            "provincie": r["provincie"].strip(),
            "rating": num(r["rating"], "rating", aid),
            "kassa": num(r["kassa"], "kassa", aid),
            "verified": r.get("verified", "").strip(),
            "bron": r.get("bron", "").strip(),
            "omschrijving": r["omschrijving"].strip(),
            "offers": offers,
        })

    # warn about ids that have offers but no attraction row
    orphans = set(offers_by_id) - seen
    if orphans:
        print(f"WAARSCHUWING: offers zonder attractie-rij genegeerd: {', '.join(sorted(orphans))}")

    out = {
        "_comment": "GEGENEREERD door ingest.py uit attractions.csv + offers.csv -- niet handmatig bewerken.",
        "site": config["site"],
        "categories": cats,
        "attractions": attractions,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"Ingest klaar: {len(attractions)} attracties, {len(offer_rows)} offers -> {OUT}")


if __name__ == "__main__":
    main()
