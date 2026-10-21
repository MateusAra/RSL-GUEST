# Spec 006 — Extração de Dados

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D5 (Doc 4) |
| Fase da RSL atendida | Fase 7 (Doc 3) |
| Grupo funcional | F7 (Doc 1) |
| Requisitos | RF33–RF38 · RNF01, RNF04 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Extrair dados dos estudos incluídos em formulários estruturados (Blocos A–I), com valores controlados, vínculo a RQs, citação textual + página obrigatórias, vereditos H1/H2 e verificação por segundo revisor. É o núcleo da rastreabilidade (P3): nenhum dado substantivo existe sem sua evidência.

## 2. Atores
R1 (extrai), R2 (verifica), R3 (arbitra vereditos), `admin` (configura formulários), OR (lê).

## 3. Escopo
**Dentro:** motor de formulários dinâmicos, Blocos A–I, listas controladas com "Outro — especificar", campos de controle, evidência textual, vereditos H1/H2, extração piloto (≥ 10%) e verificação cruzada, subcamada de RSLs.
**Fora:** codificação temática (spec 007); qualquer extração por IA (proibida, P2).

## 4. Blocos do formulário (Doc 3 / Protocolo §9)

| Bloco | Conteúdo |
|:-----:|----------|
| A | Identificação bibliográfica e controles (Q-O1..O17: extrator, verificador, data, DOI/URL, idioma, status/pré-print) |
| B | Sistemas multiagente (MAS) |
| C | XAI |
| D | RAI / Confiança |
| E | Métricas |
| F | Domínio de aplicação |
| G | Lacunas e direções futuras |
| H | Metodologia do estudo (tipo, research type/Wieringa, fase do ciclo, amostra) |
| I | Vereditos H1/H2 (Q-I1..I4: veredito, citação, direção de efeito) |

## 4a. Catálogo de campos do Protocolo v4.0 (§9) — Blocos A–I, 59 campos

Fonte: `docs/fonte/Protocolo_RSL_XAI_MAS_v4.docx`, §9.2–9.10. O protocolo organiza a extração em 9 blocos, ancorados às RQs, na planilha `ficha_extracao_xai_mas.xlsx`. Os IDs do Bloco A usam o prefixo `Q-O` no original; preservei assim. A "Nota" do §9.10 diz que os vereditos Q-I1 e Q-I2 são atribuídos por um revisor e **conferidos por outro**; divergência vai ao terceiro revisor.

**Bloco A — Identificação bibliográfica**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-O1 | Título do estudo | Texto livre |
| Q-O2 | Ano de publicação | 2016–2026 |
| Q-O3 | Autores | Sobrenome, Inicial. |
| Q-O4 | Afiliação institucional | Universidade / Empresa |
| Q-O5 | País da afiliação | Brasil / EUA / China... |
| Q-O6 | Veículo de publicação | Journal / Conferência / Tese |
| Q-O7 | Tipo de contribuição | Survey / Experimento / Estudo de caso / Arquitetura proposta |
| Q-O8 | Número de citações | Valor numérico (Scopus ou WoS) |
| Q-O9 | Base de dados de origem | IEEE / ACM / Scopus / WoS / arXiv / Manual |
| Q-O10 | Forma de entrada no corpus | Busca automática / Snowballing backward / Snowballing forward / Indicação — + registro de versões múltiplas do mesmo estudo, se houver |
| Q-O11 | Extrator | Nome do revisor que realizou a extração |
| Q-O12 | Verificador | Nome do revisor que conferiu a extração |
| Q-O13 | Data da extração | DD/MM/AAAA |
| Q-O14 | Identificador do estudo (DOI/URL) | DOI ou URL canônica |
| Q-O15 | Idioma | Inglês / Português / Chinês |
| Q-O16 | Status de publicação | Publicado (peer-reviewed) / Pré-print arXiv / Tese/Dissertação |
| Q-O17 | Notas livres | Espaço para observações do extrator |
| Q-O18 | Objetivo declarado do estudo (novo na v4.0; GUEST Ext1) | Texto livre (objetivo/questão de pesquisa declarada pelos autores) |

