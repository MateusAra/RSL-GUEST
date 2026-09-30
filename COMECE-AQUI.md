# Comece aqui — Orientação inicial para o SDD do sistema da RSL

Você já tem: constituição, 11 specs de back/regras de negócio e a spec de front (`frontend/spec-front.md`). Antes de gerar código, faltam decisões e um ambiente de trabalho. Este guia diz o que fazer, em que ordem.

## 1. Onde você está no processo SDD

```
Constituição ✅ → Specs (o quê/por quê) ✅ → Clarificar ⏳ → Plano (como) ⬜ → Tarefas ⬜ → Implementar ⬜ → Validar ⬜
```

Você está na etapa **Clarificar**. Não pule para o plano: os `[ESCLARECER]` viram perguntas que o agente teria de adivinhar.

## 2. Semana 0 — decisões e preparação (antes de qualquer código)

### 2.1 Decisões de conteúdo (só você, como PO, pode tomar)
| # | Decisão | Onde afeta |
|---|---------|-----------|
| 1 | κ da Fase 2 da triagem: só reportar ou alertar abaixo de 0,6? (matriz A–F, D/E e piloto já estão fixados no v4.0) | spec 004 |
| 2 | QA: os 10 critérios e o N/A (Q6, Q7, Q9) estão na spec 005, seção 9b. Falta: mínimo de critérios aplicáveis e limiar do κ ponderado | spec 005 |
| 3 | Campos A–I (59) estão na spec 006, seção 4a. Falta: quais exigem citação e página; métrica de concordância na extração | spec 006 |
| 4 | Fórmula de ponderação por qualidade (fixa por faixa × contínua) | specs 002, 008 |
| 5 | Limiares de similaridade da deduplicação (os 7 veículos e os 4 seminais já estão no v4.0) | spec 003 |
| 6 | **Aprovar ou recusar as propostas PRP-01..13** (`docs/benchmark-parsifal.md`), começando por PRP-02 (cadastro de CI/CE, Must) | specs 002–006, 008, 010 e front |

O Protocolo v4.0 já fechou os bloqueadores de conteúdo que estavam aqui. O que sobra são preferências suas.

### 2.2 Decisões técnicas (registrar como ADR)
| ADR | Decisão | Opções comuns |
|-----|---------|---------------|
| 001 | Autenticação | SSO institucional (Google/Microsoft), e-mail + senha |
| 002 | Stack back-end | Python (FastAPI/Django) ou TypeScript (NestJS); PostgreSQL |
| 003 | Stack front-end | React + TypeScript (Vite) com biblioteca de componentes acessível |
| 004 | Armazenamento de objetos | S3 compatível (MinIO, S3, GCS) |
| 005 | Cálculo estatístico (κ, α) | Biblioteca validada (ex.: scikit-learn, statsmodels, `krippendorff`) |
| 006 | Hospedagem | Institucional (UPE/Petrobras têm restrições?) × nuvem |

Se a equipe for você e assistentes de IA, prefira **uma stack que você domine ou consiga revisar**: em SDD, quem revisa o código é você.

### 2.3 Ambiente
1. Repositório Git com esta estrutura (é a mesma do ZIP; basta descompactar):
   ```
   CLAUDE.md                 instruções do agente
   constitution.md
   README.md · COMECE-AQUI.md
   specs/001-fundacao/spec.md … 011-genai-replicacao/spec.md
        (cada pasta ganha depois plan.md, tasks.md e tests/)
   frontend/spec-front.md
   docs/adr/                 decisões (ADR-001…)
   docs/fonte/               Documentos 1–4 (.docx)
   docs/benchmark-parsifal.md
   papers/README.md · extratos/   (papers/pdf/ fica fora do Git)
   src/                      código
   ```
2. `CLAUDE.md` já vem pronto na raiz. Se usar outra ferramenta, copie como `AGENTS.md`. Coloque `papers/pdf/` no `.gitignore`.
3. Ferramenta: **Claude Code** no repositório (com o kit acima) ou **GitHub Spec Kit** (`/specify`, `/clarify`, `/plan`, `/tasks`, `/implement`). O kit já está no formato compatível; basta mover os arquivos.
4. CI mínimo: lint, testes e verificação de que todo `CA-##` tem um teste (checklist manual no começo).

### 2.4 Time e papéis (Doc 4)
Você é o **PO**. Precisa de: quem revise arquitetura (ARQ), quem desenvolva (DEV, pode ser agente + você) e quem teste (QA). R1, R2 e R3 da RSL são os **usuários de aceite (UAT)** — convide-os a validar wireframes cedo.

## 3. Ciclo de cada módulo (repita 001 → 011)

