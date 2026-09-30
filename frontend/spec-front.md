# Spec de Front-end — Sistema de Apoio à RSL (v2)

| Campo | Valor |
|-------|-------|
| Versão | 2.0 (incorpora o benchmark do Parsifal; substitui a v1) |
| Status | Rascunho para revisão do PO e validação com R1/R2 |
| Escopo | Interface web de todos os módulos (specs 001–011) |
| Herda de | `constitution.md` v1.0 |
| Complementa | Specs de módulo (regras de negócio ficam lá; aqui: navegação, layout, componentes, estados) |
| Referência | `frontend/benchmark-parsifal.md` (decisões adotar/adaptar/evitar e lacunas `PRP-##`) |
| Neutralidade | Independente de framework; escolha em ADR-003 |

## Histórico
- **v1:** princípios, navegação, componentes, telas, 3 wireframes.
- **v2:** padrões de interação explícitos; semântica de status (não só cor); triagem em duas vistas (tabela + foco); página de Protocolo com âncoras; CI/CE, palavras-chave e sinônimos; tipos de campo de extração; instrumento de QA com Max Score e Cutoff; importação por fonte; avisos de pré-requisito; dashboard base; exportação seletiva; componentes com comportamento e acessibilidade; 25 critérios de aceite de interface.

## 1. Objetivo
Definir como o sistema se apresenta e se comporta para que revisores executem tarefas repetitivas e de alto risco (triagem de milhares de estudos, QA, extração com citação) com **independência garantida, evidência sempre à mão e zero perda de dados**, mantendo o fluxo linear e guiado que ferramentas de RSL consagraram (Planejar → Conduzir → Relatar).

## 2. Princípios de UX

| ID | Princípio | Consequência na interface |
|----|-----------|---------------------------|
| UX-01 | **Independência visível** (P7) | Enquanto o colega não confirmou, a UI nunca mostra voto/nota dele (nem por API); apenas "aguardando" ou "confirmado". |
| UX-02 | **Evidência à mão** (P3) | Em extração, QA e codificação o PDF fica ao lado do formulário; selecionar texto preenche citação + página. |
| UX-03 | **Nada se perde** | Rascunho salvo a cada alteração; recarregar restaura o estado; falha de rede não descarta dados. |
| UX-04 | **Teclado primeiro** em tarefas repetitivas | Triagem completa por atalhos; foco sempre visível. |
| UX-05 | **Auditoria visível** (P4) | Todo registro de decisão tem linha do tempo ("quem/quando/valor anterior"). |
| UX-06 | **Erros explicam e orientam** | A mensagem diz o que faltou e onde ("Falta a página da citação no campo C3"). |
| UX-07 | **Progresso e portão sempre presentes** | O usuário vê a fase atual e o que falta para cruzar o portão. |
| UX-08 | **Somente leitura é de fato leitura** | Para `observador`, controles de escrita não existem na tela (o servidor também recusa). |
| UX-09 | **Sem IA escondida** (P2) | Conteúdo assistido tem selo e revisão humana; nada de sugestão de voto. |
| UX-10 | **Configuração guiada por pré-requisitos** | Fases e telas dependentes exibem aviso de bloqueio com link direto para o que falta e quem pode resolver. |
| UX-11 | **Edição direta em tabelas e listas** | Cadastros simples (palavras-chave, fontes, critérios, campos) editam na própria linha; "Adicionar" cria linha nova; Enter confirma. |
| UX-12 | **Status nunca só por cor** | Todo status combina ícone + texto + cor, com contraste AA (daltonismo e impressão em P&B). |
| UX-13 | **Decisão exige confirmação** | Nenhum voto, nota ou veredito é salvo como definitivo ao mudar um campo; "Confirmar" é uma ação explícita e auditada. |
| UX-14 | **Dado bruto é intocável** | Título, resumo e metadados vindos do raw result são somente leitura; correção vira anotação com auditoria. |

## 3. Requisitos não funcionais de front

| ID | Requisito | Meta |
|----|-----------|------|
| FNF-01 | Acessibilidade | WCAG 2.2 AA: contraste, foco visível, teclado completo, rótulos de formulário, tabelas legíveis por leitor de tela, mensagens de estado com `aria-live` |
| FNF-02 | Responsividade | Desktop (≥ 1280 px) alvo principal; tablet (≥ 768 px) suportado; celular só leitura (RNF11) |
| FNF-03 | Desempenho | Lista de 1.000 estudos em ≤ 3 s (RNF14); virtualização de linhas; interação ≤ 100 ms; troca de estudo na triagem ≤ 100 ms |
| FNF-04 | Tarefa de triagem | 100 resumos em ≤ 90 min (RNF08); orienta o design da tela |
| FNF-05 | Idioma | pt-BR inicial; textos externalizados para permitir en-US |
| FNF-06 | Navegadores | Últimas 2 versões de Chrome, Edge, Firefox, Safari |
| FNF-07 | Resiliência | Falha de rede: fila local de rascunho e reenvio; indicador "não salvo" claro |
| FNF-08 | Segurança | Sem dados sensíveis em armazenamento local não criptografado; sessão expira com aviso prévio |
| FNF-09 | Densidade | Modo "confortável" e "compacto" nas tabelas (preferência do usuário) |
| FNF-10 | Impressão/exportação | Telas de resultado (PRISMA, tabelas) com versão de impressão limpa |

