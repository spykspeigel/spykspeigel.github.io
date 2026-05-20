#!/usr/bin/env python3
"""Generate Jekyll publication pages from the LaTeX CV source."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SOURCE_SECTIONS = [
    "Journal Articles",
    "Unpublished Articles and Preprints",
    "Conference Articles",
]


def yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def slugify(value: str) -> str:
    value = latex_to_text(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "publication"


def latex_to_text(value: str) -> str:
    replacements = {
        r"~": " ",
        r"\&": "&",
        r"\%": "%",
        r"``": '"',
        r"''": '"',
        "--": "-",
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "â€“": "-",
        "â€": "-",
        "Ã¨": "è",
        "Ã©": "é",
    }
    for old, new in replacements.items():
        value = value.replace(old, new)

    value = re.sub(r"\\url\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\text(?:bf|it|sl|tt)\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\{\\sl\s*([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\href\{([^{}]*)\}\{([^{}]*)\}", r"\2", value)
    value = value.replace(r"\newline", "\n").replace(r"\\", "\n")
    value = re.sub(r"\\[a-zA-Z]+", "", value)
    value = value.replace("{", "").replace("}", "")
    value = re.sub(r"[ \t]+", " ", value)
    value = re.sub(r"\n\s+", "\n", value)
    return value.strip()


def section_blocks(text: str) -> dict[str, str]:
    pattern = re.compile(
        r"\\section\{\\textcolor\{Bittersweet\}\{(?P<title>[^{}]+)\}\}"
    )
    matches = list(pattern.finditer(text))
    blocks = {}
    for index, match in enumerate(matches):
        title = match.group("title")
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        if title in SOURCE_SECTIONS:
            blocks[title] = text[start:end]
    return blocks


def href_entries(section_text: str) -> list[tuple[str, str, str]]:
    pattern = re.compile(
        r"\\href\{(?P<url>[^{}]+)\}\{\\textbf\{(?P<title>.*?)\}\}"
        r"\s*\\newline\s*(?P<body>.*?)(?=\\href\{|\\section\{|$)",
        re.DOTALL,
    )
    return [
        (match.group("url").strip(), match.group("title").strip(), match.group("body").strip())
        for match in pattern.finditer(section_text)
    ]


def first_year(*values: str) -> str:
    years = []
    for value in values:
        years.extend(re.findall(r"\b(20\d{2})\b", value))
    return years[-1] if years else "2025"


def extract_authors(body_text: str) -> str:
    lines = [line.strip(" -") for line in body_text.splitlines() if line.strip(" -")]
    for index, line in enumerate(lines):
        match = re.search(r"Co-authors?:\s*(.+)", line, flags=re.IGNORECASE)
        if match:
            authors = match.group(1).strip(" .")
            if index + 1 < len(lines):
                next_line = lines[index + 1]
                venue_like = re.search(
                    r"\b(IEEE|Automatica|Optimization|Discrete|Conference|Vol\.|DOI:|Under review)\b",
                    next_line,
                    flags=re.IGNORECASE,
                )
                if not venue_like:
                    authors = f"{authors} {next_line.strip(' .')}"
            return re.sub(r"\s+", " ", authors).strip(" .")

    patterns = [
        r"\(Under review,\s*with\s+(.+?)\)",
        r"\(with\s+(.+?)\)",
        r"White paper.*?\(co-author,\s*with\s+(.+?)\)",
    ]
    for pattern in patterns:
        match = re.search(pattern, body_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            authors = re.sub(r"\s+", " ", match.group(1)).strip(" .")
            return authors
    return ""


def extract_venue(section: str, body_text: str) -> str:
    lines = [line.strip(" -") for line in body_text.splitlines() if line.strip(" -")]
    if section == "Conference Articles":
        return lines[0] if lines else "Conference article"
    if section == "Unpublished Articles and Preprints":
        return lines[0] if lines else "Preprint"
    for line in reversed(lines):
        if "Co-author" not in line and "DOI:" not in line:
            return line
    return section.rstrip("s")


def markdown_for(section: str, order: int, url: str, title: str, body: str) -> tuple[str, str]:
    clean_title = latex_to_text(title)
    clean_body = latex_to_text(body)
    year = first_year(clean_body, url)
    date = f"{year}-01-01"
    slug = slugify(clean_title)
    filename = f"{order:02d}-{slug}.md"
    venue = extract_venue(section, clean_body)
    authors = extract_authors(clean_body)
    doi_match = re.search(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", url, flags=re.IGNORECASE)
    doi = doi_match.group(1) if doi_match else ""

    citation_parts = []
    if authors:
        citation_parts.append(f"Saroj Prasad Chhatoi with {authors}.")
    else:
        citation_parts.append("Saroj Prasad Chhatoi.")
    citation_parts.append(f"({year}). \"{clean_title}.\"")
    if venue:
        citation_parts.append(venue.rstrip(".") + ".")
    if doi:
        citation_parts.append(f"DOI: {doi}.")
    citation = " ".join(citation_parts)

    body_lines = [
        "---",
        f"title: {yaml_string(clean_title)}",
        "collection: publications",
        f"permalink: {yaml_string('/publication/' + slug)}",
        f"excerpt: {yaml_string(venue)}",
        f"date: {date}",
        f"venue: {yaml_string(venue)}",
        f"paperurl: {yaml_string(url)}",
        f"citation: {yaml_string(citation)}",
        f"section: {yaml_string(section)}",
        f"order: {order}",
        f"cv_source: {yaml_string('cv/main.tex')}",
        f"doi: {yaml_string(doi)}",
        "---",
        "",
    ]

    if authors:
        body_lines.extend([f"**Co-authors:** {authors}", ""])
    if venue:
        body_lines.extend([f"**Venue:** {venue}", ""])
    if doi:
        body_lines.extend([f"**DOI:** [{doi}]({url})", ""])
    body_lines.extend([f"[View publication]({url})", ""])

    return filename, "\n".join(body_lines)


def import_publications(tex_path: Path, output_dir: Path) -> int:
    text = tex_path.read_text(encoding="utf-8", errors="replace")
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in output_dir.glob("*.md"):
        path.unlink()

    order = 1
    for section, block in section_blocks(text).items():
        for url, title, body in href_entries(block):
            filename, markdown = markdown_for(section, order, url, title, body)
            (output_dir / filename).write_text(markdown, encoding="utf-8")
            order += 1
    return order - 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("cv/main.tex"))
    parser.add_argument("--output", type=Path, default=Path("_publications"))
    args = parser.parse_args()

    count = import_publications(args.source, args.output)
    print(f"Imported {count} publications from {args.source}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