| Etapa | O que fazer | Saída |
|-------|-------------|-------|
| 1. Clarificar | Resolver os `[ESCLARECER]` da spec | Spec sem pontos em aberto |
| 2. Planejar | Pedir ao agente o `plan.md`: modelo de dados, contratos de API, ADRs | `plan.md` revisado por você |
| 3. Tarefas | Quebrar em tarefas pequenas, cada uma ligada a RF/CA | `tasks.md` |
| 4. Testes primeiro | Escrever os `CT-*` a partir dos `CA-*` | Testes falhando (vermelho) |
| 5. Implementar | Uma tarefa por vez; commit pequeno | Testes verdes |
| 6. Validar | UAT com dados reais da RSL (Doc 4, portão do módulo) | Portão do módulo aprovado |
| 7. Sincronizar | Se o comportamento mudou, atualize a spec primeiro | Spec = código |

Prompts-modelo:
- *Planejar:* "Leia `constitution.md` e `specs/003-…/spec.md`. Proponha o plan.md: entidades e relacionamentos, endpoints, decisões que precisam de ADR. Não escreva código."
- *Tarefas:* "Gere tasks.md a partir do plan.md: tarefas ≤ 4h, cada uma citando RF e CA, na ordem de dependência."
- *Implementar:* "Implemente a tarefa T-07. Escreva antes os testes dos CA-03 e CA-04. Não altere nada fora do escopo da tarefa."

## 4. Ordem de trabalho (alinhada ao Doc 4)

| Release | Módulos | Meta |
|---------|---------|------|
| **R1.0 (MVP)** | 001, 002, 003, 004, 005, 006 (só Musts) + telas correspondentes | Pronto antes do Portão 0 da RSL |
| **R2.0** | 007, 008, 009 | Antes da Fase 8 da RSL |
| **R3.0** | 010, 011 | Antes da Fase 10 da RSL |

Comece pelo **001 (fundação)** e faça um "esqueleto andante": login → criar projeto → registrar auditoria → ver a tela. Isso valida stack, CI e a integração front-back antes dos módulos grandes.

## 5. Front-end: como se encaixa
- A spec de front (`frontend/spec-front.md`, v2) usa o benchmark do Parsifal (`docs/benchmark-parsifal.md`) e é **complementar** às specs de módulo: cada tela cita os RF/CA que ela realiza. Regra de negócio fica na spec do módulo; a spec de front cobre navegação, layout, estados e comportamento.
- Ordem: para cada módulo, valide o wireframe com R1/R2 **antes** do `plan.md`. Mudança de UX é barata no papel e cara em código.
- Você pode prototipar as telas críticas (triagem, QA, extração) em um protótipo clicável; o kit traz wireframes em texto para servir de briefing.

## 6. Checklist "pronto para começar a codar"
- [ ] Pontos abertos das specs 001 e 002 resolvidos (os do MVP)
- [ ] ADRs 001–006 decididos
- [ ] Repositório e CI criados (o `CLAUDE.md` já está no kit)
- [ ] Specs 001 e 002 sem `[ESCLARECER]`
- [ ] Wireframes de 001/002 vistos por R1/R2
- [ ] Data do Portão 0 da RSL definida (dá o prazo do MVP)
- [ ] Fallback manual definido (Doc 4: Excel/Rayyan/Atlas.TI em formato importável) caso o MVP atrase

## 7. Riscos que valem atenção
1. **Escopo × calendário da RSL:** o Doc 4 estima ~28–34 semanas até o go-live; se a RSL não puder esperar, execute o MVP mínimo e use o fallback nas demais fases.
2. **Specs incompletas geram código plausível, mas errado:** a IA preenche lacunas. Os `[ESCLARECER]` existem para isso.
3. **Revisão:** o gargalo do SDD é revisar plano e código. Reserve tempo.
4. **Cálculos estatísticos:** exija validação cruzada manual (≥ 3 casos) antes de confiar em κ/α.
5. **Você como PO + pesquisador:** o sistema é ferramenta e também objeto de tese/artigo (Doc 4, D12.2.2). Decida cedo se ele será uma contribuição publicável, pois isso afeta documentação e licença.

## 8. Teste local do MVP

No PowerShell, na raiz do repositório, suba a API e o PostgreSQL:

```powershell
docker compose up --build
```

Abra `http://127.0.0.1:8002`. A aplicação roda as migrações e cria as contas locais de demonstração na primeira inicialização:

| Papel | Email | Senha |
|---|---|---|
| admin | admin@rsl.local | admin123 |
| revisor | reviewer@rsl.local | reviewer123 |
| observador | observer@rsl.local | observer123 |

Com o admin, crie uma conta na seção "Contas de usuário". Entre com ela em outra sessão para testar seu papel; o observador deve receber acesso somente de leitura. O painel principal ainda usa estudos e indicadores demonstrativos.

**Limites deste teste:** contas e sessões persistem no PostgreSQL local. Artefatos usam um volume de filesystem persistente no Compose por decisão complementar ao ADR-004; produção permanece planejada para MinIO/S3. Estudos e métricas do dashboard continuam demonstrativos. As contas e segredos padrão são exclusivos para desenvolvimento local, não para produção.
