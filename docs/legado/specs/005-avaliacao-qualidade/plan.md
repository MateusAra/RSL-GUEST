# Plano do módulo 005 — Avaliação de qualidade

Status: implementado na branch `feat/specs-002-003-005`; aguarda revisão do PO.

## Modelo de dados
- Instrumento: `project_documents` com `kind = qa_instrument`, chave `default`. Sem configuração, vale a carga do Protocolo v4.0 (`QA_V4_INSTRUMENT`, seção 9b): 10 critérios, 4 categorias, N/A em Q6, Q7 e Q9, mínimo de 7 aplicáveis.
- `quality_assessments` (+ `initial_scores`, `instrument_version`, `reopen_justification`). `initial_scores` é gravado na primeira confirmação e nunca muda (regra 11).
- `quality_arbitrations` (append-only): decisão do R3 por critério, com justificativa.

## API
| Método | Rota | RF / CA |
|--------|------|---------|
| POST | `/projects/{id}/configuration/qa_instrument/default` | RF29 · CA-01 |
| GET | `/projects/{id}/quality/instrument` | RF29 |
| POST | `/projects/{id}/studies/{sid}/quality-assessments` | RF29–RF31 · CA-02–CA-05, CA-10 |
| POST | `/projects/{id}/studies/{sid}/quality-assessments/reopen` | RNF02 · CA-09 |
| POST | `/projects/{id}/studies/{sid}/quality-arbitrations` (só `terceiro_revisor`) | RF32 · CA-08 |
| GET | `/projects/{id}/studies/{sid}/quality-status` | RF30–RF32 · CA-04, CA-08 |
| GET | `/projects/{id}/quality/summary` | RF31, RF32 · CA-06, CA-07 |

## Regras implementadas
- **Instrumento fora do protocolo (CA-01):** número de critérios diferente de 10, ou ausência de alguma das 4 categorias, exige `deviation_justification`. O sistema registra o desvio no log (§7.4) e liga o instrumento a ele.
- **Desfecho (CA-05):** `classification` mantém as faixas do §7.3 (alta/moderada/baixa) e `outcome` traz o rótulo do CA-05 (`aprovado`, `ressalva`, `excluido_qualidade`).
- **Consenso (regras 4 e 5, CA-08):** item a item. Diferença ≤ 0,5 → média dos dois; diferença > 0,5 → fila do R3, cuja nota prevalece. Arbitragens anteriores à última confirmação são ignoradas, porque se referem a notas substituídas.
- **Exclusão (CA-06):** score final < 4,0 entra em `excluded`, com motivo "qualidade", e em `counts.excluido_qualidade` (contagem PRISMA). O estudo continua no banco.
- **κ ponderado (CA-07, regra 11):** κ linear do projeto sobre os pares de itens aplicáveis das **primeiras** confirmações, conferido contra uma implementação manual independente em 20 estudos (tolerância 0,001). Abaixo de 0,6 gera alerta sem bloquear (decisão do PO na spec).
- **Reabertura (CA-09, §9):** mudar uma nota confirmada exige reabrir com justificativa. A auditoria registra as notas anterior e nova, o autor e a justificativa.
- **Categorias (CA-10):** score por categoria normalizado em 0–10, exibido separado do total. Categoria sem item aplicável fica `null`, e não 0.

## Decisões tomadas nesta implementação (validar com o PO)
- **N/A × nota:** se um avaliador marca N/A e o outro pontua o mesmo item, o item vai para o R3. A spec não trata esse caso.
- **Fora do escopo desta branch:** instrumento por tipo de estudo (regra 10; depende da classificação de tipo da spec 006/RF38), piloto de QA (US5, sem RF) e marcação de avaliação inativa quando o estudo sai do corpus por escopo (depende da spec 004).