## 4. Arquitetura de informação e navegação

### 4.1 Três macroáreas (como no fluxo consagrado das ferramentas de RSL)
```
PLANEJAR (Fase 0)              CONDUZIR (Fases 1–9)                RELATAR (Fases 10–11)
 ├ Projeto e equipe             ├ 1 Busca e importação              ├ Relato PRISMA/SEGRESS
 ├ Protocolo (página única)     ├ 2 Deduplicação                    ├ Exportação
 │   Objetivos · PICOC          ├ 3 Triagem (F1 e F2)               └ Replicação e GenAI
 │   RQs · Hipóteses            ├ 5 Qualidade (QA)
 │   Palavras-chave · Sinônimos ├ 6 Snowballing
 │   String · Fontes            ├ 7 Extração
 │   Critérios de seleção       ├ 8 Codificação
 ├ Instrumento de QA            └ 9 Análises
 ├ Formulário de extração
 ├ Glossário · Desvios · Cronograma
Transversais: Meu trabalho · Discussões · Dashboard · Cadeia de evidência · Auditoria · Administração
```

### 4.2 Regras
- **Navegação lateral por fases** (`PhaseStepper`): 🔒 bloqueado · ▶ em andamento · ✔ concluído · ⚠ com pendência. Cada estado com ícone + texto.
- **Página "Visão geral do projeto"** com checklist de configuração (`GateChecklist`): mostra o que falta antes de cada portão, com link direto.
- **"Meu trabalho"** (página inicial do revisor): pendências por fase, ordenadas por prazo do portão.
- **Barra superior:** projeto, busca global (título, DOI, chave BibTeX, ID), notificações, usuário/papel.
- **Guarda de rota por papel** (`RoleGuard`): telas de admin não aparecem para revisor; observador só vê telas de leitura.
- **Navegação ancorada** na página de Protocolo: menu lateral interno com as 8 seções e indicador de preenchimento por seção.
- **Contexto persistente:** filtros, aba de fonte, ordenação e estudo atual sobrevivem à navegação e ao recarregamento.

## 5. Padrões de interação

| ID | Padrão | Regra |
|----|--------|-------|
| INT-01 | **Tabela editável inline** | Clicar na célula edita; Enter confirma; Esc cancela; validação na célula; linha nova via "Adicionar …"; excluir exige confirmação se houver vínculos |
| INT-02 | **Lista por Enter** (`TagListInput`) | Digitar e Enter adiciona item; itens com editar/remover; seleção múltipla para remover em lote |
| INT-03 | **Rascunho e confirmação** | Alterações salvam como rascunho; decisões (voto, nota, veredito) têm botão **Confirmar**; depois só via reabertura registrada |
| INT-04 | **Autosave** | Indicador "Salvo às HH:MM" / "Salvando…" / "Não salvo"; reenvio automático; nunca perder digitação |
| INT-05 | **Conflito de edição** | Versão de registro; ao detectar, mostra quem alterou, o valor dele e opções: mesclar, manter o meu (com justificativa) ou descartar |
| INT-06 | **Aviso de bloqueio** (`BlockedStepNotice`) | Mostra o que falta, link direto, responsável e o que será liberado |
| INT-07 | **Painel lateral (drawer)** | Detalhe de estudo abre à direita sem perder a lista, com Anterior/Próximo respeitando o filtro ativo |
| INT-08 | **Ações em massa** | Barra aparece ao selecionar linhas, com contador; só ações permitidas ao papel; decisão em massa apenas no modo restrito (PRP-06) |
| INT-09 | **Filtros e abas** | Abas por fonte com contadores; filtros combináveis; estado na URL (compartilhável) |
| INT-10 | **Exportar** | Diálogo com escolha de campos/seções, formato e versão; "Marcar todos" por grupo |
| INT-11 | **Confirmação destrutiva** | Ação irreversível pede confirmação explícita com consequência descrita; ações reversíveis não pedem |
| INT-12 | **Estados vazios** | Explicam o que é a tela e oferecem a ação seguinte ("Nenhuma fonte cadastrada. Adicionar fonte") |
| INT-13 | **Ordem de leitura e foco** | Após salvar/confirmar, o foco vai para o próximo elemento útil; erros movem o foco ao primeiro campo inválido |

### Padrões de estado (obrigatórios em toda tela)
`carregando` (skeleton) · `vazio` · `erro` (mensagem + tentar de novo) · `sem permissão` · `somente leitura` · `conflito de edição` · `bloqueado por pré-requisito` · `offline/não salvo`.

## 6. Semântica de status e tokens

### 6.1 Status de estudo (rótulo + ícone + token de cor)
| Status | Rótulo | Ícone | Token de cor | Visível para |
|--------|--------|:-----:|--------------|--------------|
| Não classificado (meu) | Pendente | ○ | `status-neutral` | dono |
| Incluído | Incluir | ✔ | `status-success` | dono |
| Excluído | Excluir | ✖ | `status-danger` | dono |
| Incerto | Incerto | ? | `status-warning` | dono |
| Aguardando colega | Aguardando | ◌ | `status-info` | ambos |
| Em conflito | Conflito | ⚠ | `status-attention` | ambos e R3 |
| Duplicado | Duplicado | ⧉ | `status-muted` | todos |
| Avança | Avança | ➜ | `status-success` | todos (situação final) |
| Excluído (final) | Excluído | ✖ | `status-danger` | todos (situação final) |

