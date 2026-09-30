# Benchmark funcional — Parsifal × Sistema de Apoio à RSL

> Uso: referência **funcional** (o que a ferramenta faz e como organiza o fluxo). Não se reutiliza identidade visual, textos, código ou assets do Parsifal. Fonte: mapeamento de telas fornecido pelo PO (Review, Planning, Conducting, Reporting).

## 1. Leitura geral
O Parsifal segue um fluxo linear e dependente (**Planning → Conducting → Reporting**), com padrões recorrentes: tabelas editáveis inline, botões "Add X", listas com editar/remover, telas de bloqueio que mandam o usuário completar pré-requisitos. Esses padrões são bons e serão mantidos. O que ele **não** cobre é justamente o que o nosso Protocolo exige: votos independentes de 2 revisores, conflitos e arbitragem, κ, evidência (citação + página), auditoria imutável, governança de GenAI e pacote de replicação.

## 2. Mapa de telas: adotar, adaptar ou evitar

| # | Tela do Parsifal | O que faz | Decisão | Nossa tela (spec-front v2) | Justificativa / mudança |
|---|------------------|-----------|:-------:|----------------------------|-------------------------|
| 1 | Review (início) | Title, Description, Save; painel Authors com "main author" e "Add author" | **Adaptar** | UI-002-01 | Manter identidade + equipe; acrescentar papéis (R1, R2, R3, OR) e regra de ≥ 2 revisores + 1 R3; marcar autor principal |
| 2 | Planning › Protocol (navegação lateral ancorada) | 7 seções numa página: Objectives, PICOC, RQs, Keywords & Synonyms, Search String, Sources, Selection Criteria | **Adotar** (página única com âncoras) | UI-002-05 a UI-002-09 | Boa densidade. Acrescentar versionamento/diff, classificação Easterbrook nas RQs e hipóteses H1/H2 |
| 2a | Objectives | Textarea + Save | **Adotar** | UI-002-05 | Com histórico de versões |
| 2b | PICOC | 5 campos, termos separados por vírgula | **Adaptar** | UI-002-05 | Campos estruturados (chips) em vez de texto com vírgula; sub-questões de extração vinculadas |
| 2c | Research Questions | Lista QG/RQ1…, editar/remover, Add Question | **Adaptar** | UI-002-06 | Remover é bloqueado se houver campos vinculados (só desativar); histórico de revisão |
| 2d | Keywords & Synonyms | Tabela editável inline (Keyword, Synonyms, Related to), Import PICO Keywords | **Adotar** | UI-002-07 | **Lacuna nas specs** (ver PRP-01) |
| 2e | Search String + "Suggested Search String" | Textarea booleana; atalho com string sugerida | **Adaptar** | UI-003-01 | Editor com validação, versionamento e test-set; string sugerida é **rascunho para edição humana**, nunca automática (PRP-03) |
| 2f | Sources | Tabela Name/URL, Add Source, Add a Digital Library | **Adotar** | UI-003-02 | Acrescentar campos pesquisados, janela, limites (ex.: GS = 300) |
| 2g | Selection Criteria (CI/CE) | Duas listas, Enter para adicionar, remover selecionados | **Adotar** | UI-002-08 | **Lacuna crítica nas specs**: CI/CE são citados em todo lugar mas nenhum requisito os cadastra (PRP-02) |
| 3 | Planning › Quality Assessment Checklist | Questions, Answers (Description + Weight), Max Score automático, Cutoff Score | **Adaptar** | UI-005-01 | Manter Max Score calculado e Cutoff editável; nossas categorias Z15 e regra de N/A; faixas de corte configuráveis (PRP-08) |
| 4 | Planning › Data Extraction Form | Tabela de campos (Description, Type, Values); tipos Boolean, String, Float, Integer, Date, Select One, Select Many; Values só para selects | **Adotar tipos** | UI-006-01 | Tipos explícitos em RF33 (PRP-09); acrescentar bloco, vínculo à RQ e "exige citação" |
| 5 | Conducting › 1. Search | Aba Base String + strings por fonte; integração com Scopus/ScienceDirect | **Adaptar** | UI-003-02 | Strings por base em abas; integração via API é opcional, importação por arquivo é o caminho oficial |
| 6 | Conducting › 2. Import Studies | Tabela por fonte com contagem e botão Import | **Adotar** | UI-003-03 | Acrescentar relatório de anomalias e arquivamento do raw result |
| 7 | Conducting › 3. Study Selection | Abas por fonte; Find Duplicates; Export Articles; ação em massa; filtros por status; tabela ordenável com tag de status; modal Article Details (Details/Comments), Previous/Next, "auto-save e avançar" | **Adaptar** (é a mais rica) | UI-004-02 a UI-004-06 | Ver seção 3 abaixo |
| 8 | Conducting › 4. Quality Assessment | Tela de bloqueio com links aos pré-requisitos | **Adotar o padrão** | `BlockedStepNotice` | Padrão de pré-requisito com link direto e responsável |
| 9 | Conducting › 5. Data Extraction | Bloqueio + botão Export Data sempre visível | **Adotar o padrão** | UI-006-02, `BlockedStepNotice` | Export Data em CSV/JSON (P6) |
| 10 | Conducting › 6. Data Analysis | 3 gráficos + tabelas: artigos por fonte, aceitos por fonte, finais por ano | **Adotar como base** | UI-008-01 | Gráfico + tabela sempre juntos; barras em vez de pizza; acrescentar síntese H1/H2 e sensibilidade |
| 11 | Reporting › Export | Checkboxes agrupados (Review/Planning/Conducting) com "Toggle all" e Download | **Adotar** | UI-010-03 | Seleção de seções do relato + formato + estilo de referência |

