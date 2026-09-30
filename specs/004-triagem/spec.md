# Spec 004 — Módulo de Triagem e Seleção

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D4 (Doc 4) |
| Fase da RSL atendida | 2, 3 e 4 (Doc 3) |
| Grupo funcional | F5 (Doc 1) |
| Requisitos | RF22–RF27, RF25 · RNF05, RNF08 |
| Protocolo | §5.3.1–§5.3.4 (v4.0) |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Dois revisores (R1, R2) triam de forma independente os estudos deduplicados em duas fases (título/resumo; texto completo). Divergências vão a consenso e, persistindo, ao terceiro revisor (R3). O sistema deve garantir independência, aplicar a matriz de decisão do protocolo, medir concordância (κ) e produzir as contagens do fluxograma PRISMA. **O sistema nunca decide inclusão/exclusão sozinho por juízo; apenas aplica a regra determinística da matriz sobre votos humanos.**

## 2. Atores
`R1`, `R2` (votam) · `R3` (arbitra) · `OR`/observador (só lê) · `admin` (configura).

## 3. Escopo
**Dentro:** pilotagem, Fase 1, Fase 2, matriz A–F, fila de conflitos, arbitragem, κ, contagens PRISMA.
**Fora:** busca e importação (spec 003), deduplicação (spec 003), avaliação de qualidade (spec 005), qualquer uso de IA para sugerir votos (proibido — P2).

## 4. Histórias de usuário (priorizadas)

**US1 (P1) — Votar na Fase 1 com independência.**
Como revisor, quero ver título, resumo e keywords e votar Incluir / Excluir / Incerto citando o critério CI/CE, sem ver o voto do colega.

**US2 (P1) — Resolver conflitos.**
Como revisor, quero uma fila das divergências para chegar a consenso e, se não houver, escalar ao R3, com tudo registrado.

**US3 (P1) — Fase 2 com texto completo.**
Como revisor, quero abrir o PDF e decidir, com justificativa obrigatória para exclusão mapeada a um CE.

**US4 (P1) — Pilotar critérios.**
Como pesquisador, quero sortear uma amostra, medir κ e só liberar a triagem completa quando κ ≥ 0,6.

**US5 (P2) — Fluxograma PRISMA.**
Como pesquisador, quero contagens por etapa e o fluxograma gerado automaticamente.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF22 | O sistema DEVE permitir voto Incluir/Excluir/Incerto por revisor por estudo, exigindo o CI/CE acionado em Excluir e Incerto | Must | F5.1 | 5.3.2 |
| RF22a | O sistema DEVE ocultar o voto de um revisor do outro até que ambos confirmem (ou até a fase encerrar) | Must | F5.1 | 5.3.2 |
| RF23 | O sistema DEVE aplicar a matriz de decisão A–F sobre os votos R1×R2 com estratégia inclusiva configurável | Must | F5.2 | 5.3.3 |
| RF24 | O sistema DEVE, na Fase 2, exibir o PDF anexo e exigir justificativa mapeada a um CE para toda exclusão | Must | F5.3 | 5.3.2 |
| RF25 | O sistema DEVE sortear amostra piloto configurável (padrão 20), calcular κ de Cohen por fase e bloquear a triagem completa com κ < 0,6 | Must | F5.4 | 5.3.1 |
| RF26 | O sistema DEVE manter fila de divergências (combinações D/E), registrar consenso e escalar ao R3 quando não houver | Must | F5.5 | 5.3.3 |
| RF27 | O sistema DEVERIA gerar contagens e fluxograma PRISMA (deduplicação, F1, F2, snowballing, QA) exportável | Should | F5.6 | 14.1 |

### Matriz de decisão (Protocolo v4.0, §5.3.3)

A matriz é simétrica (a ordem R1 × R2 não importa). Cada revisor vota Incluir, Excluir ou Incerto.

| Letra | Combinação | Resultado |
|:-----:|-----------|-----------|
| A | Incluir + Incluir | Incluído (avança) |
| B | Incluir + Incerto (qualquer ordem) | Avança |
| C | Incerto + Incerto | Avança |
| D | Incluir + Excluir (qualquer ordem) | Avança, resolvido em reunião de consenso |
| E | Incerto + Excluir (qualquer ordem) | Avança, resolvido em reunião de consenso |
| F | Excluir + Excluir | **Excluído** |