### 6.2 Tokens mínimos
Cores semânticas (`status-*`, `surface`, `text`, `border`, `focus`), espaçamento em escala de 4 px, raios, sombras, tipografia (corpo 14–16 px), tema claro e escuro. Todos os pares texto/fundo ≥ 4,5:1 (AA); ícones e bordas de controles ≥ 3:1. Valores exatos definidos na identidade visual (ESCLARECER F3).

## 7. Componentes

| Componente | Função | Comportamento e acessibilidade |
|------------|--------|--------------------------------|
| `PhaseStepper` | Fases 0–11 com portões | Item bloqueado é focável e explica o bloqueio; `aria-current` na fase ativa |
| `GateChecklist` | Critérios do portão e o que falta | Cada item tem link e responsável; concluído com ✔ e texto |
| `BlockedStepNotice` | Aviso de pré-requisito | Título, o que falta, link direto, papel responsável |
| `StudyCard` | Título, autores, ano, veículo, resumo, keywords | Termos do glossário destacados; somente leitura |
| `VoteBar` | Incluir / Excluir / Incerto + CI/CE | Botões com atalho e rótulo; CI/CE obrigatório em Excluir e Incerto |
| `PeerStatusBadge` | Estado do colega sem revelar valor | Texto "Colega: aguardando/confirmou" |
| `SourceTabs` | Abas por fonte com contador | Setas alternam abas; contador anunciado |
| `FilterGroup` | Filtros de status | Rádio ou chips; estado na URL |
| `StatusTag` | Status com ícone + texto + cor | Sem cor isolada; tooltip descreve o significado |
| `BulkActionBar` | Ações sobre linhas selecionadas | Contador; ações conforme papel; confirmação em ações de risco |
| `ArticleDrawer` | Detalhe do estudo à direita | Abas: Detalhes · Critério · Discussão · Histórico; Anterior/Próximo; foco preso e Esc fecha |
| `InlineEditTable` | Tabela editável | INT-01; validação por célula; teclado completo |
| `TagListInput` | Lista alimentada por Enter | INT-02; remoção múltipla |
| `CriteriaSelect` | Seleção de CI/CE com descrição | Mostra texto do critério e termos do glossário |
| `KappaGauge` | κ/α com limiar e n | Valor + limiar + n; texto além do gráfico |
| `ScoreInput` | 0 / 0,5 / 1 / N/A + justificativa | Justificativa obrigatória; N/A recalcula denominador |
| `ScoreSummary` | Score por categoria, Max Score e Cutoff | Atualiza em tempo real; classe (aprovado/ressalva/excluído) em texto |
| `FieldTypeSelect` | Tipo de campo de extração | Boolean, String, Integer, Float, Date, Select One, Select Many; campo "Valores" só aparece nos dois últimos |
| `EvidenceField` | Valor + citação + página + âncora no PDF | Bloqueia sem citação; botão "Usar seleção do PDF" |
| `PdfViewer` | Visualização, seleção, destaque, busca | Seleção com coordenadas; destaque persistente; teclado |
| `ImportWizard` | Upload → mapeamento → prévia → relatório | Barra de progresso; anomalias listadas por linha |
| `ConflictQueue` | Divergências, estado, responsável | Ordenável; escalonar ao R3 |
| `DiffView` | Comparação de versões | Lado a lado e unificado; adições/remoções com ícone + cor |
| `AuditTimeline` | Histórico de alterações | Filtro por usuário/ação; exportável |
| `DataTable` | Tabela virtualizada | Ordenação, colunas configuráveis, densidade, exportação; cabeçalho fixo |
| `ChartCard` | Gráfico + tabela de apoio | Sempre com tabela equivalente e legenda textual; barras preferidas a pizza |
| `ChainGraph` | Cadeia RQ → conclusão | Navegável por teclado; lacunas destacadas |
| `ExportSelector` | Grupos de checkboxes com "Marcar todos" | Grupos Projeto / Planejamento / Condução; formato e estilo |
| `AiBadge` | Selo de conteúdo assistido por IA | Ícone + texto "Assistido por IA — revisado por …" |
| `SaveIndicator` | Estado de salvamento | `aria-live="polite"` |

## 8. Telas por módulo

Formato: **ID** · papéis · realiza (RF/CA/PRP) · comportamento.

### 8.1 Fundação (spec 001)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-001-01 | Login | todos | HAB-01 | Método definido em ADR-001; erro claro; aviso de expiração de sessão |
| UI-001-02 | Usuários e papéis | admin | RF51 | Tabela; papel alterado com confirmação; `observador` marcado como leitura |
| UI-001-03 | Auditoria | admin, OR | RF56, CA-03 | `AuditTimeline` global com filtros; exportação CSV/JSON |

### 8.2 Planejar — Configuração (spec 002)
A página **Protocolo** reúne as seções abaixo com navegação lateral ancorada e indicador de preenchimento; cada seção salva de forma independente e gera versão do protocolo.

