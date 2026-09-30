# Spec 007 — Codificação e Síntese Temática

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D6 (Doc 4) — liberar até a Fase 8 da RSL |
| Fase da RSL atendida | Fase 8 (Doc 3) |
| Grupo funcional | F8 (Doc 1) |
| Requisitos | RF39–RF43 · RNF01, RNF02 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Apoiar a síntese temática (Cruzes & Dybå, 2011): manter o codebook (códigos dedutivos e emergentes, versionados), aplicar códigos a segmentos com origem, medir a concordância da dupla codificação em amostra, agrupar códigos em temas e temas de ordem superior, e manter trilha de auditoria completa. O sistema não interpreta; **os pesquisadores codificam e agrupam** (P1, P2).

### Método adotado (Cruzes & Dybå, 2011)
A síntese segue as cinco etapas: (1) extrair dados, (2) codificar, (3) traduzir códigos em temas, (4) criar um modelo de temas de ordem superior, (5) avaliar a confiabilidade da síntese. A abordagem de codificação é a **integrada** (§10.2 do protocolo): lista inicial dedutiva (start list dos Blocos A–I, cerca de 30–40 códigos iniciais) mais códigos indutivos emergentes. Os autores alertam para três erros comuns: codificar num nível geral demais, ver só o que já se espera ver e codificar fora de contexto. Os dois primeiros pesam sobre a definição dos códigos; o terceiro sobre guardar o trecho com contexto.

## 2. Atores
R1 (codifica), R2 (codifica a amostra dupla e participa da sessão de temas), OR (valida o modelo final), `admin`.

## 3. Escopo
**Dentro:** codebook, importação da start list a partir dos blocos de extração, codificação com origem estudo + página, dupla codificação em amostra 15–20% com κ / α de Krippendorff, agrupamento em temas, mapa temático, audit trail.
**Fora:** extração de campos (006); exportação de log do Atlas.TI (o sistema oferece caminho alternativo de importação/exportação); sugestão de códigos por IA (proibida).

## 4. Histórias de usuário
- **US1 (P1)** Importar a start list dos Blocos A–I e a taxonomia de lacunas (Bloco G) como códigos dedutivos.
- **US2 (P1)** Criar códigos emergentes com definição e escopo e versionar mudanças.
- **US3 (P1)** Codificar segmentos textuais com origem (estudo + página).
- **US4 (P1)** Medir a concordância da dupla codificação em amostra.
- **US5 (P2)** Agrupar códigos em temas e temas de ordem superior, com mapa visual.
- **US6 (P1)** Ter o audit trail completo e exportável.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF39 | O sistema DEVE manter o codebook com códigos dedutivos (importados dos blocos) e emergentes, versionando fusões, renomeações e exclusões | Must | F8.1 | 10.2 |
| RF40 | O sistema DEVE aplicar códigos a segmentos textuais com origem obrigatória (estudo + página) | Must | F8.2 | 10.2 |
| RF41 | O sistema DEVE suportar dupla codificação em amostra (15–20%), calcular κ ou α de Krippendorff (κ ≥ 0,6) e registrar a resolução de divergências | Must | F8.2.2 | 10.4 |
| RF42 | O sistema DEVERIA agrupar códigos em temas (meta 15–20) e em temas de ordem superior (meta 5–7), verificando contra os dados originais, com mapa visual | Should | F8.3 | 10.2 passo 3–4 |
| RF43 | O sistema DEVE registrar audit trail imutável de toda decisão de codificação, com autor e data | Must | F8.4 | 10.4 |
| RF42a | *(proposta, ainda não está no Doc 2)* O sistema DEVERIA oferecer o checklist de confiabilidade da síntese, com os itens do protocolo (§10.4, itens 3 a 5: conexões texto-código-tema, confirmabilidade, transferibilidade) e os itens 18–21 de Cruzes & Dybå, a preencher antes do relato | Should | — | 10.4 |

## 6. Requisitos não funcionais
- **RNF01** Todo código aplicado leva a citação + página do estudo.
- **RNF02** Auditoria imutável do codebook e das decisões de codificação.
- **RNF04** Nenhum código aplicado sem citação; nenhum tema sem códigos.

## 7. Regras de negócio
1. Fusão de códigos preserva todos os segmentos e gera novo código com histórico dos códigos absorvidos (nunca perde a origem).
2. Excluir um código com segmentos aplicados exige migrar os segmentos ou justificar descarte, com registro.
3. O segmento codificado guarda o trecho de texto exato + estudo + página; não é permitido código "solto".
4. A amostra dupla é sorteada pelo sistema (15–20% configurável) e não pode ser escolhida manualmente.
5. κ nominal para códigos exclusivos; α de Krippendorff quando múltiplos códigos por segmento; o sistema escolhe conforme o tipo declarado do codebook.
6. Tema sem códigos vinculados não pode ser criado; código pode pertencer a vários temas com justificativa.
7. Mapa temático versionado: cada versão guarda quem a aprovou (OR valida a versão final).

