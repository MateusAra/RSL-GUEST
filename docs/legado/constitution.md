# Constituição do Projeto — Sistema de Apoio à RSL "XAI for Multi-Agent Systems"

> Regras que valem para TODAS as specs, planos e tarefas. Uma spec nunca pode contradizer este documento; se precisar, altere a constituição primeiro (com ADR).
> Versão 1.0 · Fonte: Protocolo v4.0 e Documentos 1–4.

## 1. Propósito
O sistema operacionaliza o Protocolo v4.0 da RSL. Todo módulo deve permitir executar as atividades da RSL (Doc 3) sem planilhas paralelas.

## 2. Princípios inegociáveis

| # | Princípio | Consequência verificável |
|---|-----------|--------------------------|
| P1 | **Humano decide** (RES01) | Nenhuma decisão de triagem, QA, extração ou síntese é tomada automaticamente por IA. O sistema calcula, sugere regras e registra; humanos votam. |
| P2 | **GenAI restrita** (RES02, RES03) | GenAI só é permitida para tradução assistida e melhoria linguística, com revisão humana registrada. Proibida em triagem, extração e síntese. |
| P3 | **Rastreabilidade total** (RNF01) | Todo dado derivado de estudo primário liga-se a citação textual + página. Conclusão → quote é sempre navegável. |
| P4 | **Auditoria imutável** (RNF02) | Toda alteração gera entrada append-only (quem, quando, o quê, valor anterior). Nunca há UPDATE/DELETE físico em dados de decisão. |
| P5 | **Integridade referencial** (RNF04) | Zero órfãos: estudo sem origem, campo sem RQ, código sem quote. Garantido por constraint de banco, não só por código. |
| P6 | **Reprodutibilidade** (RNF03, RNF15) | Tudo exportável em formatos abertos (CSV/JSON); o pacote de replicação reconstrói o estudo. |
| P7 | **Independência dos revisores** | Enquanto um revisor não confirma seu voto, o outro não vê o dele. Vale para triagem, QA e extração dupla. |
| P8 | **Desvio é registro, não exceção silenciosa** | Qualquer mudança de protocolo, critério ou string gera entrada no Log de Desvios com justificativa e seção afetada. |

## 3. Restrições técnicas
- Aplicação web: front SPA + API REST + SGBD relacional + armazenamento de objetos (PDFs, raw results).
- Migrações de banco versionadas; nenhuma alteração manual de schema em produção.
- Cálculo de κ (Cohen, ponderado) e α de Krippendorff **somente** com biblioteca estatística validada, mais conferência manual de ≥3 casos.
- Autenticação obrigatória; autorização por 4 papéis: `admin`, `revisor`, `terceiro_revisor`, `observador` (somente leitura) [RF51, RNF07].
- Concorrência: escrita otimista com detecção de conflito; dois revisores trabalhando em paralelo sem perda de dados [RNF05].
- Backup com RPO ≤ 24 h e restore testado [RNF12].

## 4. Convenções de spec
- IDs estáveis e nunca reutilizados: `RF##`, `RNF##`, `CT-<módulo>-##` (caso de teste), `ADR-###`.
- Requisitos no formato **"O sistema DEVE …"** (Must), **"DEVERIA …"** (Should), **"PODE …"** (Could).
- Critérios de aceite em **Dado / Quando / Então**, objetivos e mensuráveis (números, não adjetivos).
- Ambiguidade = defeito. Marcar `[ESCLARECER: …]` e resolver antes do plano.
- Spec descreve **o quê e por quê**; decisões de **como** vão para `plan.md` e ADRs.
- Cada RF da spec cita o F.n.n (Doc 1) e a seção do Protocolo (§) que operacionaliza.

## 5. Definição de Pronto (DoD)
1. Código + testes automatizados passando no CI.
2. Todo critério de aceite da spec tem ≥1 caso de teste rastreável (RF ↔ CT).
3. Log de auditoria verificado para as ações do módulo (P4).
4. UAT com dados reais da RSL aceita pelo PO.
5. Spec atualizada se o comportamento mudou (spec e código não divergem).

## 6. Gates de release (alinhados aos portões da RSL)
Nenhum portão da RSL pode ser cruzado sem o módulo correspondente em produção. Fallback manual só como exceção, registrada no Log de Desvios.

## 7. Governança
- Alterar esta constituição exige ADR aprovado pelo PO.
- Mudanças de escopo durante um portão da RSL só entram na release seguinte.
