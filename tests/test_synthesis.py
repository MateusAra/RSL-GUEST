"""Síntese temática (spec 007 adaptada): codebook, trechos, dupla codificação, temas e checklist."""

import csv
import io
import json

import numpy as np
import pytest

from rsl.agreement import cohen_kappa, coding_agreement, krippendorff_alpha

BIBTEX = b"""@article{a1, title={Alpha study}, year={2021}}
@article{a2, title={Beta study}, year={2022}}
@article{a3, title={Gamma study}, year={2023}}
"""


@pytest.fixture
def team(client, review, signup):
    """Review with an accepted corpus and a co-author (Bruno)."""
    review_id, owner = review
    base = f"/reviews/{review_id}"
    bruno = signup("bruno")
    code = client.post(f"{base}/invites", headers=owner, json={"email": "bruno@example.com"}).json()["code"]
    client.post(f"/invites/{code}/accept", headers=bruno)
    scopus = next(item for item in client.get(f"{base}/sources/suggested", headers=owner).json() if item["name"] == "Scopus")
    client.post(f"{base}/sources", headers=owner, json={"source_id": scopus["id"]})
    client.post(f"{base}/sources/{scopus['id']}/import", headers=owner,
                files={"file": ("s.bib", BIBTEX, "application/octet-stream")})
    articles = {item["title"]: item["id"] for item in client.get(f"{base}/articles", headers=owner).json()["items"]}
    client.post(f"{base}/articles/bulk", headers=owner, json={"ids": list(articles.values()), "action": "accept"})
    ids = {name: client.get("/me", headers=headers).json()["id"] for name, headers in (("owner", owner), ("bruno", bruno))}
    return {"base": base, "owner": owner, "bruno": bruno, "articles": articles, "ids": ids}


def _active_code(client, team, name, headers=None):
    headers = headers or team["owner"]
    code = client.post(f"{team['base']}/codes", headers=headers,
                       json={"name": name, "definition": f"Definição de {name}", "limits": f"Limites de {name}"}).json()
    assert client.post(f"{team['base']}/codes/{code['id']}/activate", headers=headers).status_code == 200
    return code["id"]


def _manual_alpha(first, second):
    """Independent nominal Krippendorff's alpha (2 coders, no missing data) via the coincidence matrix."""
    values = sorted(set(first) | set(second))
    index = {value: position for position, value in enumerate(values)}
    coincidence = np.zeros((len(values), len(values)))
    for a, b in zip(first, second):
        coincidence[index[a], index[b]] += 1
        coincidence[index[b], index[a]] += 1
    totals = coincidence.sum(axis=1)
    n = totals.sum()
    observed = coincidence.sum() - np.trace(coincidence)
    expected = (n * n - (totals ** 2).sum()) / (n - 1)
    return 1 - observed / expected


def _manual_kappa(first, second):
    labels = sorted(set(first) | set(second))
    n = len(first)
    observed = sum(a == b for a, b in zip(first, second)) / n
    expected = sum((first.count(label) / n) * (second.count(label) / n) for label in labels)
    return (observed - expected) / (1 - expected)


@pytest.mark.parametrize(("first", "second"), [
    ([1, 1, 0, 0, 1, 0, 1, 1], [1, 0, 0, 0, 1, 0, 1, 1]),
    ([2, 3, 3, 1, 2, 2, 3, 1, 1], [2, 3, 1, 1, 2, 3, 3, 1, 2]),
    ([0, 1, 0, 1, 0, 1], [1, 0, 1, 0, 1, 0]),
])
def test_agreement_matches_manual_reference(first, second):
    assert krippendorff_alpha(first, second) == pytest.approx(_manual_alpha(first, second), abs=0.001)
    assert cohen_kappa(first, second) == pytest.approx(_manual_kappa(first, second), abs=0.001)


def test_agreement_uses_alpha_with_multiple_codes_and_kappa_when_exclusive():
    multi = coding_agreement({1: {10, 11}, 2: {10}}, {1: {10}, 2: {10}}, [10, 11])
    assert (multi["metric"], multi["kappa"]) == ("alpha", None)
    exclusive = coding_agreement({1: {10}, 2: {11}, 3: {10}}, {1: {10}, 2: {11}, 3: {11}}, [10, 11])
    assert exclusive["metric"] == "kappa"
    assert exclusive["agreed_segments"] == 2


