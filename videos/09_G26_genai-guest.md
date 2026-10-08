# Vídeo 09 — IA generativa em revisões sistemáticas (GUEST)

**Artigo:** Kitchenham, B. et al. (2026). *Preliminary Guidelines for Using and Evaluating GenAI Tools to Support Systematic Literature Reviews* (GUEST). arXiv. (58 páginas)
**Título do vídeo:** Posso usar ChatGPT na minha revisão sistemática? As diretrizes GUEST
**Duração-alvo:** 10–11 min
**Pergunta que responde:** se, onde e como a IA generativa pode apoiar uma RSL sem comprometer o rigor?

> Antes de gravar: confira os dados do artigo (título, ano, identificador do arXiv) na fonte oficial. O identificador citado no README do projeto é arXiv 2607.24991.

---

## Roteiro

**[0:00 – 0:40] Gancho**
[VISUAL: chat com IA classificando 10 mil artigos em segundos]
"Dá para pedir a uma IA que leia dez mil resumos e diga quais incluir? Dá. Mas isso é uma revisão sistemática? As diretrizes de 2026 que vamos ver hoje respondem: depende de como você usa, valida e relata."

**[0:40 – 1:15] Em uma frase**
"A IA pode apoiar uma revisão sistemática, como uma convidada sob supervisão, nunca como substituta do pesquisador; e o seu uso precisa ser decidido, validado com métricas e relatado de forma transparente."

**[1:15 – 2:15] Contexto**
[VISUAL: cartão; Kitchenham et al.; 2026; 58 páginas; dois papéis]
"É o artigo mais longo e mais recente da série. O nome GUEST sugere a ideia de uma convidada. O texto define dois papéis. O revisor é quem faz uma revisão usando IA. O avaliador é quem estuda o desempenho da IA em revisões. Para a maioria das teses, você é o revisor; os itens marcados como 'Avaliador' só importam se a sua tese também medir a IA. E as diretrizes são preliminares: para extração, risco de viés e força da evidência, o próprio artigo diz que há pouca evidência empírica."

**[2:15 – 3:30] Ideia 1 — Os seis princípios**
[VISUAL: G1 a G6; selo DECISÃO]
"São seis princípios. Um: a responsabilidade é humana. Dois: a revisão humana do que a IA produz é necessária. Três: a IA não é autora. Quatro: declare o uso de IA, exceto em simples edição de texto. Cinco: a IA não deve criar texto, dados ou resultados da revisão. Seis: a IA não deve fazer revisão por pares. E um aviso: resumos fluentes gerados por IA, sem documentação replicável, equivalem no máximo a uma revisão de opinião de especialista, não a uma revisão sistemática."

**[3:30 – 4:45] Ideia 2 — Decidir, tarefa por tarefa**
[VISUAL: tabela de tarefas: perguntas, busca, triagem, extração, qualidade, síntese; selo DECISÃO]
"Para cada tarefa da revisão, você decide se a IA entra ou não, e justifica na tese. As diretrizes sugerem que, em tarefas de apoio, como ajudar a formular perguntas ou montar a string de busca, a validação formal pode ser dispensada desde que o uso seja totalmente relatado e humanos assumam a responsabilidade. Para tarefas de decisão, como triagem e extração, a história é outra: exige validação. E tem um alerta para estudantes: se você deixa de fazer tarefas manualmente, perde a capacidade de avaliar a saída da IA. Faça ao menos parte à mão."

**[4:45 – 6:30] Ideia 3 — Validar a triagem**
[VISUAL: matriz de confusão; exemplo com 9.695 artigos; selo FAZER]
"Na triagem, defina antes o nível de desempenho aceitável da IA, e tenha planos de contingência se a validação mostrar desempenho ruim. A validação usa uma amostra aleatória de itens, o artigo cita de 5 a 20 por cento como exemplo, que dois humanos avaliam de forma independente e a IA recebe os mesmos itens. Compare humano com humano, humano com IA e IA com a decisão de consenso. Qual métrica? O coeficiente de correlação de Matthews, o MCC, garante que o resultado é melhor que o acaso. Reporte também a matriz de confusão completa, com verdadeiros e falsos positivos e negativos, para permitir reanálise. A escolha da métrica muda quanta evidência você perde. No exemplo de 9.695 artigos, o modelo com melhor acurácia perdeu 63,3 por cento dos relevantes. Pelo MCC simples, perdeu 43,9. Pelo MCC ponderado, 5,8. O artigo não traz a fórmula do ponderado: ela está num estudo companheiro, que você deve ler antes de calcular."

