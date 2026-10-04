#!/usr/bin/env python3
"""Generate publications.qmd from publications/publications.bib.

Usage (from the repo root):
    python3 scripts/build_publications.py

Optional per-paper extras, keyed by the BibTeX key:
    publications/<key>.md   one-paragraph summary shown under the entry
    publications/<key>.png  figure shown next to the entry (.jpg also works)

Entries are sorted newest first (year, then month). The author matching
MY_NAME is shown in bold. No third-party packages required.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "publications" / "publications.bib"
OUT = ROOT / "publications.qmd"
MY_NAME = "Yang, Xin"

MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), start=1)}


def parse_bib(text):
    """Return a list of (type, key, fields, raw) for each entry."""
    entries = []
    i = 0
    while True:
        at = text.find("@", i)
        if at == -1:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[at:])
        if not m:
            i = at + 1
            continue
        # Find the matching closing brace of the entry.
        start = at + text[at:].index("{")
        depth, j = 0, start
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        raw = text[at:j + 1]
        body = text[at + m.end():j]
        entries.append((m.group(1).lower(), m.group(2), parse_fields(body), raw))
        i = j + 1
    return entries


def parse_fields(body):
    fields = {}
    i = 0
    while i < len(body):
        m = re.match(r"\s*,?\s*(\w+)\s*=\s*", body[i:])
        if not m:
            break
        name = m.group(1).lower()
        i += m.end()
        if i < len(body) and body[i] == "{":
            depth, j = 0, i
            while j < len(body):
                if body[j] == "{":
                    depth += 1
                elif body[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            value = body[i + 1:j]
            i = j + 1
        elif i < len(body) and body[i] == '"':
            j = body.index('"', i + 1)
            value = body[i + 1:j]
            i = j + 1
        else:
            m2 = re.match(r"[^,\n]+", body[i:])
            value = m2.group(0).strip() if m2 else ""
            i += m2.end() if m2 else 1
        fields[name] = " ".join(value.split())
    return fields


def latex_to_html(s):
    """Handle the small amount of LaTeX that shows up in titles and venues."""
    s = re.sub(r"\$_\{?([^$}]+)\}?\$", r"<sub>\1</sub>", s)
    s = re.sub(r"\$\^\{?([^$}]+)\}?\$", r"<sup>\1</sup>", s)
    s = s.replace(r"\&", "&amp;").replace("--", "–")
    s = s.replace("{", "").replace("}", "")
    return s


def format_author(name):
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
        display = f"{first} {last}"
    else:
        display = name.strip()
    if name.strip() == MY_NAME:
        return f"<strong>{display}</strong>"
    return display


def venue_line(etype, f):
    if etype == "article":
        parts = [f"<em>{latex_to_html(f.get('journal', ''))}</em>"]
        if f.get("volume"):
            vol = f["volume"] + (f"({f['number']})" if f.get("number") else "")
            parts.append(vol)
        if f.get("pages"):
            parts.append(latex_to_html(f["pages"]))
        parts.append(f.get("year", ""))
        return ", ".join(p for p in parts if p)
    if f.get("archiveprefix", "").lower() == "arxiv" or "arxiv" in f.get("url", ""):
        return f"<em>arXiv preprint</em> arXiv:{f.get('eprint', '')}, {f.get('year', '')}"
    venue = f.get("booktitle") or f.get("journal") or f.get("howpublished", "")
    return ", ".join(p for p in [f"<em>{latex_to_html(venue)}</em>" if venue else "", f.get("year", "")] if p)


def sort_key(entry):
    _, _, f, _ = entry
    year = int(re.sub(r"\D", "", f.get("year", "0")) or 0)
    month = MONTHS.get(f.get("month", "").lower()[:3], 0)
    return (year, month)


def render_entry(etype, key, f, raw):
    authors = ", ".join(format_author(a) for a in re.split(r"\s+and\s+", f.get("author", "")))
    links = []
    if f.get("doi") and "arxiv" not in f["doi"].lower():
        links.append(f'<a href="https://doi.org/{f["doi"]}">DOI</a>')
    if f.get("eprint") and f.get("archiveprefix", "").lower() == "arxiv":
        links.append(f'<a href="https://arxiv.org/abs/{f["eprint"]}">arXiv</a>')
    elif f.get("url") and not links:
        links.append(f'<a href="{f["url"]}">Link</a>')
    if f.get("code"):
        links.append(f'<a href="{f["code"]}">Code</a>')

    note = f.get("note", "")
    note = re.sub(r"\.?\s*arXiv:\S+$", "", note).strip()

    summary_file = ROOT / "publications" / f"{key}.md"
    figure = next((p for ext in ("png", "jpg", "jpeg")
                   if (p := ROOT / "publications" / f"{key}.{ext}").exists()), None)

    lines = ['::: {.pub}', '```{=html}']
    lines.append(f'<div class="pub-title">{latex_to_html(f.get("title", ""))}</div>')
    lines.append(f'<p class="pub-authors">{authors}</p>')
    lines.append(f'<p class="pub-venue">{venue_line(etype, f)}</p>')
    if note:
        lines.append(f'<p class="pub-note">{html.escape(note)}</p>')
    lines.append('```')
    if summary_file.exists() or figure:
        lines.append("")
        if figure:
            lines.append(f"![]({figure.relative_to(ROOT).as_posix()}){{style=\"max-width:100%;\"}}")
            lines.append("")
        if summary_file.exists():
            lines.append(summary_file.read_text().strip())
            lines.append("")
    lines.append('```{=html}')
    lines.append('<div class="pub-links">' + " ".join(links)
                 + '<details><summary>BibTeX</summary><pre><code>'
                 + html.escape(raw) + '</code></pre></details></div>')
    lines.append('```')
    lines.append(':::')
    return "\n".join(lines)


def main():
    entries = sorted(parse_bib(BIB.read_text()), key=sort_key, reverse=True)
    header = [
        "---",
        "title: Publications",
        "---",
        "",
        "<!-- Generated by scripts/build_publications.py from",
        "     publications/publications.bib. Do not edit by hand. -->",
        "",
    ]
    body = "\n\n".join(render_entry(*e) for e in entries)
    OUT.write_text("\n".join(header) + body + "\n")
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(entries)} entries.")


if __name__ == "__main__":
    main()
