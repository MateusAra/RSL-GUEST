# Plano do módulo 003 — Busca, importação, snowballing e deduplicação

Status: implementado na branch `feat/specs-002-003-005`; aguarda revisão do PO.

## Modelo de dados
- Strings de busca: `project_documents` com `kind = search_string` e chave `master` ou o id da base. São versionadas, append-only e exigem justificativa.
- Bases: catálogo fixo do §5.2.1 (`SEARCH_BASES`), com janela padrão 2016–2026 e limite de 300 no Google Scholar. O admin pode sobrescrever campos, janela e limite via `kind = search_base`.
- Seminais: `kind = seminal` (chave `SX…`, título, DOI e ano).
- Busca manual: `kind = manual_search`, uma versão por veículo.
- `search_executions` (+ `search_string_version`, `year_from`, `year_to`, `reported_result_count`).
- `raw_imports` e `studies` agora vêm de uma execução **ou** de uma rodada de snowballing (CHECK no banco). `studies` ganha `origin` (`search`, `snowball/backward`, `snowball/forward`) e `publication_type`.
- `snowball_rounds`: número, status e o resumo gravado no fechamento.
- `duplicate_decisions.method`: `automatic` (DOI exato) ou `manual`.

## API
| Método | Rota | RF / CA |
|--------|------|---------|
| POST | `/projects/{id}/search-strings/{master\|base}` | RF13 · CA-01 |
| GET | `/projects/{id}/search-bases` | RF14 · CA-02 |
| POST | `/projects/{id}/search-executions` (`reported_result_count` obrigatório; a string vem da versão adaptada da base) | RF14, RF15 · CA-02, CA-03 |
| POST | `/search-executions/{id}/imports` (relatório de anomalias e codificação) | RF15, RF16 · CA-03, CA-04 |
| GET | `/projects/{id}/search-validation` | RF17 · CA-05 |
| POST/GET | `/projects/{id}/manual-searches` | RF18 · CA-10 |
| POST/GET | `/projects/{id}/snowball-rounds`; POST `/snowball-rounds/{id}/imports`, `/snowball-rounds/{id}/close` | RF19, RF28 · CA-06, CA-09 |
| POST | `/projects/{id}/deduplication/run` | RF20 · CA-07 |
| GET | `/projects/{id}/deduplication/summary` | RF21, regra 6 · CA-08 |

**Mudança de contrato:** `POST /search-executions` não recebe mais `query`. A execução usa a versão vigente da string adaptada da base (CA-02).

## Regras implementadas
- **Sintaxe (CA-01):** parênteses e aspas balanceados, sem operador sem operando (`AND`/`OR` no início, no fim ou duplicado), sem `()` vazio. O erro informa a posição.
- **Seminais (CA-05):** um seminal conta como recuperado numa base se o DOI bate ou se o título normalizado tem similaridade ≥ 0,90, considerando as execuções da versão vigente da string daquela base. A ausência gera o alerta "SXnn não recuperado em base" e bloqueia o Portão 1. Seminal fora da janela da base (§9) pode ser liberado com `deviation_id`.
- **Deduplicação (CA-07):** DOI exato gera a decisão automática `duplicate`, editável por decisão manual. Similaridade ≥ 0,90 entra como `title_similarity` com canônico sugerido. A faixa de 0,85 a 0,90 vai para `manual_review`. A similaridade é calculada em blocos de 500 linhas (`rapidfuzz.cdist`, float32): 5.000 registros deduplicam em cerca de 3 s.
- **Canônico (CA-08):** grupos por união das decisões `duplicate` vigentes. A última escolha manual prevalece; sem ela, vale a regra de preferência. Todas as ocorrências são preservadas e o estudo conta uma vez (`unique_studies`).
- **Anomalias (CA-04):** registro sem título é descartado e listado; sem autor ou sem ano é importado e listado. Decodificação em Latin-1 gera aviso.

## Decisões tomadas nesta implementação (validar com o PO)
- **Registro canônico ("mais completo"):** periódico > anais/conferência > pré-print; depois o número de metadados preenchidos (autores, ano, veículo, DOI, resumo, keywords); depois o ano mais recente. O tipo vem do `TY` (RIS), do tipo da entrada (BibTeX) ou da coluna de tipo (CSV). DOI `10.48550/…` ou veículo arXiv conta como pré-print.
- **Incluídos no snowballing:** calculados pela triagem. Conta como incluído o candidato não duplicado com resultado `included` (matriz A) na Fase 2 da spec 004. A rodada 2 só abre com a rodada 1 fechada e pelo menos um incluído; a rodada 3 é sempre bloqueada. Casos D/E da triagem ficam como `pending` até a spec 004 implementar o consenso.
- **Faixa de revisão manual:** o limite inferior de 0,85 continua o do código original; a spec só fixa o 0,90.