**Estratégia inclusiva (adotada no protocolo):** A a E avançam; só F sai. Persistindo a divergência em D/E após o consenso, o terceiro revisor arbitra. Petersen 2015 (Tab. 6) é a origem da matriz e reporta que a estratégia mais inclusiva recupera todos os relevantes, com cerca de 25% a mais de esforço que A–D.

**Pilotagem obrigatória antes da Fase 1 (§5.3.1):** sortear **20 estudos** aleatórios; aplicar CI/CE de forma independente (com *think-aloud*); calcular κ de Cohen por fase e discutir todas as divergências; atualizar CI/CE e o glossário; repetir até **κ ≥ 0,6 na Fase 1**.

**Concordância (§5.3.4):** Fase 1, κ ≥ 0,6 aceitável e ≥ 0,8 excelente; Fase 2, κ recalculado e reportado no relato, **sem limiar definido**; QA, κ ponderado com peso linear.

## 6. Requisitos não funcionais do módulo
- **RNF05** Dois revisores votando simultaneamente em estudos distintos e no mesmo estudo sem perda de voto.
- **RNF08** Um revisor conclui a triagem de 100 resumos em ≤ 90 min (teste de tarefa).
- **RNF02** Todo voto, alteração de voto, consenso e arbitragem gera entrada de auditoria imutável.
- **RNF14** Lista de 1.000 estudos carrega em ≤ 3 s.

## 7. Regras de negócio
1. Um voto pode ser alterado até a confirmação; depois disso, só via reabertura registrada (com justificativa e auditoria).
2. Voto Excluir/Incerto sem CI/CE informado é inválido.
3. Apenas a combinação F exclui automaticamente; A–E sempre avançam ou vão a consenso.
4. Estudo excluído na Fase 2 sem CE mapeado não pode ser salvo.
5. Não há transição do piloto para a triagem completa enquanto κ < limiar configurado (padrão 0,6), salvo desvio registrado pelo `admin`.
6. O R3 só vê o estudo em conflito depois que R1 e R2 registraram tentativa de consenso.
7. Estados do estudo: `Deduplicado → F1_votado → (F1_conflito → F1_resolvido) → F1_avança | F1_excluído → F2_votado → … → Incluído | Excluído`.

8. A matriz A–F é simétrica: (R1 = Incluir, R2 = Excluir) e (R1 = Excluir, R2 = Incluir) são a mesma letra D; idem B e E.
9. O piloto segue o processo de Petersen 2015 (Fig. 17): especificar CI/CE no protocolo → revisar entre os pesquisadores → aplicação em voz alta (*think-aloud*) de um revisor sobre um estudo → piloto em subconjunto → analisar divergências e calcular concordância → se inaceitável, atualizar os critérios e repetir → seleção completa → recalcular concordância e aplicar as regras de decisão. Cada atualização de CI/CE gera nova versão (spec 002, PRP-02).
10. O κ **inicial** do piloto é registrado e não é sobrescrito por recálculos posteriores; o relato usa esse valor (Kitchenham 2007, §6.2.3).
11. Incerteza na inclusão deve poder ser investigada por análise de sensibilidade (Kitchenham 2007, §6.2.3): o sistema mantém a lista de estudos que passaram por C, D ou E para esse fim (consumida pela spec 008).

## 8. Critérios de aceite (Dado / Quando / Então)

**CA-01 (RF22)** Dado um estudo na Fase 1, quando R1 seleciona "Excluir" sem informar CI/CE, então o sistema recusa o voto e exibe a mensagem de campo obrigatório.

**CA-02 (RF22a)** Dado que R1 confirmou seu voto e R2 ainda não, quando R2 abre o estudo, então o voto de R1 não é exibido em nenhuma tela nem endpoint acessível a R2.

**CA-03 (RF23)** Dado R1 = Excluir e R2 = Excluir, quando ambos confirmam, então o estudo passa a "Excluído" com a letra F e sai do pool; e dado R1 = Incluir e R2 = Excluir, então o estudo entra na fila de conflitos (letra D) e não é excluído.

