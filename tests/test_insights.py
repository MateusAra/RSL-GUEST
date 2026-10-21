"""Análises (spec 008 adaptada): bibliometria, campos, hipóteses ponderadas, sensibilidade e instantâneos."""

import pytest

BIBTEX = b"""@article{a1, title={Alpha}, author={Ana Lima and Bruno Reis}, journal={J. XAI}, year={2019}, keywords={xai; trust}}
@inproceedings{a2, title={Beta}, author={Ana Lima and Carla Dias}, booktitle={AAMAS}, year={2021}, keywords={XAI, agents}}
@article{a3, title={Gamma}, author={Ana Lima}, journal={J. XAI}, year={2023}, keywords={trust}}
@misc{a4, title={Delta}, author={Diego Melo}, journal={arXiv}, year={2024}}
"""


@pytest.fixture
def corpus(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}"
    sources = {item["name"]: item["id"] for item in client.get(f"{base}/sources/suggested", headers=headers).json()}
    for name in ("Scopus", "IEEE Xplore"):
        client.post(f"{base}/sources", headers=headers, json={"source_id": sources[name]})
    client.post(f"{base}/sources/{sources['Scopus']}/import", headers=headers,
                files={"file": ("s.bib", BIBTEX, "application/octet-stream")})
    articles = {item["title"]: item["id"] for item in client.get(f"{base}/articles", headers=headers).json()["items"]}
    client.post(f"{base}/articles/bulk", headers=headers, json={"ids": list(articles.values()), "action": "accept"})
    # Quality: 2 questions, max score 2 → Alpha 100%, Beta 50%, Gamma 50%, Delta 100%.
    questions = [client.post(f"{base}/quality-questions", headers=headers, json={"description": q}).json()["id"] for q in ("Q1", "Q2")]
    answers = {item["description"]: item["id"] for item in client.post(f"{base}/quality-answers/suggested", headers=headers).json()}
    plan = {"Alpha": ("Sim", "Sim"), "Beta": ("Sim", "Não"), "Gamma": ("Parcialmente", "Parcialmente"), "Delta": ("Sim", "Sim")}
    for title, labels in plan.items():
        for question, label in zip(questions, labels):
            client.put(f"{base}/articles/{articles[title]}/quality", headers=headers,
                       json={"question_id": question, "answer_id": answers[label]})
    return base, headers, articles, sources


def test_bibliometrics_and_author_concentration(client, corpus):
    base, headers, _, _ = corpus
    data = client.get(f"{base}/insights", headers=headers).json()
    biblio = data["bibliometrics"]
    assert data["corpus"] == 4
    assert [item["label"] for item in biblio["per_year"]] == ["2019", "2021", "2023", "2024"]
    assert {item["label"]: item["count"] for item in biblio["per_category"]} == {"Periódico": 2, "Evento": 1, "Pré-print": 1}
    assert biblio["top_keywords"][:2] == [{"label": "trust", "count": 2}, {"label": "xai", "count": 2}]
    assert biblio["top_authors"][0] == {"label": "Ana Lima", "count": 3}
    assert {"label": "Ana Lima & Bruno Reis", "count": 1} in biblio["coauthor_pairs"]
    assert biblio["author_concentration"] == [{"author": "Ana Lima", "count": 3, "pct": 75.0}]
    assert data["quality_bands"] == {"high": 2, "moderate": 2, "low": 0, "none": 0}


def test_hypotheses_weighted_synthesis_keeps_inconclusive(client, corpus):
    base, headers, articles, _ = corpus
    hypothesis = client.post(f"{base}/hypotheses", headers=headers, json={
        "code": "H1", "statement": "XAI aumenta a confiança", "independent_variables": "XAI",
        "dependent_variables": "confiança"}).json()
    url = lambda title: f"{base}/articles/{articles[title]}/verdicts/{hypothesis['id']}"  # noqa: E731
    assert client.put(url("Alpha"), headers=headers, json={"verdict": "supports", "justification": ""}).status_code == 422
    assert client.put(url("Alpha"), headers=headers, json={"verdict": "maybe", "justification": "x"}).status_code == 422
    for title, verdict in (("Alpha", "supports"), ("Beta", "supports"), ("Gamma", "inconclusive")):
        assert client.put(url(title), headers=headers, json={"verdict": verdict, "justification": "Seção 5"}).status_code == 200

    synthesis = client.get(f"{base}/insights", headers=headers).json()["hypotheses"][0]
    verdicts = {item["verdict"]: item for item in synthesis["verdicts"]}
    assert (synthesis["rated"], synthesis["missing"]) == (3, 1)
    assert (verdicts["supports"]["count"], verdicts["inconclusive"]["count"]) == (2, 1)
    assert verdicts["inconclusive"]["pct"] == pytest.approx(33.3)
    # Alpha (100%) weighs 1.0, Beta and Gamma (50%) weigh 0.5.
    assert (verdicts["supports"]["weighted"], verdicts["inconclusive"]["weighted"]) == (1.5, 0.5)
    assert verdicts["supports"]["weighted_pct"] == 75.0
    assert verdicts["supports"]["moderate_band"] == 1

    assert client.put(url("Gamma"), headers=headers, json={"verdict": None}).json()["verdict"] is None
    assert client.get(f"{base}/verdicts", headers=headers).json()[str(articles["Alpha"])][str(hypothesis["id"])]["verdict"] == "supports"


