"""Colaboração e rastreabilidade (spec 009 adaptada, sem papéis novos)."""

import pytest

BIBTEX = b"""@article{a1, title={Alpha}, year={2021}}
@article{a2, title={Beta}, year={2022}}
@article{a3, title={Gamma}, year={2023}}
@article{a4, title={Delta}, year={2024}}
@article{a5, title={Epsilon}, year={2024}}
"""


@pytest.fixture
def team(client, review, signup):
    review_id, owner = review
    base = f"/reviews/{review_id}"
    bruno = signup("bruno")
    code = client.post(f"{base}/invites", headers=owner, json={"email": "bruno@example.com"}).json()["code"]
    client.post(f"/invites/{code}/accept", headers=bruno)
    scopus = next(item for item in client.get(f"{base}/sources/suggested", headers=owner).json() if item["name"] == "Scopus")
    client.post(f"{base}/sources", headers=owner, json={"source_id": scopus["id"]})
    client.post(f"{base}/sources/{scopus['id']}/import", headers=owner, files={"file": ("s.bib", BIBTEX, "application/octet-stream")})
    articles = {item["title"]: item["id"] for item in client.get(f"{base}/articles", headers=owner).json()["items"]}
    ids = {"owner": client.get("/me", headers=owner).json()["id"], "bruno": client.get("/me", headers=bruno).json()["id"]}
    return {"base": base, "owner": owner, "bruno": bruno, "articles": articles, "ids": ids}


def test_invite_notifies_existing_account(client, review, signup):
    review_id, owner = review
    carla = signup("carla")
    client.post(f"/reviews/{review_id}/invites", headers=owner, json={"email": "carla@example.com"})
    notifications = client.get("/notifications", headers=carla).json()
    assert notifications["unread"] == 1
    assert "convidou você" in notifications["items"][0]["message"]


def test_balanced_distribution_reassignment_and_my_filter(client, team):
    base, owner, bruno, ids = team["base"], team["owner"], team["bruno"], team["ids"]
    assert client.post(f"{base}/assignments/distribute", headers=owner,
                       json={"stage": "selection", "user_ids": [999]}).status_code == 422
    result = client.post(f"{base}/assignments/distribute", headers=owner,
                         json={"stage": "selection", "user_ids": [ids["owner"], ids["bruno"]]}).json()
    assert sorted(result["assigned"].values()) == [2, 3]
    again = client.post(f"{base}/assignments/distribute", headers=owner,
                        json={"stage": "selection", "user_ids": [ids["owner"], ids["bruno"]]}).json()
    assert sum(again["assigned"].values()) == 0

    mine = client.get(f"{base}/articles?assigned_to_me=true", headers=bruno).json()
    assert mine["total"] == int(result["assigned"][str(ids["bruno"])])
    kinds = [item["kind"] for item in client.get("/notifications", headers=bruno).json()["items"]]
    assert kinds.count("assignment") == 1

    assignments = client.get(f"{base}/assignments?stage=selection", headers=owner).json()["assignments"]
    article_id = next(int(key) for key, value in assignments.items() if value["user_id"] == ids["owner"])
    url = f"{base}/articles/{article_id}/assignment"
    assert client.put(url, headers=owner, json={"stage": "selection", "user_id": ids["bruno"]}).status_code == 422
    assert client.put(url, headers=owner, json={"stage": "selection", "user_id": ids["bruno"],
                                                "justification": "Ana de férias"}).status_code == 200
    assert client.get(f"{base}/articles?assigned_to_me=true", headers=bruno).json()["total"] == mine["total"] + 1
    activities = client.get(f"{base}/activities", headers=owner).json()
    assert any("Ana de férias" in item["target"] for item in activities)


