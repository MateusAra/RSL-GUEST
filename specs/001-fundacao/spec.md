# Spec 001 — Fundação: Autenticação, Papéis, Auditoria, Armazenamento e Backup

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D2 (Doc 4) |
| Fase da RSL atendida | Todas (transversal) |
| Grupo funcional | F11.1, F12.2 (Doc 1) |
| Requisitos | RF51, RF56 · RNF02, RNF05, RNF07, RNF12 · habilitadores HAB-01..05 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Camada transversal sobre a qual todos os módulos se apoiam: quem pode fazer o quê, registro imutável de tudo o que muda, armazenamento seguro de PDFs e resultados brutos e recuperação de desastres. Nada de negócio da RSL é decidido aqui; erros aqui contaminam todos os módulos (por isso é a primeira spec).

## 2. Atores
`admin`, `revisor`, `terceiro_revisor`, `observador` (somente leitura) e o próprio sistema (serviço de auditoria).

## 3. Escopo
**Dentro:** login e sessões, autorização por papel, serviço central de auditoria append-only, armazenamento de objetos (PDFs, raw results, anexos), migrações versionadas, backup e restore.
**Fora:** regras de negócio dos módulos; notificações (spec 009); exportação do pacote de replicação (spec 011).

## 4. Histórias de usuário
- **US1 (P1)** Como admin, quero cadastrar usuários e atribuir um dos 4 papéis para controlar o acesso.
- **US2 (P1)** Como qualquer módulo, quero registrar uma entrada de auditoria com uma chamada única para garantir rastreabilidade.
- **US3 (P1)** Como revisor, quero anexar PDFs e arquivos brutos que não podem ser alterados depois de arquivados.
- **US4 (P1)** Como pesquisador, quero restaurar os dados após falha com perda de no máximo 24 h.
- **US5 (P2)** Como orientador (observador), quero navegar em modo leitura sem risco de alterar dados.

## 5. Requisitos

| ID | Requisito | Prior. | F.n.n |
|----|-----------|:------:|-------|
| RF51 | O sistema DEVE gerenciar 4 papéis (`admin`, `revisor`, `terceiro_revisor`, `observador`) com permissões diferenciadas; `observador` é estritamente somente leitura | Must | F11.1 |
| RF56 | O sistema DEVE registrar log imutável de toda alteração de dados, com autor, data/hora, ação e valor anterior, exportável | Must | F12.2 |
| HAB-01 | O sistema DEVE autenticar todo acesso; requisições não autenticadas retornam 401 em qualquer endpoint | Must | — |
| HAB-02 | O sistema DEVE armazenar PDFs e raw results em armazenamento de objetos com hash de integridade (SHA-256) e versão imutável | Must | F3.3.2, F5.3.1 |
| HAB-03 | O sistema DEVE usar migrações de banco versionadas e reversíveis; nenhuma alteração manual de schema em produção | Must | — |
| HAB-04 | O sistema DEVE executar backup automático diário com RPO ≤ 24 h e restore testado | Must | RNF12 |
| HAB-05 | O sistema DEVERIA expor um mecanismo padrão de escrita otimista (versão de registro) para detecção de conflitos | Should | RNF05 |

## 6. Requisitos não funcionais
- **RNF02** Auditoria: entradas não editáveis nem apagáveis, inclusive por `admin`.
- **RNF07** Segurança: autorização verificada no servidor em todo endpoint (matriz papel × endpoint).
- **RNF12** Backup/restore: RPO ≤ 24 h; restore testado antes do go-live.
- **RNF05** Concorrência: base para dois revisores simultâneos sem perda de escrita.

## 7. Regras de negócio
1. Toda escrita em entidade de decisão passa pelo serviço de auditoria na mesma transação; falha na auditoria aborta a escrita.
2. A tabela de auditoria é append-only: sem UPDATE/DELETE para nenhuma credencial de aplicação.
3. `observador` nunca recebe permissão de escrita, nem por configuração do `admin`.
4. Arquivo arquivado nunca é sobrescrito; novo envio cria nova versão e mantém a anterior.
5. Um usuário pode ter um papel por projeto; o mesmo usuário não pode ser R1 e R2 no mesmo estudo.

## 8. Critérios de aceite

**CA-01 (RF51)** Dado um usuário `observador`, quando tenta qualquer operação de escrita (UI ou API), então recebe 403 e nada é alterado.

**CA-02 (RF51)** Dado um `revisor`, quando tenta acessar funções de `admin` (gerenciar usuários), então o acesso é negado.

**CA-03 (RF56)** Dada a alteração de qualquer campo de decisão, quando a transação conclui, então existe entrada com autor, data/hora UTC, ação, valor anterior e novo valor.

**CA-04 (RF56/RNF02)** Dada a tabela de auditoria, quando qualquer credencial da aplicação tenta UPDATE ou DELETE, então o banco recusa a operação.

**CA-05 (HAB-01)** Dada requisição sem token, quando chama qualquer endpoint exceto login, então a resposta é 401.

**CA-06 (HAB-02)** Dado um PDF arquivado, quando alguém envia outro arquivo com o mesmo nome, então é criada nova versão e a original permanece recuperável com o mesmo hash.

**CA-07 (HAB-04/RNF12)** Dado um backup de até 24 h, quando o restore é executado em ambiente de teste, então os dados retornam com perda ≤ 24 h e a auditoria permanece íntegra.

**CA-08 (RNF07)** Dada a matriz papel × endpoint, quando a suíte de segurança é executada, então 100% das combinações não permitidas retornam 403.

## 9. Casos de borda
- Falha do serviço de auditoria no meio de uma escrita: transação revertida, nada persiste.
- Usuário removido: registros e auditoria preservados; conta é desativada, nunca apagada.
- Relógio do servidor divergente: timestamps sempre gerados no servidor, em UTC.
- Arquivo corrompido no upload: hash não confere, envio rejeitado.

## 10. Dependências
Nenhuma (primeira da cadeia). Todas as demais specs dependem desta.

## 11. Pontos em aberto
- **Resolvido no ADR-001:** cadastro individual com email e senha; senha armazenada com hash; sessão com JWT e refresh token rotativo. SSO institucional fica fora do escopo atual.
- **Resolvido pelo PO:** um usuário tem um papel por projeto e pode ter papéis diferentes em projetos distintos.
- `[ESCLARECER 3]` Retenção de backups (quantos dias)?

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF51 | CA-01, CA-02 | CT-FND-01, CT-FND-02 |
| RF56 | CA-03, CA-04 | CT-FND-03, CT-FND-04 |
| HAB-01 | CA-05 | CT-FND-05 |
| HAB-02 | CA-06 | CT-FND-06 |
| HAB-04 | CA-07 | CT-FND-07 |
| RNF07 | CA-08 | CT-FND-08 |
