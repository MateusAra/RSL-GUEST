# ADR-003 — Stack front-end
Status: aceita
Data: 2026-09-29

Contexto:
O sistema deve funcionar como aplicação web com SPA, rotas protegidas, UX de revisão de estudos e visualização de resultados. Também é necessário manter uma interface clara para triagem, QA e extração.

Decisão:
Proposta inicial: React + TypeScript com Vite e biblioteca de componentes acessível. A abordagem oferece ciclos rápidos, organização modular e bom suporte a formulários e dashboards.

Alternativas consideradas:
- Angular: robusto e padronizado, mas mais pesado para prototipagem e revisão rápida.
- Vue: simples e produtivo, porém com menor padronização para equipes híbridas.

Consequências:
- Vantagens: familiaridade, facilidade de prototipagem, boa separação de módulos e controle de permissões por rota.
- Desvantagens: o projeto precisa manter uma política clara de estado global e acessibilidade.
- Observação: a implementação final deve ser validada com os wireframes da frente de módulo e com o PO.