def test_discussion_thread_resolution_and_notifications(client, team):
    base, owner, bruno, articles = team["base"], team["owner"], team["bruno"], team["articles"]
    alpha = articles["Alpha"]
    assert client.post(f"{base}/articles/{alpha}/comments", headers=owner, json={"body": "  "}).status_code == 422
    client.post(f"{base}/articles/{alpha}/comments", headers=owner, json={"body": "Fala de MAS?"})
    client.patch(f"{base}/articles/{alpha}", headers=bruno, json={"status": "A"})
    resolution = client.post(f"{base}/articles/{alpha}/comments", headers=bruno,
                             json={"body": "Sim, seção 3. Aceito.", "is_resolution": True}).json()
    assert (resolution["is_resolution"], resolution["resolution_status"]) == (True, "Aceito")
    thread = client.get(f"{base}/articles/{alpha}/comments", headers=owner).json()
    assert [item["body"] for item in thread] == ["Fala de MAS?", "Sim, seção 3. Aceito."]

    inbox = client.get("/notifications", headers=owner).json()
    assert inbox["unread"] == 1 and "resolveu a discussão" in inbox["items"][0]["message"]
    client.post(f"/notifications/{inbox['items'][0]['id']}/read", headers=owner)
    assert client.get("/notifications", headers=owner).json()["unread"] == 0
    assert client.post(f"/notifications/{inbox['items'][0]['id']}/read", headers=bruno).status_code == 404


def test_dashboard_counts_and_pending_per_member(client, team):
    base, owner, ids, articles = team["base"], team["owner"], team["ids"], team["articles"]
    client.post(f"{base}/assignments/distribute", headers=owner, json={"stage": "selection", "user_ids": [ids["owner"]]})
    client.post(f"{base}/articles/bulk", headers=owner, json={"ids": [articles["Alpha"], articles["Beta"]], "action": "accept"})
    data = client.get(f"{base}/dashboard", headers=owner).json()
    assert data["selection"] == {"U": 3, "A": 2, "R": 0, "D": 0}
    assert data["extraction"] == {"final": 2, "finished": 0}
    owner_row = next(item for item in data["members"] if item["user"]["id"] == ids["owner"])
    assert owner_row["stages"]["selection"] == {"assigned": 5, "pending": 3}


def test_evidence_chain_shows_links_and_explicit_gaps(client, team):
    base, owner, articles = team["base"], team["owner"], team["articles"]
    client.post(f"{base}/articles/bulk", headers=owner, json={"ids": [articles["Alpha"], articles["Beta"]], "action": "accept"})
    question = client.post(f"{base}/questions", headers=owner, json={"question": "Como os agentes se explicam?"}).json()
    field = client.post(f"{base}/extraction-fields", headers=owner, json={"description": "Técnica", "field_type": "S"}).json()
    code = client.post(f"{base}/codes", headers=owner, json={"name": "Justificativa", "definition": "d", "limits": "l"}).json()
    client.post(f"{base}/codes/{code['id']}/activate", headers=owner)
    client.post(f"{base}/articles/{articles['Alpha']}/segments", headers=owner,
                json={"text": "Agents justify plans", "page": "3", "code_ids": [code["id"]]})
    theme = client.post(f"{base}/themes", headers=owner, json={"name": "Explicações", "code_ids": [code["id"]]}).json()
    client.put(f"{base}/articles/{articles['Alpha']}/extraction", headers=owner, json={"field_id": field["id"], "value": "LIME"})

    chain = client.get(f"{base}/evidence", headers=owner).json()[0]
    assert set(chain["gaps"]) == {"Nenhum campo de extração ligado à pergunta.", "Nenhum tema ligado à pergunta.",
                                  "Conclusão ainda não registrada."}
    assert client.put(f"{base}/questions/{question['id']}/links", headers=owner,
                      json={"field_ids": [99999]}).status_code == 422
    client.put(f"{base}/questions/{question['id']}/links", headers=owner,
               json={"field_ids": [field["id"]], "theme_ids": [theme["id"]]})
    client.put(f"{base}/questions/{question['id']}/conclusion", headers=owner, json={"conclusion": "Por justificativas textuais."})

    chain = client.get(f"{base}/evidence", headers=owner).json()[0]
    alpha = next(item for item in chain["studies"] if item["title"] == "Alpha")
    assert alpha["fields"] == [{"field": "Técnica", "value": "LIME"}]
    assert alpha["segments"][0] == {"segment_id": alpha["segments"][0]["segment_id"], "text": "Agents justify plans",
                                    "page": "3", "code": "Justificativa", "theme": "Explicações"}
    assert chain["gaps"] == ["'Beta' sem valor em 'Técnica'."]
    assert chain["conclusion"] == "Por justificativas textuais."
