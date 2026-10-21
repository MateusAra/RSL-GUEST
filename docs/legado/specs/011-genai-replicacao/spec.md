# Spec 011 — Governança de GenAI e Pacote de Replicação

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D8 (Doc 4) — liberar até a Fase 10 da RSL |
| Fase da RSL atendida | Fases 10 e 11 (Doc 3) |
| Grupo funcional | F13, F14, F0.5 (Doc 1) |
| Requisitos | RF05, RF58–RF62 · RNF03, RNF13, RNF15 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Implementar a política de GenAI do Protocolo (§11) como regra do sistema, e não como promessa documental: o que é permitido, o que é proibido, o registro de uso, a revisão humana obrigatória, a declaração de uso para o relato e, ao final, a geração do pacote de replicação que permite a um terceiro reconstruir o estudo.

### Base normativa (Kitchenham et al., GUEST)
A política do Protocolo é **mais restritiva** que a GUEST, e isso é intencional. A GUEST parte de seis princípios gerais (Tab. 2): G1 humanos respondem pelo resultado; G2 toda saída assistida é revisada por humanos; G3 IA não recebe autoria; G4 todo uso de IA, exceto edição e refinamento de texto, é declarado integralmente; G5 IA não gera o texto completo nem altera dados, citações, resultados ou conclusões; G6 IA não faz revisão por pares. Para triagem, extração e síntese, a GUEST admite IA apenas como **validação adicional** do trabalho de humanos (RevA1, RevA2) e exige métricas específicas (Scr1–3, ScrRev1–3). O sistema proíbe o uso decisório e deixa a validação prospectiva como opção (RF61).

### Política do Protocolo v4.0 (§11, Apêndice B)
Fonte: `docs/fonte/Protocolo_RSL_XAI_MAS_v4.docx`. O protocolo adota só o papel **Reviewer** da GUEST; o papel Evaluator (PlanE1–E5, RepE1–E4) é N/A. Tabela de usos (§11.3):

| Uso | Status |
|-----|--------|
| Melhoria linguística e gramatical do protocolo e do relato | Permitido, declarado e registrado no log |
| Tradução assistida de literatura em chinês | Permitido, com verificação humana obrigatória das seções usadas na extração |
| Especificação de RQs e CI/CE | Não utilizado |
| Triagem automática de títulos, resumos ou textos | Não utilizado |
| Extração, codificação ou síntese | Proibido |
| QA e vereditos de hipóteses | Proibido |
| Geração de conteúdo, dados ou conclusões | Proibido |
| Pareceres de revisão por pares | Proibido |

**Gatilho de ampliação (§11.5):** qualquer uso além disso é desvio de protocolo, registrado no log de desvios, e exige antes: justificar a ferramenta e o desenho (Plan1, Plan2) e planejar dados de desempenho (Plan5); validar prospectivamente contra pelo menos dois revisores humanos (Plan6), com níveis aceitáveis e plano de contingência prévios (ScrRev1, ScrRev2); para triagem, MCC, WMCC, matriz de confusão e IC por reamostragem (Scr1–3, ScrRev3); em tarefas complexas, GenAI só como validação adicional (RevA1); atualizar o Apêndice B e a declaração de uso.

**Log GenAI (§11.4):** data (e da execução final do prompt); ferramenta, versão e parâmetros; finalidade e artefato afetado; prompt integral e estratégia; revisor humano, data da verificação e **esforço de verificação em horas**; custo. Mantido desde a Fase 0 e arquivado no pacote.

**Apêndice B:** checklist de 48 recomendações GUEST (21 atendidas, 6 a cumprir na condução, 21 N/A justificadas). O sistema deve permitir manter esse checklist e reabrir os N/A quando houver ampliação.

## 2. Atores
`admin` (configura política), R1/R2 (usam ferramentas permitidas e revisam), OR (lê), terceiro (valida o pacote).

## 3. Escopo
**Dentro:** política de usos permitidos/proibidos, selo em conteúdo assistido, log de uso (modelo, versão, parâmetros, prompts, custos), revisão humana obrigatória, gerador de declaração, validação prospectiva (Could), exportação do pacote de replicação.
**Fora:** qualquer função do sistema que use IA para triagem, extração ou síntese (proibido pela política); depósito automático no OSF (o sistema gera o ZIP; o depósito é manual).