| ID | Tela / seção | Papéis | Realiza | Comportamento |
|----|--------------|--------|---------|---------------|
| UI-002-01 | Projeto e equipe (identidade da revisão) | admin | RF01, CA-01, PRP-11 | Título e descrição; lista de autores/equipe com papel e marca de **autor principal**; bloqueia salvar com < 2 revisores ou sem R3 |
| UI-002-02 | Versões do protocolo | admin; todos leem | RF02, CA-02 | Lista de versões, `DiffView`, versão congelada em leitura com selo |
| UI-002-03 | Log de desvios | admin, R1 | RF03, CA-03 | `InlineEditTable` + formulário (etapa, justificativa, seção afetada); exportação |
| UI-002-04 | Glossário | admin; R1/R2 leem | RF06, CA-04 | Termos com vínculos a CI/CE/campos; pendências em destaque |
| UI-002-05 | Objetivos e PICOC | admin | RF08 | Objetivos em texto longo; PICOC em 5 campos com **chips** (termos separados por Enter ou vírgula) e sub-questões de extração |
| UI-002-06 | Questões de pesquisa e hipóteses | admin | RF07, RF09–RF11, CA-05, CA-08 | Lista QG/RQ1… com editar/desativar, classificação Easterbrook, motivação; hipóteses H1/H2 com VI/VD; vereditos; histórico por item |
| UI-002-07 | Palavras-chave e sinônimos | admin, R1 | **PRP-01** | Tabela `InlineEditTable` (Palavra-chave, Sinônimos, Relacionada a); "Importar termos do PICOC" |
| UI-002-08 | Critérios de seleção (CI/CE) | admin | **PRP-02** | Duas listas com `TagListInput` (Enter adiciona); cada critério tem ID (CI1, CE1…), texto e vínculo ao glossário; remoção bloqueada se houver votos que o citam (só desativar) |
| UI-002-09 | Traçabilidade | todos | RF12, CA-09 | `ChainGraph` RQ ↔ campos ↔ análises; órfãos destacados |
| UI-002-10 | Cronograma | admin | RF04, CA-10 | Linha do tempo por fase com % e dependências |
| UI-002-11 | Visão geral e checklist de configuração | todos | UX-07, PRP-13 | `GateChecklist` com o que falta antes do Portão 0 e links diretos |

### 8.3 Conduzir — Busca e deduplicação (spec 003)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-003-01 | Editor de string | admin, R1 | RF13, CA-01, PRP-03 | Editor com realce, erro na posição, versionamento; botão "Sugerir string" gera **rascunho** a partir do PICOC + palavras-chave, sempre revisado pelo humano |
| UI-003-02 | Fontes, strings por base e execuções | admin, R1 | RF14, RF15, CA-02, CA-03 | Tabela de fontes (nome, URL, campos, janela, limite); aba "String base" e abas por fonte; "Registrar execução" + upload do raw; aviso quando uma fonte tem integração automática opcional |
| UI-003-03 | Importação | R1 | RF16, CA-04 | Tabela por fonte com **contagem importada** e botão Importar (BibTeX, RIS, CSV); `ImportWizard` com relatório de anomalias |
| UI-003-04 | Test-set de seminais | R1, R2 | RF17, CA-05 | Matriz seminal × base (✔/✖); alerta e bloqueio do portão |
| UI-003-05 | Busca manual | R1 | RF18, CA-10 | Tabela de veículos com período varrido e edições não varridas |
| UI-003-06 | Snowballing | R1 | RF19, CA-06 | Rodadas, candidatos × incluídos por direção; botão da rodada 2 só se liberado |
| UI-003-07 | Deduplicação | R1, R2 | RF20, RF21, CA-07, CA-08 | Fila de pares lado a lado com diferenças destacadas; decisão registrada; grupos com canônico marcado; acionada também por "Encontrar duplicados" na triagem |

### 8.4 Conduzir — Triagem (spec 004)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-004-01 | Piloto | admin, R1, R2 | RF25, CA-05 | Sorteio da amostra; `KappaGauge`; "Liberar triagem" desabilitado com motivo enquanto κ < limiar |
| UI-004-02 | **Tabela de triagem** | R1, R2, R3 (só conflitos) | **PRP-04**, RF22 | `SourceTabs` (Todas as fontes + uma por fonte); `FilterGroup`; `DataTable` com colunas Chave, Título, Autores, Veículo, Ano, Fonte, **Meu voto**, **Situação**, Adicionado em; ordenação; seleção; "Encontrar duplicados"; "Exportar artigos" (PRP-05); clique abre o drawer |
| UI-004-03 | **Estudo — Fase 1** (drawer ou modo foco) | R1, R2 | RF22, RF22a, RF23, CA-01–03 | Ver wireframe 9.1; `VoteBar` + `CriteriaSelect`; Confirmar e avançar |
| UI-004-04 | Estudo — Fase 2 | R1, R2 | RF24, CA-04 | `PdfViewer` + `VoteBar`; exclusão exige CE mapeado |
| UI-004-05 | Fila de conflitos | R1, R2, R3 | RF26, CA-07 | `ConflictQueue`; consenso com justificativa; "Escalar ao R3"; R3 vê só os escalados |
| UI-004-06 | Contagens e PRISMA | R1, OR | RF27, CA-09 | Fluxograma gerado, contagens por etapa, PNG/SVG, impressão |

