# ADR-007 — Ferramenta genérica no estilo do Parsifal
Status: aceita
Data: 2026-10-21

Contexto:
A versão anterior foi feita sob medida para uma única RSL (XAI × MAS). Tinha papéis globais fixos, contas criadas por um administrador, regras do Protocolo v4.0 embutidas (portões, 59 campos de extração, instrumento de QA fixo, votação dupla com terceiro revisor) e só um protótipo de interface. No fork MateusAra/RSL-GUEST o objetivo passou a ser uma ferramenta que sirva a qualquer RSL.

Decisão:
- Seguir o modelo funcional do Parsifal (código aberto, MIT): revisão com autor principal e coautores; Planejamento (objetivos, PICOC, perguntas, palavras-chave e sinônimos, string de busca, fontes, critérios, checklist de qualidade, formulário de extração); Condução (busca, importação, seleção, qualidade, extração, análise); Relatório (exportação). A implementação é própria; não copiamos código, nome nem identidade visual.
- Contas: cadastro livre. Coautores entram por convite ao e-mail, aceito ou recusado pela própria pessoa.
- Seleção: status único por artigo (não classificado, aceito, rejeitado, duplicado), editável por qualquer coautor.
- Stack: FastAPI + SQLAlchemy + Alembic no back-end; React + TypeScript + Vite + react-bootstrap no front-end (confirma o ADR-003).
- A constituição e as specs 001–011 foram movidas para `docs/legado/` e deixam de valer. Os ADR-001 a 006 permanecem só como histórico.

Alternativas consideradas:
- Manter as regras do Protocolo v4.0 como modo opcional: descartado nesta fase para simplificar. A versão anterior continua na branch `feat/specs-002-003-005`.

Consequências:
- Fica mais fácil adotar a ferramenta em qualquer RSL e colaborar sem administrador.
- Perde-se a independência entre revisores, o κ e a auditoria imutável da versão anterior. Se voltarem a ser necessários, entram como recursos opcionais por revisão.
