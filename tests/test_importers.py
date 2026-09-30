from rsl_foundation.importers import normalize_title, parse_records, title_similarity


def test_ris_import_maps_bibliographic_fields():
    payload = """TY  - JOUR
TI  - Explainable Multi-Agent Systems
AU  - Doe, Jane
PY  - 2024
JO  - Journal of XAI
DO  - 10.1234/xai.2024.1
AB  - A study of explanations in MAS.
KW  - multi-agent systems
KW  - explainability
ER  -
"""

    records = parse_records(payload.encode(), "results.ris")

    assert len(records) == 1
    assert records[0]["title"] == "Explainable Multi-Agent Systems"
    assert records[0]["authors"] == ["Doe, Jane"]
    assert records[0]["year"] == 2024
    assert records[0]["doi"] == "10.1234/xai.2024.1"
    assert records[0]["keywords"] == ["multi-agent systems", "explainability"]


def test_bibtex_import_maps_bibliographic_fields():
    payload = b"""@article{doe2023,
  title = {Trust in Multi-Agent Systems},
  author = {Jane Doe and Alex Smith},
  year = {2023},
  journal = {AI Review},
  doi = {10.5678/trust.2023},
  abstract = {A study of trust mechanisms.},
  keywords = {trust, agents}
}"""

    records = parse_records(payload, "results.bib")

    assert len(records) == 1
    assert records[0]["title"] == "Trust in Multi-Agent Systems"
    assert records[0]["authors"] == ["Jane Doe", "Alex Smith"]
    assert records[0]["year"] == 2023
    assert records[0]["venue"] == "AI Review"
    assert records[0]["doi"] == "10.5678/trust.2023"


def test_csv_import_and_normalized_title_similarity():
    payload = "Title,Authors,Year,DOI,Abstract,Keywords,Journal\n" \
        '"Explicabilidade: sistemas multiagentes!","Doe, Jane",2022,10.1000/a,"Resumo",xai; mas,Venue\n'.encode()

    records = parse_records(payload, "results.csv")

    assert records[0]["title"] == "Explicabilidade: sistemas multiagentes!"
    assert records[0]["authors"] == ["Doe, Jane"]
    assert records[0]["keywords"] == ["xai", "mas"]
    assert normalize_title("Árvores, Agênticas! XAI") == "arvores agenticas xai"
    assert title_similarity("Árvores Agênticas", "arvores agenticas") == 1.0


def test_unsupported_or_malformed_import_is_rejected_without_partial_data():
    try:
        parse_records(b"not a citation", "results.ris")
    except ValueError as error:
        assert "no bibliographic records" in str(error)
    else:
        raise AssertionError("malformed input should be rejected")