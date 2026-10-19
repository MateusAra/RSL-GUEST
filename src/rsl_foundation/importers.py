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
    "publication_type": {"type", "documenttype", "publicationtype", "itemtype", "ty"},
}

PUBLICATION_TYPES = {
    "journal": {"jour", "jfull", "ejour", "mgzn", "article", "journalarticle", "journal"},
    "conference": {"conf", "cpaper", "inproceedings", "conference", "proceedings", "conferencepaper", "proceedingspaper"},
    "preprint": {"unpb", "unpublished", "preprint"},
    "thesis": {"thes", "phdthesis", "mastersthesis", "thesis", "dissertation"},
    "book": {"book", "chap", "inbook", "incollection", "bookchapter", "booksection"},
}

# Canonical preference (spec 003, RF21): journal > conference > preprint; anything else ranks last.
PUBLICATION_TYPE_RANK = {"journal": 3, "conference": 2, "preprint": 1}
COMPLETENESS_FIELDS = ("authors", "year", "venue", "doi", "abstract", "keywords")


def publication_type(raw_type: Any, venue: str | None, doi: str | None) -> str | None:
    if (doi or "").startswith("10.48550/") or "arxiv" in (venue or "").casefold():
        return "preprint"
    normalized = re.sub(r"[^a-z]", "", str(raw_type or "").casefold())
    for canonical, aliases in PUBLICATION_TYPES.items():
        if normalized in aliases:
            return canonical
    return "other" if normalized else None


def metadata_completeness(record: dict[str, Any]) -> int:
    return sum(1 for field in COMPLETENESS_FIELDS if record.get(field))


def normalize_title(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_title.casefold()).split())


def title_similarity(first: str, second: str) -> float:
    first_normalized = normalize_title(first)
    second_normalized = normalize_title(second)
    if not first_normalized or not second_normalized:
        return 0.0
    return ratio(first_normalized, second_normalized) / 100


def _decode(payload: bytes) -> tuple[str, str]:
    try:
        return payload.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        try:
            return payload.decode("latin-1"), "latin-1"
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
    venue = str(record.get("venue") or "").strip() or None
    return {
        "title": title,
        "normalized_title": normalize_title(title),
        "authors": _authors(record.get("authors", record.get("author"))),
        "year": _year(record.get("year")),
        "venue": venue,
        "doi": doi or None,
        "abstract": str(record.get("abstract") or "").strip() or None,
        "keywords": _keywords(record.get("keywords")),
        "publication_type": publication_type(record.get("publication_type"), venue, doi or None),
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


def parse_records_with_report(payload: bytes, filename: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    text, encoding = _decode(payload)
    extension = filename.rsplit(".", 1)[-1].casefold() if "." in filename else ""
    if extension == "ris":
        source_records = rispy.loads(text)
        records = [
            _canonical_record(
                {
                    "title": item.get("title") or item.get("primary_title"),
                    "authors": item.get("authors"),
                    "year": item.get("year"),
                    "venue": item.get("journal_name") or item.get("secondary_title"),
                    "doi": item.get("doi"),
                    "abstract": item.get("abstract"),
                    "keywords": item.get("keywords"),
                    "publication_type": item.get("type_of_reference"),
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
                    "publication_type": (
                        "preprint"
                        if str(item.get("archiveprefix", "")).casefold() == "arxiv"
                        else item.get("ENTRYTYPE")
                    ),
                }
            )
            for item in source_records
        ]
    elif extension == "csv":
        records = _parse_csv(text)
    else:
        raise ValueError("supported formats are RIS, BibTeX and CSV")

    # Spec 003 CA-04: incomplete records are reported, never dropped silently.
    anomalies: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        issues = [
            issue
            for issue, missing in (
                ("missing_title", not record["title"]),
                ("missing_authors", not record["authors"]),
                ("missing_year", record["year"] is None),
            )
            if missing
        ]
        if issues:
            anomalies.append({"record": index, "title": record["title"] or None, "issues": issues})
    kept = [record for record in records if record["title"]]
    if not kept:
        raise ValueError("no bibliographic records found")
    report = {
        "encoding": encoding,
        "warnings": ["file decoded as Latin-1; check accented characters"] if encoding == "latin-1" else [],
        "source_count": len(records),
        "skipped_count": len(records) - len(kept),
        "anomalies": anomalies,
    }
    return kept, report


def parse_records(payload: bytes, filename: str) -> list[dict[str, Any]]:
    return parse_records_with_report(payload, filename)[0]
