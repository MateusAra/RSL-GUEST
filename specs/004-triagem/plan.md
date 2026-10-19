# Plano do módulo 004 — Triagem (parcial: RF26, consenso e terceiro revisor)

Status: RF26 implementado na branch `feat/specs-002-003-005`; aguarda revisão do PO. Os demais requisitos estão listados em "Fora deste incremento".

## Modelo de dados
- `triage_votes` (migração 006): votos de R1 e R2 por fase.
- `triage_resolutions` (migração 011, append-only): `stage = consensus` (posição de R1 ou R2 depois da reunião) ou `stage = arbitration` (decisão do R3), com decisão, CE (quando exclui), justificativa, autor e data. Única por estudo, fase, etapa e usuário.

## API
| Método | Rota | RF / CA |
|--------|------|---------|
| POST | `/projects/{id}/studies/{sid}/triage-consensus` (`phase`, `decision` = incluir \| excluir \| sem_consenso, `criterion_id`, `justification`) | RF26 · CA-07 |
| POST | `/projects/{id}/studies/{sid}/triage-arbitration` (só `terceiro_revisor`; `decision` = incluir \| excluir) | RF26 · CA-07 |
| GET | `/projects/{id}/triage/conflicts?phase=` | RF26 · CA-03, CA-11 |
| GET | `/projects/{id}/studies/{sid}/triage-status` (+ `status`, `final_result`, `consensus`, `arbitration`) | RF23, RF26 |

## Regras implementadas
- **Fila de conflitos (CA-03, CA-11):** os casos D e E, em qualquer ordem, ficam `awaiting_consensus` com `final_result = consensus_required`. Não são excluídos e não contam como incluídos.
- **Consenso (CA-07; decisão de 19/10/2026, aguarda validação do PO):** R1 e R2 registram **cada um** sua posição depois da reunião. Posições iguais fecham o conflito (`resolved_by_consensus`). Posições diferentes, ou "sem_consenso" de qualquer um, escalam ao R3 (`escalated`).
- **Arbitragem:** o R3 só vê o conflito na fila e só pode arbitrar depois da escalada (regra 6). A decisão do R3 é final (`resolved_by_arbitration`).
- **Exclusão:** excluir no consenso ou na arbitragem exige um CE configurado no projeto (regras 2 e 4).
- **Imutabilidade (RNF02):** cada registro gera auditoria e não pode ser refeito; um segundo registro do mesmo usuário devolve 409.
- **Integração:** `_triage_result` agora devolve o resultado final já resolvido. O snowballing (spec 003) passa a contar como incluído um conflito da Fase 2 resolvido com "incluir".

## Fora deste incremento
RF24 / CA-04 (CE obrigatório na exclusão da Fase 2 e PDF anexo), RF25 / CA-05, CA-06 e CA-12 (piloto e κ de Cohen por fase), RF27 / CA-09 (PRISMA), regra 1 / CA-10 (reabertura de voto confirmado), fechamento de fase com pendências e a lista de estudos C/D/E para a análise de sensibilidade (regra 11).
