"""Automated searches: one connector per digital library API."""

from __future__ import annotations

from .base import Connector, Credentials, Filters, Page, SearchError
from .keyed_sources import IeeeConnector, ScienceDirectConnector, ScopusConnector, SpringerConnector, WebOfScienceConnector
from .open_sources import AcmOpenAlexConnector, ArxivConnector, OpenAlexConnector, SemanticScholarConnector

CONNECTORS: dict[str, type[Connector]] = {
    connector.key: connector
    for connector in (IeeeConnector, ScopusConnector, ScienceDirectConnector, SpringerConnector, WebOfScienceConnector,
                      ArxivConnector, AcmOpenAlexConnector, OpenAlexConnector, SemanticScholarConnector)
}
# Connectors a custom (non-default) source may use.
CUSTOM_CONNECTORS = ("openalex", "semantic_scholar")
# Connector of each suggested digital library (Source.name of the seeded sources).
DEFAULT_SOURCE_CONNECTORS = {
    "ACM Digital Library": "acm_openalex",
    "IEEE Xplore": "ieee",
    "ScienceDirect": "sciencedirect",
    "Scopus": "scopus",
    "SpringerLink": "springer",
    "Web of Science": "wos",
    "arXiv": "arxiv",
}

PROVIDERS = {
    "ieee": {"label": "IEEE Xplore API", "url": "https://developer.ieee.org/", "required": True, "extra": None,
             "test_connector": "ieee"},
    "elsevier": {"label": "Elsevier (Scopus e ScienceDirect)", "url": "https://dev.elsevier.com/", "required": True,
                 "extra": "Token institucional (insttoken), opcional", "test_connector": "scopus"},
    "springer": {"label": "Springer Nature API", "url": "https://dev.springernature.com/", "required": True, "extra": None,
                 "test_connector": "springer"},
    "clarivate": {"label": "Web of Science Starter API", "url": "https://developer.clarivate.com/apis/wos-starter",
                  "required": True, "extra": None, "test_connector": "wos"},
    "semantic_scholar": {"label": "Semantic Scholar", "url": "https://www.semanticscholar.org/product/api",
                         "required": False, "extra": None, "test_connector": "semantic_scholar"},
    "openalex": {"label": "OpenAlex", "url": "https://openalex.org/settings/api", "required": False, "extra": None,
                 "test_connector": "openalex"},
}


def connector_info(key: str) -> dict[str, object]:
    connector = CONNECTORS[key]
    return {
        "key": connector.key, "label": connector.label, "provider": connector.provider,
        "key_required": connector.key_required, "max_records": connector.max_records,
        "syntax_help": connector.syntax_help, "notice": connector.notice,
    }


__all__ = ["CONNECTORS", "CUSTOM_CONNECTORS", "DEFAULT_SOURCE_CONNECTORS", "PROVIDERS", "Connector", "Credentials",
           "Filters", "Page", "SearchError", "connector_info"]
