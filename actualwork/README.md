# ActualWork

**Show us your work, not your coffee.**

ActualWork is a free public archive of what people actually do at work — the problems they encounter, the tools they use, how they solve things, and what they actually produce.

Live at: `https://luthencorps.space/actualwork/`

## How It Works

ActualWork is a static site. Content lives in JSON files. A Python script generates static HTML pages from the JSON. The generated pages are deployed alongside the existing LuthenCorps website on GitHub Pages.

```
Edit JSON → Run build.py → Static HTML generated → Commit & push → GitHub Pages deploys
```

## Adding a Work Entry

1. Copy `data/entries/_TEMPLATE.json` to `data/entries/your-entry-name.json`
2. Fill in the fields (leave blank any that don't apply)
3. Run `python build.py` from the `actualwork/` directory
4. Commit and push

That's it. No source code changes needed.

## Editing a Work Entry

1. Open the entry's JSON file in `data/entries/`
2. Edit the fields
3. Run `python build.py`
4. Commit and push

## Removing a Work Entry

1. Delete the entry's JSON file from `data/entries/`
2. Run `python build.py`
3. Commit and push

## Adding an Occupation / Industry / Tool / Tag

1. Open the corresponding JSON file in `data/` (e.g., `occupations.json`)
2. Add a new object with `id`, `name`, and optionally `description`
3. Run `python build.py`
4. Commit and push

## Changing a Video

1. Open the entry's JSON file
2. Update the `video.url` field with the new URL
3. Run `python build.py`
4. Commit and push

## Building

Requirements: Python 3 (no external dependencies)

```bash
cd actualwork/
python build.py
```

This generates all HTML pages in the `actualwork/` directory.

## Deployment

The site is deployed via GitHub Pages. The existing GitHub Actions workflow (`static.yml`) deploys the entire repository root. Since `actualwork/` is a subdirectory of the root, it is automatically included.

- LuthenCorps: `https://luthencorps.space/`
- ActualWork: `https://luthencorps.space/actualwork/`

No changes to the deployment workflow are needed.

## Directory Structure

```
actualwork/
├── README.md           ← this file
├── build.py            ← static site generator
├── data/
│   ├── README.md       ← data documentation
│   ├── occupations.json
│   ├── industries.json
│   ├── tools.json
│   ├── tags.json
│   └── entries/
│       ├── _TEMPLATE.json
│       └── *.json      ← individual work entries
├── static/
│   ├── style.css
│   ├── main.js
│   └── search.js
└── [generated HTML]    ← output of build.py
    ├── index.html
    ├── work/*/index.html
    ├── occupations/*/index.html
    ├── industries/*/index.html
    ├── tools/*/index.html
    ├── tags/*/index.html
    ├── search/index.html
    ├── submit/index.html
    └── [policy pages]/index.html
```

## JSON Field Reference

See `data/README.md` for full documentation of all JSON fields.
