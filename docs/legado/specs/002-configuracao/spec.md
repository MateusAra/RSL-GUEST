# Spec 002 — Configuração do Estudo: Projeto, Protocolo, Glossário, RQs e Hipóteses

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D3 (Doc 4) |
| Fase da RSL atendida | Fase 0 (Doc 3) |
| Grupo funcional | F0, F1, F2 (Doc 1) |
| Requisitos | RF01–RF04, RF06–RF12 · RNF04 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Cadastrar e versionar tudo o que define o estudo antes da busca: projeto e equipe, protocolo, log de desvios, glossário operacional, questões de pesquisa (RQs), PICOC, hipóteses e vereditos. Esses dados alimentam critérios de triagem, campos de extração e análises; por isso a integridade e a traçabilidade são o foco.

## 2. Atores
`admin` (configura), R1/R2 (leem e propõem), OR/observador (lê).

## 3. Escopo
**Dentro:** projeto e equipe, versões do protocolo, log de desvios, cronograma, glossário, RQs (com classificação Easterbrook), PICOC, hipóteses H1/H2, vereditos do evidence mapping, traçabilidade RQ ↔ campos ↔ análises.
**Fora:** exportação/registro no OSF (spec 011); execução das buscas (spec 003).

## 4. Histórias de usuário
- **US1 (P1)** Cadastrar o projeto e a equipe com papéis.
- **US2 (P1)** Versionar o protocolo com diff e snapshot imutável.
- **US3 (P1)** Registrar desvios com etapa, justificativa e seção afetada.
- **US4 (P1)** Manter glossário operacional vinculado a CI/CE e campos.
- **US5 (P1)** Cadastrar RQs, PICOC, hipóteses e vereditos; ver a traçabilidade.
- **US6 (P2)** Definir cronograma de fases e acompanhar progresso.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF01 | O sistema DEVE cadastrar projeto com título, objetivo, tipo de estudo e equipe/papéis (≥ 2 revisores e 1 terceiro revisor) | Must | F0.1 | 1 |
| RF02 | O sistema DEVE versionar o protocolo com histórico (data, descrição, autor) e snapshot imutável por versão, com diff entre versões | Must | F0.2 | hist. |
| RF03 | O sistema DEVE registrar desvios com etapa, descrição, justificativa, data, autor e seção do protocolo afetada; log exportável | Must | F0.3 | 15 |
| RF04 | O sistema DEVERIA definir fases com duração e dependências e acompanhar % concluído | Should | F0.4 | 14.4 |
| RF06 | O sistema DEVE manter glossário versionado; cada termo vinculado a ≥ 1 CI/CE ou campo | Must | F1.1–F1.3 | 2 |
| RF07 | O sistema DEVE cadastrar a QG e as RQs com ID, enunciado, motivação e classificação Easterbrook justificada | Must | F2.1 | 4.1 |
| RF08 | O sistema DEVE estruturar o PICOC (5 elementos) com sub-questões de extração | Must | F2.2 | 4.2 |
| RF09 | O sistema DEVE cadastrar hipóteses H1/H2 com variáveis independentes e dependentes e critérios operacionais | Must | F2.3 | 3.1–3.2 |
| RF10 | O sistema DEVE configurar 4 vereditos (suporta/parcial/refuta/inconclusivo) e a regra de ponderação por score de qualidade | Must | F2.4 | 3.3 |
| RF11 | O sistema DEVE registrar cada revisão de RQ com histórico e diff | Must | F2.1.3 | 2 |
| RF12 | O sistema DEVE exibir traçabilidade bidirecional RQ ↔ campos de extração ↔ análises, sem dados órfãos | Must | F2.5 | 4.2 |

## 6. Requisitos não funcionais
- **RNF04** Integridade referencial: nenhuma RQ sem campo/análise vinculado; nenhum campo sem RQ (validação automática).
- **RNF02** Toda alteração das entidades acima gera auditoria (herdado de 001).

## 7. Regras de negócio
1. Uma versão de protocolo congelada é imutável; mudanças criam nova versão.
2. Alterar RQ, CI/CE ou string de busca após o Portão 0 exige entrada no Log de Desvios (P8).
3. Termo do glossário sem vínculo a CI/CE ou campo é sinalizado como pendente e impede o congelamento do protocolo.
4. As 4 categorias de veredito são fixas; critérios operacionais e pesos são configuráveis.
5. Exclusão de RQ com campos vinculados é bloqueada; só é permitida a desativação com justificativa.