**[6:30 – 7:45] Ideia 4 — Extração, qualidade e síntese**
[VISUAL: selo CUIDADO]
"Na extração, o artigo recomenda não usar o MCC ponderado, a menos que você justifique custos diferentes para tipos de erro, porque erros de extração são difíceis de detectar depois e podem corromper uma meta-análise em silêncio. Para risco de viés e qualidade, a IA só como validação adicional, um par de olhos extra, sem substituir os humanos. E o artigo não considera viável hoje usar a IA para gerar o instrumento de avaliação de qualidade. Na síntese qualitativa, não há métrica fechada: você define critérios e a comparação entre humano e IA."

**[7:45 – 8:45] Ideia 5 — Relatar**
[VISUAL: selo RELATAR]
"O que relatar: quais tarefas usaram IA e por quê; a ferramenta, a versão, os parâmetros, os prompts e as datas; as saídas; o desempenho medido; o custo e o esforço; as limitações; e o fluxo de seleção segundo o PRISMA 2020 ou o SEGRESS, indicando o papel da IA em cada passo. Inclua um plano de gestão de dados: onde guardar prompts, saídas e versões do modelo. Rode o prompt ao menos duas vezes, para ver a variação. E guarde tudo, para a reprodutibilidade."

**[8:45 – 9:30] Cuidado**
[VISUAL: selo CUIDADO]
"Cuidados: um, as diretrizes são preliminares e com pouca evidência em algumas etapas. Dois, o princípio sobre IA em revisão por pares é considerado restritivo pelos próprios autores, mas está na tabela: siga a política da sua instituição ou do periódico. Três, os valores de exemplo, como de 5 a 20 por cento de amostra, não têm justificativa nem tamanho mínimo no texto. Quatro, o 'padrão ouro' da extração, o valor do estudo, pode estar errado."

**[9:30 – 10:15] Para a sua tese**
[VISUAL: selos DECISÃO / RELATAR]
"Para a sua tese: escreva a sua posição sobre IA. Se você decide não usar IA em triagem, extração, codificação e síntese, declare isso e justifique; é uma decisão legítima e deixa a reprodutibilidade mais simples. Se usar IA em tarefas de apoio, relate tudo. Se usar em tarefas de decisão, defina métricas, nível aceitável, amostra de validação e plano de contingência antes de começar."

**[10:15 – 10:45] Fechamento da série**
"Resumindo: IA como convidada, validação com métricas definidas antes, relato transparente e responsabilidade humana. E com isso fechamos a série: do porquê da evidência, passando por métodos, mapeamento, protocolo, qualidade, síntese, até a IA. Se quiser, baixe o checklist da tese na descrição, e conte nos comentários qual etapa está sendo mais difícil. Obrigado por assistir."

---

## Descrição do YouTube
> Posso usar IA generativa na minha revisão sistemática? Os seis princípios do GUEST, como validar a IA na triagem (MCC, matriz de confusão), o que relatar e o que decidir antes de começar. Baseado em Kitchenham et al. (2026).
> Capítulos: 0:00 Gancho · 1:15 Contexto · 2:15 Seis princípios · 3:30 Decidir tarefa por tarefa · 4:45 Validar a triagem · 6:30 Extração, qualidade e síntese · 7:45 Relatar · 8:45 Cuidado · 9:30 Para a sua tese
> Checklist completo da tese: [LINK]

## Ficha de verificação
1. Diferencie "declarar o uso de IA" de "medir o desempenho da IA contra um nível aceitável definido antes".
2. Por que a acurácia sozinha pode esconder uma perda grande de estudos relevantes?
3. Que tarefas da sua revisão você manteria 100% manuais e por quê?

## Itens do checklist cobertos
- Princípios G1–G6; itens de relato Plan, Con e Rep; triagem Scr1–3 e ScrRev1–3; extração Ext1–7; síntese Syn1–3; risco de viés e força da evidência A1–A3; RevA1–2.
- CUIDADO: pouca evidência empírica; exemplos sem justificativa; padrão-ouro pode estar errado.
- Nota: itens marcados [CONFERIR] (por exemplo, a fórmula do MCC ponderado) dependem de outro estudo citado pelo artigo.
- Nota sobre o projeto: a constituição do projeto (P2) e a spec 011 proíbem IA em triagem, QA, extração, codificação e síntese; use este vídeo para fundamentar a decisão da tese, não para introduzir funções de IA no sistema.