def test_start_list_import_activation_and_rename_history(client, team):
    base, owner = team["base"], team["owner"]
    client.post(f"{base}/extraction-fields", headers=owner,
                json={"description": "Domínio", "field_type": "M", "lookups": ["Saúde", "Indústria"]})
    assert client.post(f"{base}/codes/import-start-list", headers=owner).json() == {"created": 2}
    assert client.post(f"{base}/codes/import-start-list", headers=owner).json() == {"created": 0}
    codes = client.get(f"{base}/codes", headers=owner).json()
    assert [(item["name"], item["kind"], item["status"]) for item in codes] == [
        ("Domínio: Indústria", "deductive", "draft"), ("Domínio: Saúde", "deductive", "draft")]

    code_id = codes[0]["id"]
    assert client.post(f"{base}/codes/{code_id}/activate", headers=owner).status_code == 422
    client.patch(f"{base}/codes/{code_id}", headers=owner, json={"definition": "Aplicação industrial", "limits": "Não inclui serviços"})
    assert client.post(f"{base}/codes/{code_id}/activate", headers=owner).json()["status"] == "active"

    assert client.patch(f"{base}/codes/{code_id}", headers=owner, json={"name": "Indústria 4.0"}).status_code == 422
    renamed = client.patch(f"{base}/codes/{code_id}", headers=owner,
                           json={"name": "Indústria 4.0", "justification": "Termo mais preciso"})
    assert renamed.json()["name"] == "Indústria 4.0"
    history = client.get(f"{base}/codes/{code_id}/history", headers=owner).json()
    last = history[-1]
    assert (last["action"], last["previous"]["name"], last["new"]["name"], last["justification"], last["user"]) == (
        "renamed", "Domínio: Indústria", "Indústria 4.0", "Termo mais preciso", "dona")


def test_segments_require_page_and_final_corpus(client, team, signup):
    base, owner, articles = team["base"], team["owner"], team["articles"]
    code_id = _active_code(client, team, "Transparência")
    url = f"{base}/articles/{articles['Alpha study']}/segments"
    assert client.post(url, headers=owner, json={"text": "trecho", "page": "", "code_ids": [code_id]}).status_code == 422
    created = client.post(url, headers=owner, json={"text": "  trecho exato  ", "page": "4", "code_ids": [code_id]})
    assert created.status_code == 201
    assert (created.json()["text"], created.json()["codes"]["final"]) == ("trecho exato", [code_id])

    client.post(f"{base}/articles/bulk", headers=owner, json={"ids": [articles["Gamma study"]], "action": "reject"})
    assert client.post(f"{base}/articles/{articles['Gamma study']}/segments", headers=owner,
                       json={"text": "x", "page": "1"}).status_code == 422
    draft = client.post(f"{base}/codes", headers=owner, json={"name": "Rascunho"}).json()
    assert client.put(f"{base}/segments/{created.json()['id']}/codes", headers=owner,
                      json={"code_ids": [draft["id"]]}).status_code == 422
    assert client.get(url, headers=signup("intruso")).status_code == 404


def test_merge_keeps_segments_and_origin_and_remove_requires_migration(client, team):
    base, owner, articles = team["base"], team["owner"], team["articles"]
    first, second, third = (_active_code(client, team, name) for name in ("Explicação local", "Explicação pontual", "Confiança"))
    for title, code_id in (("Alpha study", first), ("Beta study", second)):
        client.post(f"{base}/articles/{articles[title]}/segments", headers=owner,
                    json={"text": f"trecho {title}", "page": "2", "code_ids": [code_id]})
    merged = client.post(f"{base}/codes/merge", headers=owner, json={
        "code_ids": [first, second], "name": "Explicação local", "definition": "Explica uma decisão",
        "limits": "Não cobre o modelo inteiro", "justification": "Códigos redundantes"})
    assert merged.status_code == 201
    assert merged.json()["segments"] == 2
    codes = {item["id"]: item for item in client.get(f"{base}/codes", headers=owner).json()}
    assert codes[first]["status"] == codes[second]["status"] == "merged"
    history = client.get(f"{base}/codes/{merged.json()['id']}/history", headers=owner).json()
    assert {event["code_id"] for event in history} >= {first, second, merged.json()["id"]}
    assert history[-1]["previous"] == {"absorbed": ["Explicação local", "Explicação pontual"]}

    assert client.post(f"{base}/codes/{merged.json()['id']}/remove", headers=owner, json={}).status_code == 422
    removed = client.post(f"{base}/codes/{merged.json()['id']}/remove", headers=owner, json={"migrate_to_id": third})
    assert removed.json()["status"] == "removed"
    assert {item["id"]: item for item in client.get(f"{base}/codes", headers=owner).json()}[third]["segments"] == 2