## 8. Critérios de aceite

**CA-01 (RF01)** Dado um projeto novo, quando o admin tenta salvar com menos de 2 revisores ou sem terceiro revisor, então o sistema recusa e indica a pendência.

**CA-02 (RF02)** Dada uma versão 3.0 congelada, quando alguém tenta editar o texto, então a edição é bloqueada; quando cria a 3.1, então o diff com a 3.0 é exibido e a 3.0 permanece intacta.

**CA-03 (RF03)** Dado um desvio, quando é salvo sem justificativa ou sem seção afetada, então é recusado; salvo corretamente, aparece no log exportável (CSV/JSON).

**CA-04 (RF06)** Dado o glossário com ≥ 10 termos, quando um termo não tem vínculo, então aparece na lista de pendências e o congelamento do protocolo é bloqueado.

**CA-05 (RF07)** Dada a QG e 5 RQs, quando uma RQ é salva sem classificação Easterbrook ou sem justificativa, então é recusada.

**CA-06 (RF08)** Dado o PICOC, quando faltar algum dos 5 elementos, então o cadastro não é concluído.

**CA-07 (RF09/RF10)** Dadas H1 e H2, quando os 4 vereditos e a ponderação estão configurados, então o módulo de análises (008) consegue ler a configuração; sem os 4 vereditos, o projeto não pode ser congelado.

**CA-08 (RF11)** Dada uma RQ editada, quando salva, então a auditoria e o histórico mostram texto anterior, novo texto, autor e data.

**CA-09 (RF12/RNF04)** Dado o projeto completo, quando a validação de integridade roda, então reporta 0 RQs sem campo e 0 campos sem RQ; ao criar um campo sem RQ, a validação falha.

**CA-10 (RF04)** Dadas as fases com duração, quando o progresso é atualizado, então o % concluído e as dependências bloqueadas são exibidos.

## 9. Casos de borda
- Edição simultânea de glossário por dois usuários: conflito detectado (versão de registro), segundo salvamento pede merge.
- RQ reformulada depois da extração iniciada: novo registro de versão e alerta para revisar campos vinculados.
- Protocolo importado de documento externo: entra como versão inicial com autoria do importador.

## 10. Dependências
Spec 001 (auth, auditoria).

## 10a. Carga inicial do Protocolo v4.0 (§2–§6, §14.4)

Fonte: `docs/fonte/Protocolo_RSL_XAI_MAS_v4.docx` (versão 4.0, 29/09/2026, alinhada à GUEST). É a versão de referência das specs.

**Escopo (§6):** publicados de 2016 a 2026 (marco: consolidação da XAI moderna e do campo agêntico); inglês, português ou chinês; "agente" em sentido computacional.

**Hipóteses (§3):** verificadas por mapeamento de evidência, sem teste estatístico.
- H1 (forte): a integração de XAI na arquitetura de MAS melhora significativamente a transparência e a confiabilidade. VI: integração de XAI; VD: transparência e confiança.
- H2 (fraca): as abordagens clássicas de confiança em MAS (reputação, certificação, criptografia, monitoramento) **não são suficientes** para ecossistemas agênticos baseados em LLMs. VI: tipo de mecanismo de confiança; VD: suficiência declarada ou demonstrada.
- Vereditos (RF10): **Suporta**, **Parcialmente suporta**, **Refuta**, **Inconclusivo**, com critério operacional para cada um (§3.3).
- Regras de agregação: (1) veredito ponderado pelo score de qualidade: ≥ 7,0 pesa mais, 4,0–6,9 é reportado separadamente; (2) distribuição por subcorpus (MAS clássico × LLM, domínio, período); (3) contradições explicitadas e investigadas.

**Questões de pesquisa (§4.1), com classificação Easterbrook:** QG descritiva; RQ1 descritiva; RQ2 explicativa; RQ3 descritiva; RQ4 explicativa; RQ5 exploratória. O desdobramento preditivo de H2 é tratado na sensibilidade, não como RQ extra.

**PICOC (§4.2):** cada elemento se liga às sub-questões de extração Q1–Q15 (Population Q1–Q3; Intervention Q4–Q6; Comparison Q7–Q8; Outcome Q9–Q11; Context Q12–Q15). O RF07 guarda a relação PICOC → Q → RQ → Bloco de extração.