**Bloco B — Caracterização do MAS (RQ1 · RQ2 · RQ3)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-B1 | Tipo de sistema | MAS clássico / Ecossistema agêntico / Agente único (baseline) / Híbrido |
| Q-B2 | Tipo de agente predominante | Reativo / Deliberativo / BDI / LLM-based / Híbrido |
| Q-B3 | O sistema utiliza LLMs como agentes? | Sim / Não / Parcial — registrar modelo (GPT, LLaMA, Gemini...) |
| Q-B4 | Número de agentes | 2–5 / 6–20 / 20+ / Não especificado |
| Q-B5 | Tipo de interação entre agentes | Cooperação / Competição / Negociação / Coordenação / Emergente |
| Q-B6 | Comportamento emergente é tratado? | Sim (modelado) / Sim (mencionado) / Não / Não especificado |
| Q-B7 | Arquitetura do MAS | Centralizada / Descentralizada / Hierárquica / P2P / Não especificada |

**Bloco C — Explicabilidade (XAI) (RQ1 · RQ2 · RQ3 · RQ4)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-C1 | O que é explicado | Decisão individual / Comportamento coletivo / Política do agente / Resultado emergente / Raciocínio |
| Q-C2 | Para quem é explicado (stakeholder) | Usuário final / Regulador / Desenvolvedor / Outro agente / Auditoria / Não especificado |
| Q-C3 | Técnica XAI utilizada | LIME / SHAP / Contrafactual / Saliência / Regras / Argumentação / Narrativa / Outro |
| Q-C4 | Escopo da explicação | Local (agente individual) / Global (sistema) / Ambos |
| Q-C5 | Momento da explicação | Post-hoc / By-design (ante-hoc) / Ambos |
| Q-C6 | Formato da explicação | Texto natural / Visualização / Regras lógicas / Grafo / Numérico / Multimodal |
| Q-C7 | Objetivo da explicação | Auditoria / Depuração / Conformidade regulatória / Confiança / Interoperabilidade |
| Q-C8 | Avaliação empírica da XAI? | Sim (com usuários) / Sim (simulação) / Não — registrar método |

**Bloco D — RAI e Trustworthiness (RQ1 · RQ2)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-D1 | Dimensões de RAI abordadas | Fairness / Accountability / Transparência / Privacidade / Segurança / Robustez / Múltiplas |
| Q-D2 | Mecanismo de confiança proposto | Reputação / Certificação / Criptografia / Monitoramento / Integrado a XAI / Não proposto |
| Q-D3 | Limitações clássicas de confiança discutidas? | Sim (detalhado) / Mencionado / Não — registrar quais limitações |
| Q-D4 | Framework regulatório referenciado | EU AI Act / NIST AI RMF / IEEE EAD / Outro / Nenhum |

**Bloco E — Métricas e avaliação (RQ3 · RQ4)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-E1 | Métricas de XAI | Fidelidade / Completude / Compreensibilidade / Satisfação / Tempo / Não especificado |
| Q-E2 | Métricas de confiança | Trust score / Acurácia percebida / Adoção / Calibração / Não especificado |
| Q-E3 | Método de avaliação | Experimento / Simulação / Estudo de caso / Survey / Análise formal / Não avaliado |
| Q-E4 | Dataset ou ambiente de teste | Nome do dataset / Simulador / Ambiente real / Sintético / Não especificado |
| Q-E5 | Avaliação com stakeholders humanos? | Sim / Não — registrar perfil e método (questionário, entrevista, observação) |

**Bloco F — Domínio e contexto (RQ4)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-F1 | Domínio de aplicação | Saúde / Finanças / Infraestrutura crítica / Robótica / Educação / Indústria / Genérico / Outro |
| Q-F2 | Ambiente de aplicação | Simulação / Real / Laboratório / Não especificado |
| Q-F3 | Nível de criticidade do domínio | Alta (vida/segurança) / Média / Baixa / Não discutido |
| Q-F4 | Perfil de stakeholder estudado | Especialista técnico / Usuário leigo / Regulador / Gestor / Múltiplos / Não especificado |
| Q-F5 | Requisitos variam por domínio ou stakeholder? | Sim (explicitamente) / Implicitamente / Não discutido |

**Bloco G — Lacunas e direções futuras (RQ5)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-G1 | Limitações do estudo declaradas? | Sim / Não — descrever as principais limitações relatadas |
| Q-G2 | Lacunas em XAI para MAS identificadas? | Sim / Não — registrar as lacunas identificadas pelo estudo |
| Q-G3 | Direções futuras propostas | Texto livre — categorizar por tema na análise posterior |
| Q-G4 | Replicabilidade do estudo | Sim / Parcialmente / Não |