def test_themes_need_codes_and_show_evidence(client, team):
    base, owner, articles = team["base"], team["owner"], team["articles"]
    trust, xai = _active_code(client, team, "Confiança"), _active_code(client, team, "XAI")
    client.post(f"{base}/articles/{articles['Alpha study']}/segments", headers=owner,
                json={"text": "Agents explain their plans", "page": "7", "code_ids": [trust]})
    assert client.post(f"{base}/themes", headers=owner, json={"name": "Vazio"}).status_code == 422
    theme = client.post(f"{base}/themes", headers=owner, json={"name": "Confiança explicável", "code_ids": [trust]}).json()
    evidence = theme["codes"][0]["evidence"][0]
    assert (evidence["text"], evidence["page"], evidence["article_title"]) == ("Agents explain their plans", "7", "Alpha study")

    other = client.post(f"{base}/themes", headers=owner, json={"name": "Técnicas", "code_ids": [xai]}).json()
    assert client.post(f"{base}/themes/{other['id']}/codes", headers=owner, json={"code_id": trust}).status_code == 422
    assert client.post(f"{base}/themes/{other['id']}/codes", headers=owner,
                       json={"code_id": trust, "justification": "Aparece nos dois sentidos"}).status_code == 201
    assert client.delete(f"{base}/themes/{theme['id']}/codes/{trust}", headers=owner).status_code == 422

    higher = client.post(f"{base}/themes", headers=owner, json={"name": "Sistemas confiáveis",
                                                              "child_theme_ids": [theme["id"], other["id"]]}).json()
    themes = {item["id"]: item for item in client.get(f"{base}/themes", headers=owner).json()}
    assert themes[theme["id"]]["parent_id"] == themes[other["id"]]["parent_id"] == higher["id"]
    assert client.patch(f"{base}/themes/{higher['id']}", headers=owner, json={"parent_id": theme["id"]}).status_code == 422


def test_dual_coding_is_blind_measures_agreement_and_resolves(client, team, signup):
    base, owner, bruno, ids = team["base"], team["owner"], team["bruno"], team["ids"]
    first, second = _active_code(client, team, "Confiança"), _active_code(client, team, "XAI")
    assert client.put(f"{base}/coding/settings", headers=bruno, json={"dual_enabled": True}).status_code == 403
    assert client.put(f"{base}/coding/settings", headers=owner, json={"dual_enabled": True, "coder_a_id": ids["owner"],
                                                                     "coder_b_id": ids["owner"]}).status_code == 422
    settings = client.put(f"{base}/coding/settings", headers=owner, json={
        "dual_enabled": True, "sample_percent": 34, "coder_a_id": ids["owner"], "coder_b_id": ids["bruno"]}).json()
    assert len(settings["sample"]) == 2
    sample_id = settings["sample"][0]["article_id"]
    url = f"{base}/articles/{sample_id}/segments"

    segments = [client.post(url, headers=owner, json={"text": f"trecho {n}", "page": str(n), "code_ids": [first]}).json()
                for n in range(1, 4)]
    hidden = client.get(url, headers=bruno).json()
    assert all("coder_a" not in item["codes"] and item["codes"]["mine"] == [] for item in hidden)
    for segment, codes in zip(segments, ([first], [first], [second])):
        client.put(f"{base}/segments/{segment['id']}/codes", headers=bruno, json={"code_ids": codes})
    assert client.post(url, headers=signup("terceira"), json={"text": "x", "page": "1"}).status_code == 404

    client.post(f"{base}/coding/sample/{sample_id}/done", headers=owner)
    client.post(f"{base}/coding/sample/{sample_id}/done", headers=bruno)
    assert client.put(f"{base}/segments/{segments[0]['id']}/codes", headers=bruno, json={"code_ids": []}).status_code == 409
    visible = {item["id"]: item["codes"] for item in client.get(url, headers=bruno).json()}
    assert visible[segments[2]["id"]]["coder_a"] == [first]
    assert visible[segments[0]["id"]]["final"] == [first]

    agreement = client.get(f"{base}/coding/agreement", headers=owner).json()
    assert (agreement["metric"], agreement["segments"], agreement["agreed_segments"]) == ("kappa", 3, 2)
    assert [item["segment_id"] for item in agreement["divergences"]] == [segments[2]["id"]]
    assert client.post(f"{base}/segments/{segments[2]['id']}/resolve", headers=owner,
                       json={"code_ids": [second]}).status_code == 422
    client.post(f"{base}/segments/{segments[2]['id']}/resolve", headers=owner,
                json={"code_ids": [second], "justification": "Discutido: trata de técnica"})
    assert client.get(f"{base}/coding/agreement", headers=owner).json()["divergences"][0]["resolved"] is True


