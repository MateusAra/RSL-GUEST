# Plano do módulo 002 — Configuração

Status: implementado na branch `feat/specs-002-003-005`; aguarda revisão do PO.

## Modelo de dados
- `project_documents` (migração 004, append-only): cada versão de protocolo, critério CI/CE, termo do glossário, RQ, PICOC, hipótese, regra de vereditos e fase é uma linha nova. Nada é editado ou apagado (P4).
- `project_gates` (migração 010, append-only): confirmação do Portão 0 e do Portão 1, com autor, data e o relatório que liberou o portão.
- `protocol_deviations` (migração 004, append-only): log de desvios.

## API
| Método | Rota | RF / CA |
|--------|------|---------|
| POST | `/projects/{id}/configuration/{kind}/{key}` (`expected_version`, `deviation_id` opcionais) | RF02, RF06–RF11 · CA-02, CA-04–CA-08 |
| GET | `/projects/{id}/configuration/{kind}/{key}/diff?from_version&to_version` | RF02, RF11 · CA-02, CA-08 |
| GET | `/projects/{id}/configuration-integrity` | RF12, RNF04 · CA-04, CA-09 |
| GET | `/projects/{id}/analysis-configuration` | RF09, RF10 · CA-07 |
| GET | `/projects/{id}/schedule` | RF04 · CA-10 |
| GET | `/projects/{id}/deviations/export?format=csv\|json` | RF03 · CA-03 |
| GET/POST | `/projects/{id}/gates`, `/projects/{id}/gates/{0\|1}/confirm` | regra 2, regra 3, CA-04, CA-07 |

## Regras implementadas
- **Glossário (CA-04):** termo sem vínculo válido (CI/CE existente ou campo do catálogo de extração) é salvo, aparece em `glossary_pending` e bloqueia o Portão 0. Antes, o termo era recusado no salvamento, o que contrariava a spec.
- **Integridade (CA-09):** "campo sem RQ" = campo de conteúdo B–I (`is_substantive_field`) que nenhuma RQ ativa lista em `field_links`. Os campos de identificação (Q-O) não exigem RQ.
- **Vereditos (RF10):** os 4 vereditos são fixos; a ponderação padrão é a decidida pelo PO (≥ 7,0 → 1,0; 4,0–6,9 → 0,5) e pode ser configurada.
- **RQ (regra 5):** não há exclusão; a desativação (`active: false`) exige `deactivation_justification`. Uma reformulação com extração já iniciada nos campos ligados devolve um alerta em `warnings`.
- **Histórico (CA-08):** a auditoria guarda os dados anterior e novo de cada versão, e o diff aparece na resposta e no endpoint de diff.
- **Concorrência (§9):** `expected_version` divergente devolve 409.

## Decisões tomadas nesta implementação (validar com o PO)
- **Portões:** o Portão 0 exige a integridade completa (protocolo, RQs ligadas, campos B–I cobertos, glossário sem pendência, PICOC, H1/H2, vereditos). O Portão 1 exige o Portão 0 e os seminais recuperados em todas as bases (spec 003).
- **Desvio obrigatório:** depois do Portão 0, mudar RQ, CI/CE ou string de busca exige `deviation_id` de um desvio registrado. A spec 002 (regra 2) fala em Portão 0 e a spec 003 (regra 2) em Portão 1. Adotei a regra mais restritiva, que cobre as duas e segue o §5.1 (revisar a string exige registro no log de desvios).
- **Cronograma ([ESCLARECER 3]):** só visualização. Mostra o % por fase, o % geral ponderado pela duração e as dependências pendentes, sem bloquear nada.