### 8.5 Conduzir — Qualidade (spec 005)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-005-01 | Instrumento de QA | admin | RF29, CA-01, PRP-08 | Blocos "Perguntas", "Respostas" (descrição + peso) e "Pontuação": **Max Score calculado** a partir das perguntas e do peso máximo, **Cutoff editável**; categorias Z15; itens elegíveis a N/A; aviso de desvio se ≠ 10 critérios; atalho "Adicionar respostas sugeridas" (0 / 0,5 / 1) |
| UI-005-02 | Avaliar estudo | R1, R2 | RF30, RF31, CA-02–05 | Ver wireframe 9.2 |
| UI-005-03 | Divergências de QA | R1, R2, R3 | RF32, CA-08 | Itens com diferença > 0,5; arbitragem por item |
| UI-005-04 | Resultados de QA | R1, OR | RF31, RF32 | Distribuição de scores; classes; κ ponderado |
| UI-005-05 | Bloqueio de QA | todos | UX-10 | Se o instrumento não estiver completo, `BlockedStepNotice` com link para UI-005-01 |

### 8.6 Conduzir — Extração (spec 006)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-006-01 | Construtor do formulário | admin | RF33, CA-01, CA-02, PRP-09 | Ver wireframe 9.3; `FieldTypeSelect`; bloco, RQ vinculada e "exige citação" por campo |
| UI-006-02 | Extrair estudo | R1 | RF34, RF35, CA-03, CA-04 | Ver wireframe 9.4; se não houver campos, `BlockedStepNotice`; "Exportar dados" (CSV/JSON) sempre visível |
| UI-006-03 | Verificar extração | R2 | RF37, CA-07 | Campos do R1 em leitura com "Confirmar" ou "Discordar" por campo; PDF ao lado |
| UI-006-04 | Vereditos H1/H2 | R1, R2, R3 | RF36, CA-05 | Veredito + direção de efeito + citação; divergência vai à arbitragem |
| UI-006-05 | Piloto de extração | admin, R1, R2 | RF37, CA-06 | Concordância por campo e bloco; alerta se κ < 0,6 |

### 8.7 Conduzir — Codificação (spec 007)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-007-01 | Codebook | R1, R2 | RF39, CA-01, CA-02 | Árvore de códigos; criar/fundir/renomear com histórico |
| UI-007-02 | Codificar | R1, R2 | RF40, CA-03 | `PdfViewer` + seleção → escolher código; página automática |
| UI-007-03 | Amostra dupla | R1, R2 | RF41, CA-04 | κ/α, divergências para resolver |
| UI-007-04 | Temas e mapa | R1, R2, OR | RF42, CA-06 | Arrastar códigos para temas; mapa com versões |

### 8.8 Conduzir — Análises (spec 008)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-008-01 | **Painel base** | R1 | RF44, **PRP-12** | Três `ChartCard`: **artigos por fonte**, **aceitos por fonte** (selecionados × aceitos), **finais por ano**; cada gráfico com tabela de apoio e exportação |
| UI-008-02 | Bibliometria avançada | R1 | RF44 | Distribuições, nuvem, redes; exportar PNG/SVG/CSV |
| UI-008-03 | Síntese H1/H2 | R1, R2 | RF45, CA-01, CA-02 | Distribuição ponderada; segmentação; clique em número → estudos (drill-down) |
| UI-008-04 | Sensibilidade | R1 | RF46, CA-03, CA-04 | Seletor das 6 dimensões; resultado geral × subconjunto |
| UI-008-05 | Viés de publicação | R1 | RF47, CA-06 | Comparativo por canal; alertas de concentração |

### 8.9 Colaboração e rastreabilidade (spec 009)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-009-01 | Meu trabalho | R1, R2, R3 | RF52 | Pendências e notificações; contadores por fase |
| UI-009-02 | Atribuição de lotes | admin | RF52, CA-01 | Atribuir por fase; reatribuição com justificativa |
| UI-009-03 | Discussão do estudo | R1, R2, R3 | RF53, CA-03, PRP-07 | Aba do drawer; comentário do colega só visível após a confirmação do próprio voto |
| UI-009-04 | Dashboard de progresso | R1, R2, OR | RF54, CA-04 | Progresso por fase, κ, scores, pendências, sem revelar votos |
| UI-009-05 | Cadeia de evidência | todos | RF55, CA-05, CA-06 | `ChainGraph` RQ → conclusão em ≤ 4 cliques; lacunas destacadas |
| UI-009-06 | Modo leitura | observador | RF57, CA-07 | Aplicação sem controles de escrita |

### 8.10 Relatar — Relato, GenAI e replicação (specs 010, 011)
| ID | Tela | Papéis | Realiza | Comportamento |
|----|------|--------|---------|---------------|
| UI-010-01 | Editor do relato | R1, R2, OR | RF48, CA-01, CA-02 | Esqueleto de 9 seções; números vinculados ao sistema (origem ao clicar); marca de edição manual |
| UI-010-02 | Checklists PRISMA/SEGRESS | R1 | RF50, CA-05 | Item com localização; justificativa se "não atendido" |
| UI-010-03 | **Exportar** | R1 | RF49, CA-03, CA-04, **PRP-10** | `ExportSelector` com grupos **Projeto** (nome, autores, descrição), **Planejamento** (objetivos, PICOC, RQs, palavras-chave, string, fontes, critérios, checklist de QA, formulário de extração), **Condução** (strings por fonte, nº de estudos importados, resultados) e "Marcar todos" por grupo; formato DOCX/PDF/LaTeX; estilo de referência; "Baixar" |
| UI-011-01 | Política de GenAI | admin | RF58, CA-01 | Lista permitido/proibido; alteração exige justificativa (vai ao Log de Desvios) |
| UI-011-02 | Log de uso de IA e declaração | R1, admin | RF59, RF60, CA-03, CA-04 | Registro de uso; declaração gerada; `AiBadge` nos conteúdos |
| UI-011-03 | Pacote de replicação | R1, admin | RF05, CA-05, CA-08 | Prévia, manifesto com hashes, download do ZIP |

