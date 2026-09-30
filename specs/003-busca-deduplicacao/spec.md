# Spec 003 — Busca, Importação, Snowballing e Deduplicação

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D4 (Doc 4) |
| Fase da RSL atendida | Fases 1, 2 e 6 (Doc 3) |
| Grupo funcional | F3, F4 (Doc 1) |
| Requisitos | RF13–RF21, RF28 · RNF09, RNF10 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Registrar a estratégia de busca (string, bases, restrições), validar a string contra um test-set de estudos seminais, arquivar os resultados brutos, importá-los, tratar snowballing (backward/forward) e deduplicar, incluindo múltiplas publicações do mesmo estudo. O objetivo é reproduzir qualquer busca a partir do registro.

## 2. Atores
R1 (executa e registra buscas), R2 (revisa duplicados), `admin` (configura bases), OR (lê).

## 3. Escopo
**Dentro:** editor de string com validação booleana e versionamento, cadastro de 6 bases (WoS, Scopus, IEEE, ACM, Google Scholar, arXiv), registro de execuções, arquivo de raw results, importação BibTeX/RIS/CSV, test-set de seminais, busca manual, snowballing, deduplicação, registro canônico.
**Fora:** triagem dos estudos (spec 004); acesso automático às APIs das bases (importação por arquivo é o caminho oficial — risco R5 do Doc 4).

## 4. Histórias de usuário
- **US1 (P1)** Editar a string com validação e versionamento, e adaptá-la por base.
- **US2 (P1)** Validar a string contra o test-set de seminais.
- **US3 (P1)** Registrar cada execução e arquivar os resultados brutos imutáveis.
- **US4 (P1)** Importar resultados em BibTeX/RIS/CSV sem perda de metadados.
- **US5 (P1)** Deduplicar e agrupar múltiplas publicações com registro canônico.
- **US6 (P1)** Conduzir snowballing por rodadas com critério de parada.
- **US7 (P2)** Registrar busca manual em veículos-alvo.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF13 | O sistema DEVE editar a string com validação de sintaxe booleana e precedência, e versionar cada alteração com data e justificativa | Must | F3.1 | 5.1 |
| RF14 | O sistema DEVE cadastrar as 6 bases com campos pesquisados, janela temporal (2016–2026), limites (Google Scholar = 300) e a string adaptada à sintaxe de cada base | Must | F3.2 | 5.2 |
| RF15 | O sistema DEVE registrar cada execução (base, data, nº de resultados, campos) e arquivar o raw result imutável | Must | F3.3 | 5.4 |
| RF16 | O sistema DEVE importar BibTeX, RIS e CSV com mapeamento de metadados por base (≥ 95% corretos) | Must | F3.4 | 3.4 |
| RF17 | O sistema DEVE validar a string contra o test-set de seminais ([SX15], [SX21]–[SX23]) e alertar se algum não for recuperado em qualquer base | Must | F3.5 | 5.1 |
| RF18 | O sistema DEVERIA cadastrar busca manual (≥ 7 veículos) com período varrido e edições não varridas | Should | F3.6 | 5.2.2 |
| RF19 | O sistema DEVE gerenciar snowballing com rodadas (mín. 1, máx. 2), registrar candidatos × incluídos por rodada e direção, e aplicar o critério de parada | Must | F3.7 | 8 |
| RF20 | O sistema DEVE detectar duplicados por DOI, título normalizado e similaridade (≥ 90% dos óbvios detectados automaticamente) e manter fila de revisão manual com decisão registrada | Must | F4.1 | 6.3 |
| RF21 | O sistema DEVE agrupar múltiplas publicações (conferência × journal × pré-print), marcar o registro canônico (versão mais completa), preservar todas as ocorrências e contar o estudo 1× | Must | F4.2 | 6.3 |
| RF28 | O sistema DEVERIA encaminhar candidatos de snowballing ao mesmo fluxo de triagem e QA dos demais | Should | F3.7, F5 | 8 |

## 6. Requisitos não funcionais
- **RNF09** Interoperabilidade: 3 formatos de importação sem perda de metadados essenciais (título, autores, ano, veículo, DOI, resumo, keywords).
- **RNF10** Escalabilidade: 5.000 registros brutos importados e deduplicados sem degradação perceptível (importação de 1.000 registros em ≤ 60 s).
- **RNF02** Auditoria de string, execuções, decisões de duplicidade (herdado de 001).

## 7. Regras de negócio
1. Raw results são imutáveis; a deduplicação nunca apaga o registro bruto, apenas marca a decisão.
2. Alterar a string após o Portão 1 exige desvio registrado.
3. Registro canônico = versão mais completa; empate resolvido pela mais recente publicada em periódico; decisão editável pelo R1 com justificativa.
4. DOI exato sinaliza duplicidade automaticamente; títulos são normalizados por caixa, acentos e pontuação. Similaridade ≥ 0,90 sugere duplicidade; casos intermediários exigem revisão humana.
5. Snowballing: rodada 2 só é liberada se a rodada 1 incluir estudos novos; máx. 2 rodadas.
6. Toda contagem (total inicial, pós-deduplicação) é registrada por execução para alimentar o PRISMA.

## 8. Critérios de aceite

**CA-01 (RF13)** Dada uma string com parênteses não balanceados, quando o usuário salva, então o sistema recusa e aponta a posição do erro; dada string válida, então uma nova versão é criada com data e justificativa.

