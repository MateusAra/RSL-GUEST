# Tarefas do módulo 001 — Fundação

Status: aprovada pelo PO

## Ordem sugerida
1. Setup de ambiente e CI
2. Autenticação e autorização
3. Auditoria append-only
4. Storage e versionamento de artefatos
5. Backup/restore
6. Testes e validação UAT

## T-01 — Setup do repositório e CI
- Objetivo: preparar o ambiente de integração para a base do sistema.
- RF/HAB: HAB-03, RNF07
- Entregáveis:
  - estrutura inicial do repositório
  - .gitignore
  - stack base definida (pooled por ADR-002/003)
  - pipeline mínimo de lint/test
- Critérios: repositório limpo e reprodutível por novo desenvolvedor.

## T-02 — Modelagem de usuários, papéis e autenticação
- Objetivo: habilitar login, sessão e autorização por papel.
- RF/HAB: RF51, HAB-01, RNF07
- Entregáveis:
  - tabela de usuários
  - papéis: admin, revisor, terceiro_revisor, observador
  - endpoint de login e middleware de autenticação
- Critérios: `observador` não consegue alterar dados; autenticação obrigatória.

## T-03 — Permissões por endpoint e política de escrita
- Objetivo: aplicar autorização no servidor para cada rota relevante.
- RF/HAB: RF51, HAB-01, RNF07
- Entregáveis:
  - matriz papel x endpoint
  - guard de authorização por API
  - tratamento de `403` e `401`
- Critérios: combinações não permitidas retornam `403` sem efeito colateral.

## T-04 — Auditoria append-only
- Objetivo: registrar todas as alterações com cadeia de rastreabilidade.
- RF/HAB: RF56, RNF02
- Entregáveis:
  - tabela de eventos de auditoria
  - trigger ou service layer para append-only
  - exportação JSON/CSV
- Critérios: qualquer mudança persiste em auditoria com autor, data/UTC, ação, valor anterior e novo valor.

## T-05 — Armazenamento de artefatos e versionamento
- Objetivo: proteger PDFs e raw results sem sobrescrita.
- RF/HAB: HAB-02
- Entregáveis:
  - armazenamento de objetos com SHA-256
  - upload em nova versão
  - recuperação de versões antigas
- Critérios: arquivo novo com mesmo nome gera nova versão e mantém o original.

## T-06 — Backup, restore e migrações
- Objetivo: garantir recuperação com RPO <= 24h.
- RF/HAB: HAB-03, HAB-04, RNF12
- Entregáveis:
  - migrações versionadas
  - backup automático diário
  - restore em ambiente de teste
- Critérios: dados restaurados com perda <= 24h e auditoria íntegra.

## T-07 — Casos de teste do módulo 001
- Objetivo: validar os critérios de aceite e o comportamento do módulo.
- RF/HAB: RF51, RF56, HAB-01, HAB-02, HAB-04, RNF07
- Entregáveis:
  - CT-FND-01 .. CT-FND-08
  - execução em CI e validação de regressões
- Critérios: todos os CA-01 a CA-08 têm teste rastreável.

## T-08 — UAT e alinhamento com a spec
- Objetivo: confirmar que o módulo atende ao que a RSL exige.
- RF/HAB: todos do módulo 001
- Entregáveis:
  - checklist UAT com dados reais
  - atualização de spec se houver mudança de comportamento
  - preparação do próximo módulo (002)
- Critérios: aceite do PO e consistência entre spec e implementação.

## Mapeamento das tarefas com os critérios de aceite
- T-02: CA-01, CA-02, CA-05
- T-04: CA-03, CA-04
- T-05: CA-06
- T-06: CA-07
- T-03: CA-08
