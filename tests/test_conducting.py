"""Condução I: strings por fonte, importação, seleção, duplicados e exportação."""

import csv
import io

BIBTEX = b"""@article{doe2024,
  title = {Explainable {Multi-Agent} Systems},
  author = {Doe, Jane and Smith, Alex},
  journal = {Journal of XAI},
  year = {2024},
  volume = {12},
  pages = {1--20},
  doi = {https://doi.org/10.1234/XAI.2024.1},
  abstract = {Explanations in multi-agent systems.},
  keywords = {xai; mas}
}
@inproceedings{roe2023,
  title = {Trust in Agent Societies},
  author = {Roe, Richard},
  booktitle = {AAMAS},
  year = {2023}
}
@misc{notitle,
  author = {Nobody}
}
"""

RIS = b"""TY  - JOUR
TI  - Explainable multi-agent systems.
AU  - Doe, Jane
PY  - 2024
DO  - 10.1234/xai.2024.1
ER  -
TY  - CONF
TI  - Norms for explainable agents
AU  - Lee, Kim
PY  - 2022
SP  - 5
EP  - 9
ER  -
"""

CSV = "Title,Authors,Year,Source title,DOI\nA survey of agentic AI,\"Zhu, Y.\",2025,ACM CSUR,10.9/abc\n".encode()


def _setup(client, review):
    review_id, headers = review
    sources = client.get(f"/reviews/{review_id}/sources/suggested", headers=headers).json()
    ids = {}
    for name in ("Scopus", "IEEE Xplore"):
        source = next(item for item in sources if item["name"] == name)
        client.post(f"/reviews/{review_id}/sources", headers=headers, json={"source_id": source["id"]})
        ids[name] = source["id"]
    return review_id, headers, ids


def _import(client, review_id, headers, source_id, name, content):
    return client.post(f"/reviews/{review_id}/sources/{source_id}/import", headers=headers,
                       files={"file": (name, content, "application/octet-stream")})


def test_search_strings_per_source(client, review):
    review_id, headers, ids = _setup(client, review)
    client.put(f"/reviews/{review_id}/search-string", headers=headers, json={"search_string": "XAI AND MAS"})
    saved = client.put(f"/reviews/{review_id}/search/{ids['Scopus']}", headers=headers,
                       json={"search_string": "TITLE-ABS-KEY(XAI AND MAS)"})
    assert saved.json()["version"] == 1
    search = client.get(f"/reviews/{review_id}/search", headers=headers).json()
    assert search["base_string"] == "XAI AND MAS"
    by_source = {item["source"]["name"]: item["search_string"] for item in search["sources"]}
    assert by_source == {"IEEE Xplore": "", "Scopus": "TITLE-ABS-KEY(XAI AND MAS)"}
    assert client.put(f"/reviews/{review_id}/search/999", headers=headers, json={"search_string": "x"}).status_code == 404


def test_import_bibtex_ris_csv_and_summary(client, review, tmp_path):
    review_id, headers, ids = _setup(client, review)
    bib = _import(client, review_id, headers, ids["Scopus"], "scopus.bib", BIBTEX)
    assert bib.status_code == 201, bib.text
    assert (bib.json()["imported"], bib.json()["skipped_without_title"]) == (2, 1)
    assert _import(client, review_id, headers, ids["IEEE Xplore"], "ieee.ris", RIS).json()["imported"] == 2
    assert _import(client, review_id, headers, ids["IEEE Xplore"], "acm.csv", CSV).json()["imported"] == 1
    assert _import(client, review_id, headers, ids["Scopus"], "x.pdf", b"%PDF").status_code == 422

    articles = client.get(f"/reviews/{review_id}/articles?sort=title", headers=headers).json()
    assert articles["total"] == 5
    doe = next(item for item in articles["items"] if item["bibtex_key"] == "doe2024")
    assert (doe["title"], doe["doi"], doe["pages"], doe["journal"]) == (
        "Explainable Multi-Agent Systems", "10.1234/xai.2024.1", "1--20", "Journal of XAI")
    norms = next(item for item in articles["items"] if item["title"] == "Norms for explainable agents")
    assert norms["pages"] == "5-9"

    summary = {item["source"]["name"]: item for item in client.get(f"/reviews/{review_id}/imports", headers=headers).json()}
    assert summary["Scopus"]["articles"] == 2
    assert [item["file_name"] for item in summary["IEEE Xplore"]["files"]] == ["acm.csv", "ieee.ris"]
    assert len(list((tmp_path / "storage" / "reviews" / str(review_id)).iterdir())) == 3