## 3. Study Selection: o que muda no nosso desenho
O Parsifal permite que qualquer usuário altere o status de um artigo, com "salvar ao mudar e avançar". Isso é incompatível com o Protocolo (independência, confirmação, conflito). Adotamos a estrutura e corrigimos o comportamento.

| Elemento do Parsifal | Nosso desenho |
|----------------------|---------------|
| Abas por fonte + "All Sources" | Mantido (`SourceTabs`) com contadores por aba |
| Filtros rádio (All, Accepted, Rejected, Unclassified, Duplicated) | Filtros por **meu voto** (Incluir/Excluir/Incerto/Não classificado), **em conflito**, **duplicado**, **aguardando colega**; nunca "voto do colega" |
| Coluna Status única | Duas colunas: **Meu voto** e **Situação** (final: avança, excluído, conflito, aguardando); colega aparece só como `PeerStatusBadge` |
| Ação em massa + "Go" | Ações em massa **não decisórias** (exportar, atribuir, marcar para discussão); decisão em massa só em modo restrito (PRP-06) |
| "Find Duplicates" | Vai à fila de deduplicação (UI-003-07), com revisão humana e registro canônico |
| "Export Articles" | Exportação com escolha de campos e formato (CSV, BibTeX, RIS) |
| Modal Article Details (Details/Comments) | **Painel lateral (drawer)** com Detalhes, Critério, Discussão e Histórico; campos bibliográficos são somente leitura (vêm do raw result) |
| Status editável por select + salvar | `VoteBar` com **confirmação explícita**; rascunho automático, decisão só vale ao confirmar |
| "Automatically save the status on change and move next" | Substituído por **"Confirmar e avançar"** (opção "avançar após confirmar" nas preferências); nunca salva decisão ao mudar |
| Previous/Next | Mantido, com atalhos ←/→ e respeito ao filtro ativo |
| Título, Abstract, Keywords editáveis | **Não editáveis** (integridade do raw result); correções viram anotação com auditoria |

## 4. Onde o nosso sistema deve ser melhor que a referência

