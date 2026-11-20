# Changelog

All dates are America/New_York.

## 2026-11-18

**Initial pages (already in place before tonight's nightly run):**
- `index.html` — homepage.
- `miami-dade/index.html` — first county directory (Miami-Dade, county code 23): 911 current/active HI licensees in the main table, 10 city/county mismatches footnoted, 7 hand-verified companies.

**Nightly publish — Broward County (`/broward/`):**
- Source: DBPR home-inspector extract `data/lic04home-2026-11-18.csv`, downloaded 2026-11-18 from https://www2.myfloridalicense.com/sto/file_download/extracts/lic04home.csv (readme: https://www2.myfloridalicense.com/sto/documents/readme.pdf). SHA-256 `9e692086a719f4c2dbc4d24c293f5ae8aa7a4ddd06cc5eb1e9c487f857ca3678` (1,624,454 bytes) — same snapshot used for Miami-Dade; reused because it is less than a week old.
- Filters: occupation HI, primary status C, secondary status A, county code 16. 673 matching rows → 666 in the main table; 7 rows footnoted because their city (Aventura, Boca Raton ×2, Boynton Beach, Marco Island, Okeechobee, Winter Garden) is otherwise coded to a different county.
- Hand-verified companies (own website opened and license/name matched to the extract on 2026-11-18): Buy Right Home Inspections (HI5831), Checkmark Inspections (HI10953, name match), InspectionNow (HI2355), Sun Inspections (HI11148), Sune Home Inspection (HI3633). Inspect and Protect (HI18768) noted separately because its licensee's mailing county is Miami-Dade. Write-ups live in `data/companies/broward.html`.
- Added `data/broward-inspectors.json` (filtered table, no street addresses).
- `index.html`: Broward linked in nav, "Live now" and "What's next" cards. `sitemap.xml`: added `/broward/` (lastmod 2026-11-18); existing entries kept.
- `scripts/next_county.py` upgraded: city/county mismatch footnotes, source citation + SHA-256 on page, mitigation-signing caveat, city filter, display normalization for obvious city misspellings, and hand-verified company fragments read from `data/companies/<slug>.html` (stub "verification pending" when absent).
- Deploy: **pending** — no git repo, remote, or hosting config (netlify.toml, .github/workflows, CNAME) exists. Nothing was deployed.

## 2026-11-19

**Nightly publish — Palm Beach County (`/palm-beach/`):**
- Source: re-downloaded https://www2.myfloridalicense.com/sto/file_download/extracts/lic04home.csv on 2026-11-19 and saved as `data/lic04home-2026-11-19.csv`. SHA-256 `9e692086a719f4c2dbc4d24c293f5ae8aa7a4ddd06cc5eb1e9c487f857ca3678` (1,624,454 bytes) — byte-identical to the 2026-11-18 snapshot, so counts match the earlier pages.
- `scripts/next_county.py` confirmed Palm Beach (county code 60, 482 current/active HI licenses) as the next unpublished county.
- Filters: occupation HI, primary status C, secondary status A, county code 60. 482 matching rows → 478 in the main table; 4 rows footnoted because their city (Hialeah, Port St. Lucie ×2 — one written "PSL" in the extract, Punta Gorda) is otherwise coded to a different county.
- Hand-verified companies (own website opened and license/name matched to the extract on 2026-11-19): Cornerstone Home Inspections (HI10762), Home Scan Inspections (HI11676), Palm Beach Inspections, LLC (HI12371 and HI15474, name match), SteelSight Home Inspections (HI18142, name match), 3S Dynamic (HI18222), Wright Way Home Inspections (HI4609). Prices quoted only for Home Scan and Palm Beach Inspections, from pages opened that night. Write-ups live in `data/companies/palm-beach.html`.
- Added `data/palm-beach-inspectors.json` (filtered table, no street addresses).
- `index.html`: Palm Beach linked in nav, "Live now" and "What's next" cards; "Next up" now Hillsborough. `sitemap.xml`: added `/palm-beach/` (lastmod 2026-11-19), homepage lastmod bumped to 2026-11-19; existing entries kept.
- `scripts/next_county.py`: added Palm Beach city-spelling fixes (Del Ray Beach, Delray, Jupter, Lakeworth Beach, "Loxahatchee, Fl", West Palm Baach/Bch/Beaach, PSL); the city→county mismatch check now uses the normalized city; new `--county <slug>` flag to regenerate an existing county page. Note: under the normalized check Miami-Dade would compute 910 table rows / 11 footnotes (vs. the published 911 / 10); the Miami-Dade and Broward pages were not regenerated tonight (Broward is unchanged at 666 / 7).
- Deploy: commit `0c4464b` ("Add Palm Beach County directory") pushed to `origin/main` (fast-forward, no force). GitHub Pages build for `0c4464b` reported `built` at 2026-11-19 22:07 ET; `curl -sI .../palm-beach/` → HTTP 200 and homepage → HTTP 200. Live: https://hernandez188515-del.github.io/florida-wind-mitigation-directory/palm-beach/ . No traffic or revenue source is connected.
