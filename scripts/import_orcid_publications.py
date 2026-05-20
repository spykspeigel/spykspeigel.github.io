#!/usr/bin/env python3
"""Import public ORCID works into Jekyll _publications markdown files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path


API_ROOT = "https://pub.orcid.org/v3.0"
GENERATED_MARKER = "orcid_put_code:"


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def nested_value(data: dict | None, *keys: str) -> str:
    current = data
    for key in keys:
        if current is None:
            return ""
        current = current.get(key)
    if isinstance(current, dict):
        return str(current.get("value") or "")
    return str(current or "")


def yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "publication"


def publication_date(work: dict) -> tuple[str, str]:
    date = work.get("publication-date") or {}
    year = nested_value(date, "year") or "1900"
    month = nested_value(date, "month") or "01"
    day = nested_value(date, "day") or "01"
    return f"{year}-{month.zfill(2)}-{day.zfill(2)}", year


def external_id(work: dict, id_type: str) -> tuple[str, str]:
    external_ids = ((work.get("external-ids") or {}).get("external-id") or [])
    for item in external_ids:
        if item.get("external-id-type", "").lower() == id_type.lower():
            value = item.get("external-id-value") or ""
            url = nested_value(item, "external-id-url")
            return value, url
    return "", ""


def contributors(work: dict) -> list[str]:
    people = []
    for contributor in ((work.get("contributors") or {}).get("contributor") or []):
        name = nested_value(contributor, "credit-name")
        if name:
            people.append(name)
    return people


def citation_for(work: dict, year: str, venue: str, doi: str) -> str:
    existing = nested_value(work, "citation", "citation-value")
    if existing:
        return existing

    names = contributors(work)
    title = nested_value(work, "title", "title")
    author_text = ", ".join(names) if names else "Unknown author"
    pieces = [f"{author_text}. ({year}). \"{title}.\""]
    if venue:
        pieces.append(venue + ".")
    if doi:
        pieces.append(f"DOI: {doi}.")
    return " ".join(pieces)


def markdown_for(orcid_id: str, work: dict) -> tuple[str, str]:
    title = nested_value(work, "title", "title") or "Untitled work"
    date, year = publication_date(work)
    venue = nested_value(work, "journal-title")
    doi, doi_url = external_id(work, "doi")
    url = nested_value(work, "url") or doi_url
    work_type = work.get("type") or "work"
    put_code = str(work.get("put-code") or "")
    citation = citation_for(work, year, venue, doi)
    authors = contributors(work)

    slug = slugify(f"{year}-{title}")
    filename = f"{date}-{slug}.md"
    permalink = f"/publication/{slug}"
    excerpt_bits = [work_type.replace("-", " ")]
    if venue:
        excerpt_bits.append(venue)
    excerpt_bits.append(year)
    excerpt = ", ".join(excerpt_bits) + "."

    body = [
        "---",
        f"title: {yaml_string(title)}",
        "collection: publications",
        f"permalink: {yaml_string(permalink)}",
        f"excerpt: {yaml_string(excerpt)}",
        f"date: {date}",
        f"venue: {yaml_string(venue)}",
        f"paperurl: {yaml_string(url)}",
        f"citation: {yaml_string(citation)}",
        f"orcid_put_code: {yaml_string(put_code)}",
        f"orcid: {yaml_string(orcid_id)}",
        f"doi: {yaml_string(doi)}",
        f"work_type: {yaml_string(work_type)}",
        "---",
        "",
    ]

    if authors:
        body.append("**Authors:** " + ", ".join(authors))
        body.append("")
    if venue:
        body.append(f"**Venue:** {venue}")
        body.append("")
    if doi:
        body.append(f"**DOI:** [{doi}]({doi_url or url})")
        body.append("")
    if url:
        body.append(f"[View publication]({url})")
        body.append("")
    body.append("Imported from ORCID.")
    body.append("")

    return filename, "\n".join(body)


def import_publications(orcid_id: str, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    for path in output_dir.glob("*.md"):
        if GENERATED_MARKER in path.read_text(encoding="utf-8"):
            path.unlink()

    works = get_json(f"{API_ROOT}/{orcid_id}/works")
    written = 0
    for group in works.get("group", []):
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        put_code = summaries[0].get("put-code")
        if not put_code:
            continue
        work = get_json(f"{API_ROOT}/{orcid_id}/work/{put_code}")
        filename, markdown = markdown_for(orcid_id, work)
        (output_dir / filename).write_text(markdown, encoding="utf-8")
        written += 1

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("orcid_id", help="ORCID iD, for example 0000-0002-1187-3689")
    parser.add_argument(
        "--output",
        default="_publications",
        type=Path,
        help="Directory for generated publication markdown files",
    )
    args = parser.parse_args()

    count = import_publications(args.orcid_id, args.output)
    print(f"Imported {count} ORCID works into {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