**CA-02 (RF14)** Dadas as 6 bases cadastradas, quando a janela 2016–2026 e o limite GS = 300 são consultados, então estão registrados; uma base sem string adaptada não permite registrar execução.

**CA-03 (RF15)** Dada uma execução registrada, quando o arquivo raw é enviado, então recebe hash e não pode ser alterado; nova execução gera novo registro.

**CA-04 (RF16)** Dado um arquivo RIS de 1.000 registros, quando importado, então ≥ 95% têm título, autores, ano e DOI (quando existente) corretos e os demais são listados em relatório de anomalias.

**CA-05 (RF17)** Dado o test-set com 4 seminais, quando a string é validada e um seminal não aparece em uma base, então o sistema emite alerta nomeando estudo e base e bloqueia a confirmação do Portão 1.

**CA-06 (RF19)** Dada a rodada 1 sem estudos incluídos, quando o R1 tenta abrir a rodada 2, então é bloqueado (critério de parada); com inclusões, libera; a rodada 3 é sempre bloqueada.

**CA-07 (RF20)** Dado um conjunto com 100 duplicados óbvios (mesmo DOI), quando a deduplicação roda, então ≥ 90 são marcados automaticamente; pares de similaridade intermediária vão à fila manual.

**CA-08 (RF21)** Dado um estudo com versão de conferência e versão estendida em periódico, quando agrupados, então o periódico é sugerido como canônico, ambas as ocorrências são preservadas e a contagem final é 1.

**CA-09 (RF28)** Dado um candidato de snowballing, quando aceito, então entra na triagem (spec 004) com a origem "snowball/backward" ou "snowball/forward" registrada.

**CA-10 (RF18)** Dada a busca manual, quando um veículo é cadastrado sem período varrido, então o registro é recusado.

## 9. Casos de borda
- Arquivo com codificação inválida (UTF-8/Latin-1): detectar e informar; não importar parcialmente sem aviso.
- Registro sem DOI e com título quase idêntico em idiomas diferentes: vai à fila manual.
- Base que exporta apenas 200 registros por vez: permitir várias importações da mesma execução, consolidadas.
- Estudo seminal fora da janela temporal: alerta com opção de justificar exceção via desvio.

## 10. Dependências
Specs 001 e 002 (RQs e critérios). Alimenta a spec 004.

## 11. Pontos em aberto
- **Resolvido pelo PO:** normalizar títulos por caixa, acentos e pontuação; DOI exato sinaliza duplicidade e similaridade ≥ 0,90 sugere duplicidade, mantendo casos intermediários para revisão humana.
- ~~`[ESCLARECER 2]`~~ **Resolvido com o v4.0 (§5.2.2):** os 7 veículos da busca manual são JAAMAS (Springer), TADS (ACM), Expert Systems with Applications, Information Sciences, AAMAS, KES-AMSTA e ICMSCI (IEEE). O v4.0 corrigiu a troca de nomes que existia no v2.0.
  Bases automáticas (§5.2.1), com campos e restrição temporal (2016–2026): Web of Science (Topic), Scopus (TITLE-ABS-KEY), IEEE Xplore (All Metadata), ACM DL (Title, Abstract & Keywords), Google Scholar (título + resumo, **limitado aos 300 primeiros resultados por execução**) e arXiv (cs.MA, cs.AI, cs.CL).
  String (§5.1): sem o termo isolado "MAS". Se o test-set indicar perda de recall, "MAS" pode entrar **restrito ao título** em bases que permitam, com registro no log de desvios.
  Documentação obrigatória (§5.4): por base, nome, campos, string adaptada, **data de execução**, anos e nº de resultados; busca manual, veículo, período e edições não varridas; raw results arquivados no OSF; snowballing, rodadas, direção e candidatos × incluídos.
  Snowballing (§8): backward e forward (Scopus e WoS), no máximo 2 rodadas, mínimo 1; parar quando uma rodada não acrescenta relevantes; cada candidato passa pelas mesmas fases de seleção e pelo QA; origem em Q-O10.
  Duplicados (§6.3): identificados no Rayyan por DOI e título; o duplicado aponta para o registro canônico; múltiplas publicações do mesmo estudo usam a versão mais completa e contam uma vez.
  Estudo terciário (§8): se houver 3 ou mais RSLs sobre MAS + XAI/RAI, avaliar revisão de revisões com AMSTAR-2, em seção separada. Não há requisito para isso; se quiser, vira proposta.
- ~~`[ESCLARECER 3]`~~ **Resolvido com o v4.0 (§5.1):** os 4 estudos seminais SX15, SX21, SX22 e SX23 devem ser recuperados pela string **em cada base** antes da busca definitiva. Falha em recuperar qualquer um exige revisar a string, com registro no log de desvios. A checagem é de recuperação por base; quasi-sensibilidade numérica não é exigida.

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF13 | CA-01 | CT-BUS-01 |
| RF14 | CA-02 | CT-BUS-02 |
| RF15 | CA-03 | CT-BUS-03 |
| RF16, RNF09 | CA-04 | CT-BUS-04 |
| RF17 | CA-05 | CT-BUS-05 |
| RF18 | CA-10 | CT-BUS-10 |
| RF19 | CA-06 | CT-BUS-06 |
| RF20 | CA-07 | CT-BUS-07 |
| RF21 | CA-08 | CT-BUS-08 |
| RF28 | CA-09 | CT-BUS-09 |
