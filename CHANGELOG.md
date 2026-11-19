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
