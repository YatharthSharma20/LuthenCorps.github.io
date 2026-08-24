#!/usr/bin/env python3
"""
ActualWork — Static Site Generator

Reads JSON data from data/ and generates static HTML pages.
No external dependencies — uses only Python standard library.

Usage:
    cd actualwork/
    python build.py

Output:
    Generates HTML files in the actualwork/ directory, including:
    - index.html (homepage)
    - work/<entry-id>/index.html (individual entries)
    - occupations/index.html (occupation listing)
    - occupations/<id>/index.html (individual occupation)
    - industries/index.html
    - industries/<id>/index.html
    - tools/index.html
    - tools/<id>/index.html
    - tags/index.html
    - tags/<id>/index.html
    - search/index.html
    - submit/index.html
    - terms/index.html
    - privacy/index.html
    - copyright/index.html
    - disclaimer/index.html
    - guidelines/index.html
    - report/index.html
    - content-policy/index.html
"""

import json
import os
import re
import html as html_module
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
STATIC_DIR = os.path.join(SCRIPT_DIR, 'static')
BASE_PATH = '/actualwork'


# ============================================================
# Data Loading
# ============================================================

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_entries():
    entries_dir = os.path.join(DATA_DIR, 'entries')
    entries = []
    for fname in os.listdir(entries_dir):
        if fname.startswith('_') or not fname.endswith('.json'):
            continue
        with open(os.path.join(entries_dir, fname), 'r', encoding='utf-8') as f:
            entry = json.load(f)
            entries.append(entry)
    # Sort by dateAdded descending, then by title
    entries.sort(key=lambda e: (e.get('dateAdded', ''), e.get('title', '')), reverse=True)
    return entries


def build_lookup(items):
    return {item['id']: item for item in items}


# ============================================================
# HTML Helpers
# ============================================================

def esc(text):
    """Escape HTML."""
    if text is None:
        return ''
    return html_module.escape(str(text))


def description_to_text(desc):
    """Convert a description (string or list) to a flat text string."""
    if desc is None:
        return ''
    if isinstance(desc, list):
        return ' '.join(str(item) for item in desc)
    return str(desc)


