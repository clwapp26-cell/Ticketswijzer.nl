#!/usr/bin/env python3
"""
TicketsWijzer — one-command build.

Reads the data in this gen/ folder + the guide bodies in ../data/hubs/, and
writes the finished website to ../site/.

USAGE (from the ticketswijzer folder):
    python gen/build_all.py

To add/change an attraction: edit gen/attractions.csv and gen/offers.csv.
To add a guide: drop an HTML body in ../data/hubs/ and add an entry to gen/hubs.json.
Then run this script again and push to GitHub.
"""
import csv, json, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))      # gen/
PROJ = os.path.dirname(HERE)                            # ticketswijzer/


def num(v):
    return float(str(v).replace(",", ".").strip())


def ingest():
    site = json.load(open(os.path.join(HERE, "site.json"), encoding="utf-8"))
    cats = site["categories"]
    A = list(csv.DictReader(open(os.path.join(HERE, "attractions.csv"), encoding="utf-8-sig")))
    O = list(csv.DictReader(open(os.path.join(HERE, "offers.csv"), encoding="utf-8-sig")))
    off = defaultdict(list)
    for o in O:
        off[o["id"].strip()].append({"v": o["v"].strip(), "p": num(o["p"]), "t": o["t"].strip(), "url": o["url"].strip()})
    attractions, seen = [], set()
    for r in A:
        aid = r["id"].strip()
        if aid in seen:
            sys.exit(f"FOUT: dubbele id '{aid}' in attractions.csv")
        seen.add(aid)
        if r["cat"].strip() not in cats:
            sys.exit(f"FOUT: onbekende categorie '{r['cat']}' bij '{aid}' (zie site.json)")
        if not off.get(aid):
            sys.exit(f"FOUT: geen offers gevonden voor '{aid}' in offers.csv")
        attractions.append({
            "id": aid, "naam": r["naam"].strip(), "cat": r["cat"].strip(), "plaats": r["plaats"].strip(),
            "provincie": r["provincie"].strip(), "rating": num(r["rating"]), "kassa": num(r["kassa"]),
            "verified": r.get("verified", "").strip(), "bron": r.get("bron", "").strip(),
            "omschrijving": r["omschrijving"].strip(), "offers": off[aid],
        })
    orphans = set(off) - seen
    if orphans:
        print("WAARSCHUWING: offers zonder attractie genegeerd:", ", ".join(sorted(orphans)))
    json.dump({"site": site["site"], "categories": cats, "attractions": attractions},
              open(os.path.join(HERE, "data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"ingest: {len(attractions)} attracties, {len(O)} offers")


if __name__ == "__main__":
    ingest()
    sys.path.insert(0, HERE)
    import engine
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PROJ, "site")
    engine.build(out)
    print("Klaar. Commit en push de 'site' map om live te zetten.")
