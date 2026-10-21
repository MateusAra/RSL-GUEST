"""Connectors that need no key: arXiv, OpenAlex (also ACM via OpenAlex) and Semantic Scholar."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ElementTree
from collections.abc import Iterator
from typing import Any

import httpx

from .base import Connector, Credentials, Filters, Page, SearchError, clean, record, year_range

ATOM = {"a": "http://www.w3.org/2005/Atom", "os": "http://a9.com/-/spec/opensearch/1.1/",
        "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivConnector(Connector):
    key = "arxiv"
    label = "arXiv"
    page_size = 200
    delay = 3.0  # arXiv API terms: no more than one request every three seconds
    syntax_help = 'Sintaxe do arXiv: prefixos ti:, abs:, all:, au:, cat: com AND, OR, ANDNOT e aspas, ex.: abs:"large language model" AND ti:review'

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        years = year_range(filters)
        if years:
            query = f"({query}) AND submittedDate:[{years[0]}01010000 TO {years[1]}12312359]"
        start = 0
        while start < limit:
            if start:
                self.sleep(self.delay)
            size = min(self.page_size, limit - start)
            response = self.request(client, "GET", "https://export.arxiv.org/api/query",
                                    params={"search_query": query, "start": start, "max_results": size})
            try:
                root = ElementTree.fromstring(response.content)
            except ElementTree.ParseError as exc:
                raise SearchError("O arXiv devolveu uma resposta que não é Atom válido.") from exc
            entries = root.findall("a:entry", ATOM)
            if len(entries) == 1 and "api/errors" in (entries[0].findtext("a:id", "", ATOM)):
                raise SearchError(f"O arXiv não aceitou a string de busca: {clean(entries[0].findtext('a:summary', '', ATOM))}")
            total = int(root.findtext("os:totalResults", "0", ATOM) or 0)
            yield Page(total=total, records=[self._record(entry) for entry in entries], raw=response.text)
            start += size
            if not entries or start >= total:
                return

    @staticmethod
    def _record(entry: ElementTree.Element) -> dict[str, str]:
        arxiv_id = entry.findtext("a:id", "", ATOM).rsplit("/abs/", 1)[-1]
        bare_id = re.sub(r"v\d+$", "", arxiv_id)
        link = next((item.get("href") for item in entry.findall("a:link", ATOM) if item.get("rel") == "alternate"), "")
        return record(
            bibtex_key=f"arxiv{bare_id}".replace("/", "_").replace(".", "_"),
            title=entry.findtext("a:title", "", ATOM),
            author="; ".join(clean(author.findtext("a:name", "", ATOM)) for author in entry.findall("a:author", ATOM)),
            journal=entry.findtext("arxiv:journal_ref", "", ATOM) or "arXiv",
            year=entry.findtext("a:published", "", ATOM)[:4],
            abstract=entry.findtext("a:summary", "", ATOM),
            document_type="preprint",
            doi=entry.findtext("arxiv:doi", "", ATOM) or f"10.48550/arXiv.{bare_id}",
            url=link or f"https://arxiv.org/abs/{arxiv_id}",
            keywords="; ".join(item.get("term", "") for item in entry.findall("a:category", ATOM)),
            publisher="arXiv",
            note=entry.findtext("arxiv:comment", "", ATOM),
        )


OPENALEX_TYPES = {"journal-article": "article", "proceedings-article": "inproceedings", "posted-content": "preprint",
                  "book-chapter": "inbook", "book": "book", "dissertation": "phdthesis"}


def openalex_abstract(index: dict[str, list[int]] | None) -> str:
    """OpenAlex ships abstracts as an inverted index (word → positions)."""
    if not index:
        return ""
    positions = {position: word for word, places in index.items() for position in places}
    return " ".join(positions[position] for position in sorted(positions))


class OpenAlexConnector(Connector):
    key = "openalex"
    label = "OpenAlex"
    provider = "openalex"
    page_size = 200
    delay = 0.2
    extra_filter = ""
    syntax_help = ('Busca no título e no resumo (OpenAlex). Aceita AND, OR, NOT em maiúsculas, aspas e parênteses, '
                   'ex.: ("systematic review" OR "mapping study") AND LLM')

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        # Commas separate OpenAlex filters, and carry no meaning in a boolean string.
        parts = [f"title_and_abstract.search:{query.replace(',', ' ')}"]
        years = year_range(filters)
        if years:
            parts.append(f"publication_year:{years[0]}-{years[1]}")
        if self.extra_filter:
            parts.append(self.extra_filter)
        params: dict[str, Any] = {"filter": ",".join(parts), "per-page": min(self.page_size, limit), "cursor": "*"}
        if credentials.key:
            params["api_key"] = credentials.key
        fetched = 0
        while fetched < limit and params["cursor"]:
            if fetched:
                self.sleep(self.delay)
            response = self.request(client, "GET", "https://api.openalex.org/works", params=params)
            body = response.json()
            results = body.get("results", [])[: limit - fetched]
            fetched += len(results)
            yield Page(total=body.get("meta", {}).get("count"), records=[self._record(item) for item in results],
                       raw=response.text)
            params["cursor"] = body.get("meta", {}).get("next_cursor") if results else None

    @staticmethod
    def _record(work: dict[str, Any]) -> dict[str, str]:
        location = work.get("primary_location") or {}
        venue = location.get("source") or {}
        biblio = work.get("biblio") or {}
        pages = "-".join(part for part in (biblio.get("first_page"), biblio.get("last_page")) if part)
        institutions = dict.fromkeys(
            institution.get("display_name", "") for authorship in work.get("authorships", [])
            for institution in authorship.get("institutions", []) if institution.get("display_name")
        )
        return record(
            title=work.get("display_name") or work.get("title"),
            author="; ".join((authorship.get("author") or {}).get("display_name", "") for authorship in work.get("authorships", [])),
            journal=venue.get("display_name"),
            year=work.get("publication_year"),
            pages=pages,
            volume=biblio.get("volume"),
            abstract=openalex_abstract(work.get("abstract_inverted_index")),
            document_type=OPENALEX_TYPES.get(work.get("type_crossref") or "", work.get("type") or ""),
            doi=work.get("doi"),
            url=location.get("landing_page_url") or work.get("doi") or work.get("id"),
            affiliation="; ".join(institutions),
            keywords="; ".join(item.get("display_name", "") for item in work.get("keywords", [])),
            publisher=venue.get("host_organization_name"),
            issn=venue.get("issn_l"),
            language=work.get("language"),
            note=f"OpenAlex {str(work.get('id', '')).rsplit('/', 1)[-1]}",
        )


ACM_PUBLISHER = "P4310319798"  # Association for Computing Machinery in OpenAlex


class AcmOpenAlexConnector(OpenAlexConnector):
    key = "acm_openalex"
    label = "ACM Digital Library (via OpenAlex)"
    extra_filter = f"primary_location.source.publisher_lineage:{ACM_PUBLISHER}"
    notice = ("A ACM não oferece API de busca. Esta busca usa os metadados abertos do OpenAlex restritos às publicações "
              "da ACM: a sintaxe e os resultados não são idênticos aos do site dl.acm.org, e o relato registra isso.")


class SemanticScholarConnector(Connector):
    key = "semantic_scholar"
    label = "Semantic Scholar"
    provider = "semantic_scholar"
    page_size = 1000
    delay = 1.1  # 1 request per second without a key
    syntax_help = 'Sintaxe do Semantic Scholar: + (e), | (ou), - (não), aspas e parênteses, ex.: "systematic review" + (LLM | "language model")'
    FIELDS = "title,authors,year,venue,abstract,externalIds,url,publicationTypes,journal,publicationVenue"

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        params: dict[str, Any] = {"query": query, "fields": self.FIELDS}
        years = year_range(filters)
        if years:
            params["year"] = f"{years[0]}-{years[1]}"
        headers = {"x-api-key": credentials.key} if credentials.key else {}
        fetched = 0
        while fetched < limit:
            if fetched:
                self.sleep(self.delay)
            response = self.request(client, "GET", "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
                                    params=params, headers=headers)
            body = response.json()
            data = body.get("data") or []
            data = data[: limit - fetched]
            fetched += len(data)
            yield Page(total=body.get("total"), records=[self._record(item) for item in data], raw=response.text)
            if not data or not body.get("token"):
                return
            params["token"] = body["token"]

    @staticmethod
    def _record(paper: dict[str, Any]) -> dict[str, str]:
        ids = paper.get("externalIds") or {}
        journal = paper.get("journal") or {}
        types = paper.get("publicationTypes") or []
        kind = "inproceedings" if "Conference" in types else "article" if "JournalArticle" in types else (types[0] if types else "")
        return record(
            title=paper.get("title"),
            author="; ".join(author.get("name", "") for author in paper.get("authors") or []),
            journal=journal.get("name") or paper.get("venue"),
            year=paper.get("year"),
            pages=journal.get("pages"),
            volume=journal.get("volume"),
            abstract=paper.get("abstract"),
            document_type=kind,
            doi=ids.get("DOI") or (f"10.48550/arXiv.{ids['ArXiv']}" if ids.get("ArXiv") else ""),
            url=paper.get("url"),
            publisher=(paper.get("publicationVenue") or {}).get("name"),
            note=f"Semantic Scholar {paper.get('paperId', '')}",
        )