## 9. Wireframes das telas críticas (texto)

### 9.1 Triagem: tabela + drawer de estudo (UI-004-02 / UI-004-03)
```
┌ Projeto ▸ Conduzir ▸ 3 Triagem F1 ────────────────────────────── R1 ▾ ┐
│ Abas: [Todas 1000] [ACM 310] [IEEE 402] [Scopus 288]                    │
│ Filtro: (•) Todos ( ) Pendentes ( ) Incluir ( ) Excluir ( ) Incerto     │
│         ( ) Em conflito ( ) Duplicados ( ) Aguardando colega            │
│ [Encontrar duplicados] [Exportar artigos ▾]     Selecionados: 0 [Ações ▾]│
├──┬───────┬───────────────────────┬────────┬─────┬───────┬────────┬─────┤
│☐ │ Chave │ Título ▲              │ Autor  │ Ano │ Fonte │ Meu voto│Situ.│
│☐ │ li21  │ Explainable agents…   │ Li     │2021 │ IEEE  │ ✔ Incl. │ ◌   │
│☐ │ ma22  │ Trust in MAS…         │ Ma     │2022 │ ACM   │ ○ Pend. │ —   │
│☐ │ ro23  │ XAI for swarms…       │ Rossi  │2023 │ Scop. │ ✖ Excl. │ ⚠   │
└──┴───────┴───────────────────────┴────────┴─────┴───────┴────────┴─────┘
                                        ┌ Drawer: Estudo ma22 ─────────────┐
                                        │ [← Ant.]  22 / 1000  [Próx. →]   │
                                        │ Abas: Detalhes·Critério·Discussão│
                                        │       ·Histórico                 │
                                        │ Título / Autores / Veículo / DOI │
                                        │ Resumo (somente leitura)         │
                                        │ Keywords (glossário destacado)   │
                                        │ [I Incluir][E Excluir][U Incerto]│
                                        │ Critério*: [CE3 ▾]  Nota: [ … ]  │
                                        │ Colega: ◌ aguardando             │
                                        │ Rascunho salvo 14:02             │
                                        │ [Confirmar e avançar]  [Fechar]  │
                                        └──────────────────────────────────┘
Atalhos: I/E/U votam · Enter confirma · ←/→ navegam · J/K linhas da tabela · C critérios · D discussão · Esc fecha
```
Regras: título, resumo e metadados são somente leitura; a coluna "Situação" nunca revela o voto do colega; "Confirmar e avançar" respeita o filtro ativo; nada é salvo como decisão ao apenas mudar o botão.

### 9.2 Avaliação de qualidade (UI-005-02)
```
┌ QA · Estudo #128 ─────────────── Score parcial 7,5 / Max 10 · Cutoff 4,0 ┐
│ PdfViewer (esquerda)             │ Critérios (direita)                   │
│ ▒▒▒ texto ▒▒▒                    │ Reporting                             │
│ ▒▒▒ destaque ▒▒▒                 │  Q1 ScoreInput [0][0,5][1][N/A]       │
│                                  │      Justificativa: ……………           │
│                                  │  Q2 …                                 │
│                                  │ Rigor · Credibility · Relevance       │
│                                  │ ScoreSummary: Rep 8,0 · Rig 7,0 …     │
│                                  │ Classe: ✔ aprovado (≥ 7,0)            │
│                                  │ [Confirmar avaliação]  Colega: ◌      │
└──────────────────────────────────┴───────────────────────────────────────┘
```

### 9.3 Construtor do formulário de extração (UI-006-01)
```
┌ Planejar ▸ Formulário de extração ───────────── Bloco: [C — XAI ▾] ─────┐
│ Descrição                   │ Tipo             │ Valores        │ RQ │Cit│
│ Método de explicação        │ Select One    ▾  │ Post-hoc; Ante-│RQ2 │ ✔ │
│                             │                  │ hoc; Híbrido   │    │   │
│ Usa avaliação humana?       │ Boolean       ▾  │ — (n/a)        │RQ4 │ ✖ │
│ Nº de agentes               │ Integer       ▾  │ — (n/a)        │RQ1 │ ✖ │
│ Domínios de aplicação       │ Select Many   ▾  │ Saúde; Óleo…   │RQ3 │ ✔ │
│ [Adicionar campo]      Sem RQ vinculada: 0 · Sem citação exigida: 12    │
└──────────────────────────────────────────────────────────────────────────┘
Tipos: Boolean · String · Integer · Float · Date · Select One · Select Many. "Valores" só habilita em Select One/Many. Campo sem RQ não salva.
```

