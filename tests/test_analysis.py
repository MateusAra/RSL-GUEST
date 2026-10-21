"""Condução II: avaliação de qualidade, extração de dados e análise."""

import csv
import io

BIBTEX = b"""@article{a1, title={Alpha study}, author={A}, year={2021}}
@article{a2, title={Beta study}, author={B}, year={2022}}
@article{a3, title={Gamma study}, author={C}, year={2022}}
@article{a4, title={Delta study}, author={D}, year={2023}}
"""


def _prepared(client, review):
    review_id, headers = review
    base = f"/reviews/{review_id}"
    scopus = next(item for item in client.get(f"{base}/sources/suggested", headers=headers).json() if item["name"] == "Scopus")
    client.post(f"{base}/sources", headers=headers, json={"source_id": scopus["id"]})
    client.post(f"{base}/sources/{scopus['id']}/import", headers=headers,
                files={"file": ("s.bib", BIBTEX, "application/octet-stream")})
    articles = {item["title"]: item["id"] for item in client.get(f"{base}/articles", headers=headers).json()["items"]}
    accepted = [articles["Alpha study"], articles["Beta study"], articles["Gamma study"]]
    client.post(f"{base}/articles/bulk", headers=headers, json={"ids": accepted, "action": "accept"})
    client.post(f"{base}/articles/bulk", headers=headers, json={"ids": [articles["Delta study"]], "action": "reject"})
    return base, headers, articles


def test_quality_assessment_scores_against_cutoff(client, review):
    base, headers, articles = _prepared(client, review)
    questions = [client.post(f"{base}/quality-questions", headers=headers, json={"description": text}).json()
                 for text in ("Q1?", "Q2?")]
    answers = {item["description"]: item["id"]
               for item in client.post(f"{base}/quality-answers/suggested", headers=headers).json()}
    client.put(f"{base}/quality-cutoff", headers=headers, json={"quality_cutoff_score": 1.5})

    def answer(title, question, label):
        return client.put(f"{base}/articles/{articles[title]}/quality", headers=headers,
                          json={"question_id": question["id"], "answer_id": answers[label]})

    assert answer("Alpha study", questions[0], "Sim").json() == {
        "article_id": articles["Alpha study"], "score": 1.0, "complete": False, "passed": False}
    assert answer("Alpha study", questions[1], "Parcialmente").json()["passed"] is True
    answer("Beta study", questions[0], "Não")
    answer("Beta study", questions[1], "Parcialmente")
    assert answer("Delta study", questions[0], "Sim").status_code == 422

    summary = client.get(f"{base}/quality-assessment", headers=headers).json()
    assert summary["max_score"] == 2.0
    by_title = {item["title"]: item for item in summary["articles"]}
    assert set(by_title) == {"Alpha study", "Beta study", "Gamma study"}
    assert (by_title["Alpha study"]["score"], by_title["Alpha study"]["complete"]) == (1.5, True)
    assert by_title["Beta study"]["passed"] is False

    extraction = client.get(f"{base}/data-extraction", headers=headers).json()
    assert [item["title"] for item in extraction["articles"]] == ["Alpha study"]


def test_data_extraction_typed_values_and_export(client, review):
    base, headers, articles = _prepared(client, review)
    fields = {}
    for description, field_type, lookups in (
        ("Validado?", "B", []), ("Autor principal", "S", []), ("Acurácia", "F", []), ("Agentes", "I", []),
        ("Publicado em", "D", []), ("Domínio", "O", ["Saúde", "Indústria"]), ("Técnicas", "M", ["LIME", "SHAP"]),
    ):
        fields[description] = client.post(f"{base}/extraction-fields", headers=headers,
                                          json={"description": description, "field_type": field_type, "lookups": lookups}).json()
    alpha = articles["Alpha study"]

    def put(field, value):
        return client.put(f"{base}/articles/{alpha}/extraction", headers=headers,
                          json={"field_id": fields[field]["id"], "value": value})

    lookups = {lookup["value"]: lookup["id"] for field in fields.values() for lookup in field["lookups"]}
    assert put("Validado?", "talvez").status_code == 422
    assert put("Validado?", "True").json()["value"] == "True"
    assert put("Autor principal", "  Ana  ").json()["value"] == "Ana"
    assert put("Acurácia", "0,93").json()["value"] == "0.93"
    assert put("Agentes", "3.5").status_code == 422
    assert put("Agentes", "12").json()["value"] == "12"
    assert put("Publicado em", "21/10/2026").status_code == 422
    assert put("Publicado em", "2026-10-21").json()["value"] == "2026-10-21"
    assert put("Domínio", [lookups["Saúde"], lookups["Indústria"]]).status_code == 422
    assert put("Domínio", lookups["Saúde"]).json()["value"] == lookups["Saúde"]
    assert put("Técnicas", [lookups["SHAP"], lookups["LIME"]]).json()["value"] == sorted([lookups["LIME"], lookups["SHAP"]])
    assert put("Técnicas", [999999]).status_code == 422

    assert client.put(f"{base}/articles/{articles['Delta study']}/extraction", headers=headers,
                      json={"field_id": fields["Agentes"]["id"], "value": "1"}).status_code == 422
    assert client.put(f"{base}/articles/{alpha}/extraction-status", headers=headers,
                      json={"finished": True}).json()["finished_data_extraction"] is True

    extraction = client.get(f"{base}/data-extraction", headers=headers).json()
    alpha_values = next(item for item in extraction["articles"] if item["id"] == alpha)["values"]
    assert alpha_values[str(fields["Agentes"]["id"])] == "12"

    rows = list(csv.reader(io.StringIO(client.get(f"{base}/data-extraction/export", headers=headers).text)))
    assert rows[0][4:] == ["Validado?", "Autor principal", "Acurácia", "Agentes", "Publicado em", "Domínio",
                           "Técnicas", "Extração concluída"]
    alpha_row = next(row for row in rows if row[0] == "Alpha study")
    assert alpha_row[4:] == ["Sim", "Ana", "0.93", "12", "2026-10-21", "Saúde", "LIME; SHAP", "Sim"]
    assert len(rows) == 4


def test_analysis_charts_data(client, review):
    base, headers, _ = _prepared(client, review)
    data = client.get(f"{base}/analysis", headers=headers).json()
    assert data["per_source"] == [{"source": "Scopus", "total": 4, "accepted": 3}]
    assert data["status_totals"] == {"U": 0, "A": 3, "R": 1, "D": 0}
    assert data["final_per_year"] == [{"year": "2021", "count": 1}, {"year": "2022", "count": 2}]
    assert data["final_total"] == 3