**Bloco H — Metodologia do estudo primário (novo na v3.0)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-H1 | Tipo de pesquisa | Survey / Experimento controlado / Estudo de caso / Análise bibliográfica / Pesquisa-ação / Outro |
| Q-H2 | Research type (Wieringa et al.) | Validation research / Evaluation research / Solution proposal / Philosophical paper / Opinion paper / Experience paper |
| Q-H3 | Fase do ciclo de desenvolvimento | Engenharia de requisitos / Design / Codificação / Testes e code review / Gestão de projetos / Operação / Não especificada |
| Q-H4 | Amostra/população do estudo | n (número), perfil dos participantes ou dos sistemas analisados |

**Bloco I — Resultados e verificação das hipóteses (novo na v3.0; alimenta Seção 3.3)**

| ID | Campo | Valores / exemplo |
|----|-------|-------------------|
| Q-I1 | Veredito para H1 (hipótese forte) | Suporta / Parcialmente suporta / Refuta / Inconclusivo — + citação textual com página que fundamenta o veredito |
| Q-I2 | Veredito para H2 (hipótese fraca) | Suporta / Parcialmente suporta / Refuta / Inconclusivo — + citação textual com página |
| Q-I3 | Direção do efeito XAI → transparência/confiança | Positiva / Negativa / Nula / Não medido |
| Q-I4 | Se empírico: estatísticas reportadas | Tamanho de efeito / Intervalo de confiança / p-valor / Testes utilizados / Não aplicável |

Regras do §9.1 e §6.3 que a spec já deve refletir:
- **Cadeia de evidência:** todo dado de valor substantivo leva citação textual e página ou seção.
- **Dupla extração:** os blocos substantivos **B, C, D, E e I** são extraídos de forma independente pelos dois revisores num subconjunto piloto de **pelo menos 10% do corpus**. No corpus completo, extração única com verificação cruzada pelo segundo revisor.
- **Imersão prévia:** os dois revisores leem o conjunto completo do corpus ao menos uma vez antes da extração.
- **RSLs incluídas (via CI3):** não recebem os Blocos B a F; formam subcamada própria (fonte de snowballing, insumo do Bloco G, síntese separada, sem contar como evidência primária).
- **Pré-prints:** marcados no Bloco A (Q-O16) e tratados em análise de sensibilidade.
- **Campos "Sim / Não — registrar …"** (Q-B3, Q-C8, Q-D3, Q-E5, Q-G1, Q-G2) pedem um segundo campo de texto obrigatório quando a resposta é "Não" ou "Parcial".

## 5. Histórias de usuário
- **US1 (P1)** Extrair Blocos A–I com campos tipados e listas controladas.
- **US2 (P1)** Ser bloqueado se um campo substantivo não tiver citação + página.
- **US3 (P1)** Registrar vereditos H1/H2 com citação e dupla verificação.
- **US4 (P1)** Verificar a extração do colega contra o PDF.
- **US5 (P2)** Fazer extração piloto em dupla e ver a concordância.
- **US6 (P2)** Tratar RSLs incluídas com formulário reduzido.

## 6. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF33 | O sistema DEVE configurar formulários com 9 blocos (A–I), campos tipados (texto, lista fechada, numérico, data), listas controladas com "Outro — especificar" e vínculo campo ↔ RQ | Must | F7.1 | 9 |
| RF34 | O sistema DEVE exigir os campos de controle: extrator, verificador, data, DOI/URL, idioma e status de publicação | Must | F7.2 | 9.2 |
| RF35 | O sistema DEVE exigir citação textual + página/seção nos campos substantivos dos Blocos B–I, bloqueando o salvamento sem eles | Must | F7.3 | 9.1 |
| RF36 | O sistema DEVE registrar veredito H1/H2 com citação de suporte e dupla verificação; divergência vai à arbitragem | Must | F7.4 | 9.10, 3.3 |
| RF37 | O sistema DEVERIA suportar extração dupla em piloto (≥ 10% do corpus) com concordância (κ ≥ 0,6) e verificação cruzada do corpus completo por R2 | Should | F7.5 | 9.1 |
| RF38 | O sistema DEVERIA marcar RSLs incluídas como subcamada com formulário reduzido (Bloco G + referências), sem contagem dupla | Should | F7.6 | 6.3 |

