# Publishing and nightly page additions

This is a static site. There is no server-side code.

It is live on GitHub Pages at https://hernandez188515-del.github.io/florida-wind-mitigation-directory/ (repo: https://github.com/hernandez188515-del/florida-wind-mitigation-directory). `sitemap.xml` and `robots.txt` already use that URL. Keep new sitemap entries on the same host, including the repo subpath. Internal links and asset paths are relative so they work under that subpath.

## What’s already live in this folder

- `index.html` — homepage
- `miami-dade/index.html` — first county directory (Miami-Dade)
- `broward/index.html` — second county directory (Broward), added November 18, 2026
- `palm-beach/index.html` — third county directory (Palm Beach), added November 19, 2026
- `hillsborough/index.html` — fourth county directory (Hillsborough), added November 21, 2026
- `lee/index.html` — fifth county directory (Lee), added November 22, 2026
- `orange/index.html` — sixth county directory (Orange), added November 24, 2026
- `pinellas/index.html` — seventh county directory (Pinellas), added November 25, 2026
- `guides/wind-mitigation-vs-4-point-vs-roof-certification/index.html` — first hand-written explainer (wind mitigation vs. 4-point vs. roof certification; signers, April 1, 2026 OIR-B1-1802 change, wind credits, published prices), added November 20, 2026
- `guides/2026-wind-mitigation-form-question-by-question/index.html` — second hand-written explainer (all nine questions on OIR-B1-1802 Rev. 04/26, changes from Rev. 01/12, documentation checklist, rule status), added November 23, 2026
- `guides/citizens-4-point-and-roof-age-requirements/index.html` — third hand-written explainer (Citizens Property Insurance 4-point rule for homes over 20 years old, 25/50-year roof-age limits, 5-year remaining-useful-life rule, proof of replacement, current Insp4pt 03 25 / RCF-1 03 25 forms and signers, s. 627.7011(5), 2026 status), added November 26, 2026
- `assets/styles.css`
- `data/lic04home-2026-11-18.csv` — official Florida DBPR home-inspector extract downloaded November 18, 2026 (America/New_York)
- `data/lic04home-2026-11-19.csv` — re-download on November 19, 2026; byte-identical to the November 18 file (same SHA-256)
- `data/lic04home-2026-11-26.csv` — re-download on November 26, 2026; differs from the November 19 file (SHA-256 `a66628f1913aea3997a38b101d742b61fd5f50906674d6631ba9723827f4f880`; 9,184 lines vs. 9,133; 7,857 current/active HI vs. 7,816). Published county tables were still generated from the November 19 file
- `data/miami-dade-inspectors.json` — the filtered Miami-Dade table (no street addresses)
- `data/broward-inspectors.json` — the filtered Broward table (no street addresses)
- `data/palm-beach-inspectors.json` — the filtered Palm Beach table (no street addresses)
- `data/hillsborough-inspectors.json` — the filtered Hillsborough table (no street addresses)
- `data/lee-inspectors.json` — the filtered Lee table (no street addresses)
- `data/orange-inspectors.json` — the filtered Orange table (no street addresses)
- `data/pinellas-inspectors.json` — the filtered Pinellas table (no street addresses)
- `data/companies/<slug>.html` — hand-verified company write-ups; `scripts/next_county.py` includes them verbatim and shows a “verification pending” stub when the file is missing
- `CHANGELOG.md` — dated log of each nightly run
- `sitemap.xml`, `robots.txt`

## Page types the nightly run should add

Add **one new HTML page per night**, in this order of priority:

1. **County directory pages** — one page per Florida county that has at least one current, active home-inspector license in the extract. The Miami-Dade page is the template. After Miami-Dade, the next largest counties in the November 18, 2026 extract were Broward (673), Palm Beach (482), Hillsborough (408), Lee (360), Orange (346), Pinellas (334), Duval (256), and Brevard and Pasco (249 each). Sixty-five of Florida’s 67 counties had at least one current/active record; Glades and Taylor had none in this file.
2. **City directory pages** — only after the county page for that city exists. In the same extract there were 657 unique Florida city+county combinations; 259 had five or more current/active inspectors.
3. **Explainer pages** (less often, and written by hand rather than generated): what a wind mitigation form covers, 4-point vs. full home inspection, the April 1, 2026 OIR-B1-1802 form change, and “who is legally allowed to sign.”

Do not auto-generate individual inspector profile pages until there is a review step. The public extract includes mailing addresses that should stay unpublished.

## Where the listing data comes from

Primary source, every run:

- Profession page: https://www2.myfloridalicense.com/home-inspectors/public-records/
- CSV: https://www2.myfloridalicense.com/sto/file_download/extracts/lic04home.csv
- Layout and codes: https://www2.myfloridalicense.com/sto/documents/readme.pdf

Filters to apply unless a page’s methodology says otherwise:

