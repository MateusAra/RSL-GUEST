# CLAUDE.md — instruções para o agente

Projeto: sistema de apoio à RSL "XAI for Multi-Agent Systems". Desenvolvimento orientado por especificação (SDD). Pesquisador responsável: Wladimir Farias Tenório Filho (PO).

## Antes de qualquer alteração
1. Leia `constitution.md`. Ela vale para tudo.
2. Leia a spec do módulo em `specs/NNN-…/spec.md` e, se houver tela, `frontend/spec-front.md`.
3. Se a tarefa toca método (triagem, QA, síntese, GenAI), leia o extrato em `papers/extratos/` citado na spec.

## Regras
- Não implemente nada que não esteja na spec. Comportamento novo → proponha alteração na spec primeiro.
- Item marcado `[ESCLARECER]` **não** se resolve sozinho: pergunte ao PO ou implemente só o que a spec já fixa.
- Requisitos entre parênteses como "proposta" ou `PRP-##` só entram após aprovação do PO.
- Nenhuma função de IA em triagem, QA, extração, codificação ou síntese (constituição P2; spec 011).
- Decisões humanas exigem confirmação explícita e ficam na auditoria imutável; nunca apague registros.
- κ e α só por biblioteca validada, conferida em ≥ 3 casos manuais (tolerância 0,001).
- Escreva os testes dos `CA-##` antes do código. Cada tarefa cita RF e CA. Commits pequenos.
- O Protocolo v4.0 (`docs/fonte/`) prevalece sobre artigos. Divergência vira `[ESCLARECER]`, não decisão sua.
- Decisão técnica relevante → ADR em `docs/adr/`.

## Fluxo por módulo
clarificar → `plan.md` (modelo de dados, API, ADRs) → `tasks.md` (≤ 4 h cada) → testes → implementar → validar com o PO → sincronizar a spec.

## Estrutura
`constitution.md` · `specs/` · `frontend/` · `docs/` (ADRs, fontes, benchmark) · `papers/` · `src/`
Idioma: documentação em português do Brasil; código e identificadores em inglês.
