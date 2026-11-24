# GATE 2024 (IISc Bengaluru) — faithful frontend clone

A runnable, responsive static clone of **https://gate2024.iisc.ac.in/** (WordPress + Divi theme), built from a
strictly read-only mirror of the production site (plain HTTP GETs only — nothing on production was modified).

## Run

```bash
cd /workspace/gate2024-clone
./run.sh            # or: npm start   (http://localhost:8080/)
./run.sh 3000       # any other port
```

Only Node.js is needed to serve the site (`server.js` has zero dependencies). `site/` is plain static HTML/CSS/JS,
so any static server pointed at `site/` also works.

## Layout

| Path | What it is |
|---|---|
| `site/` | **The deliverable** — generated static site (44 HTML pages incl. pagination, authentic CSS/JS/fonts/images/PDFs) |
| `server.js` | zero-dependency static server (directory → `index.html`, wget `@ver=` asset names, 404s) |
| `build.py` | rebuilds `site/` from `source-mirror/` (link rewriting, asset localisation, clone add-ons) |
| `source-mirror/` | raw read-only wget mirror of production (+ downloaded PDFs, Font Awesome) |
| `src/clone/clone.js`, `clone.css` | clone add-ons: client-side search, notifications panel, link hygiene |
| `src/tables.py` | Ninja Tables row data (see “Tables” below) → `site/clone/tables/*.json` |
| `site/clone/search-index.js` | generated search index (pages, restored table rows, downloads, notifications) |
| `tools/check.js` | crawler: console/page errors, 4xx local requests, broken internal links + download links |
| `tools/functional-test.js` | dropdowns, mobile/tablet menu, search overlay + page, notifications, downloads |
| `tools/compare.js`, `sbs.py`, `compare-jobs.json` | original-vs-clone screenshots + side-by-side PNGs |
| `visual-comparison/` | `original-*.png`, `clone-*.png`, `compare-*.png`, `func-*.png` |

`npm run build` · `npm run check` · `npm test` · `npm run compare` (the last three need the server running and
use the system Chrome at `/usr/bin/google-chrome`; override with `CHROME=/path/to/chrome`).

## What is faithful

* Original Divi markup, CSS (et-cache), theme/plugin JS, Interstate (Adobe Typekit kit used by the original),
  images, logos, banners, favicons, YouTube embeds — all pages are the real HTML, relinked locally.
* All internal links (menu, dropdowns, footer, announcements, shortlinks `?p=NNN`) point to local pages.
* Downloads (Information Brochures, syllabus PDFs, DA sample papers, PwD guidelines/certificates, newspaper ad,
  poster, 1983 brochure, statistical report) are served locally.

## Clone add-ons (requested functionality)

* **Search** — magnifier button (top-right of the header; next to the hamburger on tablet/mobile) or press `/`.
  Instant results over all pages, restored tables, downloads and notifications, keyboard navigation (↑/↓/Enter/Esc).
  The site’s own `/search/` page and WordPress search forms work client-side (`/search/?s=brochure`).
* **Notifications** — bell button with unread badge, panel listing all 14 posts from the “Notifications” category
  (newest first), mark-as-read, dismiss (×), restore, “View all notifications”. State is kept in `localStorage`.
  The original homepage notifications ticker and “View All” button work as on production.

## Deliberate deviations (documented)

| Item | Production | Clone |
|---|---|---|
| Ninja Tables (31 tables on 12 pages) | `admin-ajax.php` answers **HTTP 403** → tables are empty on the live site | 9 tables restored from the official Information Brochure (27 Sep 2023) + text published on the site (important dates, eligibility, papers & codes, XE/XH/XL sections, two-paper combinations, question pattern ×2, fees, zonal contacts), each captioned as restored. 22 tables whose rows exist in no accessible source (year-wise old papers, master papers/keys, mock-test links, exam schedule, new combinations, fee-change charges) show a notice row linking the brochure/Download page — nothing invented. |
| Footer “Page Views” hit counter | third-party `counter.websiteout.com` script (currently injects ad text, ~410 px tall) | not loaded (it would count clone visits on production’s counter); box kept with a static “Hit counter” label. This is the only cause of the full-page height difference. |
| Footer “Home” link | `http://10.0.94.4` (intranet IP, broken) | links to the clone homepage |
| Statistical report link on homepage | `/2024/06/…Version2.pdf` → 404 | points to the working `/2026/04/…Version.pdf` that the Download page uses |
| Download page | loads a second jQuery 3.5.1 from Google CDN → `magnificPopup is not a function` | duplicate jQuery removed (zero console errors) |
| Font Awesome | cdnjs | vendored locally (`site/vendor/fontawesome`) |

Interstate is still loaded from Adobe Typekit exactly like the original (licensed kit, not self-hosted); if it is
unavailable the theme’s fallback fonts are used.