def test_selection_filters_update_bulk_and_criteria(client, review):
    review_id, headers, ids = _setup(client, review)
    _import(client, review_id, headers, ids["Scopus"], "scopus.bib", BIBTEX)
    _import(client, review_id, headers, ids["IEEE Xplore"], "ieee.ris", RIS)
    exclusion = client.post(f"/reviews/{review_id}/criteria", headers=headers,
                            json={"criteria_type": "E", "description": "Fora do tema"}).json()
    items = client.get(f"/reviews/{review_id}/articles", headers=headers).json()["items"]

    rejected = client.patch(f"/reviews/{review_id}/articles/{items[0]['id']}", headers=headers,
                            json={"status": "R", "selection_criteria_id": exclusion["id"], "comments": "Sem MAS."})
    assert (rejected.json()["status_label"], rejected.json()["selection_criteria_id"]) == ("Rejeitado", exclusion["id"])
    assert client.patch(f"/reviews/{review_id}/articles/{items[1]['id']}", headers=headers,
                        json={"selection_criteria_id": 9999}).status_code == 404

    bulk = client.post(f"/reviews/{review_id}/articles/bulk", headers=headers,
                       json={"ids": [items[1]["id"], items[2]["id"], 99999], "action": "accept"})
    assert bulk.json() == {"affected": 2}
    listing = client.get(f"/reviews/{review_id}/articles?status=A", headers=headers).json()
    assert listing["total"] == 2
    assert listing["status_counts"] == {"U": 1, "A": 2, "R": 1, "D": 0}
    assert client.get(f"/reviews/{review_id}/articles?source_id={ids['Scopus']}", headers=headers).json()["total"] == 2
    assert client.get(f"/reviews/{review_id}/articles?q=norms", headers=headers).json()["total"] == 1

    page = client.get(f"/reviews/{review_id}/articles?page=2&page_size=3&sort=year&order=desc", headers=headers).json()
    assert (len(page["items"]), len(page["ids"])) == (1, 4)

    client.post(f"/reviews/{review_id}/articles/bulk", headers=headers, json={"ids": [items[3]["id"]], "action": "remove"})
    assert client.get(f"/reviews/{review_id}/articles", headers=headers).json()["total"] == 3


def test_find_and_resolve_duplicates(client, review):
    review_id, headers, ids = _setup(client, review)
    _import(client, review_id, headers, ids["Scopus"], "scopus.bib", BIBTEX)
    _import(client, review_id, headers, ids["IEEE Xplore"], "ieee.ris", RIS)
    groups = client.post(f"/reviews/{review_id}/articles/find-duplicates", headers=headers).json()
    assert len(groups) == 1
    titles = sorted(item["title"] for item in groups[0]["articles"])
    assert titles == ["Explainable Multi-Agent Systems", "Explainable multi-agent systems."]

    keep, duplicate = (item["id"] for item in groups[0]["articles"])
    resolved = client.post(f"/reviews/{review_id}/articles/resolve-duplicates", headers=headers,
                           json=[{"keep_id": keep, "duplicate_ids": [duplicate]}])
    assert resolved.json() == {"marked": 1}
    assert client.post(f"/reviews/{review_id}/articles/find-duplicates", headers=headers).json() == []
    assert client.get(f"/reviews/{review_id}/articles?status=D", headers=headers).json()["total"] == 1


def test_manual_article_and_exports(client, review):
    review_id, headers, ids = _setup(client, review)
    created = client.post(f"/reviews/{review_id}/articles", headers=headers, json={
        "source_id": ids["Scopus"], "title": "Manual entry on {XAI}", "author": "Silva, A.", "year": "2021",
        "doi": "doi: 10.5/Manual"})
    assert created.status_code == 201
    assert created.json()["doi"] == "10.5/manual"
    client.patch(f"/reviews/{review_id}/articles/{created.json()['id']}", headers=headers, json={"status": "A"})
    _import(client, review_id, headers, ids["Scopus"], "scopus.bib", BIBTEX)

    bibtex = client.get(f"/reviews/{review_id}/articles-export?format=bibtex&status=A", headers=headers)
    assert bibtex.headers["content-type"].startswith("application/x-bibtex")
    assert bibtex.text.count("@") == 1
    assert "title = {Manual entry on XAI}" in bibtex.text

    exported = client.get(f"/reviews/{review_id}/articles-export?format=csv", headers=headers)
    rows = list(csv.DictReader(io.StringIO(exported.text)))
    assert len(rows) == 3
    assert {row["status"] for row in rows} == {"Aceito", "Não classificado"}
