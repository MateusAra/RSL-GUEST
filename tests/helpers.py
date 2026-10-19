from fastapi.testclient import TestClient

from rsl_foundation.extraction import EXTRACTION_FIELD_IDS, is_substantive_field

SUBSTANTIVE_FIELDS = sorted(field_id for field_id in EXTRACTION_FIELD_IDS if is_substantive_field(field_id))
VERDICTS = ["suporta", "parcialmente suporta", "refuta", "inconclusivo"]
REVIEWER_ONE = ("reviewer@rsl.local", "reviewer123")
REVIEWER_TWO = ("reviewer2@rsl.local", "reviewer2123")
THIRD_REVIEWER = ("third-reviewer@rsl.local", "reviewer3123")

DEFAULT_MEMBERS = [
    {"email": "reviewer@rsl.local", "role": "revisor"},
    {"email": "reviewer2@rsl.local", "role": "revisor"},
    {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
]


def login(client: TestClient, email: str = "admin@rsl.local", password: str = "admin123") -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_project(client: TestClient, token: str, title: str = "Projeto de teste") -> dict:
    response = client.post(
        "/api/v1/projects",
        headers=auth(token),
        json={
            "title": title,
            "objective": "Validar critérios de aceite.",
            "study_type": "systematic_literature_review",
            "members": DEFAULT_MEMBERS,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def save_search_string(
    client: TestClient, project_id: str, headers: dict, base: str = "scopus", query: str = "XAI AND MAS", **extra
):
    return client.post(
        f"/api/v1/projects/{project_id}/search-strings/{base}",
        headers=headers,
        json={"query": query, "justification": "String adaptada à sintaxe da base.", **extra},
    )


def create_execution(
    client: TestClient,
    project_id: str,
    headers: dict,
    base: str = "scopus",
    query: str = "XAI AND MAS",
    reported_result_count: int = 1,
    **extra,
) -> dict:
    adapted = save_search_string(client, project_id, headers, base, query)
    assert adapted.status_code == 201, adapted.text
    response = client.post(
        f"/api/v1/projects/{project_id}/search-executions",
        headers=headers,
        json={"base": base, "reported_result_count": reported_result_count, **extra},
    )
    assert response.status_code == 201, response.text
    return response.json()


def import_file(client: TestClient, execution_id: str, headers: dict, file_name: str, content: bytes):
    return client.post(
        f"/api/v1/search-executions/{execution_id}/imports",
        headers=headers,
        files={"file": (file_name, content, "application/octet-stream")},
    )


def ris(*records: dict) -> bytes:
    lines = []
    for record in records:
        lines.append(f"TY  - {record.get('type', 'JOUR')}")
        lines.append(f"TI  - {record['title']}")
        for author in record.get("authors", ["Doe, Jane"]):
            lines.append(f"AU  - {author}")
        if record.get("year"):
            lines.append(f"PY  - {record['year']}")
        if record.get("venue"):
            lines.append(f"JO  - {record['venue']}")
        if record.get("doi"):
            lines.append(f"DO  - {record['doi']}")
        if record.get("abstract"):
            lines.append(f"AB  - {record['abstract']}")
        lines.append("ER  -")
    return ("\n".join(lines) + "\n").encode()


def configure(client: TestClient, project_id: str, headers: dict, kind: str, key: str, data: dict, **extra):
    return client.post(
        f"/api/v1/projects/{project_id}/configuration/{kind}/{key}",
        headers=headers,
        json={"data": data, **extra},
    )


def research_question(field_links: list[str] | None = None, **overrides) -> dict:
    return {
        "text": "Quais abordagens de XAI são integradas a MAS?",
        "motivation": "Mapear o estado da arte.",
        "classification": "descritiva",
        "classification_justification": "Descreve abordagens existentes.",
        "field_links": SUBSTANTIVE_FIELDS if field_links is None else field_links,
        "analysis_links": ["A-RQ1-distribuicao"],
        **overrides,
    }


def configure_complete_protocol(client: TestClient, project_id: str, headers: dict) -> None:
    """Configuration that satisfies the Portão 0 integrity check (spec 002)."""
    steps = [
        ("protocol", "protocolo", {"text": "Protocolo v4.0", "description": "Carga inicial", "frozen": True}),
        ("criteria", "CI1", {"text": "Aborda MAS."}),
        ("glossary", "MAS", {"definition": "Sistema multiagente.", "criteria_links": ["CI1"]}),
        ("research_question", "RQ1", research_question()),
        ("picoc", "main", {"elements": {
            "population": "MAS", "intervention": "XAI", "comparison": "Confiança clássica",
            "outcome": "Transparência", "context": "Ecossistemas agênticos",
        }}),
        ("hypothesis", "H1", {"independent_variables": ["XAI"], "dependent_variables": ["confiança"],
                              "operational_criteria": ["evidência textual"]}),
        ("hypothesis", "H2", {"independent_variables": ["mecanismo"], "dependent_variables": ["suficiência"],
                              "operational_criteria": ["evidência textual"]}),
        ("verdict_rules", "default", {"verdicts": VERDICTS}),
    ]
    for kind, key, data in steps:
        response = configure(client, project_id, headers, kind, key, data)
        assert response.status_code == 201, response.text


def deviation(client: TestClient, project_id: str, headers: dict, section: str = "§5.1") -> str:
    response = client.post(
        f"/api/v1/projects/{project_id}/deviations",
        headers=headers,
        json={"stage": "busca", "description": "Ajuste", "justification": "Necessário.", "affected_section": section},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]