def test_sensitivity_filters_reapply_without_changing_data(client, corpus):
    base, headers, articles, sources = corpus
    high_quality = client.get(f"{base}/insights?min_quality_pct=70", headers=headers).json()
    assert high_quality["corpus"] == 2
    assert high_quality["comparison"]["corpus"] == 4
    assert client.get(f"{base}/insights?year_from=2021&year_to=2023", headers=headers).json()["corpus"] == 2
    assert client.get(f"{base}/insights?categories=journal,conference", headers=headers).json()["corpus"] == 3
    assert client.get(f"{base}/insights?source_ids={sources['IEEE Xplore']}", headers=headers).json()["corpus"] == 0
    assert client.get(f"{base}/insights", headers=headers).json()["corpus"] == 4
    assert client.get(f"{base}/articles?status=A", headers=headers).json()["total"] == 4


def test_field_frequency_and_crosstab(client, corpus):
    base, headers, articles, _ = corpus
    domain = client.post(f"{base}/extraction-fields", headers=headers,
                         json={"description": "Domínio", "field_type": "O", "lookups": ["Saúde", "Indústria"]}).json()
    validated = client.post(f"{base}/extraction-fields", headers=headers, json={"description": "Validado", "field_type": "B"}).json()
    lookups = {item["value"]: item["id"] for item in domain["lookups"]}
    for title, area, flag in (("Alpha", "Saúde", "True"), ("Beta", "Saúde", "False"), ("Gamma", "Indústria", "True")):
        client.put(f"{base}/articles/{articles[title]}/extraction", headers=headers, json={"field_id": domain["id"], "value": lookups[area]})
        client.put(f"{base}/articles/{articles[title]}/extraction", headers=headers, json={"field_id": validated["id"], "value": flag})

    fields = {item["field"]: item for item in client.get(f"{base}/insights", headers=headers).json()["fields"]}
    assert fields["Domínio"]["values"] == [{"label": "Saúde", "count": 2}, {"label": "Indústria", "count": 1}]
    assert fields["Domínio"]["unanswered"] == 1
    table = client.get(f"{base}/insights/crosstab?field_a={domain['id']}&field_b={validated['id']}", headers=headers).json()
    assert (table["rows"], table["columns"], table["matrix"]) == (["Indústria", "Saúde"], ["Não", "Sim"], [[0, 1], [1, 1]])
    assert client.get(f"{base}/insights/crosstab?field_a={domain['id']}&field_b={domain['id']}", headers=headers).status_code == 422


def test_weighting_settings_and_immutable_snapshots(client, corpus, signup):
    base, headers, articles, _ = corpus
    assert client.put(f"{base}/analysis-settings", headers=headers, json={
        "high_min_pct": 50, "high_weight": 1, "moderate_min_pct": 60, "moderate_weight": 0.5,
        "author_concentration_pct": 20}).status_code == 422
    client.put(f"{base}/analysis-settings", headers=headers, json={
        "high_min_pct": 90, "high_weight": 1, "moderate_min_pct": 40, "moderate_weight": 0.25, "author_concentration_pct": 80})
    first = client.post(f"{base}/insights/snapshots", headers=headers, json={"label": "Antes", "filters": {"min_quality_pct": 70}}).json()
    assert (first["corpus"], first["settings"]["moderate_weight"]) == (2, 0.25)

    client.post(f"{base}/articles/bulk", headers=headers, json={"ids": [articles["Alpha"]], "action": "reject"})
    stored = client.get(f"{base}/insights/snapshots/{first['id']}", headers=headers).json()
    assert stored["results"]["corpus"] == 2
    assert client.get(f"{base}/insights?min_quality_pct=70", headers=headers).json()["corpus"] == 1
    assert [item["label"] for item in client.get(f"{base}/insights/snapshots", headers=headers).json()] == ["Antes"]
    assert client.get(f"{base}/insights/snapshots/{first['id']}", headers=signup("fora")).status_code == 404