### 9.4 Extração (UI-006-02)
```
┌ Extração · Estudo #128 · Bloco C — XAI ────────── R1 · Verificador: R2 ─┐
│ PdfViewer                        │ Campo C3 · Método de explicação       │
│ ▒▒ trecho selecionado ▒▒         │  Valor: [ Post-hoc ▾ ]  ou Outro: [ ] │
│                                  │  EvidenceField:                       │
│  [ Usar seleção como citação ]   │   Citação: "……………………………"           │
│                                  │   Página: [ 7 ]  Seção: [ 4.2 ]       │
│                                  │  RQ: RQ2 (vinculada)                  │
│                                  │  ⚠ Falta citação em C5                │
│ Blocos: A ✔  B ✔  C ▶  D ○ …     │ [Salvar rascunho] [Concluir bloco]    │
│ [Exportar dados ▾]  Salvo 14:05  │                                       │
└──────────────────────────────────┴───────────────────────────────────────┘
```

### 9.5 Página Protocolo com navegação ancorada (UI-002-05..08 + 003-01/02)
```
┌ Planejar ▸ Protocolo (v4.0 — rascunho) ────────────── [Congelar versão] ┐
│ ▸ Objetivos ✔      │ Objetivos                                          │
│ ▸ PICOC ✔          │ [ texto longo ……………………………………………… ]  [Salvar]        │
│ ▸ Questões e hip. ◐│ ─────────────────────────────────────────────────  │
│ ▸ Palavras-chave ○ │ PICOC                                              │
│ ▸ String ✔         │ População: [chip][chip]  Intervenção: [chip]…      │
│ ▸ Fontes ✔         │ Comparação · Resultado · Contexto                  │
│ ▸ Critérios CI/CE ○│ ─────────────────────────────────────────────────  │
│ (ícone + texto     │ Critérios de inclusão   │ Critérios de exclusão     │
│  de estado)        │ CI1 …  [remover]        │ CE1 …  [remover]          │
│                    │ [ Digite e pressione Enter para adicionar ]         │
└────────────────────┴────────────────────────────────────────────────────┘
```

### 9.6 Importação por fonte (UI-003-03)
```
┌ Conduzir ▸ 1 Busca ▸ Importar estudos ────────────────────────────────┐
│ Fonte        │ Execução registrada │ Importados │ Anomalias │ Ação    │
│ ACM DL       │ 12/10 · 312         │ 310        │ 2 ⚠ ver   │ [Importar ▾]│
│ IEEE Xplore  │ 12/10 · 402         │ 402        │ 0         │ [Importar ▾]│
│ Scopus       │ — não registrada    │ 0          │ —         │ Registrar execução primeiro │
└────────────────────────────────────────────────────────────────────────┘
Importar ▾: BibTeX · RIS · CSV
```

