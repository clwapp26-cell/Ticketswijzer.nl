#!/usr/bin/env python3
"""
TicketsWijzer static-site generator (entry point).

The generation logic lives in sitegen_core.py; this file just runs it so the
command stays the same.

Data workflow:  edit data/attractions.csv + data/offers.csv (+ data/hubs/*.html)
                -> python3 ingest.py   (writes data/attractions.json)
                -> python3 build.py    (writes site/)
"""
from sitegen_core import build

if __name__ == "__main__":
    build()
