# Spec 005 — Avaliação de Qualidade (QA)

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D5 (Doc 4) |
| Fase da RSL atendida | Fases 2 (piloto) e 5 (Doc 3) |
| Grupo funcional | F6 (Doc 1) |
| Requisitos | RF29–RF32 · RNF02 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Aplicar o checklist de qualidade (Zhou et al., 2015, adaptado no Protocolo v4.0 §7: 10 critérios em 4 categorias — Reporting, Rigor, Credibility, Relevance) por dois avaliadores independentes, calcular scores, classificar por faixas de corte, medir concordância (κ ponderado) e arbitrar divergências. O sistema calcula e registra; **humanos pontuam** (P1).

### Propósito do QA (Zhou et al., 2015, P1–P5; Kitchenham 2007, §6.3.3)
Zhou classifica cinco propósitos: P1 seleção, P2 explicar diferenças entre resultados, P3 ponderação, P4 interpretação, P5 recomendações. Neste projeto o QA serve a **P1** (score < 4,0 exclui), **P3** (ponderação da síntese, spec 008) e **P4** (flag de ressalva na interpretação). Kitchenham exige que o protocolo diga *como* os dados de qualidade serão usados; quando o uso é P1, os dados devem ser coletados **antes** da extração principal, em formulário separado (o que a Fase 5 antes da Fase 7 já cumpre).

## 2. Atores
R1, R2 (avaliam), R3 (arbitra), `admin` (configura instrumento), OR (lê).

## 3. Escopo
**Dentro:** configuração do instrumento, avaliação dupla independente com justificativa, score total e por categoria, faixas de corte, κ ponderado, fila de divergências e arbitragem, piloto do QA.
**Fora:** decisão de inclusão por escopo (spec 004); uso de IA para pontuar (proibido, P2).

## 4. Histórias de usuário
- **US1 (P1)** Configurar o checklist (categorias, critérios, escala 0/0,5/1, N/A).
- **US2 (P1)** Avaliar cada estudo de forma independente, justificando cada critério.
- **US3 (P1)** Ver score, classificação e flag de ressalva/exclusão.
- **US4 (P1)** Medir κ ponderado e arbitrar divergências.
- **US5 (P2)** Rodar o piloto de QA antes da avaliação completa.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF29 | O sistema DEVE configurar o checklist com 10 critérios em 4 categorias, escala 0/0,5/1 e itens marcáveis como N/A, com recálculo do denominador quando houver N/A | Must | F6.1 | 7.4 |
| RF30 | O sistema DEVE permitir 2 avaliações independentes por estudo, com justificativa registrada por critério pontuado | Must | F6.2 | 7.5 |
| RF31 | O sistema DEVE calcular score total (0–10) e por categoria e classificar: ≥ 7,0; 4,0–6,9 (flag de ressalva); < 4,0 (exclusão, propósito P1) | Must | F6.3 | 7.3 |
| RF32 | O sistema DEVE calcular κ ponderado (peso linear), reportá-lo e gerenciar fila de divergências com arbitragem do R3 | Must | F6.4 | 7.5 |

## 6. Requisitos não funcionais
- **RNF02** Auditoria de cada pontuação, alteração e arbitragem.
- **RNF05** Dois avaliadores simultâneos sem perda de escrita.
- Precisão: κ ponderado difere da conferência manual em ≤ 0,001.

## 7. Regras de negócio
1. Independência (P7): a avaliação do outro só aparece após ambos confirmarem.
2. Item N/A é excluído do denominador; score = (soma dos pontos aplicáveis ÷ nº de critérios aplicáveis) × 10.
3. N/A só é permitido em critérios marcados como "elegíveis a N/A" no instrumento: Q6 e Q7 (RSLs e estudos conceituais) e Q9 (sem stakeholders humanos por design).
4. Divergência > 0,5 ponto em um item vai à arbitragem do R3 (Doc 3, A5.4.1).
5. Score final do estudo = média dos dois avaliadores após consenso; se arbitrado, prevalece a decisão do R3 item a item.
6. Score < 4,0 exclui o estudo do corpus e gera registro no PRISMA (motivo "qualidade"); 4,0–6,9 mantém o estudo com flag de ressalva.
7. Excluído por qualidade é mantido no banco com motivo (nunca apagado).

