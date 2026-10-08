# Vídeo 01 — Evidência em vez de opinião

**Artigo:** Kitchenham, B. A.; Dybå, T.; Jørgensen, M. (2004). *Evidence-based Software Engineering*. ICSE 2004. (9 páginas)
**Título do vídeo:** Por que a engenharia de software precisa de evidência? (o artigo que inspirou as RSLs)
**Duração-alvo:** 8–9 min
**Pergunta que responde:** por que decidir com base em evidência, e quais são os limites disso em software?

---

## Roteiro

**[0:00 – 0:30] Gancho**
[VISUAL: pergunta na tela: "TDD é melhor?", "Microsserviços valem a pena?"]
"Já te disseram que uma prática é melhor, e você perguntou: segundo quem? Em muita equipe, a escolha de tecnologia vem de moda, de hype ou de quem fala mais alto. Este artigo de 2004 pergunta: e se a gente decidisse como a medicina decide, olhando evidência?"

**[0:30 – 1:00] Em uma frase**
"A ideia central: a engenharia de software pode, em boa parte, adotar a abordagem da medicina baseada em evidência, juntando a melhor evidência de pesquisa, a experiência prática e os valores das pessoas afetadas, mas com dois problemas próprios da área."

**[1:00 – 2:00] Contexto**
[VISUAL: cartão do artigo; autores; ICSE 2004; 9 páginas]
"O artigo é de Kitchenham, Dybå e Jørgensen, apresentado na ICSE em 2004. São nove páginas, um bom primeiro texto porque é curto e é de posição, não um experimento. Ele parte de uma observação: na medicina, nos anos 80 e 90, estudos mostraram que não organizar a pesquisa em revisões sistemáticas podia custar vidas, e que o julgamento de especialistas ficava atrás dos resultados dessas revisões. Daí nasceu a medicina baseada em evidência. Os autores perguntam: dá para fazer o mesmo em software?"

**[2:00 – 3:30] Ideia 1 — Os cinco passos**
[VISUAL: cinco etapas em sequência; selo FAZER]
"Eles adaptam os cinco passos da medicina para a engenharia de software.
Um: transformar a necessidade de informação em uma pergunta que dá para responder.
Dois: buscar a melhor evidência.
Três: avaliar essa evidência criticamente, olhando validade, ou seja, o quanto está perto da verdade; impacto, o tamanho do efeito; e aplicabilidade, se serve na prática de desenvolvimento.
Quatro: integrar isso à sua experiência e ao contexto.
Cinco: avaliar como você mesmo executou os passos e melhorar da próxima vez.
Perceba que uma revisão sistemática é basicamente os passos dois e três feitos com método."

**[3:30 – 4:30] Ideia 2 — Pergunta bem formulada**
[VISUAL: exemplo: "Programação em par" (tecnologia) + "desenvolvedores iniciantes" (população) + "defeitos" (desfecho)]
"Uma boa pergunta tem três partes: o fator de estudo, que aqui é a tecnologia; a população; e os desfechos. E tem um cuidado de nível de abstração. 'Métodos de projeto' é amplo demais. 'Métodos orientados a objetos' ou 'programação em par' já funciona. Mas se você restringir demais a população, pode eliminar evidência útil. Guarde isso: o nível de detalhe da pergunta decide quantos estudos você vai encontrar."

**[4:30 – 5:30] Ideia 3 — Buscar e avaliar**
[VISUAL: dois estágios: "revisões prontas" → "estudos individuais"; selo CUIDADO sobre viés de publicação]
"A medicina busca em dois estágios: primeiro revisões sistemáticas que já existem, depois estudos individuais com strings de busca. O artigo chama atenção para o viés de publicação: resultados positivos são mais publicados que os negativos, e isso superestima o efeito numa revisão. Na medicina existe até registro prévio de ensaios para combater isso. Na engenharia de software, não existe um equivalente à Cochrane, a organização que reúne revisões na medicina, e a evidência é fragmentada e pouco integrada."

**[5:30 – 7:00] Ideia 4 — Os dois problemas da área**
[VISUAL: dois ícones: "habilidade" e "ciclo de vida"]
"Aqui está a parte mais importante. Os autores apontam duas diferenças entre software e medicina.
A primeira é o fator habilidade. Em software, as técnicas dependem da habilidade de quem as aplica. Não dá para fazer duplo-cego: o desenvolvedor sabe que técnica está usando. Isso deixa experimentos vulneráveis a viés do participante e do pesquisador. Os autores sugerem reduzir a interação entre pesquisador e participante, com alocação aleatória automatizada, correção cega e análise cega, e aceitar que nossos experimentos serão menos rigorosos que os ensaios médicos, e qualificá-los.
A segunda é o fator ciclo de vida. Uma técnica de projeto, por exemplo, interage com requisitos, código e testes, e seu efeito aparece muito depois. É difícil isolar causa e efeito. E medidas imediatas, como a qualidade do projeto, são más substitutas do resultado final, como a confiabilidade do produto."

**[7:00 – 8:00] Cuidado**
[VISUAL: selo CUIDADO]
"O artigo também faz uma autocrítica que vale para a sua tese. Ele não diz que é só aplicar o modelo da medicina. Reconhece que o movimento tem críticos, que pesquisa é falível, que as evidências são difíceis de generalizar. E conclui que há tipos de estudo mais promissores, como os de teste de software, e outros mais difíceis, como tecnologias de análise e projeto. Ou seja: evidência ajuda, mas não elimina o julgamento."

**[8:00 – 8:45] Para a sua tese**
[VISUAL: selos DECISÃO / RELATAR]
"Para a sua tese, três usos. Um: justifique a sua revisão sistemática com este argumento: um único estudo, mesmo rigoroso, não basta, e a área sofre com evidência fragmentada. Dois: formule a pergunta com tecnologia, população e desfecho, e calibre o nível de abstração. Três: descreva a estratégia de busca, justifique-a e discuta os riscos dela. O artigo cita como exemplo de rigor uma revisão que fez exatamente isso."

**[8:45 – 9:15] Fechamento**
"Resumindo: evidência é melhor que opinião sozinha, os cinco passos organizam o processo, e há duas limitações específicas de software: habilidade e ciclo de vida. No próximo vídeo vamos ao artigo que ensina a julgar se um estudo empírico é confiável. Até lá."

---

## Descrição do YouTube
> Por que a engenharia de software precisa de evidência? Neste vídeo: os 5 passos da engenharia de software baseada em evidência, como formular uma pergunta de pesquisa, o viés de publicação e as duas limitações da área (habilidade e ciclo de vida).
> Artigo: Kitchenham, Dybå & Jørgensen (2004), *Evidence-based Software Engineering*, ICSE.
> Capítulos: 0:00 Gancho · 1:00 Contexto · 2:00 Cinco passos · 3:30 Pergunta bem formulada · 4:30 Buscar e avaliar · 5:30 Dois problemas da área · 7:00 Cuidado · 8:00 Para a sua tese
> Checklist da tese: [LINK] · Próximo vídeo: [LINK]

## Ficha de verificação (para o espectador)
1. O que os cinco passos têm de comum com uma RSL?
2. Dê um exemplo de pergunta ampla demais e uma bem calibrada.
3. O que é viés de publicação e como afetaria a sua revisão?

## Itens do checklist cobertos (para destacar na tela)
- FAZER: formular a pergunta em três partes (tecnologia, população, desfecho).
- DECISÃO: calibrar o nível de abstração da tecnologia e da população.
- CUIDADO: viés de publicação; fator habilidade; fator ciclo de vida.
- RELATAR: método de busca, justificativa e riscos.
