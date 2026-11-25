#!/usr/bin/env python3
"""Generate the next unpublished Florida county directory page from a DBPR extract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_BASE = "https://hernandez188515-del.github.io/florida-wind-mitigation-directory"

COUNTY_CODES = {
    "11": "Alachua", "12": "Baker", "13": "Bay", "14": "Bradford", "15": "Brevard",
    "16": "Broward", "17": "Calhoun", "18": "Charlotte", "19": "Citrus", "20": "Clay",
    "21": "Collier", "22": "Columbia", "23": "Miami-Dade", "24": "DeSoto", "25": "Dixie",
    "26": "Duval", "27": "Escambia", "28": "Flagler", "29": "Franklin", "30": "Gadsden",
    "31": "Gilchrist", "32": "Glades", "33": "Gulf", "34": "Hamilton", "35": "Hardee",
    "36": "Hendry", "37": "Hernando", "38": "Highlands", "39": "Hillsborough", "40": "Holmes",
    "41": "Indian River", "42": "Jackson", "43": "Jefferson", "44": "Lafayette", "45": "Lake",
    "46": "Lee", "47": "Leon", "48": "Levy", "49": "Liberty", "50": "Madison", "51": "Manatee",
    "52": "Marion", "53": "Martin", "54": "Monroe", "55": "Nassau", "56": "Okaloosa",
    "57": "Okeechobee", "58": "Orange", "59": "Osceola", "60": "Palm Beach", "61": "Pasco",
    "62": "Pinellas", "63": "Polk", "64": "Putnam", "65": "St. Johns", "66": "St. Lucie",
    "67": "Santa Rosa", "68": "Sarasota", "69": "Seminole", "70": "Sumter", "71": "Suwannee",
    "72": "Taylor", "73": "Union", "74": "Volusia", "75": "Wakulla", "76": "Walton",
    "77": "Washington",
}

SLUGS = {code: name.lower().replace(" ", "-").replace(".", "") for code, name in COUNTY_CODES.items()}

SOURCE_PAGE = "https://www2.myfloridalicense.com/home-inspectors/public-records/"
SOURCE_CSV = "https://www2.myfloridalicense.com/sto/file_download/extracts/lic04home.csv"
SOURCE_README = "https://www2.myfloridalicense.com/sto/documents/readme.pdf"
DFS_URL = "https://www.myfloridacfo.com/division/consumers/storm/mitigation-notices-inspections-and-forms"
DBPR_SEARCH = "https://www.myfloridalicense.com/wl11.asp?mode=0&amp;search=LicRelo"

# Display-only fixes for obvious spelling variants in the extract's city field.
CITY_FIXES = {
    "FT LAUDERDALE": "FORT LAUDERDALE", "FT. LAUDERDALE": "FORT LAUDERDALE",
    "FORT LAUDERDALE, FL": "FORT LAUDERDALE", "CORAL SPRING": "CORAL SPRINGS",
    "CORALSPRINGS": "CORAL SPRINGS", "DERRFIELD BEACH": "DEERFIELD BEACH",
    "LAUDERDHILL": "LAUDERHILL", "LAUD BY TRHE SEA": "LAUDERDALE-BY-THE-SEA",
    "LAUDERDALE BY THE SE": "LAUDERDALE-BY-THE-SEA", "SW RANCHES": "SOUTHWEST RANCHES",
    "POMPANO": "POMPANO BEACH", "FT MYERS": "FORT MYERS", "FT. MYERS": "FORT MYERS",
    # Palm Beach County variants (added 2026-11-19)
    "DEL RAY BEACH": "DELRAY BEACH", "DELRAY": "DELRAY BEACH", "JUPTER": "JUPITER",
    "LAKEWORTH BEACH": "LAKE WORTH BEACH", "LOXAHATCHEE, FL": "LOXAHATCHEE",
    "WEST PALM BAACH": "WEST PALM BEACH", "WEST PALM BCH": "WEST PALM BEACH",
    "WEST PALM BEAACH": "WEST PALM BEACH", "PSL": "PORT ST. LUCIE",
    # Hillsborough County variants (added 2026-11-21)
    "SUN CITY CENTERR": "SUN CITY CENTER", "ST PETERSBURG": "ST. PETERSBURG",
    # Lee County variants (added 2026-11-22)
    "N. FT. MYERS": "NORTH FORT MYERS", "N. FORT MYERS": "NORTH FORT MYERS",
    "N FORT MYERS": "NORTH FORT MYERS", "N FT MYERS": "NORTH FORT MYERS",
    "BONITA SPGS": "BONITA SPRINGS", "BONITA SPRING": "BONITA SPRINGS",
    # Orange County variants (added 2026-11-24)
    "ORALANDO": "ORLANDO",
}


def raw_city(row) -> str:
    return re.sub(r"\s+", " ", row[8].strip().upper())


def norm_city(row) -> str:
    c = raw_city(row)
    return CITY_FIXES.get(c, c)


def display_city(row) -> str:
    c = raw_city(row)
    c = CITY_FIXES.get(c, c)
    return c.title().replace("-By-The-", "-by-the-")


def city_home_county(all_rows) -> dict:
    """Most common county code per city across the whole statewide HI file."""
    tally: dict[str, Counter] = {}
    for r in all_rows:
        tally.setdefault(norm_city(r), Counter())[r[11]] += 1
    return {city: cnt.most_common(1)[0][0] for city, cnt in tally.items()}


def split_mismatches(inspectors, home_county, code):
    """Rows whose city is predominantly coded to a different county are footnoted, not tabled."""
    main, flagged = [], []
    for r in inspectors:
        home = home_county.get(norm_city(r), code)
        (flagged if home != code else main).append((r, home))
    return [r for r, _ in main], flagged


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_active(csv_path: Path):
    rows = []
    with csv_path.open(newline="", encoding="latin-1") as f:
        for r in csv.reader(f):
            if len(r) < 18:
                continue
            if r[1] == "HI" and r[13] == "C" and r[14] == "A":
                rows.append(r)
    return rows


def existing_county_slugs() -> set[str]:
    slugs = set()
    for path in ROOT.iterdir():
        if path.is_dir() and (path / "index.html").exists() and path.name not in {"assets", "data", "scripts"}:
            slugs.add(path.name)
    return slugs


def license_display(row) -> str:
    alt = row[20].strip() if len(row) > 20 else ""
    if alt.upper().startswith("HI"):
        return alt.replace(" ", "")
    return "HI" + row[12].lstrip("0")


def pick_next(rows, already: set[str]):
    counts = Counter(r[11] for r in rows if r[11] in COUNTY_CODES)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], COUNTY_CODES[kv[0]]))
    for code, n in ranked:
        slug = SLUGS[code]
        if slug not in already:
            return code, COUNTY_CODES[code], slug, n
    return None


def load_all_hi(csv_path: Path):
    with csv_path.open(newline="", encoding="latin-1") as f:
        return [r for r in csv.reader(f) if len(r) >= 18 and r[1] == "HI"]


def companies_fragment(slug: str, name: str) -> str:
    """Hand-verified company write-ups live in data/companies/<slug>.html and are never generated."""
    frag = ROOT / "data" / "companies" / f"{slug}.html"
    if frag.exists():
        return frag.read_text()
    return (
        "        <p class=\"kicker\">Checked against company websites</p>\n"
        "        <h2>Companies that advertise these inspections</h2>\n"
        f"        <p><em>Verification pending.</em> No {escape(name)} company has been checked against its own website and matched to the official license file yet. "
        "Companies will be added here only after a person opens the company’s site and matches a licensee name or HI license number to the DBPR extract.</p>\n"
    )


def render_county(name: str, slug: str, code: str, inspectors: list, flagged: list,
                  today: str, csv_path: Path, sha: str, statewide: int) -> str:
    pretty_day = date.fromisoformat(today).strftime("%B %-d, %Y")
    # The extract date comes from the saved file name (data/lic04home-YYYY-MM-DD.csv) so a reused
    # snapshot is not described as downloaded on the page-generation day.
    m = re.search(r"(\d{4}-\d{2}-\d{2})", csv_path.name)
    extract_day = date.fromisoformat(m.group(1)) if m else date.fromisoformat(today)
    extract_pretty = extract_day.strftime("%B %-d, %Y")
    short_day = extract_day.strftime("%b %-d, %Y")
    body_rows = []
    for r in inspectors:
        body_rows.append(
            "<tr>"
            f"<td>{escape(r[2].strip())}</td>"
            f"<td>{escape(display_city(r))}</td>"
            f"<td class='mono'>{escape(r[10].strip()[:5])}</td>"
            f"<td class='mono'>{escape(license_display(r))}</td>"
            "<td>Current / Active</td>"
            f"<td class='mono'>{escape(r[15].strip())}</td>"
            f"<td class='mono'>{escape(r[17].strip())}</td>"
            "</tr>"
        )
    flag_rows = []
    for r, home in flagged:
        other = COUNTY_CODES.get(home, f"code {home}")
        flag_rows.append(
            "<tr>"
            f"<td>{escape(r[2].strip())}</td>"
            f"<td>{escape(display_city(r))}</td>"
            f"<td class='mono'>{escape(r[10].strip()[:5])}</td>"
            f"<td class='mono'>{escape(license_display(r))}</td>"
            f"<td>Official extract lists county code {escape(code)} ({escape(name)}), but this city is otherwise coded to {escape(other)} County in the same file.</td>"
            "</tr>"
        )
    n = len(inspectors)
    nf = len(flagged)
    expiries = sorted({r[17].strip() for r in inspectors})
    exp_pill = (f"All licenses shown expire {expiries[0]} in this file" if len(expiries) == 1
                else f"Expiration dates: {', '.join(expiries)}")
    flagged_section = ""
    if nf:
        flagged_section = f"""
      <section class="section" id="footnotes">
        <h2>Records in this extract with county code {escape(code)} but a city outside {escape(name)}</h2>
        <p>{nf} current/active home-inspector row{'s are' if nf != 1 else ' is'} coded as county {escape(code)} ({escape(name)}) but list a city that is otherwise coded to a different county in the same statewide file. They are not in the table above. This is a data-quality note, not a claim about where those people work.</p>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Licensee name</th>
                <th>City in extract</th>
                <th>ZIP</th>
                <th>License</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>
              {"".join(flag_rows)}
            </tbody>
          </table>
        </div>
      </section>
