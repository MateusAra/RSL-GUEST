# ADR-002 — Stack back-end e banco de dados
Status: aceita
Data: 2026-09-29

Contexto:
A constituição exige API REST, banco relacional, migrações versionadas, backups e escrita otimista. O sistema também precisa de rastreabilidade e controle do acesso, além de um bom suporte para testes e manutenção.

Decisão:
Proposta inicial: Python + FastAPI + PostgreSQL. Esta escolha favorece rapidez de desenvolvimento, validação por tipos, documentação OpenAPI e integração com bibliotecas estatísticas.

Alternativas consideradas:
- Django + PostgreSQL: mais completo para auth e admin, porém mais pesado e menos flexível em endpoints sob demanda.
- Node/NestJS + PostgreSQL: bom para TypeScript, mas exige mais decisões de arquitetura para estatísticas e auditoria.

Consequências:
- Vantagens: stack leve, testável, bem documentada, compatível com migrações e endpoints REST.
- Desvantagens: exige disciplina de versionamento de schema e revisão de segurança.
- Observação: esta decisão permanece pendente de validação pelo PO e pelos arquiteto/desenvolvedor da equipe.
