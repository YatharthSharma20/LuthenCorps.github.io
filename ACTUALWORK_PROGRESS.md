# ActualWork — Progress Log

## Current Status

**Tasks 1–7 complete.** The full ActualWork site is built and generating correctly from JSON data. All pages (homepage, work entries, occupations, industries, tools, tags, search, submit, legal/policy pages) are generated and served at `/actualwork/`. LuthenCorps remains completely untouched.

## Completed

- **Task 1**: Inspected existing LuthenCorps repository.
  - Pure static HTML site, no framework, no build system.
  - GitHub Actions deploys entire repo root via `actions/upload-pages-artifact@v3` with `path: '.'`.
  - Entry point: `index.html` at root. CSS inline in each HTML file.
  - Pages: index, about, services, contact, how-it-works, gibberish-pdf-generator, gpg.
  - Assets: luthencorps.png, og-image.png at root.
  - SEO: robots.txt, sitemap.xml, Google verification file.
  - Conclusion: adding `actualwork/` directory requires zero changes to existing files.

- **Task 2**: Established isolated ActualWork directory structure.
  - Created `actualwork/` directory with `data/`, `static/`, subdirectories.
  - Created JSON data files: `occupations.json`, `industries.json`, `tools.json`, `tags.json`.
  - Created `_TEMPLATE.json` for easy entry creation.
  - Created `data/README.md` documenting all fields.

- **Task 3**: Implemented build script and templates.
  - Created `build.py` — Python static site generator using only stdlib.
  - Generates all HTML pages from JSON data.
  - Uses directory-based clean URLs (`work/entry-id/index.html`).
  - All paths use `/actualwork/` base path for GitHub Pages compatibility.

- **Task 4**: Built ActualWork homepage and global layout.
  - Homepage with motto: "Show us your work, not your coffee."
  - Explanation text, Explore/Submit links.
  - Recently Added section, Occupations listing, Industries listing.
  - Clean header with navigation, footer with policy links.
  - CSS: clean archive aesthetic — Source Serif/Source Sans fonts, neutral colors, simple borders, no effects.

- **Task 5**: Implemented Work Entry pages.
  - Individual entry pages with title, meta, video embed, problem, description, process, result, tools, tags, related entries.
  - YouTube privacy-enhanced embeds (youtube-nocookie.com).
  - Lazy-loading video iframes via IntersectionObserver.
  - Created 3 sample entries:
    - Django Unchained making-of (placeholder video)
    - Debugging a Data Pipeline (data engineering example)
    - Structural Load Analysis (structural engineering example)

- **Task 6**: Implemented discovery features.
  - Occupation listing and detail pages (e.g., `/actualwork/occupations/filmmaker/`).
  - Industry listing and detail pages.
  - Tool listing and detail pages.
  - Tag listing and detail pages.
  - Client-side search with JSON index (search across all fields).
  - Filter dropdowns: occupation, industry, tool, work type.

- **Task 7**: Implemented contribution and policy pages.
  - Show Your Work (submission instructions, email-based).
  - Contributor Guidelines.
  - Content & Submission Policy.
  - Terms of Use.
  - Privacy Policy.
  - Copyright & Takedown Policy.
  - Disclaimer.
  - Report / Remove Content.

## In Progress

Nothing — all implementation tasks complete.

## Next Steps

- **Task 8**: Verify GitHub Pages integration (paths, assets, base URL).
- **Task 9**: Full end-to-end testing.
- **Task 10**: Final review and documentation.

## Files Added

### Root
- `ACTUALWORK_PROGRESS.md` — this progress log

### `actualwork/`
- `README.md` — project documentation
- `build.py` — static site generator

### `actualwork/data/`
- `README.md` — data field documentation
- `occupations.json` — 5 occupations
- `industries.json` — 3 industries
- `tools.json` — 11 tools
- `tags.json` — 14 tags
- `entries/_TEMPLATE.json` — entry template
- `entries/django-unchained-making-of.json` — placeholder entry
- `entries/debugging-data-pipeline.json` — sample entry
- `entries/structural-load-analysis.json` — sample entry

### `actualwork/static/`
- `style.css` — stylesheet
- `main.js` — nav toggle + lazy video loading
- `search.js` — client-side search

### Generated HTML (output of build.py)
- `actualwork/index.html` — homepage
- `actualwork/work/*/index.html` — 3 entry pages
- `actualwork/occupations/index.html` + 5 individual pages
- `actualwork/industries/index.html` + 3 individual pages
- `actualwork/tools/index.html` + 11 individual pages
- `actualwork/tags/index.html` + 14 individual pages
- `actualwork/search/index.html`
- `actualwork/submit/index.html`
- `actualwork/terms/index.html`
- `actualwork/privacy/index.html`
- `actualwork/copyright/index.html`
- `actualwork/disclaimer/index.html`
- `actualwork/guidelines/index.html`
- `actualwork/content-policy/index.html`
- `actualwork/report/index.html`

## Existing Files Modified

> **No existing LuthenCorps files modified.**

Verified via `git status`: only `ACTUALWORK_PROGRESS.md` and `actualwork/` are new. All existing files remain unchanged.

## Decisions

1. **No framework**: ActualWork uses the same approach as LuthenCorps — pure static HTML/CSS/JS.
2. **Python build script**: stdlib-only Python script generates HTML from JSON. Satisfies the requirement that adding entries only requires JSON edits.
3. **Directory-based routing**: Clean URLs via `work/entry-id/index.html` structure, compatible with GitHub Pages.
4. **Complete isolation**: Everything ActualWork lives inside `actualwork/`. Zero coupling with LuthenCorps.
5. **Source Serif / Source Sans fonts**: Clean, readable typography that looks like an archive/reference site, not a SaaS product.
6. **Privacy-enhanced video embeds**: Using youtube-nocookie.com for YouTube embeds.
7. **Email-based submissions**: Simple, no-account submission process via email.
8. **3 sample entries**: Created multiple entries to demonstrate multi-entry features (filtering, search, related entries).

## Problems / Issues

- Browser-based visual testing not available (Playwright installation failed). Verified via curl and server logs that all pages serve with 200 status codes.
- No favicon for ActualWork (uses browser default). Not critical.

## Testing

- **Build**: `python build.py` runs successfully, generates 52+ HTML pages.
- **Local server**: All pages serve correctly at their expected URLs (verified via curl and HTTP server logs).
- **LuthenCorps protection**: `git status` confirms no existing files modified.
- **Path correctness**: All generated HTML uses `/actualwork/` base path for CSS, JS, and internal links.
- **JSON-driven content**: All 3 entries generated from JSON files with correct metadata.
