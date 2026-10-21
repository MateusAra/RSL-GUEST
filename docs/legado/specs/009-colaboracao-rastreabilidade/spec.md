# Spec 009 — Colaboração, Dashboard e Cadeia de Evidência

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D8 (Doc 4) — liberar até a Fase 10 da RSL (parte do fluxo de trabalho é usada desde a Fase 3) |
| Fase da RSL atendida | Transversal (Doc 3) |
| Grupo funcional | F11, F12 (Doc 1) |
| Requisitos | RF52–RF55, RF57 · RNF01, RNF04, RNF05 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Coordenar o trabalho da equipe (atribuição de lotes, notificações, discussões), mostrar o progresso (dashboard) e tornar navegável a cadeia de evidência RQ → busca → seleção → QA → extração → codificação → conclusão, incluindo o modo somente leitura para o orientador. Papéis e auditoria estão na spec 001.

## 2. Atores
R1, R2, R3, `admin` (atribui), OR (observa).

## 3. Escopo
**Dentro:** atribuição de lotes por fase, notificações de pendências/conflitos, threads de discussão por estudo, dashboard, cadeia de evidência navegável, modo somente leitura.
**Fora:** papéis, autenticação e log (001); geração do relato (010).

## 4. Histórias de usuário
- **US1 (P1)** Como admin, atribuir lotes de estudos aos revisores por fase de forma balanceada.
- **US2 (P1)** Como revisor, ser avisado das pendências e conflitos.
- **US3 (P2)** Como revisor, discutir um estudo em um fio de conversa cuja resolução fica vinculada à decisão final.
- **US4 (P2)** Como pesquisador, ver o progresso, κ, scores e pendências por fase.
- **US5 (P2)** Como orientador, navegar da conclusão à citação sem poder editar.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF52 | O sistema DEVE atribuir lotes de estudos por fase (balanceados entre R1 e R2) e notificar pendências | Must | F11.2 | 5.3, 7 |
| RF53 | O sistema DEVERIA registrar discussões por estudo, com thread e resolução vinculada à decisão final | Should | F11.3 | 5.3.3 |
| RF54 | O sistema DEVERIA exibir dashboard de progresso (estudos processados, pendências, κ, scores) atualizado por fase | Should | F11.4 | 14.4 |
| RF55 | O sistema DEVERIA exibir cadeia de evidência navegável RQ → campo → citação → conclusão, por estudo e por RQ, sem quebras | Should | F12.1 | 9.1 |
| RF57 | O sistema DEVERIA fornecer modo somente leitura ao orientador/auditores | Should | F12.3 | 14.3 |

## 6. Requisitos não funcionais
- **RNF01** Rastreabilidade: da conclusão de qualquer análise à citação em ≤ 4 cliques.
- **RNF04** Nenhuma quebra na cadeia (sem elo faltante) no corpus final.
- **RNF05** Concorrência: duas pessoas atribuindo/discutindo simultaneamente sem perda.
- **RNF14** Dashboard com 1.000 estudos carrega em ≤ 3 s.

## 7. Regras de negócio
1. A atribuição padrão é dupla (todo estudo tem R1 e R2 na triagem e no QA); balanceamento refere-se à ordem e à carga, não à divisão do trabalho.
2. Reatribuição de lote exige justificativa registrada e não apaga votos já dados.
3. Notificação é emitida quando: novo lote atribuído, conflito criado, arbitragem solicitada, portão prestes a fechar com pendências.
4. Thread de discussão nunca é apagada; resolução é um campo separado que aponta para a decisão (voto, consenso, arbitragem).
5. Dashboard mostra somente agregados que o usuário tem permissão de ver; R1 não vê votos pendentes de R2 (P7).
6. Cadeia de evidência só exibe elos existentes; elo faltante aparece explicitamente como lacuna, nunca é preenchido.
7. O modo somente leitura desativa todos os controles de escrita, e o servidor recusa escrita (403).

## 8. Critérios de aceite

**CA-01 (RF52)** Dado um pool de 1.000 estudos e 2 revisores, quando o lote da Fase 1 é atribuído, então ambos recebem os 1.000 (dupla independente) em ordens diferentes e o dashboard mostra 0% concluído para ambos.

**CA-02 (RF52)** Dado um conflito criado na triagem, então R1 e R2 recebem notificação em até 1 min.

**CA-03 (RF53)** Dado um estudo em conflito, quando R1 e R2 discutem e chegam a consenso, então a resolução é registrada e vinculada ao consenso; a discussão permanece consultável.

**CA-04 (RF54)** Dado o final da Fase 3, então o dashboard mostra % votado por revisor, κ, nº de conflitos abertos e pendências, sem revelar votos individuais de um ao outro antes da confirmação.

**CA-05 (RF55)** Dada uma conclusão sobre H1, quando o usuário navega a cadeia, então chega à RQ, aos campos, aos estudos e à citação + página em ≤ 4 cliques.

**CA-06 (RF55/RNF04)** Dado um campo cuja citação foi removida, então a cadeia mostra o elo como lacuna e a validação de integridade falha.

**CA-07 (RF57)** Dado um usuário `observador`, quando abre qualquer tela, então nenhum botão de escrita aparece e chamadas de escrita à API retornam 403.

**CA-08 (RNF05)** Dadas duas atribuições simultâneas ao mesmo lote, quando ambas são enviadas, então uma é aplicada e a outra recebe aviso de conflito, sem perda de dados.

## 9. Casos de borda
- Revisor indisponível: `admin` reatribui, mantendo os votos já dados.
- Estudo sem RQ alcançável pela cadeia: sinalizado como órfão.
- Thread com muitas mensagens: paginação sem alterar a ordem.
- Notificação para usuário desativado: descartada com registro.

## 10. Dependências
Spec 001 (papéis/auditoria), specs 004–008 (fontes de dados da cadeia e do dashboard).

## 11. Pontos em aberto
- `[ESCLARECER 1]` Canal de notificação (só no sistema, e-mail também)?
- `[ESCLARECER 2]` "Balanceada" (RF52): confirmar que a atribuição é sempre dupla e o balanceamento é só de ordem/carga.
- `[ESCLARECER 3]` Quem pode fechar uma discussão (qualquer participante ou só o autor da decisão)?

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF52 | CA-01, CA-02, CA-08 | CT-COL-01, 02, 08 |
| RF53 | CA-03 | CT-COL-03 |
| RF54 | CA-04 | CT-COL-04 |
| RF55, RNF01, RNF04 | CA-05, CA-06 | CT-COL-05, 06 |
| RF57 | CA-07 | CT-COL-07 |
