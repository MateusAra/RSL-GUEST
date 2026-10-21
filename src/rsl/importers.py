"""Bibliographic file import (BibTeX, RIS, CSV) into article dictionaries."""

from __future__ import annotations

import csv
import io
import re
import unicodedata
from typing import Any

import bibtexparser
import rispy
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

ARTICLE_TEXT_FIELDS = (
    "bibtex_key", "title", "author", "journal", "year", "pages", "volume", "abstract", "document_type",
    "doi", "url", "affiliation", "author_keywords", "keywords", "publisher", "issn", "language", "note",
)
FIELD_LIMITS = {
    "bibtex_key": 100, "title": 1000, "author": 1000, "journal": 1000, "year": 10, "pages": 20, "volume": 100,
    "document_type": 100, "doi": 200, "url": 500, "affiliation": 500, "author_keywords": 1000, "keywords": 1000,
    "publisher": 200, "issn": 50, "language": 50, "note": 500,
}
CSV_ALIASES = {
    "bibtex_key": {"key", "bibtexkey", "id"},
    "title": {"title", "articletitle", "documenttitle", "ti"},
    "author": {"author", "authors", "au", "creator"},
    "journal": {"journal", "sourcetitle", "publicationtitle", "venue", "booktitle", "so", "jo"},
    "year": {"year", "publicationyear", "py", "date"},
    "pages": {"pages", "pagerange"},
    "volume": {"volume", "vl"},
    "abstract": {"abstract", "ab", "summary"},
    "document_type": {"documenttype", "type", "itemtype", "dt"},
    "doi": {"doi", "di"},
    "url": {"url", "link", "pdflink"},
    "affiliation": {"affiliation", "affiliations"},
    "author_keywords": {"authorkeywords", "de"},
    "keywords": {"keywords", "indexkeywords", "kw", "tags"},
    "publisher": {"publisher", "pb"},
    "issn": {"issn", "sn"},
    "language": {"language", "languageoforiginaldocument", "la"},
    "note": {"note", "notes"},
}


DOCUMENT_CATEGORIES = {
    "journal": "Periódico",
    "conference": "Evento",
    "preprint": "Pré-print",
    "thesis": "Tese ou dissertação",
    "book": "Livro ou capítulo",
    "other": "Outro",
}
_CATEGORY_ALIASES = {
    "journal": {"article", "jour", "jfull", "ejour", "mgzn", "journalarticle", "journal"},
    "conference": {"inproceedings", "conference", "proceedings", "conf", "cpaper", "conferencepaper", "proceedingspaper"},
    "preprint": {"unpublished", "unpb", "preprint"},
    "thesis": {"phdthesis", "mastersthesis", "thes", "thesis", "dissertation"},
    "book": {"book", "inbook", "incollection", "chap", "bookchapter", "booksection"},
}


def document_category(document_type: str, journal: str = "", doi: str = "") -> str:
    """Group raw BibTeX/RIS/CSV document types into a few comparable publication channels."""
    if doi.startswith("10.48550/") or "arxiv" in journal.casefold():
        return "preprint"
    normalized = re.sub(r"[^a-z]", "", document_type.casefold())
    return next((category for category, aliases in _CATEGORY_ALIASES.items() if normalized in aliases), "other")


def normalize_title(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_title.casefold()).split())


def normalize_doi(doi: str) -> str:
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", doi.strip(), flags=re.IGNORECASE).casefold()


def _decode(payload: bytes) -> tuple[str, str]:
    try:
        return payload.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return payload.decode("latin-1"), "latin-1"


def _join(value: Any, separator: str) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return separator.join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def _year(value: Any) -> str:
    match = re.search(r"(?:19|20)\d{2}", str(value or ""))
    return match.group(0) if match else ""


