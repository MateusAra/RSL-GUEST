# Spec 008 — Análises: Bibliometria, Síntese de Hipóteses, Sensibilidade e Viés

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D7 (Doc 4) — liberar até a Fase 9 da RSL |
| Fase da RSL atendida | Fase 9 (Doc 3) |
| Grupo funcional | F9 (Doc 1) |
| Requisitos | RF44–RF47 · RNF10, RNF14 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Produzir, a partir dos dados do próprio sistema, as análises da RSL: bibliometria, distribuição de vereditos H1/H2 ponderada por qualidade e segmentada por subcorpus, análise de sensibilidade em 6 dimensões e comparação entre canais de publicação (viés de publicação). As análises devem ser reexecutáveis e conferíveis manualmente.

## 2. Atores
R1 (executa), R2 (confere), OR (lê), `admin` (configura ponderação).

## 3. Escopo
**Dentro:** distribuições e redes bibliométricas, síntese de vereditos, motor de sensibilidade, comparativo por canal, exportação de tabelas/figuras.
**Fora:** meta-análise estatística formal (decisão A9.5 do Doc 3 — usa-se effect direction plot se inviável); geração do texto do relato (spec 010).

## 4. Histórias de usuário
- **US1 (P1)** Ver a distribuição de vereditos H1/H2 ponderada por score de qualidade e segmentada.
- **US2 (P1)** Reexecutar as análises por subconjuntos (sensibilidade) e ver onde os achados mudam.
- **US3 (P2)** Gerar bibliometria (distribuições, nuvens, redes).
- **US4 (P2)** Comparar resultados por canal (periódico, conferência, pré-print).

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF44 | O sistema DEVERIA gerar ≥ 5 análises bibliométricas (ano, base, veículo, método, research type, afiliação, citações; nuvem de palavras; redes de coocorrência, cocitação e coautoria) com visualizações exportáveis | Should | F9.1 | 10.1 |
| RF45 | O sistema DEVE sintetizar vereditos H1/H2 com ponderação por score de qualidade, segmentados por subcorpus (LLM × clássico, domínio, período, canal) | Must | F9.2 | 10.1 D, 3.3 |
| RF46 | O sistema DEVE reexecutar análises por 6 dimensões de sensibilidade: qualidade (≥ 7,0), tipo de sistema, tipo de estudo, domínio, período (2016–2020 × 2021–2026) e canal (com/sem pré-prints) | Must | F9.3 | 10.3 |
| RF47 | O sistema DEVERIA comparar resultados por canal e sinalizar concentração de autoria/grupos | Should | F9.4 | 10.5 |

## 6. Requisitos não funcionais
- **RNF10** Escalabilidade: análises sobre corpus de ≥ 500 estudos incluídos sem degradação perceptível.
- **RNF14** Performance: qualquer análise sobre 1.000 registros retorna em ≤ 3 s (exceto redes, ≤ 15 s).
- **RNF01** Todo número exibido leva à lista de estudos que o compõem (drill-down).
- **RNF03** Reprodutibilidade: mesma base + mesmos parâmetros ⇒ mesmos resultados; parâmetros da execução ficam registrados.

## 7. Regras de negócio
1. Só entram nas análises estudos "Incluídos" com QA concluído; RSLs (subcamada) ficam de fora da síntese H1/H2.
2. Estudos com ressalva (4,0–6,9) são reportados separadamente na síntese (Doc 3 A9.2.2) além de ponderados.
3. Ponderação conforme a regra configurada na spec 002 (RF10); a regra usada fica gravada junto ao resultado.
4. Cada execução de análise gera um "instantâneo" imutável com data, filtros, versão dos dados e ponderação.
5. Estudo com múltiplas publicações conta 1× (registro canônico).
6. Sensibilidade nunca altera os dados; apenas reaplica filtros.
7. Vereditos "inconclusivo" permanecem no denominador e são exibidos, nunca descartados.

## 8. Critérios de aceite