**CA-04 (RF24)** Dado um estudo na Fase 2, quando o revisor marca "Excluir" sem CE mapeado, então o registro não é salvo.

**CA-05 (RF25)** Dada uma amostra piloto de 20 estudos votada por R1 e R2 com κ = 0,52, quando o admin tenta liberar a triagem completa, então o sistema bloqueia e informa o κ obtido e o limiar; com κ ≥ 0,6, libera.

**CA-06 (RF25)** Dado o mesmo conjunto de votos, quando o κ é recalculado manualmente em ≥ 3 casos de conferência, então a diferença para o valor do sistema é ≤ 0,001.

**CA-07 (RF26)** Dado um conflito, quando R1 e R2 registram decisão de consenso com justificativa, então o estudo sai da fila e a decisão consta na auditoria; quando registram "sem consenso", então o estudo é escalado ao R3, que registra a arbitragem com autor e data.

**CA-08 (RNF05)** Dado R1 e R2 votando ao mesmo tempo no mesmo estudo, quando ambos salvam, então os dois votos persistem sem sobrescrita.

**CA-09 (RF27)** Dada a triagem concluída, quando o pesquisador gera o PRISMA, então as contagens por etapa somam corretamente (total − duplicados − excluídos F1 − excluídos F2 = incluídos) e o fluxograma é exportável.

**CA-10 (RNF02)** Dada qualquer alteração de voto reaberta, então a auditoria mostra valor anterior, novo valor, autor, data e justificativa.

**CA-11 (RF23)** Dado R1 = Excluir e R2 = Incluir, então a letra é D, igual a R1 = Incluir e R2 = Excluir; dado R1 = Incerto e R2 = Excluir (ou o inverso), então a letra é E e o estudo vai à fila de conflitos.

**CA-12 (RF25)** Dado um piloto com κ inicial = 0,52 que, após ajuste dos CI/CE, chega a 0,71 em nova rodada, então o relatório exibe as duas rodadas e o κ inicial permanece registrado.

## 9. Casos de borda
- Estudo sem resumo: exibir aviso e permitir voto Incerto com CE apropriado.
- Revisor que abandona a sessão com voto não confirmado: rascunho preservado, não visível ao outro.
- Estudo atribuído a apenas um revisor por erro: sistema alerta pendência dupla; fase não fecha.
- PDF indisponível na Fase 2: registrar como excluído por CE2 (texto completo irrecuperável) após tentativa documentada.
- Múltiplas publicações do mesmo estudo: triar somente o registro canônico (spec 003).
- Fechar a fase com votos pendentes: bloqueado.

## 10. Dependências
- Spec 001 (fundação: autenticação, auditoria) e spec 003 (busca e deduplicação) concluídas.
- Glossário e CI/CE cadastrados (spec 002).

## 11. Fora de escopo / assunções
- Sem sugestão por IA de votos (P1, P2).
- Assume 2 revisores + 1 terceiro revisor disponíveis (ASS01).

## 12. Pontos em aberto
- ~~`[ESCLARECER 1]`~~ **Resolvido com o v4.0:** matriz confirmada; D e E avançam e vão a reunião de consenso, com arbitragem do terceiro revisor se persistir.
- ~~`[ESCLARECER 2]`~~ **Resolvido com o v4.0:** o piloto de 20 estudos é feito antes da Fase 1 (κ ≥ 0,6); na Fase 2 o κ é recalculado sobre o trabalho real.
- **Resolvido pelo PO:** na Fase 2, reportar κ e alertar quando κ < 0,6, sem bloquear o fechamento da fase.

## 13. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF22 | CA-01 | CT-TRI-01 |
| RF22a | CA-02 | CT-TRI-02 |
| RF23 | CA-03, CA-11 | CT-TRI-03, CT-TRI-11 |
| RF24 | CA-04 | CT-TRI-04 |
| RF25 | CA-05, CA-06, CA-12 | CT-TRI-05, CT-TRI-06, CT-TRI-12 |
| RF26 | CA-07 | CT-TRI-07 |
| RF27 | CA-09 | CT-TRI-09 |
| RNF05 | CA-08 | CT-TRI-08 |
| RNF02 | CA-10 | CT-TRI-10 |
