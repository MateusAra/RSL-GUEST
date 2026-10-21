# Vídeo 02 — Como julgar um estudo empírico

**Artigo:** Kitchenham, B. A.; Pfleeger, S. L.; Pickard, L. M.; Jones, P. W.; Hoaglin, D. C.; El Emam, K.; Rosenberg, J. (2002). *Preliminary Guidelines for Empirical Research in Software Engineering*. IEEE TSE 28(8). (14 páginas)
**Título do vídeo:** Seu estudo é confiável? As diretrizes que ensinam a ler (e criticar) pesquisas em software
**Duração-alvo:** 9–10 min
**Pergunta que responde:** como saber se um estudo empírico foi bem desenhado, analisado e relatado?

---

## Roteiro

**[0:00 – 0:40] Gancho**
[VISUAL: manchete "Estudo mostra que X melhora a produtividade em 30%"]
"Você lê que um estudo mostrou que uma prática melhora a produtividade. Você acredita? Antes de acreditar, vale perguntar: quem foram os participantes? A hipótese foi definida antes ou depois de olhar os dados? Quantos testes foram feitos até aparecer um resultado 'significativo'? Este artigo de 2002 é um guia para fazer essas perguntas."

**[0:40 – 1:10] Em uma frase**
"Ele reúne diretrizes para planejar, conduzir, analisar, relatar e interpretar estudos empíricos em engenharia de software, para que os estudos sejam melhores e para que a gente consiga combiná-los em revisões e meta-análises."

**[1:10 – 2:15] Contexto**
[VISUAL: cartão do artigo; 14 páginas; IEEE TSE 2002]
"Os autores começam com uma afirmação forte: o padrão da pesquisa empírica em software é baixo. Eles dizem que não é crítica só a software, e mostram que áreas como medicina e psiquiatria também têm erros de metodologia e de estatística em artigos publicados. As diretrizes foram montadas a partir de guias médicos, de diretrizes de psicologia e da experiência dos autores, e se dirigem a vários leitores: quem lê, quem revisa, quem escreve, quem planeja, quem faz meta-análise e quem edita periódicos. Elas são chamadas de preliminares: são uma proposta para debate."

**[2:15 – 3:00] A estrutura: seis áreas**
[VISUAL: tabela com seis áreas e códigos C, D, DC, A, P, I]
"As diretrizes se dividem em seis áreas. Contexto, com o código C. Desenho, D. Condução e coleta de dados, DC. Análise, A. Apresentação dos resultados, P. E interpretação, I. Vou escolher as ideias mais úteis para quem faz revisão."

**[3:00 – 4:15] Ideia 1 — Contexto e hipótese**
[VISUAL: exemplo de hipótese rasa x hipótese com teoria; selo FAZER]
"Primeiro: descreva o contexto. Setor, tipo de organização, experiência da equipe, processos. Sem isso, ninguém consegue replicar o estudo nem saber se o resultado vale para o seu caso. Segundo: a hipótese. Os autores criticam a hipótese rasa, algo como 'não há correlação entre complexidade e defeitos'. Qualquer que seja o resultado, você não aprende nada sobre por quê. A hipótese funda vem de uma teoria. E ela deve ser declarada antes da análise dos dados. Se o estudo é exploratório, diga isso antes e diga quais perguntas está investigando."

**[4:15 – 5:30] Ideia 2 — Desenho**
[VISUAL: população → amostra → alocação; selo DECISÃO]
"No desenho, as decisões são: qual a população? Como os participantes foram selecionados? Como foram alocados aos tratamentos? Qual a unidade experimental, a pessoa, a equipe ou a organização? Qual o tamanho de amostra necessário? Se não define a população, não dá para generalizar nada. Um exemplo do artigo: uma pesquisa em que os participantes foram recrutados por convite aberto e por anúncios na internet. Sem método de amostragem científico, os resultados não podem ser generalizados para uma população definida. E atenção a medidas substitutas: contar linhas de código alteradas no lugar de medir o esforço de manutenção exige justificativa, e 'não conseguimos medir' não é justificativa."