def slugify(text):
    """Convert a display name or slug string to a URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


def slug_to_name(slug):
    """Convert a slug like 'some-thing' to display name 'Some Thing'."""
    return slug.replace('-', ' ').title()


def auto_discover_entities(entries, occupations, industries, tools, tags):
    """Scan entries and auto-discover any entities not in the master lists.

    Returns updated copies of (occupations, industries, tools, tags, work_types).
    """
    occ_lookup = {o['id'] for o in occupations}
    ind_lookup = {i['id'] for i in industries}
    tool_lookup = {t['id'] for t in tools}
    tag_lookup = {t['id'] for t in tags}

    new_occupations = list(occupations)
    new_industries = list(industries)
    new_tools = list(tools)
    new_tags = list(tags)
    work_type_set = set()

    for entry in entries:
        # Occupations
        occ_id = entry.get('occupation', '')
        if occ_id and occ_id not in occ_lookup:
            new_occupations.append({
                'id': occ_id,
                'name': slug_to_name(occ_id),
                'description': ''
            })
            occ_lookup.add(occ_id)

        # Industries
        ind_id = entry.get('industry', '')
        if ind_id and ind_id not in ind_lookup:
            new_industries.append({
                'id': ind_id,
                'name': slug_to_name(ind_id),
                'description': ''
            })
            ind_lookup.add(ind_id)

        # Tools — entries may use display names or slugs
        for tool_ref in entry.get('tools', []):
            tool_slug = slugify(tool_ref)
            if tool_slug not in tool_lookup:
                new_tools.append({
                    'id': tool_slug,
                    'name': tool_ref  # preserve original display name
                })
                tool_lookup.add(tool_slug)

        # Tags — entries may use display names or slugs
        for tag_ref in entry.get('tags', []):
            tag_slug = slugify(tag_ref)
            if tag_slug not in tag_lookup:
                new_tags.append({
                    'id': tag_slug,
                    'name': tag_ref
                })
                tag_lookup.add(tag_slug)

        # Work types
        for wt in entry.get('workTypes', []):
            work_type_set.add(wt)

    # Build work type objects
    work_types = sorted([{'id': wt, 'name': slug_to_name(wt)} for wt in work_type_set],
                        key=lambda x: x['name'])

    return new_occupations, new_industries, new_tools, new_tags, work_types


def youtube_embed_url(video_url):
    """Convert YouTube URL to embed URL."""
    # Handle youtu.be/ID
    m = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', video_url)
    if m:
        return 'https://www.youtube-nocookie.com/embed/' + m.group(1)
    # Handle youtube.com/watch?v=ID
    m = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', video_url)
    if m:
        return 'https://www.youtube-nocookie.com/embed/' + m.group(1)
    return video_url


def youtube_thumb_url(video_url):
    """Get YouTube thumbnail URL."""
    m = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', video_url)
    if not m:
        m = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', video_url)
    if m:
        return 'https://img.youtube.com/vi/' + m.group(1) + '/hqdefault.jpg'
    return ''


def make_url(path):
    """Create a URL relative to the base path."""
    return BASE_PATH + '/' + path.lstrip('/')


# ============================================================
# Template Parts
# ============================================================

def render_head(title, description=''):
    desc_meta = ''
    if description:
        desc_meta = f'<meta name="description" content="{esc(description)}">'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{desc_meta}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600&family=Source+Serif+4:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{make_url('static/style.css')}">
</head>
<body>
'''


def render_header():
    return f'''<header class="site-header">
<div class="site-container">
<a href="{make_url('/')}" class="site-title">ActualWork</a>
<button class="nav-toggle" aria-expanded="false" aria-controls="main-nav">Menu</button>
<nav class="site-nav" id="main-nav" aria-label="Main navigation">
<a href="{make_url('/')}">Home</a>
<a href="{make_url('occupations/')}">Occupations</a>
<a href="{make_url('industries/')}">Industries</a>
<a href="{make_url('tools/')}">Tools</a>
<a href="{make_url('search/')}">Search</a>
<a href="{make_url('submit/')}">Submit</a>
<a href="{make_url('builder/')}">Builder</a>
</nav>
</div>
</header>
'''


def render_footer():
    return f'''<footer class="site-footer">
<div class="site-container">
<div class="footer-links">
<a href="{make_url('/')}">Home</a>
<a href="{make_url('search/')}">Search</a>
<a href="{make_url('submit/')}">Submit</a>
<a href="{make_url('builder/')}">Builder</a>
<a href="{make_url('guidelines/')}">Contributor Guidelines</a>
<a href="{make_url('content-policy/')}">Content Policy</a>
<a href="{make_url('terms/')}">Terms of Use</a>
<a href="{make_url('privacy/')}">Privacy Policy</a>
<a href="{make_url('copyright/')}">Copyright &amp; Takedown</a>
<a href="{make_url('disclaimer/')}">Disclaimer</a>
<a href="{make_url('report/')}">Report Content</a>
</div>
<p>ActualWork is a public archive of what people actually do at work.</p>
</div>
</footer>
<script src="{make_url('static/main.js')}"></script>
</body>
</html>
'''


def render_entry_card(entry, occupations_lookup, show_description=True):
    """Render a single entry as a list item."""
    occ = occupations_lookup.get(entry.get('occupation', ''), {})
    occ_name = occ.get('name', '')
    person = entry.get('person', '')
    company = entry.get('company', '')

    meta_parts = []
    if person:
        meta_parts.append(f'<span>{esc(person)}</span>')
    if occ_name:
        meta_parts.append(f'<span><a href="{make_url("occupations/" + esc(entry["occupation"]) + "/")}">{esc(occ_name)}</a></span>')
    if company:
        meta_parts.append(f'<span>{esc(company)}</span>')

    meta_html = ''
    if meta_parts:
        meta_html = f'<div class="entry-meta">{"".join(meta_parts)}</div>'

    desc_html = ''
    if show_description and entry.get('description'):
        desc = description_to_text(entry['description'])
        if len(desc) > 200:
            desc = desc[:200] + '…'
        desc_html = f'<div class="entry-description">{esc(desc)}</div>'

    return f'''<li class="entry-item">
<div class="entry-title"><a href="{make_url("work/" + esc(entry["id"]) + "/")}">{esc(entry["title"])}</a></div>
{meta_html}
{desc_html}
</li>'''


def render_entry_list(entries, occupations_lookup, show_description=True):
    if not entries:
        return '<p>No entries yet.</p>'
    items = [render_entry_card(e, occupations_lookup, show_description) for e in entries]
    return '<ul class="entry-list">' + '\n'.join(items) + '</ul>'


# ============================================================
# Page Generators
# ============================================================

def generate_homepage(entries, occupations, industries, occupations_lookup):
    title = 'ActualWork — Show us your work, not your coffee.'
    desc = 'A public archive of what people actually do at work — the problems they encounter, the tools they use, how they solve things, and what they produce.'

    # Count entries per occupation
    occ_counts = {}
    for e in entries:
        occ = e.get('occupation', '')
        if occ:
            occ_counts[occ] = occ_counts.get(occ, 0) + 1

    # Count entries per industry
    ind_counts = {}
    for e in entries:
        ind = e.get('industry', '')
        if ind:
            ind_counts[ind] = ind_counts.get(ind, 0) + 1

    popular_occ_html = ''
    if occupations:
        sorted_occs = [o for o in occupations if occ_counts.get(o['id'], 0) > 0]
        sorted_occs.sort(key=lambda o: occ_counts.get(o['id'], 0), reverse=True)
        top_occs = sorted_occs[:5]
        if top_occs:
            items = []
            for o in top_occs:
                count = occ_counts.get(o['id'], 0)
                items.append(f'<li class="category-item"><a href="{make_url("occupations/" + esc(o["id"]) + "/")}">{esc(o["name"])}</a> <span class="count">({count})</span></li>')
            popular_occ_html = f'''<h2 class="section-heading">Top Occupations</h2>
<ul class="category-list">{"".join(items)}</ul>'''

    popular_ind_html = ''
    if industries:
        sorted_inds = [i for i in industries if ind_counts.get(i['id'], 0) > 0]
        sorted_inds.sort(key=lambda i: ind_counts.get(i['id'], 0), reverse=True)
        top_inds = sorted_inds[:3]
        if top_inds:
            items = []
            for i in top_inds:
                count = ind_counts.get(i['id'], 0)
                items.append(f'<li class="category-item"><a href="{make_url("industries/" + esc(i["id"]) + "/")}">{esc(i["name"])}</a> <span class="count">({count})</span></li>')
            popular_ind_html = f'''<h2 class="section-heading">Top Industries</h2>
<ul class="category-list">{"".join(items)}</ul>'''

    recent_html = ''
    if entries:
        recent = entries[:5]
        recent_html = f'''<h2 class="section-heading">Recently Added</h2>
{render_entry_list(recent, occupations_lookup)}'''

    return (render_head(title, desc)
            + render_header()
            + f'''<main class="site-container">
<div class="hero">
<h1 class="hero-motto">Show us your work, not your coffee.</h1>
<p class="hero-description">ActualWork is a public archive of what people actually do at work — the problems they encounter, the tools they use, how they solve things, and what they actually produce.</p>
<p class="hero-description">Not "day in my life" content. Not corporate jargon. The actual work.</p>
<div class="hero-actions">
<a href="{make_url('search/')}">Explore ActualWork</a>
<a href="{make_url('submit/')}">Show Your Work</a>
</div>
</div>
<hr>
{recent_html}
{popular_ind_html}
{popular_occ_html}
</main>
'''
            + render_footer())


def generate_entry_page(entry, occupations_lookup, industries_lookup, tools_lookup, tags_lookup, all_entries):
    occ = occupations_lookup.get(entry.get('occupation', ''), {})
    ind = industries_lookup.get(entry.get('industry', ''), {})
    occ_name = occ.get('name', '')
    ind_name = ind.get('name', '')
    person = entry.get('person', '')
    company = entry.get('company', '')
    experience = entry.get('experience', '')

    title = entry['title'] + ' — ActualWork'
    desc = description_to_text(entry.get('description', '')) or entry.get('problem', '')
    if len(desc) > 160:
        desc = desc[:157] + '...'

    # Meta section
    meta_parts = []
    if person:
        meta_parts.append(f'<span>{esc(person)}</span>')
    if occ_name:
        meta_parts.append(f'<span><a href="{make_url("occupations/" + esc(entry["occupation"]) + "/")}">{esc(occ_name)}</a></span>')
    if company:
        meta_parts.append(f'<span>{esc(company)}</span>')
    if ind_name:
        meta_parts.append(f'<span><a href="{make_url("industries/" + esc(entry["industry"]) + "/")}">{esc(ind_name)}</a></span>')
    if experience:
        meta_parts.append(f'<span>{esc(experience)} experience</span>')

    meta_html = ''
    if meta_parts:
        meta_html = f'<div class="entry-page-meta">{"".join(meta_parts)}</div>'

    # Video
    video_html = ''
    video = entry.get('video', {})
    if video.get('url'):
        embed_url = youtube_embed_url(video['url'])
        video_html = f'''<div class="video-container video-lazy" data-src="{esc(embed_url)}" data-title="{esc(entry["title"])}">
<noscript><iframe src="{esc(embed_url)}" title="{esc(entry["title"])}" allowfullscreen></iframe></noscript>
<p style="text-align:center; padding: 2em; color: #888;">Loading video…</p>
</div>'''

    # Problem
    problem_html = ''
    if entry.get('problem'):
        problem_html = f'''<div class="entry-section">
<h2>The Objective</h2>
<p>{esc(entry["problem"])}</p>
</div>'''

    # Description
    desc_html = ''
    if entry.get('description'):
        raw_desc = entry['description']
        if isinstance(raw_desc, list):
            desc_items = ''.join(f'<li>{esc(item)}</li>' for item in raw_desc)
            desc_body = f'<ul class="description-list">{desc_items}</ul>'
        else:
            desc_body = f'<p>{esc(raw_desc)}</p>'
        context_body = ''
        if entry.get('context'):
            context_body = f'<p class="entry-context" style="color: #666; font-style: italic; margin-bottom: 1em;">{esc(entry["context"])}</p>'

        desc_html = f'''<div class="entry-section">
<h2>What Happened</h2>
{context_body}
{desc_body}
</div>'''

    # Process
    process_html = ''
    if entry.get('process'):
        steps = ''.join(f'<li>{esc(step)}</li>' for step in entry['process'])
        process_html = f'''<div class="entry-section">
<h2>The Actual Work</h2>
<ol class="process-list">{steps}</ol>
</div>'''

    # Result
    result_html = ''
    if entry.get('result'):
        result_html = f'''<div class="entry-section">
<h2>Conclusion</h2>
<p>{esc(entry["result"])}</p>
</div>'''

    # Tools
    tools_html = ''
    if entry.get('tools'):
        tool_items = []
        for tid in entry['tools']:
            tool_slug = slugify(tid)
            tool = tools_lookup.get(tool_slug, {})
            name = tool.get('name', tid)
            tool_items.append(f'<li><a href="{make_url("tools/" + esc(tool_slug) + "/")}">{esc(name)}</a></li>')
        tools_html = f'''<div class="entry-section">
<h2>Tools Used</h2>
<ul class="tag-list">{"".join(tool_items)}</ul>
</div>'''

    # Tags
    tags_html = ''
    if entry.get('tags'):
        tag_items = []
        for tid in entry['tags']:
            tag_slug = slugify(tid)
            tag = tags_lookup.get(tag_slug, {})
            name = tag.get('name', tid)
            tag_items.append(f'<li><a href="{make_url("tags/" + esc(tag_slug) + "/")}">{esc(name)}</a></li>')
        tags_html = f'''<div class="entry-section">
<h2>Tags</h2>
<ul class="tag-list">{"".join(tag_items)}</ul>
</div>'''

    # Work types
    wt_html = ''
    if entry.get('workTypes'):
        wt_items = []
        for wt in entry['workTypes']:
            label = wt.replace('-', ' ').title()
            wt_items.append(f'<li><a href="{make_url("work-types/" + esc(wt) + "/")}">{esc(label)}</a></li>')
        wt_html = f'''<div class="entry-section">
<h2>Type of Work</h2>
<ul class="tag-list">{"".join(wt_items)}</ul>
</div>'''

    # Original video link
    source_html = ''
    if video.get('url'):
        source_html = f'''<div class="entry-section">
<h2>Original Video</h2>
<p><a href="{esc(video["url"])}" target="_blank" rel="noopener noreferrer">Watch on {esc(video.get("platform", "the original platform").title())}</a></p>
</div>'''

    # Related entries (same occupation or tags)
    related_html = ''
    related = [e for e in all_entries
               if e['id'] != entry['id']
               and (e.get('occupation') == entry.get('occupation')
                    or bool(set(e.get('tags', [])) & set(entry.get('tags', []))))]
    if related:
        related = related[:5]
        items = [render_entry_card(e, occupations_lookup, show_description=False) for e in related]
        related_html = f'''<div class="related-section">
<h2>Related Work</h2>
<ul class="entry-list">{"".join(items)}</ul>
</div>'''

    # Report link
    report_html = f'''<div class="entry-section" style="margin-top: 2rem; font-size: 0.85rem;">
<a href="{make_url('report/')}" style="color: #888;">Report or request removal of this content</a>
</div>'''

    return (render_head(title, desc)
            + render_header()
            + f'''<main class="site-container">
<div class="entry-page-header">
<h1 class="entry-page-title">{esc(entry["title"])}</h1>
{meta_html}
</div>
{video_html}
{problem_html}
{desc_html}
{process_html}
{result_html}
{tools_html}
{wt_html}
{tags_html}
{source_html}
{report_html}
{related_html}
</main>
'''
            + render_footer())


def generate_occupation_page(occ, entries, occupations_lookup):
    filtered = [e for e in entries if e.get('occupation') == occ['id']]
    title = f'What does a {occ["name"]} actually do? — ActualWork'
    desc = occ.get('description', '')

    desc_html = ''
    if desc:
        desc_html = f'<p class="browse-description">{esc(desc)}</p>'

    return (render_head(title, desc)
            + render_header()
            + f'''<main class="site-container browse-page">
<h1>What does a {esc(occ["name"])} actually do?</h1>
{desc_html}
{render_entry_list(filtered, occupations_lookup)}
</main>
'''
            + render_footer())


def generate_listing_page(title_text, description, items, entries, occupations_lookup, url_prefix, count_fn):
    title = f'{title_text} — ActualWork'
    item_list = []
    for item in items:
        count = count_fn(item['id'])
        count_str = f' <span class="count">({count})</span>' if count > 0 else ''
        desc_html = ''
        if item.get('description'):
            desc_html = f'<div class="category-description">{esc(item["description"])}</div>'
        item_list.append(f'<li class="category-item"><a href="{make_url(url_prefix + esc(item["id"]) + "/")}">{esc(item["name"])}</a>{count_str}{desc_html}</li>')

    return (render_head(title, description)
            + render_header()
            + f'''<main class="site-container browse-page">
<h1>{esc(title_text)}</h1>
<p class="browse-description">{esc(description)}</p>
<ul class="category-list">{"".join(item_list)}</ul>
</main>
'''
            + render_footer())


def generate_category_detail_page(item, entries, occupations_lookup, filter_fn, category_label):
    filtered = [e for e in entries if filter_fn(e, item['id'])]
    title = f'{item["name"]} — {category_label} — ActualWork'
    desc = item.get('description', '')

    desc_html = ''
    if desc:
        desc_html = f'<p class="browse-description">{esc(desc)}</p>'

    return (render_head(title, desc)
            + render_header()
            + f'''<main class="site-container browse-page">
<h1>{esc(item["name"])}</h1>
{desc_html}
<h2 class="section-heading">Work Entries</h2>
{render_entry_list(filtered, occupations_lookup)}
</main>
'''
            + render_footer())


def generate_search_page(entries, occupations, industries, tools, occupations_lookup, tools_lookup, tags_lookup):
    title = 'Search — ActualWork'
    desc = 'Search the ActualWork archive.'

    # Build search index
    search_entries = []
    for entry in entries:
        occ = occupations_lookup.get(entry.get('occupation', ''), {})
        tool_names = [tools_lookup.get(slugify(t), {}).get('name', t) for t in entry.get('tools', [])]
        tag_names = [tags_lookup.get(slugify(t), {}).get('name', t) for t in entry.get('tags', [])]
        search_text = ' '.join([
            entry.get('title', ''),
            entry.get('person', ''),
            occ.get('name', ''),
            entry.get('company', ''),
            entry.get('industry', ''),
            entry.get('problem', ''),
            description_to_text(entry.get('description', '')),
            ' '.join(tool_names),
            ' '.join(tag_names),
            ' '.join(entry.get('workTypes', []))
        ]).lower()

        search_entries.append({
            'id': entry['id'],
            'title': entry['title'],
            'url': make_url('work/' + entry['id'] + '/'),
            'personName': entry.get('person', ''),
            'occupation': entry.get('occupation', ''),
            'occupationName': occ.get('name', ''),
            'companyName': entry.get('company', ''),
            'industry': entry.get('industry', ''),
            'description': description_to_text(entry.get('description', '')),
            'tools': entry.get('tools', []),
            'workTypes': entry.get('workTypes', []),
            'searchText': search_text
        })

    search_index_json = json.dumps(search_entries)

    # Build filter options
    occ_options = ''.join(f'<option value="{esc(o["id"])}">{esc(o["name"])}</option>' for o in occupations)
    ind_options = ''.join(f'<option value="{esc(i["id"])}">{esc(i["name"])}</option>' for i in industries)
    tool_options = ''.join(f'<option value="{esc(t["id"])}">{esc(t["name"])}</option>' for t in tools)

    # Collect unique work types
    work_types = set()
    for e in entries:
        for wt in e.get('workTypes', []):
            work_types.add(wt)
    work_types = sorted(work_types)
    wt_options = ''.join(f'<option value="{esc(wt)}">{esc(wt.replace("-", " ").title())}</option>' for wt in work_types)

    return (render_head(title, desc)
            + render_header()
            + f'''<main class="site-container browse-page">
<h1>Search</h1>
<div class="search-container">
<label for="aw-search-input" class="sr-only">Search entries</label>
<input type="search" id="aw-search-input" class="search-input" placeholder="Search entries…" autocomplete="off">
<p class="search-info" id="aw-search-info"></p>
</div>
<div class="filter-bar">
<label>Filter:</label>
<select data-filter="occupation" aria-label="Filter by occupation">
<option value="">All occupations</option>
{occ_options}
</select>
<select data-filter="industry" aria-label="Filter by industry">
<option value="">All industries</option>
{ind_options}
</select>
<select data-filter="tool" aria-label="Filter by tool">
<option value="">All tools</option>
{tool_options}
</select>
<select data-filter="workType" aria-label="Filter by work type">
<option value="">All work types</option>
{wt_options}
</select>
</div>
<div id="aw-search-results" class="search-results"></div>
<script>window.ACTUALWORK_SEARCH_INDEX = {search_index_json};</script>
<script src="{make_url('static/search.js')}"></script>
</main>
'''
            + render_footer())


def generate_submit_page():
    title = 'Show Your Work — ActualWork'
    desc = 'Submit a link to a work-related video for the ActualWork archive.'

    return (render_head(title, desc)
            + render_header()
            + f'''<main class="site-container submit-page">
<h1>Show Your Work</h1>
<p>ActualWork is a curated archive. We collect videos where people show what they actually do at their jobs — the real problems, the real tools, the real process.</p>

<h2>What we're looking for</h2>
<p>Videos that show actual professional work. Not "day in my life" vlogs focused on coffee and commutes. Not motivational career advice. Small details about your day or environment are welcome as context, but the focus must remain on the actual work:</p>
<ul>
<li>What problem did you face?</li>
<li>What tools did you use?</li>
<li>What steps did you take?</li>
<li>What went wrong?</li>
<li>How did you fix it?</li>
<li>What was the conclusion?</li>
</ul>

<h2>How to submit</h2>
<ol class="submit-steps">
<li>You have a video published on YouTube (or another public platform) that shows real professional work.</li>
<li>Send the link by email to <strong>actualwork@luthencorps.space</strong> with the subject line <strong>"ActualWork Submission"</strong>.</li>
<li>Include: your name (or alias), your job title, and a brief description of what the video shows.</li>
<li>We review all submissions manually. If accepted, we create an entry that links back to your original video.</li>
</ol>

<h2>What happens next</h2>
<p>ActualWork does not host your video. We embed it from the original platform. You remain the creator and host. The entry on ActualWork links to your video and describes the work shown.</p>
<p>If you want your entry updated or removed, email us and we will handle it promptly.</p>

<h2>Guidelines</h2>
<p>Please review our <a href="{make_url('guidelines/')}">Contributor Guidelines</a> and <a href="{make_url('content-policy/')}">Content &amp; Submission Policy</a> before submitting.</p>
</main>
'''
            + render_footer())


def generate_policy_page(slug, heading, content_html):
    title = f'{heading} — ActualWork'
    return (render_head(title)
            + render_header()
            + f'''<main class="site-container policy-page">
<h1>{esc(heading)}</h1>
<p class="last-updated">Last updated: August 2026</p>
{content_html}
</main>
'''
            + render_footer())


def generate_builder_page():
    title = 'JSON Builder — ActualWork'
    desc = 'Create and preview JSON entries for the ActualWork archive.'
    
    html = f'''<main class="site-container builder-page" style="max-width: 1200px;">
<h1>JSON Entry Builder</h1>
<p>Use this tool to easily format an ActualWork JSON entry. Fill out the fields on the left and the raw JSON will update on the right.</p>

<div class="builder-layout" style="display: flex; flex-wrap: wrap; gap: 2rem; margin-top: 2rem;">
    <!-- Form Side -->
    <div class="builder-form" style="flex: 1; min-width: 300px; max-width: 600px;">
        <form id="jsonForm">
            <div class="form-group">
                <label>ID (Filename)</label>
                <input type="text" id="field_id" placeholder="e.g. software-engineer-day" class="form-control">
                <small>Auto-generated from title if left blank</small>
            </div>
            <div class="form-group">
                <label>Title *</label>
                <input type="text" id="field_title" required class="form-control">
            </div>
            <div class="form-group">
                <label>Person (Optional)</label>
                <input type="text" id="field_person" class="form-control">
            </div>
            <div class="form-group">
                <label>Occupation *</label>
                <input type="text" id="field_occupation" placeholder="e.g. software-engineer" required class="form-control">
            </div>
            <div class="form-group">
                <label>Company (Optional)</label>
                <input type="text" id="field_company" class="form-control">
            </div>
            <div class="form-group">
                <label>Industry *</label>
                <input type="text" id="field_industry" placeholder="e.g. technology" required class="form-control">
            </div>
            <div class="form-group">
                <label>Experience (Optional)</label>
                <input type="text" id="field_experience" placeholder="e.g. 5 years" class="form-control">
            </div>
            <div class="form-group">
                <label>Video Platform *</label>
                <select id="field_platform" class="form-control">
                    <option value="youtube">youtube</option>
                </select>
            </div>
            <div class="form-group">
                <label>Video URL *</label>
                <input type="url" id="field_video_url" placeholder="https://youtube.com/watch?v=..." required class="form-control">
            </div>
            
            <hr style="margin: 2rem 0;">
            
            <div class="form-group">
                <label>Problem *</label>
                <input type="text" id="field_problem" placeholder="What problem did they face?" required class="form-control">
            </div>
            <div class="form-group">
                <label>Context (Optional)</label>
                <textarea id="field_context" placeholder="Optional context about their work day or environment" rows="2" class="form-control"></textarea>
            </div>
            <div class="form-group">
                <label>Description (Optional, multi-line allowed)</label>
                <textarea id="field_description" placeholder="Brief description of what happened. One line per item to create a list." rows="3" class="form-control"></textarea>
            </div>
            
            <div class="form-group">
                <label>Process * (One step per line)</label>
                <textarea id="field_process" placeholder="Step 1: ...&#10;Step 2: ..." rows="6" required class="form-control"></textarea>
            </div>
            <div class="form-group">
                <label>Conclusion (Optional)</label>
                <textarea id="field_conclusion" placeholder="What was the outcome?" rows="3" class="form-control"></textarea>
            </div>
            
            <hr style="margin: 2rem 0;">
            
            <div class="form-group">
                <label>Tools (Comma separated)</label>
                <input type="text" id="field_tools" placeholder="python, sql, aws" class="form-control">
            </div>
            <div class="form-group">
                <label>Tags (Comma separated)</label>
                <input type="text" id="field_tags" placeholder="debugging, on-call, data" class="form-control">
            </div>
            <div class="form-group">
                <label>Work Types (Comma separated)</label>
                <input type="text" id="field_workTypes" placeholder="debugging, analysis" class="form-control">
            </div>
        </form>
    </div>
    
    <!-- Preview Side -->
    <div class="builder-preview" style="flex: 1; display: flex; flex-direction: column; min-width: 300px;">
        <div class="preview-actions" style="margin-bottom: 1rem; display: flex; gap: 1rem;">
            <button id="btn_copy" class="btn">Copy JSON</button>
            <button id="btn_download" class="btn">Download File</button>
        </div>
        <pre id="json_output" style="background: #1e1e1e; color: #d4d4d4; padding: 1rem; border-radius: 4px; overflow-x: auto; flex: 1; margin: 0; min-height: 500px;">{{}}</pre>
    </div>
</div>

<script>
function slugify(text) {{
    return text.toString().toLowerCase()
        .replace(/\\s+/g, '-')
        .replace(/[^\\w\\-]+/g, '')
        .replace(/\\-\\-+/g, '-')
        .replace(/^-+/, '')
        .replace(/-+$/, '');
}}

function splitLines(text) {{
    return text.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
}}

function splitComma(text) {{
    return text.split(',').map(l => l.trim()).filter(l => l.length > 0);
}}

function updateJson() {{
    const idField = document.getElementById('field_id').value.trim();
    const title = document.getElementById('field_title').value.trim();
    
    const id = idField || (title ? slugify(title) : '');
    
    const data = {{
        id: id,
        title: title,
        person: document.getElementById('field_person').value.trim(),
        occupation: document.getElementById('field_occupation').value.trim(),
        company: document.getElementById('field_company').value.trim(),
        industry: document.getElementById('field_industry').value.trim(),
        experience: document.getElementById('field_experience').value.trim(),
        video: {{
            platform: document.getElementById('field_platform').value,
            url: document.getElementById('field_video_url').value.trim()
        }},
        problem: document.getElementById('field_problem').value.trim(),
        context: document.getElementById('field_context').value.trim()
    }};
    
    const descLines = splitLines(document.getElementById('field_description').value);
    if (descLines.length === 1) {{
        data.description = descLines[0];
    }} else if (descLines.length > 1) {{
        data.description = descLines;
    }} else {{
        data.description = "";
    }}
    
    data.process = splitLines(document.getElementById('field_process').value);
    
    const conclusion = document.getElementById('field_conclusion').value.trim();
    if (conclusion) {{
        data.result = conclusion;
    }} else {{
        data.result = "";
    }}
    
    data.tools = splitComma(document.getElementById('field_tools').value);
    data.tags = splitComma(document.getElementById('field_tags').value);
    data.workTypes = splitComma(document.getElementById('field_workTypes').value);
    
    const jsonString = JSON.stringify(data, null, 2);
    document.getElementById('json_output').textContent = jsonString;
    return {{ jsonString, id }};
}}

document.getElementById('jsonForm').addEventListener('input', updateJson);

document.getElementById('btn_copy').addEventListener('click', () => {{
    const {{ jsonString }} = updateJson();
    navigator.clipboard.writeText(jsonString).then(() => {{
        const btn = document.getElementById('btn_copy');
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = 'Copy JSON', 2000);
    }});
}});

document.getElementById('btn_download').addEventListener('click', () => {{
    const {{ jsonString, id }} = updateJson();
    const filename = (id || 'entry') + '.json';
    const blob = new Blob([jsonString], {{ type: 'application/json' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}});

// Initialize
updateJson();
</script>
<style>
.form-group {{ margin-bottom: 1rem; }}
.form-group label {{ display: block; margin-bottom: 0.25rem; font-weight: 600; color: var(--color-text); font-size: 0.9rem; }}
.form-control {{ width: 100%; padding: 0.5rem; border: 1px solid var(--color-border); border-radius: 4px; font-family: inherit; font-size: 1rem; background: var(--color-bg); color: var(--color-text); box-sizing: border-box; }}
.form-control:focus {{ outline: 2px solid var(--color-primary); border-color: transparent; }}
.form-group small {{ color: #666; font-size: 0.8rem; display: block; margin-top: 0.25rem; }}
.btn {{ padding: 0.5rem 1rem; border: none; border-radius: 4px; background: #e5e7eb; color: #374151; cursor: pointer; font-family: inherit; font-size: 1rem; font-weight: 600; transition: background 0.2s; }}
.btn:hover {{ background: #d1d5db; }}
</style>
</main>'''

    return (render_head(title, desc)
            + render_header()
            + html
            + render_footer())


# ============================================================
# Policy Page Contents
# ============================================================

TERMS_CONTENT = '''
<h2>About ActualWork</h2>
<p>ActualWork is a free, public archive of professional work. The site curates and links to videos published by professionals on external platforms.</p>

<h2>Use of the Site</h2>
<p>You may browse, search, and share content on ActualWork freely. The site is provided as-is for informational and educational purposes.</p>

<h2>Content</h2>
<p>Work entries on ActualWork consist of metadata (descriptions, tags, tools) and embedded videos hosted on external platforms. ActualWork does not host the videos. The embedded videos remain the property of their original creators.</p>

<h2>Accuracy</h2>
<p>We make reasonable efforts to ensure that descriptions accurately reflect the content of linked videos, but we do not guarantee the accuracy, completeness, or timeliness of any information on the site.</p>

<h2>User Conduct</h2>
<p>Do not use ActualWork to distribute spam, malware, or any content that violates applicable law.</p>

<h2>Changes</h2>
<p>We may update these terms at any time. Continued use of the site constitutes acceptance of the current terms.</p>
'''

PRIVACY_CONTENT = '''
<h2>What We Collect</h2>
<p>ActualWork is a static website. We do not use cookies, tracking scripts, or analytics. We do not collect personal data from visitors.</p>

<h2>Embedded Videos</h2>
<p>We embed videos from third-party platforms (such as YouTube). These platforms may set their own cookies and collect data according to their own privacy policies. We use privacy-enhanced embedding modes where available (e.g., youtube-nocookie.com).</p>

<h2>Submissions</h2>
<p>If you submit a video link via email, we receive your email address and the information you include. We use this only to review your submission and contact you if needed. We do not share your email with third parties.</p>

<h2>Hosting</h2>
<p>The site is hosted on GitHub Pages. GitHub may collect server logs (IP addresses, request data) according to their own privacy statement.</p>
'''

COPYRIGHT_CONTENT = f'''
<h2>Copyright &amp; Content Ownership</h2>
<p>Videos linked on ActualWork are hosted on their original platforms and remain the intellectual property of their creators. ActualWork embeds these videos and provides descriptive metadata.</p>

<h2>Takedown Requests</h2>
<p>If you are the creator or rights holder of a video linked on ActualWork and want the entry removed, please contact us:</p>
<p>Email: <strong>actualwork@luthencorps.space</strong></p>
<p>Subject: <strong>Takedown Request</strong></p>
<p>Include:</p>
<ul>
<li>The URL of the ActualWork entry</li>
<li>The URL of the original video</li>
<li>Your relationship to the content (creator, rights holder, etc.)</li>
</ul>
<p>We will process takedown requests promptly, typically within a few business days.</p>

<h2>Fair Use</h2>
<p>ActualWork's use of video embeds and descriptive metadata is intended for educational, informational, and archival purposes.</p>
'''

DISCLAIMER_CONTENT = '''
<h2>General Disclaimer</h2>
<p>ActualWork is an informational archive. It is not a substitute for professional advice in any field.</p>

<h2>Professional Work Shown</h2>
<p>The work processes, tools, and methods shown in entries reflect the practices of individual professionals. They may not represent best practices, industry standards, or current methods. They should not be used as instructions or tutorials without independent verification.</p>

<h2>No Endorsement</h2>
<p>Inclusion of a work entry on ActualWork does not constitute endorsement of the person, company, methods, or tools shown.</p>

<h2>Liability</h2>
<p>ActualWork and its maintainers are not liable for any damages arising from the use of information presented on this site.</p>
'''

GUIDELINES_CONTENT = f'''
<h2>What We Accept</h2>
<p>We accept links to publicly available videos that show real professional work. The ideal submission shows:</p>
<ul>
<li>A specific problem or task</li>
<li>The actual process of working on it</li>
<li>Tools and methods used</li>
<li>Challenges encountered</li>
<li>The outcome</li>
</ul>

<h2>What We Don't Accept</h2>
<ul>
<li>Videos focused primarily on lifestyle content (commute, meals, office tours)</li>
<li>Motivational or career-advice content without substantive work demonstration</li>
<li>Promotional or advertising content</li>
<li>Content that reveals confidential, proprietary, or private information</li>
<li>Content that violates the privacy of other people</li>
</ul>

<h2>Confidentiality</h2>
<p>Do not submit videos that reveal:</p>
<ul>
<li>Trade secrets or proprietary company information</li>
<li>Patient, client, or customer information</li>
<li>Private personal information of other people</li>
<li>Restricted internal data or systems</li>
<li>Unreleased proprietary designs or products</li>
</ul>
<p>You should have the right to share everything shown in your video.</p>

<h2>Curation</h2>
<p>All submissions are reviewed manually. Acceptance is at our discretion. We may edit the metadata (title, description, tags) for clarity and consistency.</p>

<h2>Removal</h2>
<p>You can request removal of your entry at any time by emailing <strong>actualwork@luthencorps.space</strong>.</p>
'''

CONTENT_POLICY_CONTENT = f'''
<h2>Submission Policy</h2>
<p>By submitting a video link to ActualWork, you confirm that:</p>
<ul>
<li>You are the creator of the video, or you have the right to share it</li>
<li>The video does not contain confidential or proprietary information that you are not authorized to share</li>
<li>The video does not violate the privacy of other people</li>
<li>The video is publicly available on its hosting platform</li>
</ul>

<h2>Content Standards</h2>
<p>Entries on ActualWork must show genuine professional work. We do not accept:</p>
<ul>
<li>Fabricated or misleading content</li>
<li>Content designed primarily to promote a product or service</li>
<li>Content that harasses, threatens, or discriminates against any person or group</li>
<li>Content that violates applicable law</li>
</ul>

<h2>Moderation</h2>
<p>ActualWork is a curated archive. All entries are reviewed before publication. We reserve the right to decline submissions or remove existing entries at our discretion.</p>

<h2>Reporting</h2>
<p>To report content that violates this policy, please use our <a href="{make_url('report/')}">Report Content</a> page.</p>
'''

REPORT_CONTENT = '''
<h2>Report or Request Removal</h2>
<p>If you believe content on ActualWork should be removed or modified, please contact us:</p>
<p>Email: <strong>actualwork@luthencorps.space</strong></p>
<p>Subject: <strong>Content Report</strong></p>

<h2>Reasons for Reporting</h2>
<ul>
<li>You are the video creator and want your entry removed</li>
<li>The entry contains inaccurate information about you or your work</li>
<li>The content reveals confidential or private information</li>
<li>The content violates copyright</li>
<li>The content is offensive, misleading, or inappropriate</li>
<li>Any other concern</li>
</ul>

<h2>What to Include</h2>
<ul>
<li>The URL of the ActualWork entry</li>
<li>A description of the issue</li>
<li>Your relationship to the content (if applicable)</li>
</ul>

<h2>Response Time</h2>
<p>We aim to respond to all reports within a few business days. Urgent requests (privacy, safety) will be prioritized.</p>
'''


# ============================================================
# Build Orchestration
# ============================================================

def write_page(relative_path, html_content):
    """Write an HTML page to disk."""
    full_path = os.path.join(SCRIPT_DIR, relative_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f'  wrote {relative_path}')


def build():
    print('ActualWork build starting...')
    print(f'  Data: {DATA_DIR}')
    print(f'  Output: {SCRIPT_DIR}')
    print()

    # Load data from master JSON files
    entries = load_entries()
    occupations_base = load_json('occupations.json')
    industries_base = load_json('industries.json')
    tools_base = load_json('tools.json')
    tags_base = load_json('tags.json')

    print(f'  Loaded {len(entries)} entries')
    print(f'  Loaded {len(occupations_base)} occupations (from JSON)')
    print(f'  Loaded {len(industries_base)} industries (from JSON)')
    print(f'  Loaded {len(tools_base)} tools (from JSON)')
    print(f'  Loaded {len(tags_base)} tags (from JSON)')

    # Auto-discover entities referenced in entries but missing from master lists
    occupations, industries, tools, tags, work_types = auto_discover_entities(
        entries, occupations_base, industries_base, tools_base, tags_base)

    discovered_occ = len(occupations) - len(occupations_base)
    discovered_ind = len(industries) - len(industries_base)
    discovered_tools = len(tools) - len(tools_base)
    discovered_tags = len(tags) - len(tags_base)
    if discovered_occ or discovered_ind or discovered_tools or discovered_tags:
        print(f'  Auto-discovered: {discovered_occ} occupations, {discovered_ind} industries, '
              f'{discovered_tools} tools, {discovered_tags} tags')
    print(f'  Collected {len(work_types)} work types from entries')
    print()

    occupations_lookup = build_lookup(occupations)
    industries_lookup = build_lookup(industries)
    tools_lookup = build_lookup(tools)
    tags_lookup = build_lookup(tags)
    work_types_lookup = build_lookup(work_types)

    # Helper: check if an entry uses a tool (by slug or display name)
    def entry_has_tool(entry, tool_id):
        return any(slugify(t) == tool_id for t in entry.get('tools', []))

    # Helper: check if an entry has a tag (by slug or display name)
    def entry_has_tag(entry, tag_id):
        return any(slugify(t) == tag_id for t in entry.get('tags', []))

    # Helper: check if an entry has a work type
    def entry_has_work_type(entry, wt_id):
        return wt_id in entry.get('workTypes', [])

    # Homepage
    write_page('index.html', generate_homepage(entries, occupations, industries, occupations_lookup))

    # Entry pages
    for entry in entries:
        write_page(f'work/{entry["id"]}/index.html',
                   generate_entry_page(entry, occupations_lookup, industries_lookup, tools_lookup, tags_lookup, entries))

    # Occupation listing
    write_page('occupations/index.html',
               generate_listing_page('Occupations',
                                     'Browse work entries by occupation.',
                                     occupations, entries, occupations_lookup,
                                     'occupations/',
                                     lambda oid: sum(1 for e in entries if e.get('occupation') == oid)))

    # Individual occupation pages
    for occ in occupations:
        write_page(f'occupations/{occ["id"]}/index.html',
                   generate_occupation_page(occ, entries, occupations_lookup))

    # Industry listing
    write_page('industries/index.html',
               generate_listing_page('Industries',
                                     'Browse work entries by industry.',
                                     industries, entries, occupations_lookup,
                                     'industries/',
                                     lambda iid: sum(1 for e in entries if e.get('industry') == iid)))

    # Individual industry pages
    for ind in industries:
        write_page(f'industries/{ind["id"]}/index.html',
                   generate_category_detail_page(ind, entries, occupations_lookup,
                                                  lambda e, iid: e.get('industry') == iid,
                                                  'Industry'))

    # Tool listing
    write_page('tools/index.html',
               generate_listing_page('Tools',
                                     'Browse work entries by tools used.',
                                     tools, entries, occupations_lookup,
                                     'tools/',
                                     lambda tid: sum(1 for e in entries if entry_has_tool(e, tid))))

    # Individual tool pages
    for tool in tools:
        write_page(f'tools/{tool["id"]}/index.html',
                   generate_category_detail_page(tool, entries, occupations_lookup,
                                                  lambda e, tid: entry_has_tool(e, tid),
                                                  'Tool'))

    # Tag listing
    write_page('tags/index.html',
               generate_listing_page('Tags',
                                     'Browse work entries by tag.',
                                     tags, entries, occupations_lookup,
                                     'tags/',
                                     lambda tid: sum(1 for e in entries if entry_has_tag(e, tid))))

    # Individual tag pages
    for tag in tags:
        write_page(f'tags/{tag["id"]}/index.html',
                   generate_category_detail_page(tag, entries, occupations_lookup,
                                                  lambda e, tid: entry_has_tag(e, tid),
                                                  'Tag'))

    # Work type listing
    if work_types:
        write_page('work-types/index.html',
                   generate_listing_page('Types of Work',
                                         'Browse work entries by type of work.',
                                         work_types, entries, occupations_lookup,
                                         'work-types/',
                                         lambda wtid: sum(1 for e in entries if entry_has_work_type(e, wtid))))

        # Individual work type pages
        for wt in work_types:
            write_page(f'work-types/{wt["id"]}/index.html',
                       generate_category_detail_page(wt, entries, occupations_lookup,
                                                       lambda e, wtid: entry_has_work_type(e, wtid),
                                                       'Type of Work'))

    # Search page
    write_page('search/index.html',
               generate_search_page(entries, occupations, industries, tools, occupations_lookup, tools_lookup, tags_lookup))

    # Submit page
    write_page('submit/index.html', generate_submit_page())

    # Builder page
    write_page('builder/index.html', generate_builder_page())

    # Policy pages
    write_page('terms/index.html', generate_policy_page('terms', 'Terms of Use', TERMS_CONTENT))
    write_page('privacy/index.html', generate_policy_page('privacy', 'Privacy Policy', PRIVACY_CONTENT))
    write_page('copyright/index.html', generate_policy_page('copyright', 'Copyright & Takedown Policy', COPYRIGHT_CONTENT))
    write_page('disclaimer/index.html', generate_policy_page('disclaimer', 'Disclaimer', DISCLAIMER_CONTENT))
    write_page('guidelines/index.html', generate_policy_page('guidelines', 'Contributor Guidelines', GUIDELINES_CONTENT))
    write_page('content-policy/index.html', generate_policy_page('content-policy', 'Content & Submission Policy', CONTENT_POLICY_CONTENT))
    write_page('report/index.html', generate_policy_page('report', 'Report or Remove Content', REPORT_CONTENT))

    print()
    print(f'Build complete. {len(entries)} entries processed.')
    print(f'  Occupations: {len(occupations)} | Industries: {len(industries)} | Tools: {len(tools)} | Tags: {len(tags)} | Work Types: {len(work_types)}')
    print(f'Site available at: {BASE_PATH}/')


if __name__ == '__main__':
    build()
