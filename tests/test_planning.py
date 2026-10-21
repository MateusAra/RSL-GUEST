"""Planejamento: protocolo, checklist de qualidade e formulário de extração."""


def test_objective_picoc_and_questions(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}"
    assert client.put(f"{base}/objective", headers=headers, json={"objective": "Mapear XAI em MAS."}).status_code == 200
    picoc = {"population": "multi-agent systems, MAS", "intervention": "explainability", "comparison": "",
             "outcome": "trust", "context": "industry"}
    assert client.put(f"{base}/picoc", headers=headers, json=picoc).json()["outcome"] == "trust"

    first = client.post(f"{base}/questions", headers=headers, json={"question": "RQ1?"}).json()
    second = client.post(f"{base}/questions", headers=headers, json={"question": "RQ2?"}).json()
    assert client.post(f"{base}/questions", headers=headers, json={"question": "  "}).status_code == 422
    client.patch(f"{base}/questions/{first['id']}", headers=headers, json={"question": "RQ1 revisada?"})
    assert client.put(f"{base}/questions/order", headers=headers, json={"ids": [second["id"], first["id"]]}).status_code == 204

    planning = client.get(f"{base}/planning", headers=headers).json()
    assert planning["objective"] == "Mapear XAI em MAS."
    assert [item["question"] for item in planning["questions"]] == ["RQ2?", "RQ1 revisada?"]
    assert client.delete(f"{base}/questions/{first['id']}", headers=headers).status_code == 204


def test_keywords_synonyms_import_and_generated_search_string(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}"
    client.put(f"{base}/picoc", headers=headers, json={"population": "multi-agent systems, MAS", "intervention": "XAI",
                                                        "comparison": "", "outcome": "trust", "context": "ignored"})
    imported = client.post(f"{base}/keywords/import-picoc", headers=headers).json()
    assert imported["created"] == 4
    assert client.post(f"{base}/keywords/import-picoc", headers=headers).json()["created"] == 0

    xai = next(item for item in imported["keywords"] if item["description"] == "XAI")
    client.post(f"{base}/keywords", headers=headers, json={"description": "explainable AI", "synonym_of_id": xai["id"]})
    synonym = client.post(f"{base}/keywords", headers=headers, json={"description": "interpretability",
                                                                    "synonym_of_id": xai["id"]}).json()
    assert client.post(f"{base}/keywords", headers=headers, json={"description": "x",
                                                                 "synonym_of_id": synonym["id"]}).status_code == 422

    generated = client.post(f"{base}/search-string/generate", headers=headers).json()["search_string"]
    assert generated == 'MAS AND "multi-agent systems" AND trust AND (XAI OR "explainable AI" OR interpretability)'
    saved = client.put(f"{base}/search-string", headers=headers, json={"search_string": generated})
    assert saved.json()["version"] == 1
    assert client.get(f"{base}/planning", headers=headers).json()["search_string"] == generated

    client.delete(f"{base}/keywords/{xai['id']}", headers=headers)
    remaining = [item["description"] for item in client.get(f"{base}/planning", headers=headers).json()["keywords"]]
    assert remaining == ["MAS", "multi-agent systems", "trust"]


def test_sources_and_criteria(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}"
    suggested = client.get(f"{base}/sources/suggested", headers=headers).json()
    scopus = next(item for item in suggested if item["name"] == "Scopus")
    assert client.post(f"{base}/sources", headers=headers, json={"source_id": scopus["id"]}).status_code == 201
    assert client.post(f"{base}/sources", headers=headers, json={"source_id": scopus["id"]}).status_code == 409
    custom = client.post(f"{base}/sources", headers=headers, json={"name": "BDTD", "url": "https://bdtd.ibict.br"}).json()
    assert client.patch(f"{base}/sources/{custom['id']}", headers=headers,
                        json={"name": "BDTD (IBICT)", "url": ""}).json()["name"] == "BDTD (IBICT)"
    assert client.patch(f"{base}/sources/{scopus['id']}", headers=headers, json={"name": "x"}).status_code == 422
    assert "Scopus" not in [item["name"] for item in client.get(f"{base}/sources/suggested", headers=headers).json()]

    client.post(f"{base}/criteria", headers=headers, json={"criteria_type": "I", "description": "Aborda MAS"})
    exclusion = client.post(f"{base}/criteria", headers=headers, json={"criteria_type": "E", "description": "Não é inglês"}).json()
    planning = client.get(f"{base}/planning", headers=headers).json()
    assert [item["name"] for item in planning["sources"]] == ["BDTD (IBICT)", "Scopus"]
    assert [item["description"] for item in planning["inclusion_criteria"]] == ["Aborda MAS"]
    assert client.delete(f"{base}/criteria/{exclusion['id']}", headers=headers).status_code == 204
    assert client.delete(f"{base}/sources/{scopus['id']}", headers=headers).status_code == 204


def test_quality_checklist_max_score_and_cutoff(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}"
    for text in ("O objetivo está claro?", "O método é adequado?", "Há ameaças à validade?"):
        client.post(f"{base}/quality-questions", headers=headers, json={"description": text})
    answers = client.post(f"{base}/quality-answers/suggested", headers=headers).json()
    assert [(item["description"], item["weight"]) for item in answers] == [("Sim", 1.0), ("Parcialmente", 0.5), ("Não", 0.0)]
    assert len(client.post(f"{base}/quality-answers/suggested", headers=headers).json()) == 3

    planning = client.get(f"{base}/planning", headers=headers).json()
    assert planning["quality_max_score"] == 3.0
    assert client.put(f"{base}/quality-cutoff", headers=headers, json={"quality_cutoff_score": 4}).status_code == 422
    assert client.put(f"{base}/quality-cutoff", headers=headers, json={"quality_cutoff_score": 1.5}).json() == {
        "quality_cutoff_score": 1.5, "quality_max_score": 3.0}


def test_extraction_form_field_types_and_select_values(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}/extraction-fields"
    assert client.post(base, headers=headers, json={"description": "Domínio", "field_type": "O"}).status_code == 422
    domain = client.post(base, headers=headers, json={"description": "Domínio", "field_type": "O",
                                                      "lookups": ["Saúde", "Indústria", "Saúde"]}).json()
    assert [item["value"] for item in domain["lookups"]] == ["Indústria", "Saúde"]
    year = client.post(base, headers=headers, json={"description": "Ano do estudo", "field_type": "I"}).json()
    changed = client.patch(f"{base}/{domain['id']}", headers=headers,
                           json={"description": "Domínio", "field_type": "M", "lookups": ["Saúde", "Educação"]}).json()
    assert (changed["field_type_label"], [item["value"] for item in changed["lookups"]]) == (
        "Seleção múltipla", ["Educação", "Saúde"])
    assert client.put(f"{base}/order", headers=headers, json={"ids": [year["id"], domain["id"]]}).status_code == 204
    fields = client.get(f"/reviews/{review_id}/planning", headers=headers).json()["data_extraction_fields"]
    assert [item["description"] for item in fields] == ["Ano do estudo", "Domínio"]


def test_planning_items_are_isolated_between_reviews(client, review, signup):
    review_id, headers = review
    question = client.post(f"/reviews/{review_id}/questions", headers=headers, json={"question": "RQ?"}).json()
    other_headers = signup("outro")
    other_id = client.post("/reviews", headers=other_headers, json={"title": "Outra"}).json()["id"]
    assert client.delete(f"/reviews/{other_id}/questions/{question['id']}", headers=other_headers).status_code == 404
    assert client.get(f"/reviews/{review_id}/planning", headers=other_headers).status_code == 404