**[5:30 – 6:30] Ideia 3 — Coleta e análise**
[VISUAL: selo CUIDADO; ícone de caça-pesca de resultados]
"Na coleta: defina cada medida, com entidade, atributo, unidade e regra de contagem. Se a medida é subjetiva, relate a concordância entre avaliadores, como o kappa. Registre quem desistiu do estudo e em surveys a taxa de resposta. Na análise, o risco clássico é o de testar demais. Faça muitos testes e alguns darão significativos por acaso. O artigo mostra a conta: com dez testes e um nível geral de 0,05, a correção de Bonferroni exigiria 0,005 para cada um. O ponto prático: relate quantos testes fez, não só os que deram certo."

**[6:30 – 7:30] Ideia 4 — Apresentar e interpretar**
[VISUAL: p-valor pequeno com correlação 0,1]
"Na apresentação: mostre o tamanho do efeito e o intervalo de confiança, não só o p-valor. Disponibilize dados brutos, ou deixe-os disponíveis para auditoria confidencial. Na interpretação: diferencie significância estatística de importância prática. Com uma amostra grande, até uma correlação de 0,1 pode ser estatisticamente significativa, e praticamente irrelevante. E defina o tipo de estudo: experimento controlado, observacional, e se é confirmatório ou exploratório. Estudos exploratórios só sustentam conclusões fracas. E correlação, sozinha, não prova causa."

**[7:30 – 8:30] Cuidado**
[VISUAL: selo CUIDADO]
"Dois cuidados. Primeiro, este artigo trata de estudos empíricos em geral, com bastante estatística. Não precisa dominar cada detalhe, como desenhos cross-over ou imputação de dados. O objetivo, para você, é entender por que cada diretriz existe. Segundo, não use as diretrizes como regra de excluir estudos. Um estudo mal relatado pode ter sido bem conduzido. É sobre isso que o manual de revisão sistemática insiste mais à frente."

**[8:30 – 9:30] Para a sua tese**
[VISUAL: selos DECISÃO / FAZER / RELATAR]
"Para a sua tese: use as seis áreas como lente para avaliar cada estudo primário da sua revisão. Ao extrair dados, procure: contexto, população e amostragem, tratamentos, medidas e como foram definidas, tipo de estudo, tamanho amostral, desistências e método estatístico. Se a sua tese também avalia algo com participantes, como um sistema, use as diretrizes como guia: defina a população, declare hipóteses antes, relate limitações de validade interna e externa e discuta o que foi feito para reduzir viés."

**[9:30 – 10:00] Fechamento**
"Resumindo: contexto e hipótese claros, desenho com população e amostragem definidas, medidas bem definidas, análise honesta sobre os testes feitos, e conclusões que não vão além dos resultados. No próximo vídeo: como escolher o método certo para cada pergunta, com o capítulo do Easterbrook e colegas."

---

## Descrição do YouTube
> Como julgar se um estudo empírico em engenharia de software é confiável: contexto, hipótese, desenho, coleta, análise, apresentação e interpretação. Para quem vai ler e extrair dados de estudos primários numa revisão sistemática.
> Artigo: Kitchenham et al. (2002), *Preliminary Guidelines for Empirical Research in Software Engineering*, IEEE TSE.
> Capítulos: 0:00 Gancho · 1:10 Contexto · 2:15 As seis áreas · 3:00 Hipótese e contexto · 4:15 Desenho · 5:30 Coleta e análise · 6:30 Apresentar e interpretar · 7:30 Cuidado · 8:30 Para a sua tese

## Ficha de verificação
1. Dado um estudo primário, quais 3 informações de desenho você extrairia?
2. Por que um estudo exploratório não sustenta conclusões fortes?
3. O que é "tipo de estudo" e por que declarar o errado engana o leitor?

## Itens do checklist cobertos
- C1–C4 (contexto e hipóteses), D1–D11 (desenho), DC1–DC6 (coleta), A1–A5 (análise), P1–P6 (apresentação), I1–I4 (interpretação).
- CUIDADO: hipótese rasa; testes múltiplos; população indefinida; significância x relevância; confirmatório x exploratório.