## 7. Requisitos não funcionais
- **RNF01** Rastreabilidade: para qualquer valor extraído, o caminho até a citação + página é navegável.
- **RNF04** Integridade referencial: 0 campos sem RQ e 0 registros sem estudo de origem.
- **RNF02** Auditoria de cada edição de campo (herdado de 001).

## 8. Regras de negócio
1. Campos dos Blocos B–I marcados como "substantivos" exigem citação e página; campos de mera identificação (Bloco A) não.
2. "Outro — especificar" exige texto livre; valores frequentes podem ser promovidos a opção da lista por decisão do admin, com versão do formulário.
3. O verificador (R2) não pode ser o mesmo usuário que o extrator (R1).
4. Um registro só é "concluído" após verificação (RF37) ou justificativa registrada de dispensa.
5. Vereditos usam apenas as 4 categorias configuradas na spec 002; direção de efeito é campo obrigatório junto ao veredito.
6. Estudo marcado como RSL usa formulário reduzido e não entra nas contagens de vereditos H1/H2.
7. Mudança no formulário depois do início da extração cria nova versão e sinaliza registros afetados; nunca altera valores já extraídos automaticamente.

## 9. Critérios de aceite

**CA-01 (RF33)** Dado o formulário, quando o admin cria um campo sem RQ vinculada, então o sistema recusa (RNF04).

**CA-02 (RF33)** Dado um campo de lista fechada, quando o extrator escolhe "Outro" sem texto, então o salvamento é recusado.

**CA-03 (RF34)** Dado o Bloco A, quando o extrator tenta concluir sem DOI/URL, idioma ou status, então é bloqueado.

**CA-04 (RF35)** Dado um campo substantivo preenchido sem citação ou sem página, quando o extrator salva, então o registro não é salvo.

**CA-05 (RF36)** Dado que R1 registrou veredito "suporta" e R2 verificou "parcial", quando ambos confirmam, então o registro vai à arbitragem do R3 e a decisão final consta na auditoria.

**CA-06 (RF37)** Dada uma piloto de ≥ 10% do corpus extraída em dupla, quando o cálculo roda, então o sistema mostra a concordância por campo e por bloco e alerta se κ < 0,6.

**CA-07 (RF37)** Dado o fim da extração, quando o admin tenta fechar a fase, então o sistema bloqueia se houver registros sem verificação cruzada.

**CA-08 (RF38)** Dada uma RSL marcada como subcamada, então só os campos do formulário reduzido são exigidos e ela não aparece nas contagens de veredito.

**CA-09 (RNF01)** Dado o relatório de 10 conclusões escolhidas aleatoriamente, quando cada valor é seguido de volta, então chega-se à citação + página do estudo em todos os 10.

## 10. Casos de borda
- Estudo com dados em figura ou tabela: citar como "Tabela X, p. Y"; a página é obrigatória, o tipo de fonte é opcional.
- Estudo com múltiplos experimentos ou domínios: permitir múltiplos valores para campos marcados como repetíveis.
- Idioma diferente de inglês/português: campo de idioma obrigatório; sem tradução automática por IA (P2).
- PDF substituído após extração: novo hash e alerta para reverificar as citações.

## 11. Dependências
Specs 001, 002 (RQs e vereditos), 004 (corpus), 005 (scores ligados ao registro para ponderação).

## 12. Pontos em aberto
- ~~`[ESCLARECER 1]`~~ **Resolvido com o v4.0:** o catálogo completo está na seção 4a (59 campos, Blocos A–I).
- **Resolvido pelo PO:** exigir citação textual e página/seção nos campos substantivos B–I; Bloco A fica sem essa exigência.
- **Resolvido pelo PO:** calcular κ por campo categórico; para campos livres, registrar divergências e resolução por consenso.

## 13. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF33 | CA-01, CA-02 | CT-EXT-01, CT-EXT-02 |
| RF34 | CA-03 | CT-EXT-03 |
| RF35 | CA-04 | CT-EXT-04 |
| RF36 | CA-05 | CT-EXT-05 |
| RF37 | CA-06, CA-07 | CT-EXT-06, CT-EXT-07 |
| RF38 | CA-08 | CT-EXT-08 |
| RNF01 | CA-09 | CT-EXT-09 |