**CA-01 (RF45)** Dado um corpus com vereditos e scores conhecidos, quando a síntese roda, então a distribuição ponderada coincide (± 0,001) com o cálculo manual de ≥ 3 casos.

**CA-02 (RF45)** Dados estudos de um subcorpus LLM e outro clássico, quando a segmentação é aplicada, então a soma dos segmentos é igual ao total (sem perda nem duplicação).

**CA-03 (RF46)** Dadas as 6 dimensões, quando o usuário executa cada uma, então a análise é reexecutada sobre o subconjunto correto e mostra lado a lado o resultado geral e o do subconjunto.

**CA-04 (RF46)** Dado o filtro "sem pré-prints", então nenhum estudo de status pré-print aparece em contagens ou gráficos.

**CA-05 (RF44)** Dado o corpus final, quando a bibliometria é gerada, então ≥ 5 análises são produzidas e exportáveis em PNG/SVG e CSV.

**CA-06 (RF47)** Dado um autor ou grupo com > 20% dos estudos, então o sistema sinaliza concentração; abaixo do limiar, não.

**CA-07 (RNF01)** Dado qualquer número de uma tabela, quando o usuário clica, então vê a lista de estudos que o compõem.

**CA-08 (RNF03)** Dada uma análise executada em uma data, quando reexecutada com o mesmo instantâneo, então o resultado é idêntico.

**CA-09 (RNF14)** Dado um corpus sintético de 1.000 registros, quando a síntese roda, então retorna em ≤ 3 s.

## 9. Casos de borda
- Subconjunto vazio (ex.: sem estudos ≥ 7,0 no período): mensagem explícita, sem erro.
- Estudo sem score de qualidade: excluído da ponderação com aviso e listado.
- Dados alterados depois de uma análise: instantâneo antigo permanece; análise nova é criada.
- Metadados de afiliação inconsistentes: normalização assistida, nunca automática silenciosa.

## 10. Dependências
Specs 002 (vereditos e ponderação), 003 (metadados), 005 (scores), 006 (vereditos e campos), 007 (temas, para tabelas cruzadas).

## 11. Pontos em aberto
- `[ESCLARECER 1]` Limiar de "concentração de autoria" (proposta 20%).
- `[ESCLARECER 2]` Fórmula de ponderação: o v4.0 (§3.3) só diz que ≥ 7,0 pesa mais e que 4,0–6,9 é reportado separadamente; falta o valor do peso (ver spec 002, ESCLARECER 2). Kitchenham 2007 §6.3.3 recomenda também investigar se a qualidade se associa aos desfechos.
- `[ESCLARECER 5]` O v4.0 prevê ainda: bibliometria em 4 grupos (A desempenho, B mapeamento, C redes, D síntese de hipóteses), viés de publicação qualitativo (§10.5: periódicos × conferências × pré-prints; concentração em poucos grupos) e **effect direction plot** no lugar de meta-análise (§10.6, direção do efeito em Q-I3). Confirme que os RF44–RF47 cobrem os quatro grupos e o gráfico de direção do efeito.
- ~~`[ESCLARECER 3]`~~ **Resolvido com o v4.0:** o número de citações é o campo Q-O8 ("valor numérico, Scopus ou WoS"), extraído por pessoa; o forward snowballing também usa Scopus e WoS.
- ~~`[ESCLARECER 4]`~~ **Resolvido com o v4.0 (§10.3):** período = ano de publicação, com corte 2016–2020 × 2021–2026 (campo Q-O2).

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF44 | CA-05 | CT-ANA-05 |
| RF45 | CA-01, CA-02 | CT-ANA-01, CT-ANA-02 |
| RF46 | CA-03, CA-04 | CT-ANA-03, CT-ANA-04 |
| RF47 | CA-06 | CT-ANA-06 |
| RNF01, RNF03, RNF14 | CA-07, CA-08, CA-09 | CT-ANA-07, 08, 09 |
