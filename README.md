# Kit SDD — Sistema de Apoio à RSL "XAI for Multi-Agent Systems"

Derivado dos Documentos 1–4 (funcionalidades, matriz de requisitos, atividades da RSL e do desenvolvimento). Formato Spec-Driven Development: **constituição → specs por módulo → (próximo) plano → tarefas → implementação**.

## Arquivos do kit
- `COMECE-AQUI.md`: orientação inicial (decisões, ambiente, ciclo por módulo, checklist)
- `constitution.md`: regras transversais
- `specs/001-…/spec.md … 011-…/spec.md`: specs por módulo (regras de negócio e critérios de aceite)
- `CLAUDE.md`: instruções para o agente de código
- `papers/`: mapa das referências (siglas K07, Z15, P15, CD11, G26…) e extratos; PDFs ficam só no seu computador
- `docs/`: `adr/` (decisões), `fonte/` (Documentos 1–4 em .docx), `benchmark-parsifal.md`
- `frontend/spec-front.md` (v2): princípios de UX, padrões de interação, componentes, telas por módulo, 9 wireframes e 25 critérios de aceite de interface
- `docs/benchmark-parsifal.md`: o que adotar, adaptar ou evitar do Parsifal e 13 propostas (`PRP-01..13`) de mudança nas specs de módulo, aguardando aprovação do PO

## Como usar
0. Leia `COMECE-AQUI.md` primeiro.
1. `constitution.md` vale para todas as specs; alterações exigem ADR.
2. Cada spec descreve **o quê e por quê**, com requisitos, regras de negócio e critérios de aceite Dado/Quando/Então. **Como** implementar vai no `plan.md` de cada módulo (próximo passo).
3. Resolva os `[ESCLARECER]` de cada spec antes de planejar o módulo.
4. Ordem de trabalho = ordem de dependência abaixo (alinhada às fases D2–D8 do Doc 4).

## Mapa de specs

| Spec | Módulo | Fase dev (Doc 4) | Fase RSL (Doc 3) | Requisitos | Depende de |
|------|--------|:----------------:|:----------------:|------------|------------|
| 001 | Fundação: auth, papéis, auditoria, armazenamento, backup | D2 | Todas | RF51, RF56 · HAB-01..05 | — |
| 002 | Configuração: projeto, protocolo, glossário, RQs, hipóteses | D3 | 0 | RF01–RF04, RF06–RF12 | 001 |
| 003 | Busca, importação, snowballing, deduplicação | D4 | 1, 2, 6 | RF13–RF21, RF28 | 001, 002 |
| 004 | Triagem e seleção | D4 | 2, 3, 4 | RF22–RF27 (+ RF22a) | 001–003 |
| 005 | Avaliação de qualidade | D5 | 2, 5 | RF29–RF32 | 001, 002, 004 |
| 006 | Extração de dados | D5 | 7 | RF33–RF38 | 001, 002, 004, 005 |
| 007 | Codificação e síntese temática | D6 | 8 | RF39–RF43 | 001, 002, 006 |
| 008 | Análises | D7 | 9 | RF44–RF47 | 002, 003, 005–007 |
| 009 | Colaboração, dashboard, cadeia de evidência | D8 | Transversal | RF52–RF55, RF57 | 001, 004–008 |
| 010 | Relato PRISMA/SEGRESS | D8 | 10 | RF48–RF50 | 002–008, 011 |
| 011 | Governança de GenAI e pacote de replicação | D8 | 10, 11 | RF05, RF58–RF62 | todas |

Cobertura: os 62 requisitos funcionais (RF01–RF62) aparecem cada um em exatamente uma spec. Os 15 RNFs são tratados nas specs onde se aplicam (ver seção "Requisitos não funcionais" de cada uma) e nos testes de sistema da fase D9.

Observações de escopo:
- **PRP-01..13** (benchmark do Parsifal) são propostas que não alteram as specs de módulo até a aprovação do PO. A mais importante é a **PRP-02**: nenhum requisito cadastra os critérios de inclusão/exclusão (CI/CE), embora todas as specs de triagem dependam deles.
- **RF22a** é um requisito adicionado (independência dos revisores: ocultar o voto do colega). Vem do princípio P7 da constituição; não está no Doc 2. Confirme se deve entrar na matriz.
- **HAB-01..05** (spec 001) são habilitadores técnicos que não existem no Doc 2 (autenticação, armazenamento com hash, migrações, backup, escrita otimista).
- **RF05** (pacote de replicação) está no grupo A do Doc 2, mas foi implementado na spec 011 conforme D8.3.5 do Doc 4.

## Pontos em aberto (`[ESCLARECER]`) — resumo por spec

| Spec | Abertos | Temas principais |
|------|:-------:|------------------|
| 001 | 3 | Método de autenticação; acúmulo de papéis; retenção de backups |
| 002 | 3 | Fonte de importação do protocolo; valor do peso de qualidade; cronograma só visual |
| 003 | 1 | Limiares de similaridade da deduplicação |
| 004 | 1 | κ da Fase 2 (sem limiar no protocolo) |
| 005 | 2 | Mínimo de critérios aplicáveis; limiar de κ ponderado |
| 006 | 2 | Quais campos exigem citação; métrica de concordância na extração |
| 007 | 2 | Atlas.TI × sistema; aprovar RF42a |
| 008 | 3 | Limiar de concentração de autoria; valor do peso; cobertura do §10.5–10.6 |
| 009 | 3 | Canal de notificação; atribuição sempre dupla; quem fecha discussões |
| 010 | 2 | Estilo de referência; Zotero/Mendeley por arquivo ou API |
| 011 | 3 | Ferramentas de tradução; direitos autorais dos PDFs; manifesto e anonimização |

Total: 25 pontos abertos (eram 35). Os artigos e o Protocolo v4.0 fecharam 10.

**Protocolo de referência:** `docs/fonte/Protocolo_RSL_XAI_MAS_v4.docx` (versão 4.0, 29/09/2026, alinhada à GUEST). A numeração do v4.0 (§5.3.3 matriz, §7.4 QA, §9 extração, §11 GenAI, §14.3 pacote) é a que as specs citam. Ele resolveu a matriz A–F, os 10 critérios de QA e N/A, os Blocos A–I (59 campos), a hipótese H2 e os vereditos, os 7 veículos da busca manual e a política de GenAI.

**Bloqueadores restantes:** nenhum de conteúdo. O que falta são decisões suas (ver `COMECE-AQUI.md`, seção 2) e os ADRs.

## Convenções
- IDs: `RF##`, `RNF##`, `HAB-##`, `CA-##` (critério de aceite, local da spec), `CT-<módulo>-##` (caso de teste).
- Prioridade MoSCoW: DEVE (Must) · DEVERIA (Should) · PODE (Could).
- Toda spec cita F.n.n (Doc 1) e § do Protocolo v4.0.

## Próximos passos sugeridos
1. Resolver os `[ESCLARECER]`, começando pelos três bloqueadores.
2. Enviar ao PO a decisão sobre PRP-01..13 e RF42a.
3. Escrever o `plan.md` (modelo de dados, contratos de API, ADRs) para o módulo 001 e depois 002, na ordem de dependência.
4. Gerar tarefas (`tasks.md`) e os casos de teste `CT-*` por módulo.
