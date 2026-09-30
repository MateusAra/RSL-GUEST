# ADR-006 — Hospedagem e infraestrutura
Status: aceita
Data: 2026-09-29

Contexto:
A constituição exige ambiente controlado, backup com RPO ≤ 24h, autenticação e migrações versionadas. A infraestrutura também precisa seguir regras institucionais, quando existirem.

Decisão:
Proposta inicial: ambiente de desenvolvimento e produção em containerização com infraestrutura institucional ou cloud, conforme disponibilidade e políticas da organização. A implementação deve manter um pipeline de backup, restore e observabilidade simples.

Alternativas consideradas:
- Hospedagem totalmente local: mais controle, porém com mais risco operacional e menos escalabilidade.
- Hospedagem em cloud pública: mais ágil e fácil de escalar, mas exige atenção a políticas institucionais e custos.

Consequências:
- Vantagens: independência de solução fixa durante a fase de planejamento, com espaço para cumprir o RPO e os critérios de backup.
- Desvantagens: a decisão final depende de políticas internas e da infraestrutura disponível.
- Observação: esta ADR deve ser atualizada quando a equipe definir a infraestrutura operacional final.
