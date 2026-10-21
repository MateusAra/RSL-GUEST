# RSL — apoio a revisões sistemáticas da literatura

Ferramenta web para conduzir revisões sistemáticas em equipe, seguindo o fluxo consagrado pelo Parsifal: **Revisão → Planejamento → Condução → Relatório**.

- **Contas próprias:** qualquer pessoa cria a conta, cria revisões e convida coautores pelo e-mail. O convidado aceita ou recusa logado na própria conta, e o convite fica esperando se a pessoa ainda não tiver conta.
- **Planejamento:** objetivos, PICOC, perguntas de pesquisa, palavras-chave e sinônimos (com importação do PICOC), string de busca gerada e editável, fontes (bibliotecas sugeridas ou próprias), critérios de inclusão e exclusão, checklist de qualidade (respostas com peso, pontuação máxima, nota de corte) e formulário de extração (booleano, texto, real, inteiro, data, seleção única e múltipla).
- **Condução:** strings por fonte; importação de BibTeX, RIS e CSV; seleção de estudos com abas por fonte, filtros, ação em massa, detecção de duplicados e modal com Anterior/Próximo; avaliação de qualidade; extração de dados com exportação CSV; análise com gráficos.
- **Síntese temática:** codebook (dedutivo e emergente, com histórico), trechos com página, dupla codificação opcional com α de Krippendorff/κ de Cohen, temas e mapa temático, checklist de confiabilidade.
- **Análises:** bibliometria, cruzamento de campos de extração, hipóteses opcionais com vereditos ponderados pela qualidade, sensibilidade por filtros e instantâneos.
- **Painel da equipe:** atribuição de estudos, discussões por estudo, notificações no sistema, progresso e cadeia de evidência por pergunta de pesquisa.
- **Relatório:** relato PRISMA 2020 (fluxograma calculado, esqueleto escrito pelos pesquisadores, checklist de 27 itens) em Word e LaTeX, com referências em BibTeX/RIS, estilos APA e ABNT e histórico de versões; e exportação livre por seções.

## Executar com Docker
```bash
docker compose up --build
```
Abra http://127.0.0.1:8002 e crie a primeira conta. Antes de qualquer uso fora da sua máquina, troque `POSTGRES_PASSWORD` e `RSL_JWT_SECRET`.

## Executar localmente (SQLite)
```bash
pip install -r requirements.txt
cd web && npm install && npm run build && cd ..
PYTHONPATH=src uvicorn rsl.app:app --port 8002
```
Para desenvolver o front com recarga automática, mantenha a API na porta 8002 e rode `npm run dev` dentro de `web/` (o Vite faz proxy de `/api`).

| Variável | Padrão | Uso |
|---|---|---|
| `RSL_DATABASE_URL` | `sqlite+pysqlite:///./rsl.sqlite3` | Banco (SQLite ou PostgreSQL via `postgresql+psycopg://`) |
| `RSL_JWT_SECRET` | valor de desenvolvimento | Chave dos tokens de sessão |
| `RSL_STORAGE_PATH` | `./storage` | Arquivos importados |
| `RSL_WEB_DIST` | `./web/dist` | Build do front servido pela API |

## Testes
```bash
python -m pytest -q
cd web && npm run build
```

## Estrutura
- `src/rsl/` — API FastAPI (`routers/` por área, `models/` SQLAlchemy, `importers.py`, `security.py`)
- `migrations/` — Alembic
- `web/` — React + TypeScript + Vite + react-bootstrap
- `tests/` — pytest, com um banco SQLite novo por teste
- `docs/adr/` — decisões; o ADR-007 registra a mudança para a ferramenta genérica
- `docs/legado/` — specs, protocolo e material da versão anterior, feita sob medida para uma RSL

O fluxo funcional segue o [Parsifal](https://github.com/vitorfs/parsifal) (MIT); a implementação é independente.
