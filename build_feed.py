"""Builds the compact station feed the watch downloads.

Reads gasvaktin's gas.min.json and writes:
    {"c": [company, ...],
     "s": [[companyIndex, name, lat, lon, p95, diesel], ...]}
Stations are sorted by 95 price (stations without one last), so the watch
doesn't have to sort them. Missing prices are null.

Usage: python build_feed.py <output.json>
"""
import json
import sys
import urllib.request

SOURCE_URL = "https://raw.githubusercontent.com/gasvaktin/gasvaktin/master/vaktin/gas.min.json"


def round_or_none(value, digits):
    return None if value is None else round(float(value), digits)


def build(source):
    companies = []
    rows = []
    for st in source["stations"]:
        geo = st.get("geo") or {}
        lat, lon = geo.get("lat"), geo.get("lon")
        p95, diesel = st.get("bensin95"), st.get("diesel")
        name, company = st.get("name"), st.get("company")
        if None in (lat, lon, name, company) or (p95 is None and diesel is None):
            continue
        if company not in companies:
            companies.append(company)
        rows.append([
            companies.index(company),
            name,
            round(float(lat), 4),
            round(float(lon), 4),
            round_or_none(p95, 1),
            round_or_none(diesel, 1),
        ])
    rows.sort(key=lambda r: (r[4] is None, r[4] or 0))
    return {"c": companies, "s": rows}


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: build_feed.py <output.json>")
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as resp:
        source = json.load(resp)
    feed = build(source)
    if not feed["s"]:
        sys.exit("no stations in source feed; refusing to publish an empty feed")
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(feed, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