**Glossário (§2, RF06):** 9 termos com definição operacional e referências-base: MAS (≥ 2 agentes autônomos que interagem, com arquitetura declarada ou inferível), Ecossistema Agêntico, Agente LLM, XAI, RAI, Trustworthiness, Explicação post-hoc × by-design, Comportamento emergente, Stakeholder da explicação, e RSL/estudo primário/secundário/terciário. Nota de validade de construto: "explicabilidade" não é sinônimo de interpretabilidade, transparência ou accountability; os códigos dos Blocos C e D registram qual dimensão o estudo operacionaliza.

**Critérios (o que o PRP-02 carregaria):**

| ID | Inclusão |
|----|----------|
| CI1 | Aborda MAS, ecossistemas agênticos, colaboração, coordenação, autonomia ou emergência em contextos de IA (definições da Seção 2) |
| CI2 | Aborda XAI, RAI, Confiança ou Ética |
| CI3 | Estudo de caso, arquitetura, survey ou revisão sistemática que trate diretamente de MAS + XAI/RAI |
| CI4 | Publicado entre 2016 e 2026 |
| CI5 | Periódico, anais, workshop revisado por pares, tese ou dissertação, **ou pré-print arXiv elegível (§6.3)** |
| CI6 | Texto completo disponível |

| ID | Exclusão |
|----|----------|
| CE1 | Duplicados (regra de múltiplas publicações, §6.3) |
| CE2 | Texto completo não disponível integralmente |
| CE3 | Livros, capítulos e relatórios técnicos (exceto teses e dissertações) |
| CE4 | Agente isolado, sem interação em MAS (exceto baseline comparativo) |
| CE5 | Não aborda Trust, XAI ou Responsabilidade |
| CE6 | Explicabilidade em contexto não computacional |
| CE7 | XAI só em modelos preditivos isolados, sem vínculo com MAS ou agentes |
| CE8 | "Agente" só no sentido genérico de software agent, sem arquitetura MAS |

**Cronograma indicativo (§14.4, RF04):** Fase 0 registro no OSF e aprovação (2 sem.); 1 string, buscas e deduplicação (3); 2 pilotagem (1); 3 triagem Fase 1 + κ (4); 4 Fase 2 + κ (4); 5 QA + κ ponderado (3); 6 snowballing (2); 7 extração (6); 8 codificação e síntese (8); 9 sensibilidade, hipóteses e bibliometria (4); 10 relato (8). Total: 45 semanas.

**Log de desvios (§15):** toda alteração de procedimento **após o registro no OSF** entra com data, etapa, desvio, justificativa e autor (RF08).

## 11. Pontos em aberto
- **Resolvido pelo PO:** a carga inicial do Protocolo v4.0 será por script revisado; edições posteriores ocorrerão pelos formulários.
- **Resolvido pelo PO:** ponderação por faixa: score ≥ 7,0 recebe peso 1,0; score 4,0–6,9 recebe peso 0,5 e também será reportado separadamente. As distribuições sem ponderação também serão exibidas.
- ~~`[ESCLARECER 3]`~~ **Decidido em 19/10/2026 (aguarda validação do PO):** o cronograma (RF04) é só visualização: mostra % concluído e dependências pendentes, sem bloquear fases. Os bloqueios reais vêm dos portões.
- **Decidido em 19/10/2026 (aguarda validação do PO):** portões mínimos. O Portão 0 exige a validação de integridade completa (RF12, CA-04, CA-07); depois dele, alterar RQ, CI/CE ou string de busca exige um desvio registrado (regra 2). Ver `plan.md`.

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF01 | CA-01 | CT-CFG-01 |
| RF02 | CA-02 | CT-CFG-02 |
| RF03 | CA-03 | CT-CFG-03 |
| RF04 | CA-10 | CT-CFG-10 |
| RF06 | CA-04 | CT-CFG-04 |
| RF07 | CA-05 | CT-CFG-05 |
| RF08 | CA-06 | CT-CFG-06 |
| RF09, RF10 | CA-07 | CT-CFG-07 |
| RF11 | CA-08 | CT-CFG-08 |
| RF12, RNF04 | CA-09 | CT-CFG-09 |