- Occupation code `HI` (exclude `CRS1` courses and `PVDR` providers in the same file)
- Primary status `C` (Current)
- Secondary status `A` (Active)
- County code from the official table (Miami-Dade is `23`, Broward `16`, Palm Beach `60`, and so on)

Save a dated copy of each download under `data/lic04home-YYYY-MM-DD.csv` and record the SHA-256. Keep street addresses out of generated HTML. If a row’s county code and city disagree (for example, county 23 with a city of Cape Coral), keep it out of the main county table and footnote it, as the Miami-Dade page does.

A home-inspector license is not, by itself, proof that someone has completed the hurricane-mitigation training required to sign form OIR-B1-1802. Generated pages must keep that caveat. Company-level “advertises wind mitigation / 4-point” highlights should only be added when a person has checked the company’s own website and matched a license number or licensee name to the official extract. Do not invent prices; quote them only from a page you opened, with the date checked.

Optional later sources, if a page needs them and they are still public:

- Florida DFS, who may sign a mitigation form: https://www.myfloridacfo.com/division/consumers/storm/mitigation-notices-inspections-and-forms
- Licensed general / building / residential contractors, professional engineers, architects, and building-code inspectors (other DBPR or FBPE extracts), because those licensees may also sign the form
- An inspector’s own website, for phone numbers, service area, and published prices

Re-verify any license at the official search before relying on it: https://www.myfloridalicense.com/wl11.asp?mode=0&search=LicRelo

## How a nightly run should work

A simple scheduled job (GitHub Actions, Netlify scheduled function, or a cron user on a box) should:

1. Download a fresh `lic04home.csv` and store it as `data/lic04home-YYYY-MM-DD.csv`.
2. Parse it with the filters above.
3. Look at existing county folders (today: `miami-dade/`, `broward/`, `palm-beach/`, `hillsborough/`, `lee/`, `orange/`, `pinellas/`). Choose the next unpublished county, preferably the remaining county with the most current/active inspectors.
4. Generate that county’s `index.html` from the same layout as Miami-Dade: intro and caveats, then the license table (name, mailing city, ZIP, license number, status, first licensed, expiration). Leave the “companies that advertise these inspections” section as a stub unless someone has verified companies for that county.
5. Refresh previously generated **tables** if license status changed, but do not silently overwrite hand-verified company write-ups.
6. Update the homepage so the new county is linked (the “Live now” / “What’s next” area).
7. Add the new path to `sitemap.xml` with that day’s `lastmod`, and keep the homepage and older county pages listed.
7b. Run `python3 scripts/seo.py` from the site root before committing (the county generator runs it automatically after `--write`; run it by hand after adding or editing a guide). It refreshes every page's canonical/Open Graph/JSON-LD block, the shared nav, the related-pages + featured-listing block, and rebuilds `sitemap.xml` from the pages on disk. It only rewrites text between its own `seo:` markers and the `<nav>`. To list a new guide in the top nav, add it to `NAV_GUIDES` in that script. A real Q&A section using `<div class="faq-item"><h3>Question</h3><p>Answer</p></div>` gets FAQPage JSON-LD automatically.
7c. After the push is live, notify IndexNow (Bing, Yandex, Seznam, Naver) of the new or changed URLs:

   ```bash
   python3 scripts/indexnow.py https://hernandez188515-del.github.io/florida-wind-mitigation-directory/<new-path>/
   ```

   With no arguments it submits every URL in `sitemap.xml`. A 200 or 202 response means accepted.
8. Commit and push the changed files so GitHub Pages rebuilds:

   ```bash
   git add -A && git commit && git push
   ```

   From the site root (`/workspace/directory-site` on the box, or a clone of the repo). Use a short commit message that names the new page, for example `Add Palm Beach County directory`. If there is nothing to commit, do not force a commit.

`scripts/next_county.py` is a starting point for steps 3–7. Run it from the site root after a new extract is in `data/`. It prints what it would do; pass `--write` only when you intend to create the page.

Example:

```bash
python3 scripts/next_county.py --csv data/lic04home-2026-11-18.csv
python3 scripts/next_county.py --csv data/lic04home-2026-11-18.csv --write
# regenerate one existing county (e.g. after editing its data/companies/<slug>.html):
python3 scripts/next_county.py --csv data/lic04home-2026-11-19.csv --county palm-beach --write
```

The script does not write `data/<slug>-inspectors.json`; generate that separately with the same filters.

## Deploying

The site is published from the `main` branch root of https://github.com/hernandez188515-del/florida-wind-mitigation-directory to GitHub Pages. The live URL is https://hernandez188515-del.github.io/florida-wind-mitigation-directory/. A `.nojekyll` file is in the root so GitHub does not run Jekyll.

Nightly runs should write the new page, then from this folder run:

```bash
git add -A && git commit && git push
```

That is enough to ship the page. Do not re-enable Pages or change other repositories. If the site later moves to a custom domain, update the host in `sitemap.xml`, `robots.txt`, and `SITE_BASE` in `scripts/next_county.py`.