### 9.7 Aviso de bloqueio (padrão `BlockedStepNotice`)
```
┌ Conduzir ▸ 5 Qualidade ────────────────────────────────────────────────┐
│ 🔒 Esta etapa ainda não pode começar                                   │
│ Falta: (1) perguntas do instrumento de QA  (2) respostas com pesos     │
│ Responsável: admin (Ana)                                               │
│ [Ir para o instrumento de QA →]                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 9.8 Exportar relato (UI-010-03)
```
┌ Relatar ▸ Exportar ─────────────────────────────────────────────────────┐
│ Projeto        [Marcar todos]  ☑ Nome  ☑ Autores  ☑ Descrição           │
│ Planejamento   [Marcar todos]  ☑ Objetivos ☑ PICOC ☑ RQs ☑ Palavras-chave│
│                ☑ String ☑ Fontes ☑ Critérios ☑ Checklist QA ☑ Form. extr.│
│ Condução       [Marcar todos]  ☑ Strings por fonte ☑ Nº importados ☐ …  │
│ Formato: (•) DOCX ( ) PDF ( ) LaTeX   Estilo de referência: [ … ▾]      │
│ Problemas detectados: 0                                   [Baixar]      │
└──────────────────────────────────────────────────────────────────────────┘
```

## 10. Critérios de aceite de front (CA-UI)

| ID | Critério |
|----|----------|
| CA-UI-01 | Dado o usuário R2 com R1 já confirmado, quando abre o estudo, então nenhum voto/nota do R1 aparece na tela nem na resposta da API; só o `PeerStatusBadge`. |
| CA-UI-02 | Dada a triagem, quando o revisor usa apenas o teclado (I/E/U, Enter), então conclui 100 estudos sem usar o mouse. |
| CA-UI-03 | Dado o formulário de extração, quando o usuário seleciona texto no PDF e clica "Usar seleção", então citação e página são preenchidas corretamente. |
| CA-UI-04 | Dada uma queda de conexão durante a edição, quando volta, então o rascunho é reenviado e o indicador muda de "não salvo" para "salvo". |
| CA-UI-05 | Dado um observador, quando navega por qualquer tela, então nenhum botão/campo de escrita é renderizado. |
| CA-UI-06 | Dada uma fase bloqueada, quando o usuário a seleciona, então vê o motivo, o link para resolver e o responsável. |
| CA-UI-07 | Dada qualquer tela principal, quando testada com verificador automático, então há 0 violações críticas WCAG 2.2 AA e a navegação por Tab é completa. |
| CA-UI-08 | Dada uma lista de 1.000 estudos, quando aberta, então renderiza em ≤ 3 s e a rolagem mantém fluidez em máquina de referência. |
| CA-UI-09 | Dados dois usuários editando o mesmo registro, quando o segundo salva, então vê o conflito, o valor do outro e escolhe mesclar ou manter o seu com justificativa. |
| CA-UI-10 | Dada uma mensagem de erro de validação, então ela indica o campo e a regra violada. |
| CA-UI-11 | Dada a tabela de triagem, quando o revisor altera o voto no drawer sem confirmar e fecha, então a decisão permanece como rascunho (não conta como voto) e a linha mostra "Pendente (rascunho)". |
| CA-UI-12 | Dada a tabela de triagem, então a coluna "Situação" mostra apenas "aguardando" ou a situação final; nenhuma coluna, filtro, ordenação ou exportação revela o voto do colega antes da confirmação. |
| CA-UI-13 | Dado um estudo, então título, resumo, autores e metadados do raw result não podem ser editados; correções ficam em anotação auditada. |
| CA-UI-14 | Dado qualquer status, então é distinguível sem cor (ícone + texto) e cumpre contraste AA. |
| CA-UI-15 | Dada a página Protocolo, quando o usuário navega pelo menu lateral, então rola até a seção correspondente e o indicador de preenchimento reflete o estado real. |
| CA-UI-16 | Dada uma lista de critérios, quando o usuário digita um texto e pressiona Enter, então o critério é criado com ID sequencial; tentar remover critério citado por votos oferece apenas "desativar". |
| CA-UI-17 | Dado o construtor de formulário, quando o tipo é Boolean, String, Integer, Float ou Date, então o campo "Valores" fica desabilitado; em Select One/Many, é obrigatório. |
| CA-UI-18 | Dado o instrumento de QA com N perguntas e peso máximo P, então o Max Score exibido é calculado automaticamente e o Cutoff é editável e salvo com auditoria. |
| CA-UI-19 | Dada a importação, então cada fonte mostra a contagem importada e as anomalias; fonte sem execução registrada não permite importar. |
| CA-UI-20 | Dado o painel base de análises, então os três gráficos (por fonte, aceitos por fonte, finais por ano) têm tabela equivalente e a soma das barras coincide com os totais da tabela. |
| CA-UI-21 | Dada a exportação, quando "Marcar todos" é acionado em um grupo, então todos os itens do grupo ficam marcados/desmarcados e o resumo do que será incluído é exibido antes de baixar. |
| CA-UI-22 | Dada uma etapa com pré-requisito pendente, então o aviso lista o que falta com link direto e o botão de ação da etapa fica desabilitado com motivo. |
| CA-UI-23 | Dado o filtro, a aba e a ordenação escolhidos, quando o usuário recarrega ou compartilha o link, então o mesmo estado é restaurado. |
| CA-UI-24 | Dado o "Confirmar e avançar", quando o próximo estudo do filtro ativo não existe, então o sistema informa a conclusão da lista e oferece ir aos pendentes/conflitos. |
| CA-UI-25 | Dado qualquer conteúdo assistido por IA, então o `AiBadge` é exibido e o botão de salvar exige a marca de revisão humana. |

## 11. Estratégia de testes de front
- **E2E por fluxo crítico:** triagem com 2 usuários simultâneos; estudo pelo drawer com rascunho e confirmação; extração com citação por seleção; QA com N/A e cutoff; conflito → consenso → R3; importação por fonte; exportação seletiva; PRISMA.
- **Acessibilidade:** verificação automática no CI + revisão manual com leitor de tela nas telas críticas (triagem, QA, extração, Protocolo).
- **Regressão visual** nos componentes; **teste de contraste** dos tokens.
- **Teste de usabilidade** com R1/R2: 100 resumos em ≤ 90 min; configuração completa do protocolo sem ajuda.
- **Testes de contrato** front↔API por spec de módulo.
- **Teste de independência:** verificação automática de que nenhuma resposta de API ao R2 contém voto do R1 antes da confirmação.

## 12. Pontos em aberto
- `[ESCLARECER F1]` Framework e biblioteca de componentes (ADR-003).
- `[ESCLARECER F2]` Visualizador de PDF: destaque persistente e seleção com coordenadas.
- `[ESCLARECER F3]` Identidade visual (cores, logo, tipografia): UPE, laboratório ou neutra?
- `[ESCLARECER F4]` Idioma inicial: só pt-BR ou pt-BR + en-US no MVP?
- `[ESCLARECER F5]` Redes bibliométricas: biblioteca de grafos e limite de nós.
- `[ESCLARECER F6]` Tablet: requisito real ou desejável?
- `[ESCLARECER F7]` **Decisão em massa (PRP-06):** permitir "excluir vários com o mesmo CE"? Ganho de tempo × risco à independência.
- `[ESCLARECER F8]` Aprovar PRP-01 a PRP-13 (benchmark, seção 5), em especial **PRP-02 (CI/CE), que é Must**.
- `[ESCLARECER F9]` A vista em tabela de triagem mostra também o "meu rascunho"? (proposta: sim, com rótulo "rascunho").

## 13. Rastreabilidade
Cada tela cita RF/CA da spec de módulo e, quando aplicável, o `PRP-##` do benchmark. Testes E2E citam o ID da tela (`UI-nnn-nn`) e o CA-UI correspondente. Telas com `PRP-##` só entram na implementação depois da aprovação do PO e da atualização da spec de módulo afetada.
