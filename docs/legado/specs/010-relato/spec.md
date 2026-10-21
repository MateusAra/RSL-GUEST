# Spec 010 — Relato: PRISMA / SEGRESS e Exportação

| Campo | Valor |
|-------|-------|
| Status | Rascunho para revisão do PO |
| Fase de desenvolvimento | D8 (Doc 4) — liberar até a Fase 10 da RSL |
| Fase da RSL atendida | Fase 10 (Doc 3) |
| Grupo funcional | F10 (Doc 1) |
| Requisitos | RF48–RF50 · RNF09, RNF15 |
| Herda de | `constitution.md` v1.0 |

## 1. Contexto e objetivo
Gerar o esqueleto do relato da RSL conforme PRISMA 2020 / SEGRESS com dados do sistema (contagens, fluxograma, tabelas), preencher os checklists de conformidade e exportar o relato em DOCX, PDF e LaTeX com referências gerenciadas. O texto interpretativo (discussão, conclusões) é escrito pelo pesquisador; o sistema **não redige** conteúdo científico (P2).

## 2. Atores
R1 (redige), R2 e OR (revisam), `admin`.

## 3. Escopo
**Dentro:** esqueleto com 9 seções, inserção automática de contagens, fluxograma e tabelas, checklists PRISMA/SEGRESS, apêndices automáticos, exportação DOCX/PDF/LaTeX, integração com Zotero/Mendeley por arquivo (BibTeX/RIS).
**Fora:** geração de texto por IA; declaração de uso de GenAI (spec 011, inserida aqui como bloco).

## 4. Histórias de usuário
- **US1 (P1)** Gerar o esqueleto do relato com contagens, fluxograma e tabelas populadas.
- **US2 (P1)** Exportar o relato em DOCX, PDF e LaTeX com citações.
- **US3 (P2)** Preencher e exportar os checklists PRISMA 2020 e SEGRESS.
- **US4 (P2)** Gerar apêndices automáticos (formulário, checklist QA, planilha de vereditos, codebook).

## 5. Requisitos funcionais

| ID | Requisito | Prior. | F.n.n | § |
|----|-----------|:------:|-------|---|
| RF48 | O sistema DEVE gerar o esqueleto do relato conforme PRISMA 2020 / SEGRESS com 9 seções, populado automaticamente com contagens, fluxograma e tabelas | Must | F10.1 | 14.1 |
| RF49 | O sistema DEVE exportar o relato em DOCX, PDF e LaTeX com referências (Zotero/Mendeley via BibTeX/RIS) | Must | F10.3 | 14.1 |
| RF50 | O sistema DEVERIA preencher checklists PRISMA/SEGRESS e exportá-los como apêndice | Should | F10.2 | 14.1 |

## 6. Requisitos não funcionais
- **RNF09** Interoperabilidade: importação/exportação de referências em BibTeX e RIS sem perda de campos essenciais.
- **RNF15** Exportabilidade: dados das tabelas e apêndices em CSV/JSON além do texto.
- **RNF01** Todo número inserido no texto é derivado do sistema, com referência de origem.

## 7. Regras de negócio
1. Números no esqueleto (contagens, κ, scores) vêm sempre do sistema no momento da geração; edição manual sobrepõe com marca visível e auditoria.
2. Cada geração cria uma versão datada do relato; versões anteriores permanecem.
3. Seção de desvios do método é preenchida com o Log de Desvios (spec 002, §15 do protocolo).
4. Ameaças à validade (§12 do protocolo) e a declaração de uso de GenAI são blocos obrigatórios no esqueleto.
5. Item de checklist só é marcado "atendido" com localização (seção/página) no relato; itens não atendidos exigem justificativa.
6. Exportação para LaTeX preserva os identificadores de citação; DOCX e PDF usam o mesmo estilo de referência escolhido no projeto.
7. Não há geração de texto científico por IA; ferramentas de tradução assistida seguem a spec 011.

## 8. Critérios de aceite

**CA-01 (RF48)** Dado o estudo concluído, quando o esqueleto é gerado, então as 9 seções existem e as contagens (identificados, deduplicados, excluídos F1, F2, QA, incluídos) somam corretamente e coincidem com o PRISMA da spec 004.

**CA-02 (RF48)** Dado um desvio registrado, então aparece na seção "Desvios do protocolo" com data e justificativa.

**CA-03 (RF49)** Dado o relato, quando exportado para DOCX, PDF e LaTeX, então os três contêm o mesmo conteúdo e as citações resolvem para a bibliografia sem referências ausentes.

**CA-04 (RF49)** Dada uma referência com campo faltante, então a exportação lista o problema em relatório e não falha silenciosamente.

**CA-05 (RF50)** Dado o checklist PRISMA 2020, quando o usuário marca um item como atendido sem localização, então é recusado; com localização, é aceito; o checklist exportável mostra todos os itens.

**CA-06 (RNF15)** Dados os apêndices, então tabelas de dados (planilha de vereditos, codebook) são exportadas também em CSV/JSON.

**CA-07 (RNF01)** Dado um número no texto gerado, quando o usuário pede a origem, então o sistema mostra a consulta/registro correspondente.

## 9. Casos de borda
- Dados alterados depois da geração: relato antigo mantido; aviso de "dados mais recentes disponíveis".
- Seção manual sobrescrita e nova geração: nunca perder texto do autor; mostrar diff.
- Caracteres especiais (acentos, símbolos) em LaTeX: escapados corretamente.
- Referência duplicada na bibliografia: detectada e listada.

## 10. Dependências
Specs 002 (protocolo, desvios), 003–008 (dados), 011 (declaração de GenAI).

## 11. Pontos em aberto
- `[ESCLARECER 1]` Estilo de referência exigido pelo periódico-alvo (IST, JAAMAS, AI Review, ESWA) — afeta RF49.
- ~~`[ESCLARECER 2]`~~ **Resolvido com o v4.0 (§14.1):** as 9 seções são (1) resumo estruturado, (2) introdução e background, (3) questões de pesquisa (QG, RQ1–RQ5 com classificação Easterbrook), (4) método (protocolo, log de desvios e declaração de uso de GenAI), (5) estudos incluídos e excluídos com fluxograma PRISMA e lista de excluídos com razão, (6) resultados (bibliometria, síntese temática, verificação das hipóteses), (7) discussão, (8) conclusões, (9) referências e apêndices (extração, checklist de QA, vereditos, codebook, checklist GUEST, log GenAI). Formato: PRISMA 2020 e SEGRESS. Periódicos-alvo (§14.2): IST, JAAMAS, AI Review, ESWA.
- `[ESCLARECER 3]` Integração com Zotero/Mendeley é só por arquivo (BibTeX/RIS) ou por API?

## 12. Rastreabilidade

| Requisito | Critérios de aceite | Casos de teste |
|-----------|--------------------|----------------|
| RF48 | CA-01, CA-02 | CT-REL-01, 02 |
| RF49, RNF09 | CA-03, CA-04 | CT-REL-03, 04 |
| RF50 | CA-05 | CT-REL-05 |
| RNF15 | CA-06 | CT-REL-06 |
| RNF01 | CA-07 | CT-REL-07 |