## 4. Histórias de usuário
- **US1 (P1)** Configurar a política: tradução assistida e melhoria linguística permitidas; triagem, extração e síntese proibidas.
- **US2 (P1)** Ver selo em qualquer conteúdo assistido e ter a revisão humana registrada.
- **US3 (P1)** Gerar a declaração de uso de IA para o relato.
- **US4 (P1)** Gerar o pacote de replicação completo.
- **US5 (P2)** Registrar modelo, versão, parâmetros, prompts e custos.
- **US6 (P3)** Validar prospectivamente o uso de IA contra um baseline humano, se um dia for adotado.

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF05 | O sistema DEVE exportar o pacote completo para depósito público em ZIP, com os 10 itens do §14.3: (i) protocolo e versões, (ii) strings por base com datas, (iii) resultados brutos, (iv) excluídos no texto completo com razão, (v) extração A–I, (vi) QA com notas, (vii) codebook e log de codificação, (viii) scripts de bibliometria, (ix) log de desvios, (x) log GenAI e checklist GUEST | Must | F0.5, F14.1 | 14.3 |
| RF58 | O sistema DEVE embutir a política de GenAI: tradução permitida; triagem, extração e síntese proibidas | Must | F13.1 | 11 |
| RF59 | O sistema DEVE gerar a declaração de uso de GenAI pronta para inserção no relato | Must | F13.1.2 | 11 |
| RF60 | O sistema DEVERIA registrar modelo, versão, parâmetros, prompts, data e custo de todo uso de GenAI (se aplicável) | Should | F13.2 | 11 |
| RF61 | O sistema PODE validar prospectivamente o uso de IA com amostra de 5–20%, métricas MCC/WMCC e baseline humano de 2 revisores (se um dia usado) | Could | F13.3.2 | 11 |
| RF62 | O sistema DEVE exigir e registrar revisão humana para toda saída assistida por IA | Must | F13.3.1 | 11 |

## 6. Requisitos não funcionais
- **RNF13** Transparência: todo conteúdo assistido por IA é identificável (selo) e revisável.
- **RNF03** Reprodutibilidade: o pacote permite a um terceiro reexecutar buscas e cálculos.
- **RNF15** Exportabilidade: dados do pacote em CSV/JSON.
- **RNF02** Auditoria de todo uso de IA e da revisão humana (herdado de 001).

## 7. Regras de negócio
1. Nenhuma função de triagem, QA, extração, codificação ou síntese pode chamar serviço de IA; a política bloqueia no servidor, não só na interface (RES02).
2. Os usos permitidos (tradução assistida, melhoria linguística) só se aplicam a campos de texto de apoio e exigem revisão humana antes de salvar.
3. Saída de IA nunca é salva como dado de decisão; fica em rascunho até a confirmação humana (P1).
4. Mudança na política exige ADR, aprovação do PO e registro no Log de Desvios.
5. A declaração de uso reflete o que o log de uso realmente contém; sem uso, a declaração afirma "nenhum uso de GenAI nas etapas de triagem, extração e síntese".
6. O pacote é gerado a partir de um instantâneo congelado; contém manifesto com hash de cada arquivo.
7. O pacote não inclui PDFs de terceiros sujeitos a direitos autorais; inclui apenas metadados e DOIs.
7a. IA nunca figura como autora em nenhum documento gerado (G3), e a declaração de uso não a apresenta como tal.
7b. Cada ferramenta permitida exige justificativa registrada da escolha (GUEST Plan1) e cada tarefa apoiada por IA fica listada na política (PlanR2, §11.3).
7d. Ampliar o uso além da tabela do §11.3 só é possível por um fluxo de desvio: o `admin` registra o desvio, cumpre os 5 passos do §11.5 e o sistema só então habilita a função. Até lá, o servidor recusa.
7c. O log de uso registra também a tarefa e o esforço humano gasto na revisão (GUEST Con3, Rep1–Rep3).
8. Dados pessoais (e-mails de revisores) não vão ao pacote público.

## 8. Critérios de aceite

