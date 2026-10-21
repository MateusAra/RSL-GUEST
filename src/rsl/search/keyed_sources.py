"""Connectors that need the researcher's own API key: IEEE Xplore, Elsevier, Springer Nature and Web of Science."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from .base import Connector, Credentials, Filters, Page, clean, record, year_range


def _pages(first: Any, last: Any) -> str:
    return "-".join(str(part) for part in (first, last) if part)


class IeeeConnector(Connector):
    key = "ieee"
    label = "IEEE Xplore"
    provider = "ieee"
    key_required = True
    page_size = 200
    delay = 0.2
    syntax_help = ('Sintaxe do IEEE Xplore (campo querytext): operadores AND, OR, NOT, aspas e campos entre aspas, '
                   'ex.: ("Abstract":"systematic review" OR "Document Title":LLM)')
    CONTENT_TYPES = {"Conferences": "inproceedings", "Journals": "article", "Magazines": "article",
                     "Early Access": "article", "Books": "inbook"}

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        params: dict[str, Any] = {"apikey": credentials.key, "querytext": query, "format": "json"}
        years = year_range(filters)
        if years:
            params.update(start_year=years[0], end_year=years[1])
        fetched = 0
        while fetched < limit:
            if fetched:
                self.sleep(self.delay)
            params.update(start_record=fetched + 1, max_records=min(self.page_size, limit - fetched))
            response = self.request(client, "GET", "https://ieeexploreapi.ieee.org/api/v1/search/articles", params=params)
            body = response.json()
            articles = body.get("articles") or []
            fetched += len(articles)
            total = body.get("total_records")
            yield Page(total=total, records=[self._record(item) for item in articles], raw=response.text)
            if not articles or (total is not None and fetched >= total):
                return

    @classmethod
    def _record(cls, item: dict[str, Any]) -> dict[str, str]:
        authors = (item.get("authors") or {}).get("authors") or []
        terms = item.get("index_terms") or {}
        index_terms = [term for group, value in terms.items() if group != "author_terms"
                       for term in (value or {}).get("terms", [])]
        return record(
            bibtex_key=f"ieee{item.get('article_number', '')}",
            title=item.get("title"),
            author="; ".join(author.get("full_name", "") for author in authors),
            journal=item.get("publication_title"),
            year=item.get("publication_year"),
            pages=_pages(item.get("start_page"), item.get("end_page")),
            volume=item.get("volume"),
            abstract=item.get("abstract"),
            document_type=cls.CONTENT_TYPES.get(item.get("content_type", ""), item.get("content_type")),
            doi=item.get("doi"),
            url=item.get("html_url") or item.get("pdf_url"),
            affiliation="; ".join(dict.fromkeys(author.get("affiliation", "") for author in authors if author.get("affiliation"))),
            author_keywords="; ".join((terms.get("author_terms") or {}).get("terms", [])),
            keywords="; ".join(index_terms),
            publisher=item.get("publisher"),
            issn=item.get("issn"),
        )


def _elsevier_headers(credentials: Credentials) -> dict[str, str]:
    headers = {"X-ELS-APIKey": credentials.key, "Accept": "application/json"}
    if credentials.extra:
        headers["X-ELS-Insttoken"] = credentials.extra
    return headers


class ScopusConnector(Connector):
    key = "scopus"
    label = "Scopus"
    provider = "elsevier"
    key_required = True
    page_size = 25
    delay = 0.15
    syntax_help = 'Sintaxe da busca avançada do Scopus, ex.: TITLE-ABS-KEY("systematic review" AND (LLM OR "language model"))'
    SUBTYPES = {"ar": "article", "cp": "inproceedings", "ch": "inbook", "bk": "book", "re": "article"}

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        complete = bool(credentials.extra)
        params: dict[str, Any] = {"query": query, "count": self.page_size, "cursor": "*",
                                  "view": "COMPLETE" if complete else "STANDARD"}
        years = year_range(filters)
        if years:
            params["date"] = f"{years[0]}-{years[1]}"
        warnings = [] if complete else [
            "Sem token institucional, o Scopus devolve só o primeiro autor e nenhum resumo (visão STANDARD). "
            "Cadastre o insttoken no Perfil ou rode a busca na rede da instituição."]
        fetched = 0
        while fetched < limit:
            if fetched:
                self.sleep(self.delay)
            response = self.request(client, "GET", "https://api.elsevier.com/content/search/scopus", params=params,
                                    headers=_elsevier_headers(credentials))
            results = response.json().get("search-results", {})
            entries = [entry for entry in results.get("entry", []) if "error" not in entry][: limit - fetched]
            fetched += len(entries)
            total = int(results.get("opensearch:totalResults") or 0)
            yield Page(total=total, records=[self._record(entry) for entry in entries], raw=response.text,
                       warnings=warnings if fetched == len(entries) else [])
            next_cursor = (results.get("cursor") or {}).get("@next")
            if not entries or fetched >= total or not next_cursor:
                return
            params["cursor"] = next_cursor

    @classmethod
    def _record(cls, entry: dict[str, Any]) -> dict[str, str]:
        authors = [author.get("authname", "") for author in entry.get("author", [])] or [entry.get("dc:creator", "")]
        link = next((item.get("@href") for item in entry.get("link", []) if item.get("@ref") == "scopus"), "")
        return record(
            bibtex_key=entry.get("eid", "").replace("-", "_"),
            title=entry.get("dc:title"),
            author="; ".join(author for author in authors if author),
            journal=entry.get("prism:publicationName"),
            year=entry.get("prism:coverDate"),
            pages=entry.get("prism:pageRange"),
            volume=entry.get("prism:volume"),
            abstract=entry.get("dc:description"),
            document_type=cls.SUBTYPES.get(entry.get("subtype", ""), entry.get("subtypeDescription")),
            doi=entry.get("prism:doi"),
            url=link,
            affiliation="; ".join(dict.fromkeys(item.get("affilname", "") for item in entry.get("affiliation", []) if item.get("affilname"))),
            author_keywords="; ".join(clean(part) for part in str(entry.get("authkeywords") or "").split("|") if clean(part)),
            issn=entry.get("prism:issn") or entry.get("prism:eIssn"),
        )


class ScienceDirectConnector(Connector):
    key = "sciencedirect"
    label = "ScienceDirect"
    provider = "elsevier"
    key_required = True
    page_size = 100
    max_records = 6000  # the API does not page past offset 6000
    delay = 0.2
    syntax_help = 'Texto da busca do ScienceDirect (campo qs), com AND, OR, NOT, aspas e parênteses, ex.: "systematic review" AND (LLM OR "language model")'

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        body: dict[str, Any] = {"qs": query}
        years = year_range(filters)
        if years:
            body["date"] = f"{years[0]}-{years[1]}"
        warnings = ["A API de busca do ScienceDirect não devolve resumos; eles ficam vazios até a triagem."]
        fetched = 0
        while fetched < limit:
            if fetched:
                self.sleep(self.delay)
            body["display"] = {"offset": fetched, "show": min(self.page_size, limit - fetched)}
            response = self.request(client, "PUT", "https://api.elsevier.com/content/search/sciencedirect", json=body,
                                    headers=_elsevier_headers(credentials))
            data = response.json()
            results = data.get("results") or []
            fetched += len(results)
            total = data.get("resultsFound")
            yield Page(total=total, records=[self._record(item) for item in results], raw=response.text,
                       warnings=warnings if fetched == len(results) else [])
            if not results or (total is not None and fetched >= total):
                return

    @staticmethod
    def _record(item: dict[str, Any]) -> dict[str, str]:
        pages = item.get("pages") or {}
        return record(
            bibtex_key=f"sd{item.get('pii', '')}",
            title=item.get("title"),
            author="; ".join(author.get("name", "") for author in item.get("authors") or []),
            journal=item.get("publicationName"),
            year=item.get("publicationDate"),
            pages=_pages(pages.get("first"), pages.get("last")),
            volume=item.get("volumeIssue"),
            document_type="article",
            doi=item.get("doi"),
            url=item.get("uri"),
            publisher="Elsevier",
        )


class SpringerConnector(Connector):
    key = "springer"
    label = "Springer Nature"
    provider = "springer"
    key_required = True
    page_size = 25
    delay = 0.5
    syntax_help = ('Sintaxe da Springer Nature Meta API: termos com AND, OR, NOT, aspas e campos como title:, keyword:, '
                   'ex.: "systematic review" AND keyword:"machine learning"')
    CONTENT_TYPES = {"Article": "article", "Chapter": "inbook", "ConferencePaper": "inproceedings", "Book": "book"}

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        years = year_range(filters)
        if years:
            query = f"({query}) onlinedatefrom:{years[0]}-01-01 onlinedateto:{years[1]}-12-31"
        fetched = 0
        while fetched < limit:
            if fetched:
                self.sleep(self.delay)
            params = {"q": query, "api_key": credentials.key, "s": fetched + 1, "p": min(self.page_size, limit - fetched)}
            response = self.request(client, "GET", "https://api.springernature.com/meta/v2/json", params=params)
            data = response.json()
            records = data.get("records") or []
            fetched += len(records)
            summary = (data.get("result") or [{}])[0]
            total = int(summary.get("total") or 0)
            yield Page(total=total, records=[self._record(item) for item in records], raw=response.text)
            if not records or fetched >= total:
                return

    @classmethod
    def _record(cls, item: dict[str, Any]) -> dict[str, str]:
        abstract = item.get("abstract") or ""
        if isinstance(abstract, dict):
            abstract = abstract.get("p") or ""
        if isinstance(abstract, list):
            abstract = " ".join(str(part) for part in abstract)
        url = next((link.get("value") for link in item.get("url") or [] if link.get("format") in ("html", "")), "")
        return record(
            title=item.get("title"),
            author="; ".join(creator.get("creator", "") for creator in item.get("creators") or []),
            journal=item.get("publicationName"),
            year=item.get("publicationDate"),
            pages=_pages(item.get("startingPage"), item.get("endingPage")),
            volume=item.get("volume"),
            abstract=abstract,
            document_type=cls.CONTENT_TYPES.get(item.get("contentType", ""), item.get("contentType")),
            doi=item.get("doi"),
            url=url or (f"https://doi.org/{item['doi']}" if item.get("doi") else ""),
            keywords="; ".join(item.get("keyword") or []),
            publisher=item.get("publisher"),
            issn=item.get("issn") or item.get("eIssn"),
            language=item.get("language"),
        )


class WebOfScienceConnector(Connector):
    key = "wos"
    label = "Web of Science"
    provider = "clarivate"
    key_required = True
    page_size = 50
    delay = 0.5
    syntax_help = 'Sintaxe da busca avançada do Web of Science, ex.: TS=("systematic review" AND (LLM OR "language model"))'
    TYPES = {"Article": "article", "Proceedings Paper": "inproceedings", "Book Chapter": "inbook", "Review": "article"}

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        years = year_range(filters)
        if years:
            query = f"({query}) AND PY=({years[0]}-{years[1]})"
        warnings = ["A Web of Science Starter API não devolve resumos; eles ficam vazios até a triagem."]
        fetched, page = 0, 1
        while fetched < limit:
            if fetched:
                self.sleep(self.delay)
            params = {"q": query, "db": "WOS", "limit": self.page_size, "page": page}
            response = self.request(client, "GET", "https://api.clarivate.com/apis/wos-starter/v1/documents",
                                    params=params, headers={"X-ApiKey": credentials.key})
            data = response.json()
            hits = (data.get("hits") or [])[: limit - fetched]
            fetched += len(hits)
            total = (data.get("metadata") or {}).get("total")
            yield Page(total=total, records=[self._record(item) for item in hits], raw=response.text,
                       warnings=warnings if page == 1 else [])
            if not hits or (total is not None and fetched >= total):
                return
            page += 1

    @classmethod
    def _record(cls, item: dict[str, Any]) -> dict[str, str]:
        source = item.get("source") or {}
        identifiers = item.get("identifiers") or {}
        types = item.get("types") or []
        return record(
            bibtex_key=str(item.get("uid", "")).replace(":", "_"),
            title=item.get("title"),
            author="; ".join(author.get("displayName") or author.get("wosStandard", "")
                             for author in (item.get("names") or {}).get("authors") or []),
            journal=source.get("sourceTitle"),
            year=source.get("publishYear"),
            pages=(source.get("pages") or {}).get("range"),
            volume=source.get("volume"),
            document_type=cls.TYPES.get(types[0], types[0]) if types else "",
            doi=identifiers.get("doi"),
            url=(item.get("links") or {}).get("record"),
            author_keywords="; ".join((item.get("keywords") or {}).get("authorKeywords") or []),
            issn=identifiers.get("issn") or identifiers.get("eissn"),
        )