"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(name)} wind mitigation and 4-point inspectors — Florida Insurance Inspections</title>
  <meta name="description" content="Licensed home inspectors with an official {escape(name)} mailing county, plus companies whose websites advertise wind mitigation or 4-point inspections. Data from the Florida DBPR extract dated {extract_pretty}.">
  <link rel="stylesheet" href="../assets/styles.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:opsz,wght@8..60,600&display=swap" rel="stylesheet">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="header">
    <div class="header-inner">
      <a class="logo" href="../">Florida Insurance <span>Inspections</span></a>
      <nav>
        <a href="../">Home</a>
        <a href="./" aria-current="page">{escape(name)} directory</a>
        <a href="#full-list">Full license list</a>
      </nav>
    </div>
  </header>

  <div class="page-hero">
    <div class="wrap">
      <div class="crumbs"><a href="../">Home</a> / {escape(name)} County</div>
      <h1>Wind mitigation and 4-point inspectors in {escape(name)}</h1>
      <p class="lede">A complete list of current, active Florida-licensed home inspectors whose official mailing county is {escape(name)}, plus a shorter list of companies checked on {pretty_day} (America/New_York) because their own websites say they offer wind mitigation or 4-point inspections.</p>
      <div class="meta-bar">
        <span class="pill">DBPR extract downloaded {short_day}</span>
        <span class="pill">{n} inspectors in the main table</span>
        <span class="pill">{escape(exp_pill)}</span>
      </div>
    </div>
  </div>

  <main id="main" class="section" style="padding-top:0">
    <div class="wrap">
      <div class="callout">
        <p><strong>Read this first.</strong> A Florida home-inspector license is necessary but not always sufficient to sign a wind mitigation form. Under Florida law, a licensed home inspector who signs the Uniform Mitigation Verification Inspection Form (OIR-B1-1802) must also have completed the required hurricane-mitigation training and proficiency exam (see the <a href="{DFS_URL}">Florida DFS summary of who may sign</a>). A home-inspector license alone is not proof of that eligibility, and this directory cannot see that training in the public license extract. Confirm the inspector can complete the current OIR-B1-1802 form, and re-check the license on the official <a href="{DBPR_SEARCH}">DBPR search</a> before you book. Listings are not endorsements, and we do not collect a referral fee from anyone listed here today.</p>
      </div>

      <section class="section" id="companies" style="padding-bottom:0.5rem">
{companies_fragment(slug, name)}
      </section>

      <section class="section" id="full-list">
        <h2>All current, active licensed home inspectors with a {escape(name)} mailing county</h2>
        <p>These {n} people appear in the official DBPR extract with occupation HI, status Current / Active, and county code {escape(code)} ({escape(name)}). This is a mailing-county list, not proof that each person currently offers wind mitigation or 4-point work, and not proof of the extra mitigation training noted above. City and ZIP come from the official file (obvious city misspellings are normalized for display); street addresses are omitted.</p>
        <div class="toolbar">
          <div class="field">
            <label for="q">Search name, city, ZIP, or license</label>
            <input type="search" id="q" placeholder="For example, Plantation or HI2355">
          </div>
          <div class="field">
            <label for="city">City</label>
            <select id="city">
              <option value="">All cities</option>
            </select>
          </div>
        </div>
        <p class="count" id="count"></p>
        <div class="table-wrap">
          <table id="inspectors">
            <thead>
              <tr>
                <th>Licensee name</th>
                <th>Mailing city</th>
                <th>ZIP</th>
                <th>License</th>
                <th>Status</th>
                <th>First licensed</th>
                <th>Expires</th>
              </tr>
            </thead>
            <tbody>
              {"".join(body_rows)}
            </tbody>
          </table>
        </div>
      </section>
{flagged_section}
      <section class="section" id="sources">
        <h2>Source file</h2>
        <p class="footnote">Florida Department of Business and Professional Regulation, Home Inspectors public extract, downloaded {extract_pretty}, America/New_York, from <a href="{SOURCE_CSV}">lic04home.csv</a> (saved as <span class="mono">{escape(csv_path.name)}</span>, SHA-256 <span class="mono">{sha}</span>). Profession page: <a href="{SOURCE_PAGE}">Home Inspectors – Public Records</a>. Layout and status codes: <a href="{SOURCE_README}">readme.pdf</a> (Primary Status C = Current, Secondary Status A = Active, county code {escape(code)} = {escape(name)}). Filters: occupation HI; primary status C; secondary status A; county code {escape(code)}. The same file had {statewide:,} current/active HI licenses statewide.</p>
      </section>
    </div>
  </main>

  <footer>
    <div class="footer-inner">
      <a class="logo" href="../">Florida Insurance <span>Inspections</span></a>
      <p>Listings are not endorsements or price quotes. License data dated {extract_pretty}; company checks {pretty_day}, America/New_York.</p>
    </div>
  </footer>
  <script>
    const input = document.getElementById("q");
    const city = document.getElementById("city");
    const rows = Array.from(document.querySelectorAll("#inspectors tbody tr"));
    const count = document.getElementById("count");
    const cities = [...new Set(rows.map(r => r.children[1].textContent.trim()))].sort((a,b) => a.localeCompare(b));
    for (const c of cities) {{
      const opt = document.createElement("option");
      opt.value = c;
      opt.textContent = c;
      city.appendChild(opt);
    }}
    function apply() {{
      const q = (input.value || "").trim().toLowerCase();
      const c = city.value;
      let n = 0;
      for (const row of rows) {{
        const text = row.textContent.toLowerCase();
        const cityName = row.children[1].textContent.trim();
        const show = (!q || text.includes(q)) && (!c || cityName === c);
        row.classList.toggle("hidden", !show);
        if (show) n++;
      }}
      count.textContent = n + " of {n} inspectors shown.";
    }}
    input.addEventListener("input", apply);
    city.addEventListener("change", apply);
    apply();
  </script>