def _clean_bibtex(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[{}]", "", value)).strip()


def _finalize(record: dict[str, Any]) -> dict[str, str]:
    article = {field: _join(record.get(field), "; ") for field in ARTICLE_TEXT_FIELDS}
    article["year"] = _year(article["year"])
    article["doi"] = normalize_doi(article["doi"]) if article["doi"] else ""
    for field, limit in FIELD_LIMITS.items():
        article[field] = article[field][:limit]
    return article


def _from_bibtex(text: str) -> list[dict[str, str]]:
    # LaTeX escapes and accents (\&, {\'e}, {\"u}) become plain Unicode; one parser per file, as parsers accumulate.
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    entries = bibtexparser.loads(text, parser).entries
    articles = []
    for entry in entries:
        value = {key: _clean_bibtex(str(item)) for key, item in entry.items()}
        articles.append(_finalize({
            "bibtex_key": value.get("ID"),
            "title": value.get("title"),
            "author": value.get("author"),
            "journal": value.get("journal") or value.get("booktitle") or value.get("series"),
            "year": value.get("year"),
            "pages": value.get("pages"),
            "volume": value.get("volume"),
            "abstract": value.get("abstract"),
            "document_type": value.get("ENTRYTYPE"),
            "doi": value.get("doi"),
            "url": value.get("url"),
            "affiliation": value.get("affiliation") or value.get("affiliations"),
            "author_keywords": value.get("author_keywords"),
            "keywords": value.get("keywords"),
            "publisher": value.get("publisher"),
            "issn": value.get("issn"),
            "language": value.get("language"),
            "note": value.get("note"),
        }))
    return articles


def _from_ris(text: str) -> list[dict[str, str]]:
    articles = []
    for entry in rispy.loads(text):
        pages = "-".join(part for part in (entry.get("start_page"), entry.get("end_page")) if part)
        articles.append(_finalize({
            "bibtex_key": entry.get("id"),
            "title": entry.get("title") or entry.get("primary_title"),
            "author": _join(entry.get("authors") or entry.get("first_authors"), " and "),
            "journal": entry.get("journal_name") or entry.get("secondary_title") or entry.get("alternate_title1"),
            "year": entry.get("year") or entry.get("publication_year") or entry.get("date"),
            "pages": pages,
            "volume": entry.get("volume"),
            "abstract": entry.get("abstract"),
            "document_type": entry.get("type_of_reference"),
            "doi": entry.get("doi"),
            "url": entry.get("urls") or entry.get("url"),
            "keywords": entry.get("keywords"),
            "publisher": entry.get("publisher"),
            "issn": entry.get("issn"),
            "language": entry.get("language"),
            "note": entry.get("notes") or entry.get("note"),
        }))
    return articles


def _from_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    headers = {re.sub(r"[^a-z0-9]", "", (header or "").casefold()): header for header in reader.fieldnames or []}
    mapping = {
        field: next((headers[alias] for alias in aliases if alias in headers), None)
        for field, aliases in CSV_ALIASES.items()
    }
    return [
        _finalize({field: row.get(column) if column else "" for field, column in mapping.items()})
        for row in reader
    ]


def parse_bibliography(payload: bytes, file_name: str) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Parse a BibTeX, RIS or CSV export. Records without title are skipped and reported."""
    text, encoding = _decode(payload)
    extension = file_name.rsplit(".", 1)[-1].casefold() if "." in file_name else ""
    if extension in {"bib", "bibtex"}:
        records = _from_bibtex(text)
    elif extension in {"ris", "txt"} and re.search(r"^TY  - ", text, flags=re.MULTILINE):
        records = _from_ris(text)
    elif extension == "csv":
        records = _from_csv(text)
    else:
        raise ValueError("Formato não suportado. Envie um arquivo .bib, .ris ou .csv.")
    kept = [record for record in records if record["title"]]
    if not kept:
        raise ValueError("Nenhuma referência com título foi encontrada no arquivo.")
    report = {
        "encoding": encoding,
        "total": len(records),
        "imported": len(kept),
        "skipped_without_title": len(records) - len(kept),
    }
    return kept, report