8. Score de categoria usa a mesma fórmula do score total, restrita aos critérios aplicáveis da categoria, e é exibido **separado**; o sistema nunca mistura "qualidade do relato" (Reporting) e "qualidade do estudo" num número só além do score total do Protocolo (Kitchenham 2007, §6.3.2: boa prática não misturar; se misturar, dar menos peso ao relato).
9. Cada critério é pontuado numa escala de três pontos (1 = sim, 0,5 = em parte, 0 = não), a mais usada nas RSLs em SE (Zhou 2015, §5.2, Ponderação); perguntas são fechadas (Zhou: quase todas as checklists são fechadas).
10. O instrumento é único por tipo de estudo: se o corpus mistura tipos (ex.: RSLs como subcamada, RF38), cada tipo usa o seu instrumento ou variante de N/A (Kitchenham 2007, §6.3.3).
11. O κ ponderado inicial (antes das resoluções) é registrado no relatório e não é sobrescrito (Kitchenham 2007, §6.2.3).

## 8. Critérios de aceite

**CA-01 (RF29)** Dado o instrumento configurado, quando o admin tenta salvar com número de critérios ≠ 10 ou sem 4 categorias, então recebe aviso de desvio do protocolo que exige justificativa.

**CA-02 (RF29)** Dado um estudo com 2 critérios N/A e 8 pontuados somando 6,0, então o score é (6,0 ÷ 8) × 10 = 7,5.

**CA-03 (RF30)** Dada uma pontuação de critério sem justificativa, quando o avaliador confirma, então o sistema recusa; com justificativa, aceita.

**CA-04 (RF30)** Dado que R1 confirmou e R2 não, quando R2 abre o estudo, então não vê as notas de R1.

**CA-05 (RF31)** Dados scores 7,0 / 6,9 / 3,9, então as classes são respectivamente "aprovado", "ressalva" e "excluído por qualidade".

**CA-06 (RF31)** Dado um score < 4,0, quando confirmado, então o estudo sai do corpus, aparece na lista de excluídos com motivo e a contagem PRISMA é atualizada.

**CA-07 (RF32)** Dado um conjunto de pontuações de 20 estudos, quando o κ ponderado é calculado, então coincide (≤ 0,001) com a conferência manual de ≥ 3 casos.

**CA-08 (RF32)** Dado um item com diferença de 1,0 ponto entre R1 e R2, quando ambos confirmam, então entra na fila do R3; diferença ≤ 0,5 é resolvida por média sem escalar.

**CA-09 (RNF02)** Dada uma nota alterada após a confirmação, então a auditoria registra valor anterior, novo valor, autor e justificativa.

**CA-10 (RF31)** Dado um estudo com score de Reporting 10,0 e de Rigor 4,0, então a tela mostra os dois valores separados, além do score total, sem fundi-los.

## 9. Casos de borda
- Estudo com todos os critérios elegíveis a N/A marcados: bloquear (mínimo de critérios aplicáveis configurável).
- Avaliador muda a pontuação depois do outro confirmar: exige reabertura registrada.
- Estudo removido do corpus por decisão posterior de escopo: manter avaliação, marcar como inativa.
- RSLs incluídas como subcamada (RF38): usar variantes de N/A definidas no instrumento.

## 9b. Instrumento do Protocolo v4.0 (§7) — carga inicial

Fonte: `docs/fonte/Protocolo_RSL_XAI_MAS_v4.docx`, §7.1–7.5. São **10 questões** em 4 categorias (3 Reporting, 4 Rigor, 1 Credibility, 2 Relevance), escala 0 / 0,5 / 1.

| # | Categoria | Critério | 1 | 0,5 | 0 |
|:-:|-----------|----------|---|-----|---|
| Q1 | Reporting | O objetivo e a questão de pesquisa estão claramente definidos? | objetivo explícito e alinhado às RQs | presente mas impreciso | ausente ou vago |
| Q2 | Reporting | As conclusões são suportadas pelos dados e respondem às questões de pesquisa? | derivadas dos dados | parcialmente fundamentadas | sem suporte |
| Q3 | Reporting | As ameaças à validade são identificadas e discutidas? | com mitigações | mencionadas sem mitigação | não discutidas |
| Q4 | Rigor | O design do estudo é adequado ao objetivo? | justificado e coerente com as RQs | adequado mas não justificado | inadequado ou ausente |
| Q5 | Rigor | O método de coleta de dados é descrito e justificado? | detalhado e justificado | descrito sem justificativa | não descrito |
| Q6 | Rigor | O MAS é caracterizado (tipo de agente, número, interações, arquitetura)? | completamente descrito | parcial | não caracterizado |
| Q7 | Rigor | A abordagem de XAI está vinculada à arquitetura do MAS? | vínculo explícito e justificado | implícito ou parcial | XAI isolada |
| Q8 | Credibility | Os requisitos de XAI/RAI/Trust são definidos ou operacionalizados? | formalizados e mensuráveis | mencionados sem formalização | ausentes |
| Q9 | Relevance | O papel dos stakeholders na explicabilidade é discutido? | identificados com impacto descrito | mencionados | não discutidos |
| Q10 | Relevance | O estudo identifica lacunas ou direções futuras em XAI para MAS? | lacunas explícitas com direções | superficiais | não abordadas |

