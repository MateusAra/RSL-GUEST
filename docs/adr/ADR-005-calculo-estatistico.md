# ADR-005 — Biblioteca para κ e α
Status: aceita
Data: 2026-09-29

Contexto:
A constituição exige que o cálculo de κ e α seja realizado apenas por biblioteca estatística validada, com conferência manual de pelo menos três casos antes da utilização operacional.

Decisão:
Proposta inicial: usar `scikit-learn` para coeficientes de concordância e `krippendorff` para α, com validação cruzada manual em um conjunto de casos de referência antes de gerar resultados de produção.

Alternativas consideradas:
- Implementação manual das fórmulas: descartada por risco de erro e baixa rastreabilidade.
- Biblioteca única para tudo: poderia ser insuficiente para métricas de forma padronizada em todos os cenários.

Consequências:
- Vantagens: maior precisão, documentação clara e maior auditabilidade das métricas.
- Desvantagens: exige validação e revisão humana antes do uso em decisões finais.
- Observação: a decisão vale para todos os módulos que calculam concordância e qualidade.
