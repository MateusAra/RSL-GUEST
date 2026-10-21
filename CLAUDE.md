# CLAUDE.md — instruções para o agente

Projeto: **RSL**, ferramenta web genérica de apoio a revisões sistemáticas da literatura, inspirada no fluxo do Parsifal (Revisão → Planejamento → Condução → Relatório). Qualquer pessoa cria a própria conta, cria revisões e convida coautores pelo e-mail.

## Estrutura
- `src/rsl/` — API FastAPI: `models/` (SQLAlchemy), `routers/` (um por área), `deps.py` (sessão, usuário atual, `MemberReview`/`OwnerReview`), `security.py` (scrypt + JWT + refresh rotativo).
- `migrations/` — Alembic. Toda mudança de modelo ganha uma migração nova.
- `web/` — React + TypeScript + Vite + react-bootstrap. `src/api.ts` é o único cliente HTTP.
- `tests/` — pytest; cada teste cria um banco SQLite próprio (`conftest.py`).
- `docs/legado/` — specs e documentos da versão anterior (sob medida para uma RSL). Não valem mais.

## Regras
- Permissão: membro (autor principal ou coautor) edita o conteúdo; só o autor principal exclui a revisão e gerencia coautores e convites. Quem não é membro recebe 404.
- Interface em português do Brasil; código e identificadores em inglês.
- Antes de concluir: `pytest -q` e `npm run build` (em `web/`) sem erro.

## Rodar localmente
```bash
pip install -r requirements.txt
cd web && npm install && npm run build && cd ..
PYTHONPATH=src uvicorn rsl.app:app --port 8002
```
Em desenvolvimento do front: API na 8002 e `npm run dev` em `web/` (proxy de `/api`).