**Faixas (§7.3):** ≥ 7,0 alta, peso pleno; 4,0–6,9 moderada, incluída com flag de ressalva e reportada separadamente; < 4,0 baixa, **excluída** (propósito P1).

**N/A (§7.3 e §7.4):** Q6 e Q7 são N/A para RSLs e estudos puramente conceituais; Q9 é N/A quando o estudo não envolve stakeholders humanos por design (ex.: contribuição puramente teórica), caso documentado na extração. O N/A sai do denominador: **score ajustado = (Σ pontos obtidos ÷ Σ pontos possíveis dos itens aplicáveis) × 10**. A contagem de N/A por estudo é reportada nos resultados.

**Procedimento (§7.5):** dupla avaliação independente; κ ponderado com peso linear sobre 0 / 0,5 / 1, reportado no relato; divergência de até 0,5 em item resolvida por discussão, maior ou persistente arbitrada pelo terceiro revisor; pontuação **por categoria** além do total, alimentando a sensibilidade (spec 008); a planilha de QA com notas e justificativas entra no pacote de replicação.

**Propósitos (§7.1):** P1 seleção (score < 4,0 exclui), P3 ponderação (hipóteses e síntese) e P4 interpretação (por categoria e sensibilidade). P2 e P5 serão avaliados quanto à viabilidade na condução e, se adotados, vão ao log de desvios.

## 9a. Comparação com a checklist de Dybå & Dingsøyr (2008, via Zhou 2015)
Zhou (§5.3) descreve as quatro dimensões e a checklist mais citada (11 critérios: 3 Reporting, 5 Rigor, 2 Credibility, 1 Relevance). A tabela abaixo reconstrói essa checklist a partir da Tab. 6 de Zhou e serve só de comparação: **a carga inicial é a da seção 9b.**

| # | Categoria | Critério (formulação de Zhou Tab. 6) | Candidato a N/A |
|:-:|-----------|--------------------------------------|:---------------:|
| 1 | Reporting | O estudo é baseado em pesquisa? | — |
| 2 | Reporting | Há declaração clara dos objetivos? | — |
| 3 | Reporting | Há descrição adequada do contexto? | — |
| 4 | Rigor | O desenho da pesquisa é adequado aos objetivos? | — |
| 5 | Rigor | A estratégia de recrutamento é adequada? | Sim (sem participantes) |
| 6 | Rigor | Havia grupo de controle para comparação? | Sim (não experimental) |
| 7 | Rigor | Os dados foram coletados de modo que responda à questão? | — |
| 8 | Rigor | A análise dos dados foi suficientemente rigorosa? | — |
| 9 | Credibility | A relação entre pesquisador e participantes foi considerada? | Sim (sem participantes) |
| 10 | Credibility | Há declaração clara dos achados? | — |
| 11 | Relevance | O estudo tem valor para pesquisa ou prática? | — |

Os N/A sugeridos são hipóteses de trabalho a validar; a coluna não vem do artigo.

## 10. Dependências
Specs 001, 002 (instrumento configurado por projeto), 004 (corpus definido).

## 11. Pontos em aberto
- ~~`[ESCLARECER 1]`~~ **Resolvido com o v4.0:** os 10 critérios e as categorias estão na seção 9b.
- ~~`[ESCLARECER 5]`~~ **Resolvido com o v4.0:** N/A existe, com Q6, Q7 e Q9 como itens elegíveis.
- **Resolvido pelo PO:** scores por categoria serão normalizados para 0–10 com a mesma fórmula do score total.
- **Resolvido pelo PO:** exigir pelo menos 7 critérios aplicáveis; reportar κ ponderado e alertar abaixo de 0,6, sem bloquear o fechamento.

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF29 | CA-01, CA-02 | CT-QA-01, CT-QA-02 |
| RF30 | CA-03, CA-04 | CT-QA-03, CT-QA-04 |
| RF31 | CA-05, CA-06, CA-10 | CT-QA-05, CT-QA-06, CT-QA-10 |
| RF32 | CA-07, CA-08 | CT-QA-07, CT-QA-08 |
| RNF02 | CA-09 | CT-QA-09 |