def test_closing_requires_verified_codebook_and_locks_changes(client, team):
    base, owner, bruno = team["base"], team["owner"], team["bruno"]
    _active_code(client, team, "Confiança")
    blocked = client.post(f"{base}/coding/close", headers=owner, json={})
    assert blocked.status_code == 422
    assert "conferido" in blocked.json()["detail"]
    assert client.post(f"{base}/coding/verify-codebook", headers=owner).status_code == 422
    assert client.post(f"{base}/coding/verify-codebook", headers=bruno).json()["codebook_verified_by_id"] == team["ids"]["bruno"]
    assert client.post(f"{base}/coding/close", headers=owner, json={}).status_code == 200
    assert client.post(f"{base}/codes", headers=owner, json={"name": "Novo"}).status_code == 409
    assert client.post(f"{base}/coding/reopen", headers=bruno).status_code == 403
    assert client.post(f"{base}/coding/reopen", headers=owner).status_code == 200
    assert client.post(f"{base}/codes", headers=owner, json={"name": "Novo"}).status_code == 201


def test_dual_coding_below_threshold_needs_justification_to_close(client, team):
    base, owner, bruno, ids = team["base"], team["owner"], team["bruno"], team["ids"]
    first, second = _active_code(client, team, "A"), _active_code(client, team, "B", headers=bruno)
    sample_id = client.put(f"{base}/coding/settings", headers=owner, json={
        "dual_enabled": True, "sample_percent": 10, "coder_a_id": ids["owner"], "coder_b_id": ids["bruno"]}).json()["sample"][0]["article_id"]
    for number in range(4):
        segment = client.post(f"{base}/articles/{sample_id}/segments", headers=owner,
                              json={"text": f"t{number}", "page": "1", "code_ids": [first if number % 2 else second]}).json()
        client.put(f"{base}/segments/{segment['id']}/codes", headers=bruno, json={"code_ids": [second if number % 2 else first]})
    for headers in (owner, bruno):
        client.post(f"{base}/coding/sample/{sample_id}/done", headers=headers)
    client.post(f"{base}/coding/verify-codebook", headers=bruno)
    agreement = client.get(f"{base}/coding/agreement", headers=owner).json()
    assert agreement["below_threshold"] is True
    refused = client.post(f"{base}/coding/close", headers=owner, json={})
    assert "abaixo de 0.6" in refused.json()["detail"]
    closed = client.post(f"{base}/coding/close", headers=owner, json={"justification": "Amostra pequena; discutido em reunião"})
    assert closed.status_code == 200
    assert len(closed.json()["problems"]) == 2


def test_event_log_export_is_complete(client, team):
    base, owner = team["base"], team["owner"]
    code_id = _active_code(client, team, "Confiança")
    client.patch(f"{base}/codes/{code_id}", headers=owner, json={"definition": "Nova", "justification": "Ajuste"})
    events = json.loads(client.get(f"{base}/coding/events?format=json", headers=owner).text)
    assert [event["action"] for event in events] == ["created", "activated", "redefined"]
    sequences = [event["sequence"] for event in events]
    assert sequences == sorted(sequences)
    rows = list(csv.DictReader(io.StringIO(client.get(f"{base}/coding/events?format=csv", headers=owner).text)))
    assert len(rows) == 3 and rows[2]["justificativa"] == "Ajuste"


def test_reliability_checklist_requires_justification(client, team):
    base, owner = team["base"], team["owner"]
    assert client.put(f"{base}/synthesis-checklist/18", headers=owner, json={"met": True, "justification": ""}).status_code == 422
    assert client.put(f"{base}/synthesis-checklist/99", headers=owner, json={"met": True, "justification": "x"}).status_code == 404
    for item in (18, 19, 20):
        client.put(f"{base}/synthesis-checklist/{item}", headers=owner, json={"met": True, "justification": "Conferido"})
    assert client.get(f"{base}/synthesis-checklist", headers=owner).json()["evaluated"] is False
    result = client.put(f"{base}/synthesis-checklist/21", headers=owner, json={"met": False, "justification": "RQ3 parcial"}).json()
    assert result["evaluated"] is True