8. A lista inicial de códigos (com definição e frequência) é conferida por outro pesquisador antes de a fase fechar (Cruzes & Dybå, item 7): R2 marca "conferido" e a marca fica na auditoria.
9. Cada código exige definição com limites explícitos, para não haver códigos intercambiáveis ou redundantes (Cruzes & Dybå §IV).
10. Checklist de confiabilidade (RF42a): (18) pressupostos e abordagem explicitados; (19) o que se afirma é sustentado pela evidência; (20) linguagem e conceitos consistentes; (21) as RQs são respondidas com base na evidência. Cada item é marcado pelo pesquisador com justificativa; nenhum item é preenchido pelo sistema.

## 8. Critérios de aceite

**CA-01 (RF39)** Dados os blocos com opções controladas (B–I), quando a start list é importada, então cada opção vira um código dedutivo com origem no campo; reimportar não duplica.

**CA-02 (RF39)** Dados 2 códigos fundidos, quando a fusão é confirmada, então todos os segmentos migram para o código novo e o histórico mostra os dois códigos originais.

**CA-03 (RF40)** Dado um segmento sem página, quando o pesquisador tenta aplicar um código, então é recusado.

**CA-04 (RF41)** Dada uma amostra dupla de 20% com κ = 0,55, então o sistema alerta que o limiar 0,6 não foi atingido e impede fechar a fase de codificação sem desvio registrado.

**CA-05 (RF41)** Dados os mesmos dados codificados, quando κ e α são recalculados manualmente em ≥ 3 casos, então a diferença é ≤ 0,001.

**CA-06 (RF42)** Dado um tema, quando o pesquisador tenta criá-lo sem códigos, então é bloqueado; ao abrir o tema, cada código mostra seus segmentos e origens para verificação contra os dados.

**CA-07 (RF43)** Dada uma decisão de renomear um código, então a auditoria mostra nome antigo, novo nome, autor, data e justificativa.

**CA-08 (RF43)** Dado o pedido de exportação do audit trail, então o arquivo (CSV/JSON) contém 100% das decisões, sem lacunas de sequência.

**CA-09 (RF39)** Dado um código sem definição, quando o pesquisador tenta ativá-lo, então é recusado; com definição e escopo, aceito.

**CA-10 (RF41)** Dada a lista inicial de códigos com frequências, quando o fechamento da fase é solicitado sem a conferência de R2, então é bloqueado; após a marca "conferido", libera.

**CA-11 (RF42a)** Dado o checklist de confiabilidade com item sem justificativa, quando o pesquisador tenta concluí-lo, então o sistema recusa; com os 4 itens justificados, marca a síntese como "avaliada".

## 9. Casos de borda
- Segmento que cruza duas páginas: registrar página inicial e final.
- Estudo removido do corpus após codificação: códigos permanecem vinculados, marcados como inativos.
- Dois pesquisadores editando o mesmo código: conflito detectado por versão de registro.
- Codebook importado do Atlas.TI: importação por arquivo com mapeamento; discrepâncias listadas.

## 10. Dependências
Specs 001, 006 (dados extraídos e start list), 002 (RQs).

## 11. Pontos em aberto
- ~~`[ESCLARECER 1]`~~ **Resolvido com o v4.0 (§10.2):** a start list do Bloco G tem 7 categorias de lacunas, derivadas de análise anterior do autor e a refinar com códigos emergentes: Limitações Metodológicas; Limitações Estatísticas e de Resultados; Questões com os Dados; Questões de Análise e Generalização; Demandas por Pesquisa Complementar; Questões Técnicas e de Ferramentas; Questões de Privacidade.
- `[ESCLARECER 2]` O sistema substitui o Atlas.TI ou convive com ele (importar/exportar)? O v4.0 (§10.2, §13) assume codificação e audit trail **no Atlas.TI 23/24** com `codebook_atlas_xai_mas.xlsx`. Se o sistema substituir o Atlas.TI, o protocolo muda (desvio); se conviver, precisa importar e exportar o codebook e o log.
- ~~`[ESCLARECER 3]`~~ **Resolvido com o v4.0 (§10.4, item 1):** dupla codificação em 15–20% dos estudos, κ (nominal) ou α de Krippendorff (multi-categoria), mínimo κ ≥ 0,6. A regra 5 da spec já reflete isso.
- `[ESCLARECER 4]` Aprovar o **RF42a** e incluí-lo no Documento 2, ou descartá-lo. O §10.4 do v4.0 lista 5 itens de confiabilidade; os itens 1 (dupla codificação) e 2 (audit trail) já são RF41 e RF43, e os itens 3 a 5 não têm requisito.

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF39 | CA-01, CA-02, CA-09 | CT-COD-01, CT-COD-02, CT-COD-09 |
| RF40 | CA-03 | CT-COD-03 |
| RF41 | CA-04, CA-05, CA-10 | CT-COD-04, CT-COD-05, CT-COD-10 |
| RF42 | CA-06 | CT-COD-06 |
| RF42a (proposta) | CA-11 | CT-COD-11 |
| RF43, RNF02 | CA-07, CA-08 | CT-COD-07, CT-COD-08 |
