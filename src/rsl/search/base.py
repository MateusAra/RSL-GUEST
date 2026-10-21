"""Common pieces of the search connectors: pages, errors, retries and pacing."""

from __future__ import annotations

import re
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..importers import finalize_record

USER_AGENT = "RSL-systematic-review-tool/1.0 (+https://github.com/MateusAra/RSL-GUEST)"
RETRY_STATUSES = {429, 500, 502, 503, 504}


class SearchError(Exception):
    """Failure shown to the researcher as is (Portuguese)."""


@dataclass
class Filters:
    year_from: int | None = None
    year_to: int | None = None


@dataclass
class Credentials:
    key: str = ""
    extra: str = ""


@dataclass
class Page:
    total: int | None
    records: list[dict[str, str]]
    raw: str
    warnings: list[str] = field(default_factory=list)


def clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def record(**values: Any) -> dict[str, str]:
    """An article dictionary in the importer format (same limits and DOI normalization)."""
    return finalize_record({key: clean(value) for key, value in values.items()})


def year_range(filters: Filters) -> tuple[int, int] | None:
    if filters.year_from is None and filters.year_to is None:
        return None
    return filters.year_from or 1900, filters.year_to or 2100


class Connector:
    key: str = ""
    label: str = ""
    provider: str | None = None  # rsl.search.PROVIDERS entry whose key the connector uses
    key_required: bool = False
    page_size: int = 100
    max_records: int = 5000
    delay: float = 1.0  # seconds between requests, per the provider's usage policy
    syntax_help: str = ""
    notice: str = ""

    def __init__(self, sleep: Callable[[float], None] = time.sleep) -> None:
        self.sleep = sleep

    def pages(self, client: httpx.Client, query: str, filters: Filters, credentials: Credentials,
              limit: int) -> Iterator[Page]:
        raise NotImplementedError

    def request(self, client: httpx.Client, method: str, url: str, attempts: int = 4, **kwargs: Any) -> httpx.Response:
        headers = {"User-Agent": USER_AGENT, **kwargs.pop("headers", {})}
        for attempt in range(attempts):
            try:
                response = client.request(method, url, headers=headers, timeout=60, **kwargs)
            except httpx.TransportError as exc:
                if attempt == attempts - 1:
                    raise SearchError(f"Não foi possível conectar ao {self.label}: {exc.__class__.__name__}.") from exc
                self.sleep(2 ** attempt * 2)
                continue
            if response.status_code in RETRY_STATUSES and attempt < attempts - 1:
                retry_after = response.headers.get("Retry-After", "")
                self.sleep(float(retry_after) if retry_after.isdigit() else 2 ** attempt * 2)
                continue
            self.check(response)
            return response
        raise AssertionError("unreachable")

    def check(self, response: httpx.Response) -> None:
        status = response.status_code
        if status < 400:
            return
        if status in (401, 403):
            raise SearchError(f"O {self.label} recusou a chave de API (inválida, expirada ou sem permissão para esta busca).")
        if status == 429:
            raise SearchError(f"O {self.label} limitou as requisições (cota esgotada). Tente mais tarde ou reduza o limite.")
        if status == 400:
            detail = clean(response.text)[:300]
            raise SearchError(f"O {self.label} não aceitou a string de busca (sintaxe inválida para a base). {detail}".strip())
        raise SearchError(f"O {self.label} respondeu com erro {status}. Tente novamente mais tarde.")
