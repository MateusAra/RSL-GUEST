from __future__ import annotations

import csv
import io
import re
import unicodedata
from typing import Any

import bibtexparser
import rispy
from rapidfuzz.fuzz import ratio


FIELD_ALIASES = {
    "title": {"title", "primarytitle", "articletitle", "ti"},
    "authors": {"authors", "author", "creator", "au"},
    "year": {"year", "publicationyear", "date", "py"},
    "venue": {"venue", "journal", "journalname", "booktitle", "publicationtitle", "jo"},
    "doi": {"doi", "digitalobjectidentifier"},
    "abstract": {"abstract", "summary", "ab"},
    "keywords": {"keywords", "keyword", "tags", "kw"},
}


def normalize_title(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_title.casefold()).split())


def title_similarity(first: str, second: str) -> float:
    first_normalized = normalize_title(first)
    second_normalized = normalize_title(second)
    if not first_normalized or not second_normalized:
        return 0.0
    return ratio(first_normalized, second_normalized) / 100


def _decode(payload: bytes) -> str:
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        try:
            return payload.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise ValueError("file encoding must be UTF-8 or Latin-1") from exc


def _year(value: Any) -> int | None:
    match = re.search(r"\b(?:19|20)\d{2}\b", str(value or ""))
    return int(match.group(0)) if match else None


def _authors(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(author).strip() for author in value if str(author).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [author.strip() for author in re.split(r"\s+and\s+|\s*;\s*|\s*\|\s*", text) if author.strip()]


def _keywords(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        values = value
    else:
        values = re.split(r"\s*[;,|]\s*", str(value))
    return [str(keyword).strip() for keyword in values if str(keyword).strip()]


def _canonical_record(record: dict[str, Any]) -> dict[str, Any]:
    title = str(record.get("title") or "").strip()
    doi = str(record.get("doi") or "").strip()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE).casefold()
    return {
        "title": title,
        "normalized_title": normalize_title(title),
        "authors": _authors(record.get("authors", record.get("author"))),
        "year": _year(record.get("year")),
        "venue": str(record.get("venue") or "").strip() or None,
        "doi": doi or None,
        "abstract": str(record.get("abstract") or "").strip() or None,
        "keywords": _keywords(record.get("keywords")),
    }


def _parse_csv(text: str) -> list[dict[str, Any]]:
    rows = csv.DictReader(io.StringIO(text))
    if not rows.fieldnames:
        return []
    aliases = {
        canonical: {
            re.sub(r"[^a-z0-9]", "", header.casefold()): header
            for header in rows.fieldnames
            if re.sub(r"[^a-z0-9]", "", header.casefold()) in names
        }
        for canonical, names in FIELD_ALIASES.items()
    }
    parsed: list[dict[str, Any]] = []
    for row in rows:
        entry = {
            field: row.get(next(iter(headers.values())), "") if headers else ""
            for field, headers in aliases.items()
        }
        parsed.append(_canonical_record(entry))
    return parsed


def parse_records(payload: bytes, filename: str) -> list[dict[str, Any]]:
    text = _decode(payload)
    extension = filename.rsplit(".", 1)[-1].casefold() if "." in filename else ""
    if extension == "ris":
        source_records = rispy.loads(text)
        records = [
            _canonical_record(
                {
                    "title": item.get("title"),
                    "authors": item.get("authors"),
                    "year": item.get("year"),
                    "venue": item.get("journal_name") or item.get("secondary_title"),
                    "doi": item.get("doi"),
                    "abstract": item.get("abstract"),
                    "keywords": item.get("keywords"),
                }
            )
            for item in source_records
        ]
    elif extension in {"bib", "bibtex"}:
        source_records = bibtexparser.loads(text).entries
        records = [
            _canonical_record(
                {
                    "title": item.get("title"),
                    "authors": item.get("author"),
                    "year": item.get("year"),
                    "venue": item.get("journal") or item.get("booktitle") or item.get("publisher"),
                    "doi": item.get("doi"),
                    "abstract": item.get("abstract"),
                    "keywords": item.get("keywords"),
                }
            )
            for item in source_records
        ]
    elif extension == "csv":
        records = _parse_csv(text)
    else:
        raise ValueError("supported formats are RIS, BibTeX and CSV")

    records = [record for record in records if record["title"]]
    if not records:
        raise ValueError("no bibliographic records found")
    return records