| Necessidade do Protocolo | Parsifal | Nosso sistema |
|--------------------------|----------|---------------|
| Independência de 2 revisores | Não | `PeerStatusBadge`, sem exposição de votos (UX-01) |
| Conflitos e arbitragem (R3) | Não | `ConflictQueue`, escalonamento |
| κ com bloqueio | Não | `KappaGauge`, bloqueio de fase |
| Evidência (citação + página) | Não | `EvidenceField` + `PdfViewer` |
| Auditoria imutável | Não | `AuditTimeline` em todo registro |
| Versionamento de protocolo e desvios | Não | `DiffView`, log de desvios |
| Governança de GenAI | Não | `AiBadge`, política, declaração |
| Pacote de replicação | Parcial (export) | ZIP com manifesto e hashes |
| Estado por fase com portões | Parcial (bloqueios) | `PhaseStepper` + `GateChecklist` |

## 5. Lacunas encontradas nas specs de módulo (propostas)

Ao cruzar as telas do Parsifal com as specs 001–011, apareceram requisitos que faltam ou estão implícitos. **As specs de módulo não foram alteradas**; as propostas abaixo aguardam aprovação do PO (prioridade = sugestão). As telas do front que dependem delas estão marcadas com o ID `PRP-##`.

| ID | Proposta | Spec afetada | Prior. | Motivo |
|----|----------|:------------:|:------:|--------|
| **PRP-01** | Cadastrar **palavras-chave e sinônimos** relacionados aos elementos do PICOC, com ação "importar termos do PICOC" | 002 | Should | Insumo da string de busca; existe no Parsifal e no processo Kitchenham |
| **PRP-02** | Cadastrar **critérios de inclusão e exclusão (CI/CE)** com ID, texto e vínculo ao glossário | 002 | **Must** | CI/CE são referenciados em RF06, RF22, RF24, mas nenhum RF os cadastra (lacuna real) |
| **PRP-03** | Gerar **string de busca sugerida** a partir de PICOC + keywords, como rascunho editável | 003 | Could | Atalho útil; decisão final sempre humana (P1) |
| **PRP-04** | **Tabela de triagem** com abas por fonte, filtros por status, ordenação, paginação e colunas configuráveis | 004 | Should | Vista de lista antes/depois do modo foco; permite retomar, auditar e navegar |
| **PRP-05** | **Exportar artigos** (selecionados ou filtrados) em CSV, BibTeX e RIS | 004 | Should | Presente no Parsifal; útil para conferência externa e para Zotero/Mendeley |
| **PRP-06** | **Ação em massa decisória restrita**: excluir vários estudos com o mesmo CE, com confirmação, limite e auditoria | 004 | Could | Ganho de produtividade, mas tensiona a independência; precisa de decisão do PO |
| **PRP-07** | **Comentário por estudo** visível ao colega apenas após a confirmação do voto | 004/009 | Should | RF53 cobre discussão; falta a regra de visibilidade |
| **PRP-08** | **Faixas de corte e cutoff configuráveis** e **Max Score calculado** a partir do instrumento | 005 | Should | Hoje as faixas (≥ 7,0 / 4,0–6,9) são fixas no texto |
| **PRP-09** | Tipos de campo de extração explícitos: **Boolean, String, Integer, Float, Date, Select One, Select Many** | 006 | Should | RF33 fala em "tipados" sem listar; "Select Many" faltava |
| **PRP-10** | **Exportação seletiva do relato** por grupos (Review, Planejamento, Condução) com "marcar todos" | 010 | Should | Facilita relatórios parciais e apêndices |
| **PRP-11** | Marcar o **autor principal** da revisão | 002 | Could | Identidade da revisão; útil para o relato |
| **PRP-12** | Gráficos-base: **artigos por fonte, aceitos por fonte, finais por ano**, sempre com tabela de apoio | 008 | Should | Detalha RF44 com entregas concretas |
| **PRP-13** | **Aviso de pré-requisito com link direto** ("falta o instrumento de QA") nas fases bloqueadas | 002/009 | Should | Padrão que reduz erro; apoia os portões |

## 6. Decisões pedidas ao PO
1. Aprovar PRP-02 (CI/CE) como Must e incluir na spec 002: é a única lacuna que impede a triagem de funcionar.
2. Decidir sobre PRP-06 (decisão em massa): ganho de tempo × risco à independência.
3. Confirmar se os demais PRP entram na matriz de requisitos (Documento 2) ou ficam no backlog de front.