</body>
</html>
"""


def update_sitemap(slug: str, today: str) -> None:
    path = ROOT / "sitemap.xml"
    text = path.read_text()
    entry = (
        "  <url>\n"
        f"    <loc>{SITE_BASE}/{slug}/</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "  </url>\n"
    )
    if f"/{slug}/" in text:
        return
    text = text.replace("</urlset>", entry + "</urlset>")
    path.write_text(text)


def update_homepage(name: str, slug: str, count: int) -> None:
    path = ROOT / "index.html"
    text = path.read_text()
    marker = "<!-- nightly:county-links -->"
    link = f'<p><a href="{slug}/">{escape(name)} County directory</a> — {count} current/active licenses in the latest extract.</p>\n'
    if f'href="{slug}/"' in text:
        return
    if marker in text:
        text = text.replace(marker, marker + "\n        " + link)
    else:
        # Fall back: append a short line in the "What's next" card if the marker is missing.
        needle = "<h2>The rest of Florida, one page at a time</h2>"
        text = text.replace(needle, needle + "\n          " + marker + "\n          " + link)
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--county", help="Regenerate a specific county slug (e.g. palm-beach) instead of picking the next unpublished one")
    args = parser.parse_args()
    rows = load_active(args.csv)
    already = existing_county_slugs()
    if args.county:
        code = next((c for c, sl in SLUGS.items() if sl == args.county), None)
        if code is None:
            raise SystemExit(f"Unknown county slug: {args.county}")
        nxt = (code, COUNTY_CODES[code], args.county, sum(1 for r in rows if r[11] == code))
    else:
        nxt = pick_next(rows, already)
    if not nxt:
        print("No unpublished counties remain in this extract.")
        return
    code, name, slug, n = nxt
    print(f"Next page: {name} County ({slug}), {n} current/active HI licenses, county code {code}")
    if not args.write:
        print("Dry run only. Pass --write to create the page and update sitemap/index.")
        return
    today = date.today().isoformat()
    in_county = sorted(
        (r for r in rows if r[11] == code),
        key=lambda r: (display_city(r).upper(), r[2]),
    )
    home = city_home_county(load_all_hi(args.csv))
    inspectors, flagged = split_mismatches(in_county, home, code)
    sha = sha256_of(args.csv)
    folder = ROOT / slug
    folder.mkdir(exist_ok=True)
    (folder / "index.html").write_text(
        render_county(name, slug, code, inspectors, flagged, today, args.csv, sha, len(rows))
    )
    update_sitemap(slug, today)
    update_homepage(name, slug, len(inspectors))
    print(f"Table rows: {len(inspectors)}; footnoted city/county mismatches: {len(flagged)}; SHA-256 {sha}")
    print(f"Wrote {folder / 'index.html'} and updated sitemap.xml and index.html")
    # Shared head tags (canonical, Open Graph, JSON-LD), nav, related-pages block and sitemap.
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "scripts" / "seo.py")], check=True)


if __name__ == "__main__":
    main()