**CA-01 (RF58)** Dada a política padrão, quando um usuário ou serviço tenta chamar IA a partir dos módulos de triagem, extração ou síntese, então o servidor recusa e registra a tentativa.

**CA-02 (RF62/RNF13)** Dada uma tradução assistida, quando o usuário tenta salvar sem revisão humana marcada, então o sistema recusa; após a revisão, o conteúdo recebe selo e a auditoria registra revisor e data.

**CA-03 (RF59)** Dado o log de uso vazio, então a declaração afirma que não houve uso nas etapas proibidas; com um uso de tradução, a declaração cita ferramenta, versão e finalidade.

**CA-04 (RF60)** Dado um uso registrado, então o log contém tarefa, modelo, versão, parâmetros, estratégia e texto do prompt, data da execução final, custo e esforço humano de revisão; campos vazios impedem o registro (GUEST Rep1–Rep3, Con3).

**CA-05 (RF05)** Dado o estudo concluído, quando o pacote é gerado, então o ZIP contém todos os itens da lista de RF05, com manifesto e hashes, e a validação de integridade confere 100% dos arquivos.

**CA-06 (RNF03)** Dado o pacote, quando um terceiro (ambiente limpo) reexecuta as contagens e o cálculo de κ a partir dos arquivos, então obtém os mesmos números do relato.

**CA-07 (RNF15)** Dado o pacote, então todas as tabelas de dados estão em CSV e JSON, sem perda de campos.

**CA-08 (RF05)** Dado um PDF de terceiros no sistema, quando o pacote é gerado, então o PDF não é incluído; apenas o metadado/DOI.

**CA-09 (RF61)** (se implementado) Dada uma amostra de 10% com baseline de 2 humanos, então o sistema exibe a matriz de confusão completa (Scr3), MCC (Scr1), WMCC (Scr2), recall e evidência perdida (1 − recall), com intervalo de confiança por reamostragem sem reposição (ScrRev3) e o tamanho da amostra. O nível de desempenho aceitável e o plano de contingência precisam estar cadastrados antes da validação (ScrRev1, ScrRev2), senão o sistema bloqueia a execução.

**CA-10 (G3)** Dado qualquer documento gerado pelo sistema (declaração, relato, pacote), então IA não consta como autora.

## 9. Casos de borda
- Alteração de dados depois do pacote gerado: novo instantâneo; pacote antigo mantido com data.
- Falha de geração no meio do ZIP: geração atômica; nada parcial é entregue.
- Nome de arquivo com caracteres especiais: normalizado com registro no manifesto.
- Tradução de trecho cujo original está protegido: aviso, sem envio a serviço externo sem confirmação.

## 10. Dependências
Todas as specs anteriores (fonte de dados); 010 (declaração de GenAI no relato).

## 11. Pontos em aberto
- `[ESCLARECER 1]` Ferramentas de tradução: o v4.0 não nomeia nenhuma. Só exige justificar a escolha (Plan1), verificação humana e registro no log. Diga quais ferramentas e se a tradução ocorre dentro ou fora do sistema. O uso é restrito à literatura em chinês.
- `[ESCLARECER 2]` Direitos autorais: confirmar a política de excluir os PDFs do pacote público (regra 7).
- `[ESCLARECER 3]` Formato do manifesto e nível de anonimização de revisores no pacote (regra 8). O §14.3 lista o conteúdo, mas não trata de manifesto nem de anonimização; as planilhas de extração trazem o nome do extrator e do verificador (Q-O11, Q-O12).
- ~~`[ESCLARECER 4]`~~ **Resolvido com o v4.0 (§11.5):** RF61 só existe como caminho do gatilho de ampliação (validação prospectiva antes de qualquer uso além do previsto). Manter como Could, desativado por padrão.

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF05, RNF03 | CA-05, CA-06, CA-08 | CT-GEN-05, 06, 08 |
| RF58 | CA-01 | CT-GEN-01 |
| RF59 | CA-03 | CT-GEN-03 |
| RF60 | CA-04 | CT-GEN-04 |
| RF61 | CA-09 | CT-GEN-09 |
| G3 (regra 7a) | CA-10 | CT-GEN-10 |
| RF62, RNF13 | CA-02 | CT-GEN-02 |
| RNF15 | CA-07 | CT-GEN-07 |
