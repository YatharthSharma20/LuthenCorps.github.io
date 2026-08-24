# ActualWork — Data Directory

This directory contains all content for the ActualWork archive. JSON files here are the **source of truth** — the build script reads them and generates static HTML pages.

## Structure

```
data/
├── occupations.json    — list of occupations (id, name, description)
├── industries.json     — list of industries (id, name, description)
├── tools.json          — list of tools (id, name)
├── tags.json           — list of tags (id, name)
└── entries/
    ├── _TEMPLATE.json  — copy this to create a new Work Entry
    └── *.json          — individual Work Entries
```

## Adding a Work Entry

1. Copy `entries/_TEMPLATE.json` to `entries/your-entry-name.json`
2. Fill in the fields (leave fields blank or empty if not applicable)
3. Run `python build.py` from the `actualwork/` directory
4. Commit and push

## Field Reference

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Unique identifier, used in URLs. Use lowercase-with-dashes. |
| `title` | Yes | Display title of the entry. |
| `person` | No | Name of the person doing the work. |
| `occupation` | Yes | Must match an `id` in `occupations.json`. |
| `company` | No | Company name. |
| `industry` | No | Must match an `id` in `industries.json`. |
| `experience` | No | Years of experience or level. |
| `problem` | No | What problem they faced. |
| `description` | No | Brief description of what happened. |
| `process` | No | Array of strings — step by step what they did. |
| `result` | No | What was the outcome. |
| `video.platform` | Yes | Currently only `youtube`. |
| `video.url` | Yes | Full URL to the video. |
| `tools` | No | Array of tool IDs (must match `tools.json`). |
| `workTypes` | No | Array of work type strings. |
| `tags` | No | Array of tag IDs (must match `tags.json`). |
| `dateAdded` | No | Date the entry was added (YYYY-MM-DD). |

## Adding Occupations, Industries, Tools, or Tags

Edit the corresponding JSON file and add a new object. Then run `python build.py`.
