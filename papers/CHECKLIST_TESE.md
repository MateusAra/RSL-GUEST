# Checklist de tese — o que os 9 papers pedem (decisões, ações, cuidados e o que relatar)

Consolidado de **K04, K02, E08, P08, K07, P15, Z15, CD11 e G26**, por fase da RSL. Cada item cita a fonte (sigla + seção/tabela/página). Para filtrar, marcar status e anotar onde registrou na tese, use a planilha `CHECKLIST_TESE.xlsx` (mesmos itens).

**Como ler**
- **DECISÃO:** escolha que você precisa tomar e registrar no protocolo/tese.
- **FAZER:** ação ou artefato que os autores exigem ou recomendam.
- **CUIDADO:** armadilha, viés ou erro comum a evitar.
- **RELATAR:** o que precisa aparecer escrito.
- `[CONFERIR]` = o agente de leitura achou o trecho ambíguo, incompleto ou uma inferência; confirme no PDF antes de citar.
- Itens marcados "(Avaliador)" no G26 só valem se sua tese também **avaliar** o desempenho de uma IA.

**Avisos**
- Itens foram extraídos por leitura assistida do texto dos PDFs; ao citar na tese, **confira o trecho original**. Há repetições entre papers (K07, P15 e K02 se sobrepõem em seleção, qualidade e validade); mantidas de propósito porque cada fonte reforça ou nuança a outra.
- K02 e K04 tratam de estudos empíricos em geral; use-os como lente para avaliar estudos primários e, se houver, a avaliação do seu próprio sistema.
- O **Protocolo v4.0** do projeto prevalece sobre artigos; divergência vira `[ESCLARECER]`.
- G26: a constituição do projeto (P2) e a spec 011 proíbem IA em triagem, QA, extração, codificação e síntese; use o G26 para **decidir e declarar** a posição da tese sobre IA, não para introduzir funções de IA.

## Índice

- [F0 — Fundamentos, justificativa e escolha do método](#f0--fundamentos-justificativa-e-escolha-do-método)
- [F1 — Pergunta de pesquisa e escopo](#f1--pergunta-de-pesquisa-e-escopo)
- [F2 — Protocolo e desenho](#f2--protocolo-e-desenho)
- [F3 — Busca](#f3--busca)
- [F4 — Seleção](#f4--seleção)
- [F5 — Avaliação de qualidade](#f5--avaliação-de-qualidade)
- [F6 — Extração e classificação](#f6--extração-e-classificação)
- [F7 — Síntese e análise](#f7--síntese-e-análise)
- [F8 — Validade e ameaças](#f8--validade-e-ameaças)
- [F9 — Relato (texto da tese)](#f9--relato-texto-da-tese)
- [F10 — Uso de IA](#f10--uso-de-ia)

## Contagem

| Fase | DECISÃO | FAZER | CUIDADO | RELATAR | Total |
|---|---|---|---|---|---|
| F0 Fundamentos, justificativa e escolha do método | 25 | 22 | 31 | 5 | 83 |
| F1 Pergunta de pesquisa e escopo | 21 | 23 | 12 | 3 | 59 |
| F2 Protocolo e desenho | 31 | 33 | 6 | 2 | 72 |
| F3 Busca | 13 | 24 | 23 | 9 | 69 |
| F4 Seleção | 14 | 28 | 14 | 6 | 62 |
| F5 Avaliação de qualidade | 19 | 31 | 35 | 3 | 88 |
| F6 Extração e classificação | 18 | 61 | 25 | 3 | 107 |
| F7 Síntese e análise | 14 | 46 | 25 | 2 | 87 |
| F8 Validade e ameaças | 3 | 38 | 37 | 8 | 86 |
| F9 Relato (texto da tese) | 4 | 8 | 4 | 47 | 63 |
| F10 Uso de IA | 3 | 5 | 10 | 1 | 19 |


## F0 — Fundamentos, justificativa e escolha do método


### DECISÃO

- [ ] Considerar o **ponto de vista** do leitor: desenvolvedor individual, gerente de projeto ou gerente sênior (a adoção de tecnologia costuma ser decisão organizacional). _(K04 §4)_
- [ ] Definir **para quem** o checklist serve na sua tese: (a) você como *leitor/avaliador* dos estudos primários; (b) você como *autor* de qualquer estudo empírico próprio (ex.: avaliar seu sistema). As diretrizes servem a leitor, revisor, autor, planejador, meta-analista e editor. _(K02 §1)_
- [ ] **Definir o tipo de estudo** (observacional, intervenção/controlado ou não etc.) e declarar se é **confirmatório** (conclusões fortes) ou **exploratório** (conclusões fracas). Não "vestir" um estudo com a reputação de outro. _(K02 I3)_
- [ ] Escolher o método a partir de três coisas: a pergunta de pesquisa, a postura filosófica e as restrições práticas (recursos, acesso, controle de variáveis, habilidades do pesquisador). Não há receita pronta. _(E08 §1, §5)_
- [ ] Declarar explicitamente a postura filosófica (positivismo/pós-positivismo, construtivismo/interpretivismo, teoria crítica, pragmatismo); é impossível fazer ou julgar pesquisa sem algum compromisso com uma postura. _(E08 §3)_
- [ ] [CONFERIR] Para a tese: dizer qual postura embasa a RSL (provável: pragmatista/pós-positivista com síntese temática construtivista). O capítulo não trata RSL; é adaptação. _(E08 §3)_
- [ ] Escolher o papel da teoria: positivista verifica teorias; construtivista busca teorias locais emergentes; crítico a vê como asserção de poder; pragmático como produto de consenso avaliado por utilidade. _(E08 §4)_
- [ ] Considerar uma estratégia de múltiplos métodos: todos os métodos têm falhas diferentes, e métodos complementares compensam fraquezas uns dos outros. _(E08 §1, §5.6)_
- [ ] Pesquisa (research design) = escolher método que explore suas forças e mitigue suas fraquezas; a validade depende de quão bem o desenho compensa as fraquezas do método. _(E08 §5)_
- [ ] Escolher entre **mapeamento** (estruturar a área; frequências; lacunas; menos esforço; visão grossa) e **RSL** (estado da evidência; leitura em profundidade; mais esforço). Eles diferem em objetivo, amplitude, validade e implicações. _(P08 Resumo, §3.2)_
- [ ] Considerar usá-los em **sequência**: mapa primeiro; depois RSL focada num subtópico. Um mapa sozinho já tem valor (acha lacunas e falta de avaliação/validação). _(P08 §4)_
- [ ] Declarar qual(is) motivo(s) justificam a revisão: resumir evidências sobre uma tecnologia, achar lacunas para pesquisas futuras, ou posicionar a nova pesquisa (típico de tese). Também pode servir para testar hipóteses teóricas. _(K07 §2.1)_
- [ ] Escolher o tipo de estudo: se há pouca evidência ou o tema é muito amplo, um mapeamento sistemático pode ser mais adequado que uma RSL; se já há várias RSLs de qualidade, considerar revisão terciária. _(K07 §2.5.1, §2.5.2)_
- [ ] Se a revisão for de pesquisador único (ex.: doutorando), definir como compensar a ausência de revisores múltiplos. A versão "leve" prioriza: protocolo, pergunta, tratamento do revisor único na seleção/extração, estratégia de busca, dados a extrair (incluindo qualidade), listas de incluídos e excluídos, diretrizes de síntese e de relato. _(K07 §9)_
- [ ] A etapa de "encomenda" não se aplica a revisão feita para necessidade própria ou de doutorando; nesse caso, incorporar a estratégia de disseminação ao protocolo. _(K07 §5.2)_
- [ ] Decidir se o trabalho é um mapeamento (estruturar a área: classificar e contar estudos) ou uma revisão sistemática (sintetizar evidência e sua força). Mapa: perguntas gerais sobre tendências/tópicos; RSL: pergunta específica sobre eficácia de uma intervenção. _(P15 §1, §2.1)_
- [ ] Escolher entre usar um checklist pronto (Dybå & Dingsøyr, Kitchenham & Charters), derivar um próprio ou adaptar de revisões anteriores do mesmo tema; registrar a escolha e a fonte. _(Z15 §5.1, Tab. 4)_
- [ ] Em mapeamentos (SMS), decidir se vale avaliar a qualidade: não é obrigatória, mas pode aumentar a credibilidade da evidência. _(Z15 §5.4)_
- [ ] Justificar a escolha da síntese temática como método de síntese: ela serve para dados qualitativos e mistos (comuns em ES) e é um dos métodos mais usados em RSLs de ES (cerca de 2/3 das que sintetizam estudos usam análise narrativa ou temática). _(CD11 §I)_
- [ ] Escolher e citar qual abordagem de análise temática será seguida (Braun & Clarke; Boyatzis; Attride-Stirling; Thomas & Harden) e justificar; elas diferem em codificação, temas e confiabilidade. _(CD11 §I, Tab. 1)_
- [ ] Se usar Thomas & Harden como base, adaptar: aqui os estudos primários (e não transcrições originais) são a unidade de análise, e a codificação linha a linha provavelmente é inviável com muitos estudos. _(CD11 §I, §III)_
- [ ] Declarar o referencial teórico (ou a ausência dele) e a postura da síntese: o método pode ser realista/essencialista ou construcionista, e sem referencial teórico a análise temática tem poder interpretativo limitado (fica quase só descritiva). _(CD11 §I)_
- [ ] Definir o propósito da síntese: desenvolver temas analíticos a partir de uma síntese descritiva e explicar achados relevantes para a pergunta da revisão (necessidade, adequação, aceitabilidade, efetividade de intervenções). _(CD11 §I)_
- [ ] Decidir, e registrar, até onde a síntese vai: descrição de temas de ordem superior, taxonomia, modelo ou teoria (o produto final influencia a profundidade do trabalho). _(CD11 §V)_
- [ ] Decida e justifique, para cada tarefa da RSL, se a IA entra ou não (planejamento, triagem, extração, qualidade, síntese, relato). A justificativa precisa estar explícita na tese. _(G26 PlanR2 (Tab. 5 p.20); Ap. B.2.4(1) p.40)_

### FAZER

- [ ] Justificar a RSL como forma de integrar a **melhor evidência de pesquisa** com experiência prática e valores das partes interessadas na decisão sobre desenvolvimento e manutenção de software. _(K04 §3)_
- [ ] Adotar os **5 passos da EBSE**: (1) pergunta respondível; (2) buscar a melhor evidência; (3) avaliar criticamente (validade, impacto, aplicabilidade); (4) integrar com expertise e contexto; (5) avaliar o próprio processo. _(K04 §4, Tab. 1)_
- [ ] Registrar que as diretrizes são **preliminares** (propostas para debate); citá-las como apoio, não como norma definitiva. _(K02 §1)_
- [ ] Positivismo: conhecimento vem de observações verificáveis e se testam hipóteses derivadas de teoria (refutar é mais produtivo que provar); associado a experimento, survey e estudo de caso confirmatório. _(E08 §3)_
- [ ] Construtivismo: significados são socialmente construídos; busca-se entender como pessoas dão sentido ao mundo e gerar teorias locais; associado a etnografia, estudos de caso exploratórios e surveys. _(E08 §3)_
- [ ] Teoria crítica: o conhecimento é julgado por libertar de sistemas restritivos; pesquisa participativa; associada à pesquisa-ação. _(E08 §3)_
- [ ] Pragmatismo: verdade é o que funciona para resolver o problema; livre uso de métodos, preferência por métodos mistos. _(E08 §3)_
- [ ] Definir com precisão os termos teóricos (ex.: o que é "XAI", "explicação", "sistema multiagente" na tese) para que estudos possam ser identificados e comparados. _(E08 §2, §4)_
- [ ] Usar a teoria para ligar a pesquisa à literatura: termos definidos permitem comparar estudos e fazer indução empírica (um estudo isolado nunca é conclusivo). _(E08 §4)_
- [ ] Estudar o método escolhido antes de aplicá-lo; pode exigir treinamento específico. _(E08 Conclusões)_
- [ ] Fazer uma busca preliminar por revisões sistemáticas já existentes sobre o fenômeno e avaliá-las antes de decidir que uma nova é necessária. _(K07 §5.1)_
- [ ] Avaliar as revisões existentes com o checklist do CRD: objetivos, fontes e restrições da busca, critérios de inclusão/exclusão e sua aplicação, critérios de qualidade e sua aplicação, extração, síntese, tratamento de diferenças entre estudos, razoabilidade de combinar estudos e se as conclusões decorrem da evidência. _(K07 §5.1)_
- [ ] Alternativamente, pontuar as revisões existentes pelos 4 critérios DARE (critérios descritos e adequados; busca provavelmente abrangente; qualidade dos estudos avaliada; dados dos estudos bem descritos). _(K07 §5.1)_
- [ ] Justificar a necessidade da revisão com argumento do tipo: o tema é importante, há resultados conflitantes/lacuna, e é preciso determinar sob que condições algo vale. _(K07 §5.1)_
- [ ] Conferir que as características de uma RSL estão presentes: protocolo prévio, busca definida e documentada, critérios explícitos de inclusão/exclusão, informações e critérios de qualidade definidos por estudo. _(K07 §2.4)_
- [ ] Seguir as três fases (planejamento, condução, relato) e tratar todas as etapas como obrigatórias, exceto "encomenda" e as avaliações formais do protocolo e do relatório (opcionais). _(K07 §4)_
- [ ] Se a revisão for encomendada, o contratante redige documento com título, contexto, perguntas, grupo consultivo, métodos, cronograma, disseminação, infraestrutura, orçamento e referências. _(K07 §5.2)_
- [ ] Registrar na justificativa para qual objetivo de mapeamento a tese o usa: (i) ver extensão/alcance/natureza da pesquisa; (ii) avaliar se vale fazer uma RSL completa; (iii) resumir/disseminar achados; (iv) identificar lacunas. _(P15 §5.1.1)_
- [ ] Usar o mapa como linha de base para uma RSL posterior: ele identifica estudos avaliativos/validados para aprofundar, refina perguntas e estima o esforço da RSL. Benefícios observados: economia de tempo (protocolo reaproveitado), visão geral, lacunas, trabalhos relacionados, conjunto de validação. _(P15 §2.2, §5.1.1)_
- [ ] Justificar a avaliação de qualidade com o argumento central: a revisão é tão boa quanto os estudos que ela reúne; avaliar com rigor os estudos incluídos aumenta a confiança nas conclusões. _(Z15 Resumo, §1)_
- [ ] Em estudo terciário/trabalho relacionado, citar as ferramentas conhecidas: escala de Jadad (ensaios randomizados), CASP (10 questões, adaptado em SE por Dybå & Dingsøyr com 11 critérios), GRADE (graus de qualidade da evidência; complexo para iniciantes). _(Z15 §2.2)_
- [ ] Planejar os 5 passos como um processo iterativo, não linear (voltar a passos anteriores é normal); a ordem apresentada serve apenas para estruturar. _(CD11 §I, Fig. 1)_

### CUIDADO

- [ ] Não adotar a abordagem só "porque todos fazem": o movimento tem críticos (pesquisa é falível, generalizações difíceis, evidência pode não bastar para a prática). Reconheça limites. _(K04 §1)_
- [ ] Dois limites específicos de SE: **fator habilidade** (impede duplo-cego; viés do sujeito e do experimentador) e **fator ciclo de vida** (difícil isolar efeito de técnica; desfechos imediatos são maus substitutos dos finais). _(K04 §5.1–5.2)_
- [ ] Evidência atual em SE é fragmentada, mal integrada e sem padrões acordados; poucas réplicas e meta-análises. Mencione isso como motivação e limitação. _(K04 §4.3)_
- [ ] Resultados de pesquisa muitas vezes não chegam à indústria e não são apresentados de forma acessível; considere um produto/seção para praticantes. _(K04 §4.4, §6)_
- [ ] O artigo parte de que a qualidade de estudos empíricos em SE costuma ser baixa (erros de estatística, conclusões que não decorrem dos resultados). Trate cada estudo primário com leitura crítica, não como verdade. _(K02 §1)_
- [ ] Regressão/correlação são, em geral, exploratórias e não provam causa; um modelo para *controlar* o desenvolvimento precisa de relações causais. _(K02 I3)_
- [ ] Muitos pesquisadores escolhem método inadequado por não entenderem os objetivos do método ou por conhecerem poucas alternativas. _(E08 §1)_
- [ ] Teorias funcionam como "lente" que filtra a observação, quer sejam explicitadas ou não; explicitá-las. Em ES, pesquisadores costumam falhar em tornar teorias explícitas, e os dados ficam difíceis de interpretar e comparar. _(E08 §4)_
- [ ] A pesquisa empírica nunca produz conhecimento certo; informar a limitação de cada método e de cada estudo. _(E08 Conclusões)_
- [ ] Terminologia dos métodos é inconsistente entre áreas e as definições do capítulo não são consenso; definir os termos usados na tese. _(E08 §5, Conclusões)_
- [ ] Mapeamento **não** estabelece "melhores práticas" baseadas em evidência (não estuda artigos em detalhe). RSL mostra onde falta evidência; mapa não. _(P08 §3.2)_
- [ ] Restringir só a estudos empíricos pode dar visão enviesada da área (só ~5% rigorosos em alguns casos); empirismo é mais fácil em certas subáreas. _(P08 §3.2)_
- [ ] Uma revisão não sistemática tem pouco valor científico se não for completa e justa; deve ser feita de modo "justo e visto como justo". _(K07 §2.2)_
- [ ] Procurar e relatar também pesquisas que contrariam a sua hipótese preferida, não só as que a apoiam. _(K07 §2.2)_
- [ ] A metodologia sistemática reduz o viés da revisão, mas não protege contra o viés de publicação presente nos estudos primários. _(K07 §2.3)_
- [ ] Uma RSL exige bem mais esforço que uma revisão tradicional; dimensionar tempo antes de se comprometer. _(K07 §2.3)_
- [ ] Em meta-análise, o ganho de poder estatístico também permite detectar pequenos vieses, não só efeitos reais. _(K07 §2.3)_
- [ ] Em ES, a metodologia deve ser adaptada: há poucos estudos empíricos, rigor metodológico menor que na medicina e dados frequentemente proprietários. Não aplicar diretrizes médicas cegamente (sem RCT nem cegamento na maioria dos casos). _(K07 §1, §3, §9)_
- [ ] O processo é iterativo: critérios de seleção, formulários de extração e métodos de síntese definidos no protocolo podem ser refinados depois; registrar cada mudança. _(K07 §4)_
- [ ] Mapas e RSLs diferem em busca, qualidade e resultado, mas partilham busca/seleção; as diretrizes do artigo valem para mapas e só parcialmente para RSLs (generalização limitada). _(P15 §2.1, §3.6.3, §5.1.5)_
- [ ] Nenhuma diretriz isolada cobre todo o processo: 24 dos 52 mapas combinaram mais de uma. Por isso o artigo consolida as atividades; justificar quais guias a tese combina e por quê. _(P15 §4.4.1, Fig. 5, Tab. 5)_
- [ ] Os guias mais usados eram Kitchenham & Charters (2007) e Petersen et al. (2008); os demais tiveram poucas citações. _(P15 §4.4.1, Fig. 5)_
- [ ] Muitos autores relatam avaliação de qualidade "por obrigação", sem entender como fazê-la bem; desenhar e aplicar uma avaliação rigorosa é difícil. _(Z15 §1)_
- [ ] Há poucas diretrizes para desenhar a avaliação de qualidade em SE; o artigo indica que são necessárias diretrizes apropriadas. _(Z15 Resumo, §1)_
- [ ] Dos 127 estudos que diziam avaliar qualidade, 17 não publicaram os critérios (seis afirmaram avaliar mas sem critérios acessíveis); não repetir essa falha. _(Z15 §4.1)_
- [ ] Não deixar o método de síntese implícito: nenhuma das 8 revisões temáticas analisadas citava o método usado. Nomear a síntese temática e o passo a passo seguido. _(CD11 §I)_
- [ ] Entenda que resumos fluentes feitos por IA, sem documentação replicável, equivalem no máximo a uma revisão de opinião de especialista, e NÃO a uma RSL. Não apresente "a IA fez a revisão" como se fosse sistemática. _(G26 §2.1 p.4; §6 p.24)_
- [ ] A IA hoje não é capaz de conduzir RSL sem supervisão; ela serve como "convidada" (guest) sob supervisão, nunca substituta do pesquisador. _(G26 Resumo p.1; §1 p.2; §8 p.27)_
- [ ] Uma RSL deve produzir evidência Válida, Rastreável, Qualificada (força da evidência avaliada) e Verificável/reprodutível. Use esses 4 critérios para checar se o uso de IA não os compromete. _(G26 §2.2 p.5)_
- [ ] Se você usar IA em tarefas e perder o hábito de fazê-las à mão, perde a capacidade de avaliar a saída da IA; para estudante de doutorado/mestrado, a RSL também é aprendizado. Faça pelo menos parte das tarefas manualmente. _(G26 §6 p.25)_
- [ ] Mapeamento sistemático, escopo e revisão rápida têm menos exigências (em geral dispensam avaliação de risco de viés e força da evidência); mesmo assim precisam de controle de processo e de relato conforme padrões. Confirme qual tipo de revisão é a sua. _(G26 §2.2 p.5; Ap. C.3, C.5 pp.45, 51)_

### RELATAR

- [ ] Registrar a postura adotada para poder argumentar por que os métodos foram escolhidos, mesmo que outros discordem. _(E08 §3)_
- [ ] Citar o(s) guia(s) seguido(s) e as diferenças/adaptações feitas, já que combinar guias gera variação na execução. _(P15 §4.4.1, §6 (RQ1))_
- [ ] Na introdução, descrever o contexto do tema, a necessidade do mapeamento e sua utilidade. _(P15 §5.3)_
- [ ] Em "trabalhos relacionados", apresentar os estudos secundários e terciários existentes na área. _(P15 §5.3)_
- [ ] Dizer qual guia/checklist embasa a avaliação (a maioria dos estudos citou alguma fonte). _(Z15 §5.1, Tab. 4)_

## F1 — Pergunta de pesquisa e escopo


### DECISÃO

- [ ] Calibrar o **nível de abstração** do fator de estudo: nem tão alto ("métodos de projeto") nem tão restrito que perca estudos; amplo o bastante para mostrar variação entre populações. _(K04 §4.1)_
- [ ] Classificar o tipo de pergunta: existência ("X existe?"); descrição/classificação ("como é X, como categorizar"); descritiva-comparativa ("X difere de Y?"). _(E08 §2)_
- [ ] Perguntas de taxa-base: frequência/distribuição ("com que frequência X ocorre?") e descritiva-de-processo ("como X normalmente acontece?"). _(E08 §2)_
- [ ] Perguntas de relação ("X e Y se relacionam/correlacionam?"). _(E08 §2)_
- [ ] Perguntas de causalidade: simples ("X causa Y?"), comparativa ("X causa mais Y que Z?") e de interação ("sob qual condição?"). _(E08 §2)_
- [ ] Perguntas de projeto (design): "qual forma eficaz de atingir X?"; pressupõem que as perguntas de conhecimento já foram respondidas. _(E08 §2)_
- [ ] [CONFERIR] Classificar cada RQ da RSL (RQ1, RQ2...) no tipo de pergunta do capítulo (ex.: classificação, frequência, descrição de processo) e justificar que a RSL é adequada para ela. É adaptação. _(E08 §2)_
- [ ] Amplitude: usar só população e intervenção (sem desfecho/desenho) para visão ampla; restringir tipos de estudo pode deixar o mapa incompleto. _(P08 §2.2)_
- [ ] Definir o tipo de pergunta (efeito de uma tecnologia, frequência de adoção/sucesso, fatores de custo e risco, impacto em confiabilidade/desempenho/custo, custo-benefício). _(K07 §5.3.1)_
- [ ] Em tese, as perguntas podem ser de interesse sobretudo acadêmico, desde que identifiquem a base existente e mostrem onde a pesquisa proposta se encaixa. _(K07 §5.3.1)_
- [ ] População: pode ser papel, categoria de engenheiro, área de aplicação ou segmento da indústria. Como há poucos estudos em ES, evitar restringir demais a população no início. _(K07 §5.3.2)_
- [ ] Definir o contexto (academia x indústria, tipo de participante, escala da tarefa) e se estudos com estudantes e tarefas pequenas serão excluídos, sabendo que em ES podem ser os únicos disponíveis. _(K07 §5.3.2)_
- [ ] Em ES, normalmente não restringir a um único desenho de estudo (como RCT) porque há escassez de estudos; prever como agregar estudos de tipos muito diferentes. _(K07 §5.3.2)_
- [ ] Se não houver evidência de resultados mistos, considerar adicionar uma pergunta sobre as condições em que os resultados diferem, como fizeram os exemplos do documento. _(K07 §5.3.1 (exemplo))_
- [ ] Decidir se consulta o público-alvo (especialistas, usuários dos resultados) para definir perguntas — ação não aplicada no mapa do próprio artigo, mas pontuada com 2 na régua "necessidade". _(P15 Tab. 8, Tab. 9)_
- [ ] Fixar as fronteiras do escopo (onde termina a área). O escopo e a redação da pergunta (aberta vs. específica) explicaram em parte por que dois mapas sobre o mesmo tema incluíram artigos diferentes. _(P15 §2.2)_
- [ ] Definir o que se quer da avaliação de qualidade antes de escolher critérios; "avaliar sem propósito" é esforço desperdiçado. _(Z15 §5.4, §7)_
- [ ] Se a meta for visão ampla do tema (mapeamento/área imatura), pode-se avaliar qualidade sem excluir por ela; dez estudos declararam não excluir por qualidade (mapas, áreas imaturas, desejo de incluir o máximo, ou agregação do reportado). _(Z15 §5.2)_
- [ ] Deixar claros os objetivos da síntese, pois eles definem quais trechos dos estudos são relevantes e o nível de codificação adequado (Tab. 2 #2 e #6). _(CD11 §II, Tab. 2)_
- [ ] Se usar IA para ajudar a formular as perguntas de pesquisa (RQs), registre isso: o paper sugere que essa tarefa pode dispensar validação formal, desde que o uso seja totalmente relatado e humanos assumam a responsabilidade. _(G26 PlanR1 (Tab. 5 p.20); §4.1 p.14; Ap. B.2.1 p.38)_
- [ ] Se a IA ajudar a definir critérios de elegibilidade (inclusão/exclusão), defina-os com base nas RQs e teste-os em amostra aleatória antes de usar; os critérios podem ser refinados da triagem por título/resumo para o texto completo. _(G26 PlanR1 (Tab. 5 p.20); Ap. C.1 p.41)_

### FAZER

- [ ] Converter a necessidade de informação em pergunta com três partes: **fator de estudo** (tecnologia), **população** e **desfechos**. _(K04 §4.1)_
- [ ] Se testar hipótese, declará-la **antes** de ver os dados e ligá-la a uma teoria (hipótese "funda"), não apenas "não há correlação entre X e Y" (hipótese rasa). _(K02 C2)_
- [ ] Se o estudo for exploratório, declarar antes da análise **quais perguntas** investiga e como. _(K02 C3)_
- [ ] Descrever pesquisas semelhantes e como a sua se relaciona com elas. _(K02 C4)_
- [ ] Especificar o **contexto** (indústria, organização, experiência da equipe, produtos, processos) com entidades, atributos e medidas definidos. _(K02 C1)_
- [ ] Esclarecer a pergunta de pesquisa antes de escolher o método; a pergunta mais óbvia nem sempre é a melhor para começar e costuma ser vaga (pressupõe definições, populações, medidas). _(E08 §2)_
- [ ] Começar por perguntas exploratórias se o campo é imaturo; métodos que dão dados qualitativos ricos ajudam a construir teorias provisórias. Uma revisão de literatura pode, em vez de estudo empírico, responder algumas dessas perguntas. _(E08 §2)_
- [ ] Perguntas típicas de mapa: quais tópicos, quantos artigos por categoria, **quais fóruns**, tendências no tempo, tipo de pesquisa/avaliação. _(P08 §2.1, Tab. 1)_
- [ ] Formular as perguntas antes de tudo: elas determinam a busca, a extração e a síntese; é a parte mais importante da revisão. _(K07 §5.3)_
- [ ] Estruturar a pergunta com PICOC (População, Intervenção, Comparação, Resultados/Outcomes, Contexto) e, se útil, tipos de estudo. _(K07 §5.3.2)_
- [ ] Descrever a Intervenção (metodologia/ferramenta/tecnologia/procedimento) e a Comparação de forma adequada. _(K07 §5.3.2)_
- [ ] Especificar todos os desfechos relevantes para praticantes (ex.: confiabilidade, custo, prazo), inclusive quando se busca melhorar um aspecto sem piorar outro. _(K07 §5.3.2)_
- [ ] Usar um mapeamento prévio para ajudar a delimitar o escopo e esperar revisar as perguntas durante a elaboração do protocolo. _(K07 §5.6)_
- [ ] Preferir perguntas claras e estreitas para limitar o escopo da revisão. _(K07 §5.6)_
- [ ] Listar as perguntas complementares que NÃO serão investigadas, para afinar os critérios de exclusão e a extração. _(K07 §6.2.2)_
- [ ] Formular perguntas de mapeamento amplas ("o que sabemos sobre X?") e desdobrá-las em subperguntas que orientem a extração (o que é abordado, onde/quando foi publicado, que tipo de evidência). _(P15 §5.1.1)_
- [ ] Incluir perguntas típicas de mapa: cobertura do tópico, fontes/anos de publicação, tipo de evidência e métodos, tendências. _(P15 §5.1.1)_
- [ ] Registrar o planejamento (escopo, perguntas, critérios) antes de executar; "planejar" concentra todas as decisões do estudo. _(P15 §5.1)_
- [ ] Escolher o(s) propósito(s) entre os cinco de Kitchenham: P1 seleção (critérios de inclusão/exclusão mais detalhados); P2 diferença (qualidade explica divergência de resultados); P3 ponderação (peso dos estudos na síntese); P4 interpretação (força das inferências); P5 recomendação (orientar pesquisas futuras). _(Z15 §5.2)_
- [ ] Casar critérios com o propósito (ex.: P5 pede critérios como "discute limitações?" e "recomenda pesquisa futura?"). _(Z15 §5.2, §7)_
- [ ] Usar as perguntas de pesquisa, hipóteses e variáveis-chave como origem da lista inicial de códigos (abordagem dedutiva/integrada); sem RQs claras, a codificação perde foco. _(CD11 §III)_
- [ ] Ao final, conferir que as RQs foram respondidas com base nas evidências da síntese (Tab. 2 #21); redigir as RQs pensando nessa verificação. _(CD11 §V, Tab. 2 #21)_
- [ ] Guarde no protocolo e no relatório final (ou material suplementar) a entrada dada à IA, a saída dela e a versão final das RQs acordada pela equipe. _(G26 Ap. B.2.1 p.38)_

### CUIDADO

- [ ] Categorias de população muito restritivas podem eliminar evidência útil. _(K04 §4.1)_
- [ ] Evitar fazer muitas atividades de pesquisa num só estudo (gerar e "validar" hipóteses com os mesmos dados). _(K02 C3)_
- [ ] Não confundir correlação com causalidade: X pode causar Y, Y causar X, ter causa comum ou co-evoluir. É muito mais difícil demonstrar causalidade. _(E08 §2)_
- [ ] Perguntas devem ser relevantes para praticantes e pesquisadores, levar a mudança (ou confirmação) de prática e revelar discrepâncias entre crenças comuns e a realidade. _(K07 §5.3.1)_
- [ ] "Não usar a intervenção" não é descrição suficiente do controle: o efeito pode ser confundido com o efeito do treinamento (problema maior com estudantes). _(K07 §5.3.2)_
- [ ] Medidas substitutas (surrogate), como defeitos em teste como proxy de qualidade, podem enganar e tornar as conclusões menos robustas. _(K07 §5.3.2)_
- [ ] Dois mapas independentes de teste de linhas de produto, com perguntas parecidas, incluíram conjuntos diferentes de artigos e concordaram em só 33% na classificação do tipo de pesquisa. _(P15 §2.2)_
- [ ] Uso real dos propósitos (96 estudos o declaram/implicam): P4 = 54, P1 = 37, P3 = 24, P5 = 11, P2 = 1 (Fig. 4). [CONFERIR: ordem dos números da Fig. 4 lida da extração] _(Z15 §5.2, Fig. 4)_
- [ ] P2 (diferenças) é pouco viável em SE: só um estudo o cumpriu, provavelmente por custo elevado, e foi herdado de outras disciplinas sem validação na prática de SE. _(Z15 §5.2)_
- [ ] Apenas 14 dos 54 estudos P4 o declararam; os outros 40 foram inferidos do uso dos critérios. Declarar explicitamente o propósito. _(Z15 §5.2)_
- [ ] 14 estudos não declaram nem permitem inferir propósito; relatam critérios e resultados sem relacionar à revisão. _(Z15 §5.2)_
- [ ] A IA pode tender a priorizar resultados mais comuns e ignorar opiniões minoritárias ou viés de publicação; revise criticamente o que ela sugerir para escopo e critérios. _(G26 §2.1 item 4 p.3)_

### RELATAR

- [ ] Perguntas de revisão (primárias e secundárias) explicitadas e, se usado, o PICOC. _(K07 §5.3.2, Tab. 8)_
- [ ] Apresentar as perguntas de pesquisa em subseção própria no método, e estruturar os resultados conforme as perguntas do mapeamento. _(P15 §5.3)_
- [ ] Relate o uso de IA na etapa de RQs e critérios (ferramenta, prompt, saída, versão final adotada). _(G26 Ap. B.2.1 p.38)_

## F2 — Protocolo e desenho


### DECISÃO

- [ ] Identificar a **população** de onde vêm sujeitos e objetos; sem população definida não há inferência. _(K02 D1)_
- [ ] Definir o **processo de seleção** dos sujeitos/objetos (amostragem aleatória ou justificar a não aleatória) e critérios de inclusão/exclusão. _(K02 D2)_
- [ ] Definir como sujeitos/objetos são **alocados aos tratamentos** (randomização; alternativas em amostras pequenas; plano para viés pós-estudo e dados ausentes). _(K02 D3)_
- [ ] Definir a **unidade experimental** (pessoa, equipe, organização) — errar infla a amostra. _(K02 D5)_
- [ ] Escolher níveis de **cegamento** possíveis (alocação, material, correção, análise). _(K02 D7)_
- [ ] **Justificar as medidas de desfecho** pela relevância aos objetivos; cuidado com medidas substitutas (ex.: linhas alteradas no lugar de esforço). _(K02 D11)_
- [ ] Definir a unidade de análise antes da coleta (empresa, projeto, equipe, desenvolvedor, evento, artefato); ela orienta amostragem e foco. _(E08 §5.2, §5.3, §6)_
- [ ] Em estudos mistos, definir antes a estratégia de coleta e a sequência dos métodos (explicativa sequencial, exploratória sequencial ou triangulação concorrente). _(E08 §5.6)_
- [ ] Definir **antes** os critérios de inclusão/exclusão alinhados às perguntas (ex.: exigir ou não empírico). _(P08 §2.3)_
- [ ] Definir a política de **profundidade de leitura**: não fixar que só o resumo será lido; permitir aprofundar quando houver dúvida. _(P08 §4)_
- [ ] Definir no protocolo se haverá meta-análise formal e quais técnicas. _(K07 §5.4)_
- [ ] Definir como serão tratados dados que exijam manipulação, suposições ou inferências, incluindo o processo de validação. _(K07 §5.4)_
- [ ] Ponderar o equilíbrio esforço × confiabilidade: aplicar uma estratégia ou subconjunto de atividades de busca; o essencial é que as conclusões sobre tendências e lacunas não mudem. Faltam estudos comparando as estratégias para recomendar uma. _(P15 §5.1.2, §6)_
- [ ] Escolher o desenho da extração: formulário com campo + valor + pergunta de pesquisa associada (modelo na Tab. 3). _(P15 §3.4, Tab. 3)_
- [ ] Definir o número de critérios. Prática: maioria usa 2 a 7; extremos vão de 1 pergunta (exige muita informação) a 31 (detalhista; cobre pouco a relevância). _(Z15 §5.1, Fig. 3)_
- [ ] Formato das perguntas: quase todos usam perguntas fechadas; só 2 estudos usaram abertas (dificultam comparação quantitativa, mas permitem extração conjunta). _(Z15 §5.1)_
- [ ] Registrar no protocolo a estratégia de extração: os três tipos de dados (publicação, contexto, achados), o modelo/formulário de extração e como será conferida. _(CD11 §II, Fig. 2)_
- [ ] Registrar no protocolo a abordagem de codificação: dedutiva (lista inicial), indutiva (grounded theory) ou integrada; o artigo diz que a integrada é a mais pertinente em RSLs. _(CD11 §III)_
- [ ] Definir quantos pesquisadores extraem e codificam (recomendação: pelo menos dois, de forma independente quando possível) e como resolver discordâncias (consenso ou árbitro externo). _(CD11 §II, §III)_
- [ ] Definir a ferramenta de apoio: gerenciador de referências, formulário de resultados por RQ ou software de análise qualitativa (o artigo diz que ajuda na codificação). _(CD11 §II, §III)_
- [ ] Definir antecipadamente quais fontes de heterogeneidade serão exploradas (resultados, desenho dos estudos, populações/intervenções/contextos) e se haverá análise de subgrupos. _(CD11 §V)_
- [ ] Definir como será tratada a qualidade dos estudos primários (avaliar ou não, ponderar ou não) e como será feita a análise de sensibilidade. _(CD11 §VI, §VII)_
- [ ] Definir o nível/tamanho do trecho codificado (palavra, frase, parágrafo ou achado inteiro). Em RSLs de ES o artigo recomenda trabalhar com os "pedaços" (achados) já extraídos. _(CD11 §III)_
- [ ] Defina planos de contingência para desempenho inadequado: devolver a tarefa a humanos que não participaram dela e/ou revisar a estratégia de prompt. _(G26 Ap. B.2.2(8) p.40; ScrRev2 (Tab. 6 p.21))_
- [ ] Defina ANTES da validação quais níveis de desempenho da IA são aceitáveis (ou o processo para defini-los), e justifique. _(G26 ScrRev1 (Tab. 6 p.21))_
- [ ] Especifique todas as tarefas da RSL que terão apoio de IA (PlanR2) e justifique a escolha das ferramentas, avaliando-as criticamente (Plan1). _(G26 PlanR2, Plan1 (Tab. 5 p.20))_
- [ ] Adote uma abordagem de estudo de caso prospectivo: usar a IA em paralelo, durante a própria RSL, para gerar evidência de desempenho (menos risco de contaminação de dados do que reanalisar RSLs antigas). _(G26 PlanR3 (Tab. 5 p.20); §4.2 p.15)_
- [ ] Defina antecipadamente a escala de validação: sorteio aleatório de uma amostra de itens (o paper cita 5% a 20% como exemplo) para a validação. [CONFERIR: o paper não justifica esse intervalo nem dá tamanho mínimo; veja o estudo companheiro [61].] _(G26 Ap. B.2.1 passo 1, p.38)_
- [ ] Planeje como a tarefa será feita se a IA substituir um dos dois revisores humanos: como resolver discordâncias humano-IA e como garantir supervisão total da saída. _(G26 Ap. B.2.1 p.39)_
- [ ] Defina como medir custo energético/computacional: use proxies viáveis (nº de chamadas de API, tokens, custo em dinheiro). _(G26 Ap. B.1.1 p.36; Ap. B.2.2(6) p.40)_
- [ ] Se a equipe tem pouca experiência com IA, considere incluir alguém com experiência em IA generativa; dê treinamento a quem usará as ferramentas. _(G26 Ap. B.2.1 p.37-38)_

### FAZER

- [ ] Seguir/adotar diretrizes explícitas de RSL e descrever o método (o artigo recomenda guidelines como ação de baixo risco para adotar já). _(K04 §6)_
- [ ] Considerar o **registro prévio** do protocolo como defesa contra viés de publicação (análogo ao registro de ensaios). _(K04 §4.2)_
- [ ] Em experimentos formais, calcular o **tamanho mínimo de amostra** (poder ≥ 0,8). _(K02 D6)_
- [ ] Definir completamente os **tratamentos/intervenções** para permitir réplica. _(K02 D10)_
- [ ] Documentar o protocolo de pesquisa planejado e todos os desvios posteriores, para que outros entendam o desenho, interpretem resultados e repliquem. _(E08 Practical Considerations)_
- [ ] Fazer piloto do instrumento de coleta e do procedimento de análise (não só da coleta): muitos problemas só aparecem ao analisar dados, mesmo com amostra pequena. _(E08 §6)_
- [ ] Definir antecipadamente os testes/análises estatísticas, para planejar a análise e a interpretação. _(E08 Practical Considerations)_
- [ ] Em pesquisa com participantes, tratar de ética e consentimento e de permissão para publicar. [CONFERIR: não se aplica diretamente a RSL] _(E08 Practical Considerations)_
- [ ] Escrever e fechar um protocolo antes de iniciar a revisão para reduzir o viés do pesquisador (seleção e análise guiadas por expectativas). _(K07 §5.4)_
- [ ] Incluir no protocolo: contexto/justificativa, perguntas, estratégia de busca (termos e fontes), critérios de seleção, procedimentos de seleção, checklists/procedimentos de qualidade, estratégia de extração, estratégia de síntese, disseminação e cronograma. _(K07 §5.4)_
- [ ] Fazer o protocolo ser avaliado: independentes se houver recursos; doutorando deve apresentá-lo ao orientador para crítica. _(K07 §5.5)_
- [ ] Checar a consistência interna do protocolo: strings derivadas das perguntas, dados a extrair respondem às perguntas, análise adequada para responder. _(K07 §5.5)_
- [ ] Piloto do protocolo é essencial: encontra erros nos procedimentos de coleta e agregação e pode levar a mudar formulários, síntese ou o método. _(K07 §5.6)_
- [ ] Todos os membros da equipe devem participar da elaboração do protocolo, para entender a extração. _(K07 §5.6)_
- [ ] Testar na fase de protocolo cada passo da condução (busca, seleção, qualidade, extração). _(K07 §6)_
- [ ] Usar o protocolo da revisão terciária (Apêndice 3) como exemplo curto de estrutura: perguntas, fontes e responsáveis, critérios, seleção, qualidade, coleta, análise, disseminação. _(K07 App. 3)_
- [ ] Estruturar o processo em três etapas: planejar, conduzir e relatar o mapeamento; documentar no protocolo todas as decisões abaixo (estratégia de busca, critérios, extração, classificação, validade). _(P15 §5)_
- [ ] Usar o checklist de 26 ações (Tab. 8) como lista de opções: para cada ação, decidir "aplico/não aplico" e justificar, para que a escolha seja informada. _(P15 §5, Tab. 8)_
- [ ] Registrar informações em todas as etapas, de modo iterativo, usando planilhas e gerenciador de referências; o processo pode exigir revisões. _(P15 §5.2)_
- [ ] Fazer a revisão do protocolo e dos critérios entre os pesquisadores (no mapa do artigo, o protocolo de busca foi desenvolvido por dois autores e revisado por um terceiro). _(P15 §3.2, Fig. 17)_
- [ ] Preferir uma estrutura de relato padronizada para facilitar avaliação e comparação entre mapas. _(P15 §5.3)_
- [ ] Definir no protocolo o instrumento de qualidade: critérios, escala e como usará os escores, antes da extração. _(Z15 §3.4, §5.1–5.3)_
- [ ] Registrar a origem de cada critério (guia adaptado) e o número de critérios; o formulário de extração do próprio estudo trouxe: guia, critérios, número, propósito, aspecto. _(Z15 §3.4, Tab. 2)_
- [ ] Procurar revisões anteriores do mesmo tema e consultar/adaptar os critérios delas (três estudos o fizeram). _(Z15 §5.1)_
- [ ] Pré-definir o processo com dois revisores independentes e um terceiro para divergências (como no próprio estudo: pelo menos duas pessoas por estudo; divergências em discussão; não resolvidas ao supervisor). _(Z15 §3.2, §6)_
- [ ] Depois da leitura inicial dos artigos, rever e atualizar o protocolo da RSL, em especial a estratégia de extração e a estratégia de síntese. _(CD11 §II)_
- [ ] Inclua no protocolo, para cada tarefa assistida por IA, a estratégia básica de prompt, que deve exigir que a ferramenta devolva informação extra para você checar a validade da resposta (ex.: resposta a cada critério e trecho/página que a sustenta). _(G26 Ap. B.2.2(1) p.39; Ap. B.1.1 p.36)_
- [ ] Inclua um plano de gestão de dados: onde guardar prompts, saídas e versões do modelo; como rotular e guardar medidas de desempenho de humanos e IA; qual controle de qualidade será aplicado aos dados. _(G26 Ap. B.2.2(2) pp.39-40; Plan5 (Tab. 5 p.20))_
- [ ] Inclua procedimentos de privacidade de dados caso precise enviar PDFs, dados sensíveis ou informação de patente à IA sem permissões e salvaguardas. _(G26 Ap. B.2.2(3) p.40)_
- [ ] Descreva no protocolo como o teste/validação da IA será integrado à condução da RSL. _(G26 Ap. B.2.2(4) p.40)_
- [ ] Defina como monitorar erros e vieses da IA: rodar o prompt final duas vezes e checar consistência; comparar com pelo menos dois pesquisadores humanos; reportar matrizes de concordância; checar viés (ex.: estudos com autoras mulheres, nomes não europeus, opiniões minoritárias). _(G26 Ap. B.2.2(5) p.40; Plan4 (Tab. 5 p.20))_
- [ ] Defina o que fazer se detectar erro/viés da IA (em geral devolver a tarefa a outro pesquisador humano). _(G26 Ap. B.2.2(7) p.40)_
- [ ] Planeje que o desempenho da IA seja comparado com resultados de pelo menos dois pesquisadores humanos. _(G26 Plan6 (Tab. 5 p.20); Ap. B.2.1(2) p.39)_

### CUIDADO

- [ ] Usar desenhos **simples** ou bem documentados; consultar estatístico para desenhos novos ou complexos (aninhados, cross-over com efeito de aprendizado). _(K02 D4)_
- [ ] Evitar grupo-controle "sem técnica": só usar controle claramente definível; comparar contra prática atual é *baseline*, não controle. _(K02 D9)_
- [ ] Restrições práticas (tempo, orçamento, pessoas, acesso a dados) frequentemente obrigam a mudar método, coleta e análise; registrar essas mudanças. _(E08 Practical Considerations)_
- [ ] Protocolos podem ser longos; o tamanho depende da complexidade da busca, da extração e da análise. _(K07 §5.4)_
- [ ] Mais ações aumentam a confiabilidade, mas pode haver ponto de retorno baixo sobre o investimento; quais escores buscar na régua ainda é questão em aberto. _(P15 §5.4)_
- [ ] Poucas perguntas específicas do tema revisado; a maioria usa perguntas gerais sobre o estudo. Considerar acrescentar critério específico se necessário. _(Z15 §5.1)_

### RELATAR

- [ ] Se avaliar o próprio trabalho, declarar interesses e o que foi feito para minimizar viés; preferir avaliadores independentes. _(K02 D8)_
- [ ] Mudanças e desvios em relação ao protocolo original, com justificativa. _(K07 §7.4, Tab. 8)_

## F3 — Busca


### DECISÃO

- [ ] Bases de SE citadas: IEEE Xplore, ACM Digital Library (indexadas por autor e palavra-chave). Não há equivalente à Cochrane/Medline em SE. _(K04 §4.2)_
- [ ] Escolher bases (todas as relevantes) ou apenas **fóruns principais** da área (conferências/periódicos), justificando. _(P08 §2.2)_
- [ ] Escolher e justificar a estratégia de busca e o critério de completude. Se restringir a periódicos/anais específicos ou a um intervalo de anos (ex.: data do primeiro artigo sobre o tema), justificar. _(K07 §6.1.5)_
- [ ] Escolher as bibliotecas digitais; o texto lista IEEExplore, ACM DL, Google Scholar, CiteSeer, Inspec, ScienceDirect, EI Compendex, e cita SpringerLink e SCOPUS como possíveis adições. [CONFERIR: lista de 2007, desatualizada.] _(K07 §6.1.5)_
- [ ] Se houver poucos estudos no tema, considerar procurar em disciplinas relacionadas (ex.: sociologia, psicologia). _(K07 §6.1.1)_
- [ ] Considerar reaproveitar uma base de dados existente de um mapeamento prévio como fonte (exemplo BESTweb). _(K07 §6.1.5 (exemplo))_
- [ ] Escolher a estratégia de busca: busca em bases, busca manual (periódicos/eventos), snowballing; escolher uma ou um subconjunto, pesando tempo × visão geral. _(P15 §5.1.2, Fig. 6, Tab. 5)_
- [ ] Escolher as bases: IEEE e ACM mais duas bases de indexação (ex.: Inspec/Compendex e Scopus) é considerado suficiente na SE. _(P15 §5.1.2 (Dyba; Kitchenham & Brereton))_
- [ ] Definir o período e o recorte temporal e declará-lo (o mapa do artigo cobriu 2004–2012, buscando em 2013). _(P15 §3.2, §3.3)_
- [ ] Definir um critério de parada: ex., se uma busca complementar (manual/snowballing) não acrescenta N novos artigos além da busca em base, parar; ou fixar um orçamento de tempo e listar o que ficou de fora. _(P15 §5.1.2 (Petticrew & Roberts))_
- [ ] Escolher os venues de busca manual (aqui: EMSE, ESEM, EASE, TSE, IST, JSS) e justificar; a busca manual serve para construir o QGS, não para esgotar a literatura. _(Z15 §3.2)_
- [ ] Escolher bases e campos: IEEE Xplore, ACM DL, ScienceDirect e SpringerLink; busca em título, palavras-chave e resumo; período 2004–2013 (início marcado por EBSE e primeiras diretrizes, 2004). _(Z15 §3.2)_
- [ ] Se usar IA para montar a string de busca booleana (query), registre a ferramenta e prompt; a validação formal pode ser dispensada, mas você deve conferir o resultado contra a opinião da equipe e relatar. _(G26 Ap. B.2.1 p.38)_

### FAZER

- [ ] Estratégia em dois estágios: (1) procurar **revisões sistemáticas já publicadas**; (2) montar strings a partir da pergunta para estudos individuais. _(K04 §4.2)_
- [ ] Buscar o mais **completo** possível (para evitar viés), descrever o método de busca, justificá-lo (bases, periódicos, período) e discutir riscos. Exemplo de rigor citado: Jasperson et al. _(K04 §6)_
- [ ] Montar a string por **PICO** guiada pelas perguntas; palavras-chave de cada aspecto. _(P08 §2.2)_
- [ ] Desenvolver a estratégia de busca em consulta com bibliotecários ou pessoas experientes. _(K07 §6.1.1)_
- [ ] Fazer buscas preliminares para achar revisões existentes e estimar o volume de estudos. _(K07 §6.1.1)_
- [ ] Testar combinações de termos e checar as strings contra uma lista de estudos primários já conhecidos. _(K07 §6.1.1)_
- [ ] Consultar especialistas da área durante a definição da estratégia. _(K07 §6.1.1)_
- [ ] Decompor a pergunta em facetas (P, I, C, O, C, tipos de estudo), listar sinônimos, abreviações e grafias alternativas, usar termos de cabeçalhos de bases/periódicos e combinar com OR e AND. _(K07 §6.1.1)_
- [ ] Identificar pesquisadores específicos para contatar diretamente atrás de fontes e trabalhos não publicados. _(K07 §6.1.1)_
- [ ] Mitigar viés de publicação com varredura de literatura cinzenta e de anais de conferência e contato com especialistas sobre resultados não publicados. _(K07 §6.1.2)_
- [ ] Usar gerenciador de referências (ex.: EndNote, Reference Manager) e um sistema de registro para garantir a obtenção dos textos completos. _(K07 §6.1.3)_
- [ ] Documentar a busca à medida que ocorre, justificando mudanças, e guardar os resultados brutos (sem filtro) para reanálise. _(K07 §6.1.4)_
- [ ] Conferir as referências dos artigos relevantes e contatar os autores que publicaram no tema (técnicas dos exemplos). _(K07 §6.1.5 (exemplo))_
- [ ] Se usar snowballing, montar bem o conjunto inicial: artigos de grupos/comunidades que não se citam entre si; tamanho não pequeno; variedade de autores, anos e editoras; palavras-chave da pergunta como base. _(P15 §5.1.2 (Wohlin))_
- [ ] Desenvolver a busca a partir das perguntas, usando PICO(C); no mapa, P (população) e I (intervenção) são os mais relevantes; C, O e contexto podem restringir demais e eliminar artigos. _(P15 §3.2, §5.1.2)_
- [ ] Obter palavras-chave de artigos já conhecidos, de padrões (IEEE, ISO/IEC), do SWEBOK, de enciclopédias/tesauros; consultar bibliotecários/especialistas; melhorar a busca iterativamente. Pouco custosas e evitam retrabalho e ruído. _(P15 §5.1.2, Tab. 5, Fig. 7)_
- [ ] Avaliar a busca com conjunto-teste de artigos conhecidos (ex.: peça a um especialista ~10 artigos que devem ser encontrados; ou use páginas de pesquisadores-chave). Também: avaliação da busca por especialista e teste-reteste. _(P15 §5.1.2, Fig. 8, Tab. 8)_
- [ ] No mapa do artigo, validaram a busca com dois conjuntos: 8 artigos conhecidos e os 321 que citavam Petersen et al. (2008); a verificação achou só 4 artigos perdidos, sinal de que as conclusões não mudariam. _(P15 §3.3, §3.6.2)_
- [ ] Refletir sobre cobertura com perguntas: sub-áreas conhecidas estão cobertas? Os principais fóruns (específicos e gerais) estão representados? Há explicação para saltos no número de publicações por ano? Particionar a área pelo que se sabe (como no exemplo de Badampudi et al.). _(P15 §5.1.2, Fig. 16)_
- [ ] Considerar a estratégia Quasi-Gold Standard (QGS): busca manual em venues-chave para formar um padrão, depois busca automática avaliada por quasi-sensibilidade e quasi-precisão, e snowballing. _(Z15 §3.2)_
- [ ] Reaproveitar listas de estudos de revisões anteriores como ponto de partida (aqui: lista de Zhang et al. 2004–2010 + 96 SLRs de 2011–2013 achadas manualmente). _(Z15 §3.2, §4.1)_
- [ ] Calcular sensibilidade = relevantes recuperados / total de relevantes × 100%. A string revisada atingiu quasi-sensibilidade 85,6% e quasi-precisão 1,55%. _(Z15 §3.2)_
- [ ] Registrar a string usada (ex.: software AND (systematic/controlled/structured/… AND review/survey/map…) OR mapping study OR scoping study OR tertiary study OR meta-analysis), e adaptar à sintaxe de cada base. _(Z15 §3.2)_
- [ ] Complementar com snowballing: Google Scholar sobre quem cita os trabalhos seminais de EBSE e as duas versões do guia (assumindo que uma SLR de qualidade os cita). _(Z15 §3.2, Tab. 1)_

### CUIDADO

- [ ] **Viés de publicação:** resultados positivos são mais publicados e superestimam efeitos. _(K04 §4.2)_
- [ ] (Aplicação à RSL) O artigo não trata de busca; use-o para saber *que informações de desenho esperar encontrar* nos estudos recuperados (população, amostragem, tratamentos, desfechos). _(K02 (inferência, [CONFERIR]))_
- [ ] Sem itens: o capítulo não trata de busca bibliográfica. Os conceitos de amostragem (representativa x intencional/purposive, 5.2 e 5.3) podem inspirar a justificativa de por que a busca cobre ou não a população de estudos. [CONFERIR] _(E08 §5.2, §5.3)_
- [ ] Buscas muito restritivas por desenho de estudo enviesam o mapa. _(P08 §2.2)_
- [ ] Bibliotecas digitais sozinhas não bastam: complementar com listas de referências, periódicos (inclusive corporativos), literatura cinzenta, anais, registros de pesquisa e Internet. _(K07 §6.1.1)_
- [ ] Nenhuma fonte única encontra todos os estudos; é preciso pesquisar várias fontes eletrônicas. _(K07 §6.1.5)_
- [ ] Máquinas de busca em ES não foram feitas para RSL; haverá buscas dependentes de cada recurso (adaptar a string a cada base). _(K07 §6.1.5)_
- [ ] Viés de publicação: resultados positivos são mais publicados, especialmente em experimentos formais e quando a tecnologia é patrocinada por grupos influentes; sem medidas especiais a RSL fica enviesada. _(K07 §6.1.2)_
- [ ] Replicar buscas em bibliotecas digitais é quase impossível; a documentação deve permitir avaliar rigor e completude. _(K07 §2.4, §6.1.4)_
- [ ] Strings muito específicas geram muitos falsos positivos e strings enormes precisam de adaptação por base; uma string mais simples pode ser tão eficaz (lição dos exemplos). _(K07 §6.1.5 (exemplo))_
- [ ] Em 52 mapas, a busca em base foi a mais comum (todos usaram), seguida de manual (20) e snowballing (14); 23 estudos não usaram nenhum apoio adicional ao desenvolver a busca. _(P15 §4.4.2, §5.1.2, Tab. B.18)_
- [ ] Evidência indica que busca manual pode ser benéfica e até mais eficaz; um estudo achou que snowballing recuperou tudo que a busca em base achou — mas depende do contexto e do tema; não há recomendação de uma abordagem. _(P15 §5.1.2)_
- [ ] PICO(C) foi usado em só 11 estudos, embora o artigo o considere útil; as estratégias mais aplicadas foram PICO e palavras de artigos conhecidos. _(P15 §4.4.2, §5.1.2)_
- [ ] Equilibrar precisão e ruído: a busca do artigo trouxe 7752 resultados (IEEE 5610, ACM 360, Scopus 1215, Inspec/Compendex 567) com muito ruído; uma string mais enxuta teria dado resultado equivalente com bem menos esforço de seleção. _(P15 §3.2, Tab. 2, §5.1.2)_
- [ ] A estratégia mais usada para avaliar a busca foi o conjunto-teste; especialista, páginas de autores e teste-reteste apareceram em 1 estudo cada. _(P15 §4.4.2, Tab. B.20)_
- [ ] Meta é "boa amostra", não "todos os artigos": mais artigos não é necessariamente melhor se os menos forem mais representativos; a população é desconhecida e não dá para amostrar aleatoriamente. _(P15 §2.2, §5.1.2, §6)_
- [ ] Buscas combinadas (snowballing + busca por um pesquisador independente) acharam partições da população que a primeira estratégia deixou vazias; mesmo assim, não dá para dizer o quão representativa é a amostra. _(P15 §5.1.2, Fig. 16)_
- [ ] Mapas de terminologia: pode haver mapas nomeados "revisão sistemática"; há risco de descartá-los na seleção. _(P15 §3.6.2)_
- [ ] Régua de estratégia de busca: 30 de 52 mapas ficaram em "sem descrição" (só um tipo de busca), 12 em "mínima", 10 em "completa". _(P15 Tab. 10, Tab. 14)_
- [ ] A string antiga perdeu estudos (sobretudo mapeamentos): strings devem ser revalidadas quando muda o tipo de estudo/período. _(Z15 §3.2)_
- [ ] Mesmo com QGS, bases limitadas (quatro) podem perder estudos; usar snowballing como mitigação. _(Z15 §6)_
- [ ] Sem itens: o artigo não trata de busca (assume que identificação dos estudos já foi feita). Para busca usar outra fonte, como Kitchenham & Charters. _(CD11 §I)_
- [ ] No estudo citado de ChatGPT para queries, ganhos de precisão às vezes vinham com perda de recall; F1 baixo (<0,6); possível vazamento por refinar prompts na mesma tarefa; dependência de MeSH limita generalização. Não assuma que a query gerada pela IA é boa. _(G26 Ap. B.2.1 p.38)_

### RELATAR

- [ ] Para bibliotecas digitais: nome da base, estratégia/string usada, data da busca e anos cobertos (Tabela 2). _(K07 §6.1.4, Tab. 2)_
- [ ] Para busca manual em periódicos: nome, anos pesquisados e edições não pesquisadas. _(K07 §6.1.4, Tab. 2)_
- [ ] Para anais: título, nome da conferência (se diferente), tradução do título se necessário e periódico, se publicado em um. _(K07 §6.1.4, Tab. 2)_
- [ ] Para estudos não publicados: grupos e pesquisadores contatados (nomes e contatos), sites pesquisados (data e URL), data/URL e condições especiais da busca. _(K07 §6.1.4, Tab. 2)_
- [ ] Justificativa da escolha das bibliotecas, periódicos e anais, e da combinação de busca eletrônica e manual. _(K07 §6.1.4)_
- [ ] Apresentar as strings por base (e campos usados), o número de resultados por base, a ferramenta de deduplicação (EndNote) e o fluxo com contagens por etapa (Fig. 1). _(P15 §3.2, Tab. 1, Tab. 2, Fig. 1)_
- [ ] Descrever como a busca foi desenvolvida e avaliada (PICO, conjunto-teste, etc.), pois isso entra na pontuação de "avaliação da busca". _(P15 Tab. 11)_
- [ ] Resultados por base: número recuperado e selecionado (Tab. 3; IEEE 989/133, ACM 129/38, ScienceDirect 244/73, Springer 274/61). [CONFERIR: números por colunas vêm embaralhados no texto extraído; Total 1636/305 provável] _(Z15 §4.1, Tab. 3)_
- [ ] Documente a data de execução, base, strings e resultados da busca (prática exemplificada pelos autores em Tabelas 9-10). _(G26 Ap. A.4 pp.29-30; Tab. 9-10 p.32)_

## F4 — Seleção


### DECISÃO

- [ ] Duplicatas: contar só o mais recente quando vários artigos reportam o mesmo estudo; estudos múltiplos no mesmo artigo tratados separadamente. _(P08 Tab. 2)_
- [ ] Decidir se haverá exclusão por idioma (a medicina recomenda evitar; para ES pode importar menos) e registrar. _(K07 §6.2.1)_
- [ ] Decidir se avaliar os estudos com autores/instituição/periódico mascarados; o texto cita evidência de que mascarar não melhora a revisão e custa tempo. _(K07 §6.2.1)_
- [ ] Decidir se haverá um terceiro estágio de seleção com critérios detalhados de qualidade. _(K07 §6.2.2)_
- [ ] Para pesquisador único: discutir incluídos/excluídos com orientador ou painel, ou usar teste-reteste em amostra aleatória após a triagem. _(K07 §6.2.3)_
- [ ] No exemplo do protocolo terciário, selecionador único com checagem dos rejeitados por 2º pesquisador; opção válida de revisor único, justificar. _(K07 App. 3)_
- [ ] Em mapas, evitar o critério (d) "exigir avaliação empírica", para ver tendências recentes ainda sem maturidade para avaliação. _(P15 §5.1.2)_
- [ ] Escolher a regra de decisão: a mais inclusiva leva A–E à etapa seguinte e exclui só F (ambos excluem). Ela achou todos os relevantes, mas com 25% mais sobrecarga que A+B+C+D, que achou 94% dos relevantes. _(P15 §5.1.2 (Ali & Petersen))_
- [ ] Escolher o resolver de divergências: revisor adicional, reunião de consenso, regras de decisão, ou medir a objetividade dos critérios (pré num piloto ou pós-revisão). _(P15 §4.4.2, Fig. 9)_
- [ ] Se a avaliação de qualidade servir de seleção (P1), aplicá-la sobre o texto completo, depois da triagem inicial por título/resumo, com critérios mais específicos. _(Z15 §5.2)_
- [ ] ScrRev1: defina e justifique, ANTES da validação, o nível aceitável de desempenho da IA (ex.: taxa máxima aceitável de FN e custo relativo FN vs FP, conforme tipo de RSL e exigências dos interessados). _(G26 ScrRev1 (Tab. 6 p.21); Ap. C.1 p.43)_
- [ ] ScrRev2: tenha planos de contingência prontos para o caso de a validação mostrar desempenho insuficiente. _(G26 ScrRev2 (Tab. 6 p.21))_
- [ ] Após a validação, decida se a IA é boa o bastante, em custo e riscos de validade, para o resto da triagem ser feito por 1 humano + IA em vez de 2 humanos. _(G26 Ap. B.2.1 passo 10, p.39)_
- [ ] Se houver poucos estudos para uma validação realista (ex.: triagem de texto completo), use a IA como assistente adicional mantendo 2 humanos em cada decisão. _(G26 Ap. C.1 p.43)_

### FAZER

- [ ] Triar por título/resumo com inclusão/exclusão explícitas. _(P08 §2.3)_
- [ ] Definir os critérios de inclusão/exclusão no protocolo a partir da pergunta de pesquisa; só refinar depois com justificativa. _(K07 §6.2.1)_
- [ ] Pilotar os critérios em um subconjunto para checar se são interpretados de modo confiável e classificam corretamente. _(K07 §6.2.1, §5.4)_
- [ ] Aplicar a seleção em estágios: no início, interpretar critérios de modo liberal e só excluir por título/resumo o que for claramente fora; obter o texto completo dos demais. _(K07 §6.2.2)_
- [ ] Em seguida, aplicar critérios práticos: idioma, periódico, autores, cenário, participantes, desenho, amostragem, data. _(K07 §6.2.2)_
- [ ] Manter lista de excluídos com o motivo, mas só depois de descartar os totalmente irrelevantes (fora de ES); registrar os que caíram nos critérios detalhados. _(K07 §6.2.2)_
- [ ] Para a revisão com 2+ avaliadores, medir concordância com Kappa de Cohen, discutir e resolver cada discordância (voltando ao protocolo ou escrevendo aos autores). _(K07 §6.2.3)_
- [ ] Investigar com análise de sensibilidade as inclusões/exclusões incertas. _(K07 §6.2.3)_
- [ ] Em duplicatas (mesma RSL/dado em várias publicações), usar a versão mais completa. _(K07 §6.4.4, App. 3)_
- [ ] Definir critérios de inclusão/exclusão objetivos: (a) relevância do tema, (b) tipo de veículo, (c) período, (d) exigência de avaliação, (e) idioma. _(P15 §5.1.2)_
- [ ] Exemplos de critérios: artigos revisados por pares em inglês até data X; foco no tema; contexto/objetivos/método minimamente presentes. Exclusões: fora do tema, sem revisão por pares, não inglês, sem texto completo, livros/literatura cinzenta, duplicados. _(P15 §3.3, §5.1.2)_
- [ ] Seguir o processo da Fig. 17: especificar critérios no protocolo → revisar entre pesquisadores → aplicar em voz alta (think-aloud) em um estudo → piloto num subconjunto → calcular concordância → ajustar critérios → selecionar → calcular concordância → aplicar regras de decisão. _(P15 §5.1.2, Fig. 17)_
- [ ] Em título/resumo, cada revisor classifica como incluir/excluir/incerto; combinar R1 e R2 nos casos A–F (Tab. 6) e definir regra para cada caso. _(P15 §5.1.2, Tab. 6)_
- [ ] Listar no apêndice os artigos incluídos e os limítrofes excluídos. _(P15 §5.3, App. A)_
- [ ] Definir critérios de inclusão: título/resumo declara tipo de revisão sistemática; área SE; revisado por pares; artigo completo/regular; contém avaliação de qualidade; texto acessível. _(Z15 §3.3)_
- [ ] Definir critérios de exclusão: não inglês; sem texto completo; literatura cinzenta sem revisão por pares; artigo curto ou com menos de seis páginas. _(Z15 §3.3)_
- [ ] Regra de seleção: incluir se atende a todos os critérios de inclusão; eliminar se atende a qualquer exclusão. _(Z15 §3.3)_
- [ ] Cada estudo checado por ao menos dois pesquisadores independentes; divergência resolvida em discussão e depois por especialista. _(Z15 §3.2, §6)_
- [ ] Registrar o processo de seleção em duas partes (título e resumo; depois leitura completa), como no exemplo de Staples & Niazi citado pelo artigo. [CONFERIR: é só um exemplo citado, não uma regra do artigo] _(CD11 §II)_
- [ ] Scr1: use o coeficiente de correlação de Matthews (MCC) para garantir que o resultado é melhor que o acaso (valores perto de zero = desempenho próximo do acaso). _(G26 Scr1 (Tab. 6 p.21); Ap. C.1 p.42)_
- [ ] Scr2: use o MCC ponderado (WMCC) para refletir que FN custa muito mais que FP; alternativamente, faça uma análise de custo-benefício com a razão de custo FP:FN. _(G26 Scr2 (Tab. 6 p.21); Ap. C.1 p.42)_
- [ ] Scr3: reporte a matriz de confusão completa (VP, FP, FN, VN) para permitir reanálise e meta-análise; com ela se calcula recall e evidência perdida (1 - Recall). _(G26 Scr3 (Tab. 6 p.21); Tab. 3 p.18)_
- [ ] ScrRev3: calcule e reporte intervalos de confiança das métricas escolhidas, por reamostragem sem reposição, para mostrar a variabilidade da estimativa. [CONFERIR: detalhes do procedimento (nº de repetições, método de IC) estão no estudo companheiro [61].] _(G26 ScrRev3 (Tab. 6 p.21); Ap. C.1 p.43)_
- [ ] Valide a IA numa amostra aleatória: dois humanos independentes decidem, discutem e resolvem discordâncias; a IA recebe os mesmos itens; compare humano-humano, humano-IA e IA-decisão consensual. _(G26 Ap. B.2.1 passos 1-3, 9, p.38-39)_
- [ ] Rode o prompt final pelo menos duas vezes para medir consistência da IA; marque os itens com resposta inconsistente como "requer avaliação adicional" e NÃO os exclua da análise de desempenho. _(G26 Ap. B.2.1 passos 7-8, p.39 e nota 12)_
- [ ] Meça esforço, tempo decorrido e todos os custos da IA (incluindo tempo humano de engenharia de prompt) para avaliar eficiência, além da eficácia. _(G26 Ap. B.2.1 passo 6, p.39)_
- [ ] Se adotar a IA, especifique mecanismos de supervisão humana. _(G26 Ap. C.1 p.43)_
- [ ] Exija que a IA devolva a resposta para cada critério de elegibilidade e o trecho/página que a sustenta, para investigar discordâncias humano-IA. _(G26 Ap. B.1.1 p.36)_

### CUIDADO

- [ ] Ao excluir estudos por "falta de dados" ou desistências, considere o impacto: quem não coletou dados pode ser sistematicamente diferente. _(K02 I4)_
- [ ] Sem itens: o capítulo não trata de seleção de estudos. [CONFERIR] Analogia: critérios devem estar ligados à proposição do estudo (como a seleção de casos no estudo de caso, §5.2). _(E08 §5.2)_
- [ ] Excluir artigos que citam o tema só em frases introdutórias do resumo (testado em protótipo, sem erros de classificação no estudo deles). _(P08 §2.3)_
- [ ] Resumos em ES são fracos; olhar também as conclusões antes de decidir. _(K07 §6.2.2)_
- [ ] A abordagem mais comum é resolver desacordos com revisor adicional/consenso; regras de decisão só em 4 estudos e medição de objetividade em 8. _(P15 §4.4.2, Tab. B.21)_
- [ ] Seleção por um único revisor é ameaça à confiabilidade; se há muito ruído óbvio, pode-se triar individualmente, mas na dúvida levar o artigo ao texto completo (postura inclusiva). _(P15 §3.3, §3.6.2)_
- [ ] Artigos limítrofes incluídos no título/resumo e excluídos depois podem merecer revisão: no mapa, a revisão dos excluídos recuperou 8 estudos. _(P15 §3.3, Fig. 1)_
- [ ] Contagens do fluxo parecem inconsistentes entre texto e figura (46+11=57 no texto; 54/44/52 na Fig. 1). [CONFERIR] ao replicar o modelo de fluxo. _(P15 §3.3, Fig. 1)_
- [ ] Excluir artigos de menos de seis páginas tem justificativa (pouco detalhe de procedimento, em especial de qualidade), mas pode eliminar relatos curtos relevantes. _(Z15 §3.3)_
- [ ] Duplicatas (e estudos do mesmo autor publicados em partes de outros artigos) distorcem contagens; dois pesquisadores devem checar. _(Z15 §6)_
- [ ] Triagem tem muito desbalanceamento de classes (poucos relevantes entre milhares): acurácia, especificidade e F1 enganam; um LLM pode ter mais de 96% de acurácia e não detectar nenhum estudo relevante. _(G26 §4.3 p.17; Tab. 3 p.18)_
- [ ] A escolha da métrica muda quanta evidência você perde: no exemplo de 9.695 artigos, o melhor LLM por acurácia perdeu 63,3% dos relevantes, por MCC simples 43,9% e por WMCC 5,8%. _(G26 §4.3 p.17)_
- [ ] [CONFERIR] A fórmula do WMCC e o peso FN:FP NÃO estão neste paper; vêm do estudo companheiro [61] (Madeyski et al.). Consulte-o antes de calcular. _(G26 §4.3 p.17; §4.4.2 p.19)_
- [ ] Em RSL formal, a triagem tradicional exige 2 humanos independentes e resolução de conflitos; mapeamentos/escopo/revisões rápidas costumam enfraquecer isso. Declare qual nível sua tese adota. _(G26 Ap. C.1 p.42)_

### RELATAR

- [ ] O valor inicial do Kappa (antes da resolução das discordâncias) no relatório final. _(K07 §6.2.3)_
- [ ] Critérios de inclusão e exclusão e a lista de excluídos com justificativa; usar fluxograma, pois estudos saem em etapas diferentes por motivos diferentes. _(K07 Tab. 8)_
- [ ] Contagens por fonte e ano: artigos encontrados, candidatos e selecionados. [CONFERIR: tabela de resultados do protocolo do Apêndice 3, adaptável.] _(K07 App. 3)_
- [ ] Reportar critérios, número de revisores, método de resolução de divergências e concordância, e o fluxo de contagens (busca → datas → critérios → texto completo → snowball → qualidade → revisão dos excluídos). _(P15 §3.3, Fig. 1)_
- [ ] Fluxo de seleção: 260 por snowballing; ao final 127 SLRs com avaliação; 110 com critérios explícitos (75 SLRs + 35 mapeamentos); 17 sem critérios. _(Z15 §4.1)_
- [ ] Reporte o fluxo de triagem e as decisões de exclusão, seguindo PRISMA 2020 ou SEGRESS, incluindo o papel da IA em cada passo. _(G26 RepR1 (Tab. 5 p.20); Tab. 4 p.19)_

## F5 — Avaliação de qualidade


### DECISÃO

- [ ] Em mapa, estudos normalmente **não** têm qualidade avaliada; decidir e justificar isso no protocolo. _(P08 §3.2)_
- [ ] Definir o que "qualidade" significa na revisão: até que ponto o estudo minimiza viés e maximiza validade interna e externa (Tabela 3). _(K07 §6.3, Tab. 3)_
- [ ] Definir os propósitos da avaliação de qualidade: critério de inclusão detalhado, explicar diferenças de resultados, ponderar estudos na síntese, guiar interpretação, guiar recomendações para pesquisa futura. _(K07 §6.3)_
- [ ] Decidir se a hierarquia de evidência (RCT no topo, opinião de especialista na base) será usada para restringir estudos. _(K07 §6.3.1)_
- [ ] Selecionar da Tabela 5 apenas as perguntas pertinentes ao seu estudo (ninguém deve usar todas) e definir escalas quando Sim/Não for enganoso. _(K07 §6.3.2, Tab. 5)_
- [ ] Especificar no protocolo como os dados de qualidade serão usados: (1) para seleção (coletar antes, em formulário separado) ou (2) para análise/síntese (coletar junto com a extração, formulário conjunto), ou ambos. _(K07 §6.3.3)_
- [ ] Pode-se justificar não fazer avaliação de qualidade, como Jørgensen; registrar a decisão e o motivo. [CONFERIR: o texto só observa que ele não fez.] _(K07 §6.3.2 (exemplo))_
- [ ] Se for revisão de revisões, o Apêndice 3 usa DARE (Y=1, P=0,5, N=0) com 4 perguntas; adaptar conforme o tipo de estudo. _(K07 App. 3)_
- [ ] Decidir se haverá avaliação de qualidade no mapa e justificar: em mapas ela é opcional, e só 14 dos 52 mapas avaliaram qualidade. _(P15 §2.1, §4.4.3, Fig. 10)_
- [ ] Escolher a escala de pontuação: binária (sim=1, não=0) ou três pontos (sim=1; parcialmente=0,5; não=0). A de três pontos é mais informativa; binária é fraca por não captar o intermediário. _(Z15 §5.2)_
- [ ] Considerar pesos diferentes para critérios mais importantes (um estudo o fez). _(Z15 §5.2)_
- [ ] Decidir se avalia a qualidade metodológica dos estudos primários: apenas 14% das revisões em ES faziam isso e nenhuma síntese temática usou avaliação de qualidade para julgar confiabilidade. O tema ainda é debatido. _(CD11 §VI, §VII)_
- [ ] Verifique se sua RSL realmente precisa de avaliação de risco de viés (RoB): é essencial para RSL quantitativa/qualitativa que gera recomendações, desnecessária para mapeamento/escopo e opcional em revisão rápida. _(G26 Ap. C.3 p.45)_
- [ ] A1: se usar IA nesta etapa, defina quais sub-tarefas serão automatizadas (ex.: destacar trechos, sugerir resposta a critério). _(G26 A1 (Tab. 6 p.21))_
- [ ] A2: defina quais informações servem de entrada para cada sub-tarefa e como são obtidas. _(G26 A2 (Tab. 6 p.21))_
- [ ] A3: especifique como a avaliação da IA será comparada com a dos humanos e como o desempenho relativo será medido. _(G26 A3 (Tab. 6 p.21))_
- [ ] Para um piloto prospectivo, aplique a IA várias vezes ao mesmo estudo com o mesmo prompt e meça a taxa de discordância; alta discordância humano-IA indica valor limitado da ferramenta. _(G26 Ap. C.3.3 p.48)_
- [ ] Força da evidência (SoE) é necessária em RSL quantitativa/qualitativa (e útil em revisão rápida), mas não costuma ser relevante em mapeamento/escopo. _(G26 Ap. C.5 p.51)_
- [ ] Em SoE, restrinja a IA a: (a) organizar a informação por achado e extrair contexto adicional; (b) servir como avaliador independente adicional (reduz viés de quem também conduziu a RSL). Duas pessoas ainda devem fazer a avaliação principal. _(G26 Ap. C.5 p.52)_

### FAZER

- [ ] Avaliar criticamente cada estudo em **validade, impacto (tamanho do efeito) e aplicabilidade**. _(K04 §4, Tab. 1 passo 3)_
- [ ] Considerar a **força da evidência** em três elementos: nível (desenho), qualidade (métodos para minimizar viés) e precisão estatística; mais **tamanho do efeito** e **relevância**. _(K04 §5.1.2)_
- [ ] Usar as áreas de K02 (contexto, desenho, condução, análise, apresentação, interpretação) como **lente de qualidade** de estudos primários: o estudo define população? hipótese? tratamentos? medidas? ameaças à validade? _(K02 §1–7)_
- [ ] [CONFERIR] Ao avaliar estudos primários, aplicar critérios de validade coerentes com a postura de cada estudo (positivista: 4 validades; construtivista: credibilidade etc.; crítica: utilidade/autenticidade). _(E08 §7)_
- [ ] [CONFERIR] Conferir se cada estudo primário declara ameaças à validade; é prática esperada em estudos positivistas. _(E08 §7)_
- [ ] Para estudos observacionais, verificar se controlaram confundidores e fizeram análise de sensibilidade de confundidores medidos e não medidos. _(K07 §6.3.1)_
- [ ] Montar o instrumento de qualidade (checklist) a partir dos vieses (seleção, desempenho, medição, atrito; Tabela 4), de itens genéricos por desenho e itens específicos do tema, e por estágio (desenho, condução, análise, conclusões). _(K07 §6.3.2, Tab. 4)_
- [ ] Usar a Tabela 5 (quantitativos: design, condução, análise, conclusões, por tipo: correlação, survey, experimento) e a Tabela 6 (18 itens para qualitativos: credibilidade, aderência a objetivos, defensabilidade do desenho, amostra, coleta, análise, ligação dados–conclusões, ética, documentação). _(K07 §6.3.2, Tab. 5, Tab. 6)_
- [ ] Avaliar a confiabilidade e a usabilidade do instrumento durante o piloto, antes de aplicá-lo a todos os estudos. _(K07 §6.3.2)_
- [ ] Usar instrumentos diferentes para tipos de estudo diferentes; qualitativos e quantitativos exigem checklists distintos. _(K07 §6.3.3)_
- [ ] Quando útil, usar a avaliação para garantir que haja informação suficiente para extrair (ex.: no próprio estudo, o processo de mapeamento precisava estar documentado). _(P15 §5.1.2)_
- [ ] Exemplo de 3 perguntas de qualidade: motivação clara? processo claramente definido (identificação, extração, classificação)? há evidência empírica/resultados apresentados? _(P15 §3.3)_
- [ ] Usar a rubrica (Tab. 9–13) para avaliar o próprio mapa ou mapas de terceiros: necessidade (0–2), estratégia de busca (0–2), avaliação da busca (0–3), extração/classificação (0–3), validade (0–1). _(P15 §5.4, Tab. 9–13)_
- [ ] Calcular a razão ações realizadas / 26 ações totais (31% no mapa do artigo); mediana nos 52 estudos foi 33% e 25% passaram de 40%. _(P15 §5.4, Fig. 20)_
- [ ] Estruturar os critérios nos quatro aspectos de Dybå & Dingsøyr: Reporting (relato), Rigor, Credibility (credibilidade) e Relevance (relevância). _(Z15 §5.3)_
- [ ] Entender cada aspecto: Reporting = qualidade do relato de motivação, objetivos e contexto (limiar mínimo, exclui não empíricos); Rigor = rigor de coleta e análise de dados; Credibility = se achados são válidos e significativos; Relevance = valor para indústria e pesquisa. _(Z15 §5.3)_
- [ ] Usar o checklist de 11 critérios de Dybå & Dingsøyr (3 relato, 5 rigor, 2 credibilidade, 1 relevância) como base; foi o mais citado (26 estudos); sete o adotaram inteiro e seis em parte. _(Z15 §5.1, §5.3, Tab. 4)_
- [ ] Critérios de Reporting mais usados: objetivo claramente declarado (54); descrição adequada do contexto (46); é baseado em pesquisa (25). _(Z15 Tab. 6)_
- [ ] Critérios de Rigor mais usados: métricas/método/desenho definidos (21); validados/justificados (19); análise de dados suficientemente rigorosa (18); grupo de controle (16); coleta descrita (16); coleta adequada à questão (16); desenho adequado aos objetivos (14); recrutamento adequado (11); análise descrita e justificada (11). _(Z15 Tab. 6)_
- [ ] Critérios de Credibilidade mais usados: declaração clara dos achados ligada aos objetivos (37); discussão de limitações/ameaças à validade (23); relação pesquisador–participantes considerada (12); replicável (7); dados suficientes para sustentar os achados (5). _(Z15 Tab. 6)_
- [ ] Critérios de Relevância: estudo tem valor para pesquisa ou prática (15); conclusões e implicações apropriadas ao público (6); abordagem validada em certa escala (2). _(Z15 Tab. 6)_
- [ ] Usar os escores conforme o propósito: P1 limiar para incluir/excluir; P3 pesos na síntese; P4 interpretar a confiança nas conclusões; P5 apontar lacunas/recomendações. _(Z15 §5.2)_
- [ ] Registrar a força da evidência (strength of evidence) de cada achado no modelo de extração. _(CD11 Fig. 2)_
- [ ] RevA1: restrinja o uso da IA a uma validação adicional do que os humanos fazem (a IA é "um par de olhos extra"), sem substituir os humanos na avaliação de RoB. _(G26 RevA1 (Tab. 6 p.21); Ap. C.6 p.53)_
- [ ] RevA2: humanos revisam toda saída da IA e assumem responsabilidade plena pelo uso. _(G26 RevA2 (Tab. 6 p.21))_
- [ ] Valide o instrumento de qualidade antes de usar: ao menos dois pesquisadores aplicam-no independentemente a poucos estudos sorteados e discutem divergências; só então avalie incluir a IA. _(G26 Ap. C.3.2 pp.47-48)_
- [ ] Mantenha 2 ou mais humanos avaliando cada estudo; decida se avaliam de forma independente ou em conjunto e se o processo ocorre em lotes (tranches). _(G26 Ap. C.3.3 p.48)_
- [ ] Formalize como combinar as respostas do instrumento num nível de RoB: RoB não é aditivo; um critério de alto risco já classifica o estudo como alto risco. Escala do exemplo: Crítico, Alto, Moderado, Baixo. _(G26 Ap. C.3 (item 4) p.46; C.3.4 p.48)_
- [ ] Avalie a força de cada achado com os 7 critérios do exemplo: limitações metodológicas, método de síntese, condução da síntese, coerência, adequação dos dados, relevância prática e risco de viés de publicação; use escala por critério (sem problema sério, problema menor, problema sério). _(G26 Ap. C.5 pp.51-52)_
- [ ] Combine critérios na escala geral: Forte (sem problemas sérios), Média (no máximo 1 problema sério), Baixa (2-3), Muito baixa (4 ou mais). [CONFERIR: os autores apresentam como exemplo de escala, não como obrigatória.] _(G26 Ap. C.5 p.52)_
- [ ] Reporte as tabelas completas de força da evidência de cada achado (recomendação citada de Lewin et al., 2018). _(G26 Ap. C.5 p.51)_

### CUIDADO

- [ ] Um único estudo, mesmo rigoroso, não basta; acumular evidência de vários estudos independentes. _(K04 §4.3)_
- [ ] Em SE, experimentos são mais vulneráveis a viés; considerá-los "menos rigorosos que ensaios médicos" e qualificá-los. _(K04 §5.1)_
- [ ] Sinais de baixa qualidade: população indefinida, hipótese rasa, testes múltiplos sem ajuste, p-valor sem tamanho de efeito, dados brutos ausentes, conclusões além dos resultados. _(K02 C2, D1, A1, P3, P4, §7.1)_
- [ ] Qualidade do estudo ≠ qualidade do relato; um estudo mal relatado pode ter sido bem conduzido. _(K02 §1 (relacionar com K07 §6.3.2))_
- [ ] Variabilidade enorme no estilo e na qualidade dos relatos empíricos dificulta comparar e agregar estudos (meta-análise). _(E08 Conclusões)_
- [ ] "Estudo de caso" em ES é frequentemente apenas um exemplo trabalhado (worked example), não um estudo de caso empírico; ao classificar métodos dos estudos primários, não aceitar o rótulo sem verificar. _(E08 §5.2)_
- [ ] Experimento com estudantes reduz validade externa; considerar ao avaliar/ponderar estudos primários. [CONFERIR: aplicação à RSL é adaptação] _(E08 §5.1)_
- [ ] A hierarquia simples é criticada: certos desenhos respondem melhor a certos tipos de pergunta (ex.: estudos qualitativos para aceitação por praticantes). Restringir aos desenhos mais adequados à pergunta. _(K07 §6.3.1)_
- [ ] Estudos observacionais/correlacionais podem ser enganosos por confundidores (exemplo da vitamina C); em ES isso afeta estimativa de custo e fatores de sucesso. _(K07 §6.3.1)_
- [ ] Cegamento, usado na medicina contra viés de desempenho/medição, quase nunca é possível em ES; os mecanismos de proteção foram adaptados na Tabela 4. _(K07 §6.3.2)_
- [ ] Ponderar resultados de meta-análise por escores de qualidade não é recomendado por nenhuma diretriz médica. _(K07 §6.3.3)_
- [ ] Não somar qualidade do estudo e qualidade do relato num único escore; se somar, dar menos peso ao relato (exemplo). _(K07 §6.3.2 (exemplo))_
- [ ] Não presumir que o que não foi relatado não foi feito; tentar contatar os autores. _(K07 §6.3.4)_
- [ ] O checklist deve medir qualidade metodológica, não qualidade de relato. _(K07 §6.3.4)_
- [ ] Há pouca evidência empírica de que a maioria dos fatores de qualidade afeta os resultados; só alocação sem ocultação e ausência de duplo cego mostram superestimar efeitos. _(K07 §6.3.4)_
- [ ] Análises estatísticas inadequadas podem ser identificadas, mas sem os dados originais (frequentemente confidenciais) não podem ser corrigidas. _(K07 §6.3.4)_
- [ ] Em RSL o foco seria avaliar a qualidade dos estudos (abordagens de Kitchenham & Brereton); em mapa a exigência deve ser baixa, pois a meta é visão ampla. _(P15 §5.1.2)_
- [ ] A avaliação de qualidade do próprio artigo foi feita por uma só pessoa. _(P15 §3.3)_
- [ ] A pontuação é com base no que foi relatado; autores que preenchem a própria rubrica percebem o que esqueceram de relatar. _(P15 §5.4)_
- [ ] Distribuição (Tab. 14): necessidade — 52 "completa"; busca — 30 sem descrição/12 mínima/10 completa; avaliação da busca — 23/22/7/0; extração — 5/32/15/0; validade — 7 sem descrição/45 completa. _(P15 Tab. 14)_
- [ ] Mediana de cumprimento é maior em periódicos do que em conferências, possivelmente por espaço de relato. _(P15 §5.5, Fig. 21)_
- [ ] Cobertura por aspecto: Rigor 80%, Reporting 61%, Credibility 56%, Relevance 25%; média de critérios por revisão 3,82, 2,75, 2,84 e 1,22; relevância quase sempre com um único critério. _(Z15 §5.3, Fig. 5, Fig. 6)_
- [ ] Relevância é negligenciada embora seja ponto forte do EBSE; credibilidade também recebe pouca atenção em vários instrumentos. Os autores recomendam dar mais atenção a credibilidade e relevância. _(Z15 §5.3, §5.4, §7)_
- [ ] Checklists longos (31 e 19 critérios) cobriram relato/rigor/credibilidade e ignoraram relevância; checklists com ≤5 critérios podem focar só 1 ou 2 aspectos. _(Z15 §5.3)_
- [ ] Mapeamentos e RSLs avaliam aspectos em padrão parecido: RSL 57/79/53/24% e MS 69/80/63/26% (Reporting/Rigor/Credibility/Relevance). [CONFERIR: atribuição das séries da Fig. 8 deduzida da proporção com n=75 e n=35] _(Z15 §5.3, Fig. 7, Fig. 8)_
- [ ] Todas as escalas só somam pontos; nenhuma deduz pontos (ex.: −1) por fatores como inconsistência dos resultados, ao contrário do GRADE. _(Z15 §5.4)_
- [ ] A maioria dos estudos adaptou o CASP sem usar todos os critérios e a maior parte dos instrumentos em SE é qualitativa/observacional, diferente de outras áreas. _(Z15 §5.4)_
- [ ] Estudos de baixa qualidade metodológica incluídos na revisão reduzem a confiabilidade da síntese; a confiabilidade depende da qualidade e da quantidade das evidências e da ponderação por qualidade. _(CD11 §VI)_
- [ ] Muitos artigos de ES descrevem mal desenho, métodos, amostra, ameaças à validade; registrar essas lacunas, pois elas atrapalham a extração e afetam a confiança nos achados. _(CD11 §II)_
- [ ] A evidência empírica de IA para RoB/força da evidência em estudos de engenharia de software é escassa e contraditória; os itens do paper são preliminares. _(G26 §4.3 p.17; §7 p.26)_
- [ ] Dois estudos com RCTs deram resultados opostos: um achou LLMs raramente melhores que baselines triviais, outro achou "acurácia e consistência substanciais"; diferem em instrumentos, estudos, modelos e prompts. _(G26 Ap. C.3.1 p.46; §7 p.27)_
- [ ] A precisão da IA caiu quando o instrumento exigia mais julgamento subjetivo; instrumentos de RoB para SE costumam ser subjetivos. _(G26 Ap. C.3.1 p.47)_
- [ ] Em SE, rótulos de tipo de estudo e análises estatísticas nem sempre estão corretos, e publicar em periódico bom não garante baixo risco de viés; não confie só no método declarado pelos autores (nem a IA). _(G26 Ap. C.3.1 p.47)_
- [ ] O paper NÃO considera viável hoje usar IA para gerar o instrumento de avaliação de qualidade de uma RSL específica. _(G26 Ap. C.3.1 p.47)_
- [ ] SoE é avaliada sobre um conjunto de estudos e exige conhecimento fora de qualquer artigo individual (ex.: experimentos de laboratório bons, mas com estudantes e tarefas simples, podem não generalizar). Há poucos achados por RSL, então talvez o esforço de treinar e validar a IA não compense. _(G26 §4.2 p.16; Ap. C.5 p.52)_

### RELATAR

- [ ] Estudo de qualidade: critérios, instrumento, como foi aplicado, como os escores entram na análise (exemplo: associação entre escore e resultado). _(K07 §6.3.3, Tab. 8)_
- [ ] Registrar o instrumento completo (lista de critérios, escala, limiar, pesos) e os escores por estudo; 17 estudos não o fizeram. _(Z15 §4.1, §5)_
- [ ] Declarar o propósito da avaliação e como os escores influenciaram seleção/síntese/interpretação. _(Z15 §5.2, §7)_

## F6 — Extração e classificação


### DECISÃO

- [ ] Definir **medidas de desfecho relevantes** para praticantes. _(K04 §4)_
- [ ] Medidas definidas com entidade, atributo, unidade e regras de contagem; se subjetivas, registrar **concordância entre avaliadores** (kappa; ICC se contínuo). _(K02 DC1, DC2)_
- [ ] [CONFERIR] Para classificar os estudos primários, usar como atributos: tipo de pergunta, método empírico (experimento, caso, survey, etnografia, pesquisa-ação, misto), postura, unidade de análise, técnica de coleta. _(E08 §2-§6)_
- [ ] Escolher técnicas de coleta compatíveis com a unidade de análise; combinar várias técnicas para triangular mesmo dentro de um método, e considerar vantagens/desvantagens para pesquisador e participantes, generalização e confiabilidade. _(E08 §6)_
- [ ] Definir **facetas** (ex.: tópico, tipo de contribuição, tipo de pesquisa). _(P08 §2.4)_
- [ ] Usar classificação de tipo de pesquisa (Wieringa): validação, avaliação, proposta de solução, filosófico, opinião, experiência; inclui categorias não empíricas. _(P08 Tab. 3, §4)_
- [ ] Se a qualidade for usada para selecionar, usar formulário separado e anterior; se for usada na análise, pode ser formulário único. _(K07 §6.4.1)_
- [ ] Definir os itens de extração a partir da pergunta (ex.: fatores de desenho do estudo e resultados, como em Jørgensen). _(K07 §6.4.2 (exemplo))_
- [ ] Para pesquisador único: orientador extrai amostra aleatória para checagem cruzada, ou teste-reteste (reextrair amostra), ou enviar dados extraídos aos autores para confirmar (exemplo de Jørgensen). _(K07 §6.4.3)_
- [ ] Incluir estudos em andamento só se houver informação de qualidade e permissão escrita dos autores. _(K07 §6.4.5)_
- [ ] No mapeamento, a extração vira classificação/categorização: classificar com detalhe suficiente para responder perguntas amplas e identificar estudos para revisões futuras, sem ser demorado. _(K07 §8)_
- [ ] Escolher como tratar o viés na extração: segundo pesquisador confere (rastreando a informação até o artigo) ou extrai de forma independente, com reunião de consenso se preciso; medir a objetividade dos critérios num piloto e/ou depois. _(P15 §3.4, §5.1.3, Fig. 11)_
- [ ] Escolher se calcula concordância na classificação: mapas permitem isso porque os artigos são distribuídos em categorias; ponderar disponibilidade dos resultados × confiabilidade (checagem por outra pessoa já ajuda). _(P15 §5.1.3)_
- [ ] Classificação por tópico: partir de uma classificação existente (SWEBOK, padrões IEEE/ISO) e consultar especialistas antes; senão, criar esquema emergente por palavras-chave. A maioria dos mapas criou esquemas novos. _(P15 §5.1.3, Fig. 13)_
- [ ] Pode-se combinar avaliação de qualidade e extração de dados em um único passo (um estudo usou perguntas abertas para isso). _(Z15 §5.1)_
- [ ] Escolher a abordagem de codificação: dedutiva (lista inicial vinda de teoria/RQs, tipicamente de uma dúzia até 30-40 códigos), indutiva (código surge dos dados, comparação constante) ou integrada (estrutura dedutiva de domínios + códigos indutivos). _(CD11 §III)_
- [ ] Escolher tipos de código úteis: conceituais, de relação (ligações entre conceitos), de sujeito (percepções dos participantes) e de características de contexto. _(CD11 §III)_
- [ ] Ext3: NÃO use WMCC na extração/classificação, a menos que você justifique custos diferentes para tipos de erro. (Diferente da triagem, em que se usa WMCC.) _(G26 Ext3 (Tab. 6 p.21); Ap. C.2.3 p.45)_

### FAZER

- [ ] Extrair, por estudo: contexto, população/amostragem, tratamentos, medidas e suas definições, tipo de estudo, tamanho amostral, taxa de resposta/desistências, método estatístico. _(K02 C1, D1–D11, DC1–DC6)_
- [ ] Descrever controles de qualidade da coleta de dados. _(K02 DC3)_
- [ ] Experimento: investigação de hipótese testável em que se manipulam variáveis independentes e se mede o efeito sobre dependentes; busca relação causa-efeito; exige hipótese clara derivada de teoria. _(E08 §5.1)_
- [ ] Quase-experimento: sem atribuição aleatória; série temporal: efeito medido em passos ao longo do tempo; menos poderosos e exigem interpretação cuidadosa. _(E08 §5.1)_
- [ ] Estudo de caso: investiga fenômeno contemporâneo em seu contexto real, quando as fronteiras entre fenômeno e contexto não são claras; responde "como/por que"; exploratório (gera hipóteses) ou confirmatório (testa teoria). _(E08 §5.2)_
- [ ] Estudo de caso exige questão "como/por que", proposição de estudo, amostragem intencional (caso crítico, extremo, típico), múltiplos casos como replicações (literais ou teóricas) e unidade de análise definida. _(E08 §5.2)_
- [ ] Survey: caracteriza uma população ampla via amostra representativa de população bem definida, geralmente para perguntas de taxa-base; planos transversal, caso-controle ou coorte. _(E08 §5.3)_
- [ ] Etnografia: estuda uma comunidade para entender como seus membros dão sentido às interações; evita teorias prévias; resultado é descrição rica; inclui observação participante; amostragem em cadeia. _(E08 §5.4)_
- [ ] Pesquisa-ação: o pesquisador intervém para resolver problema real e estuda a experiência; exige dono do problema colaborador, reflexão crítica, mudança real e abordagem iterativa; sem grupo de controle por imperativo moral. _(E08 §5.5)_
- [ ] Métodos mistos: combina dados quantitativos e qualitativos, dentro de um estudo ou entre estudos; estratégias: explicativa sequencial (quanti depois quali), exploratória sequencial (quali depois quanti) e triangulação concorrente. _(E08 §5.6)_
- [ ] Registrar a combinação de técnicas de coleta (questionários, observação/vídeo, instrumentação, entrevistas, grupos focais) como exemplificado por Jane e Joe. _(E08 §6)_
- [ ] Construir o **esquema de classificação** por *keywording*: ler resumos, extrair palavras-chave e contexto, combinar e **agrupar em categorias**; se o resumo for pobre, ler introdução/conclusão. _(P08 §2.4, Fig. 2)_
- [ ] Registrar numa planilha a **justificativa de cada classificação**; permitir que o esquema evolua (criar, fundir, dividir categorias). _(P08 §2.5)_
- [ ] Projetar formulários de extração que captem tudo o que é necessário para as perguntas e para os critérios de qualidade; definir e pilotar junto com o protocolo. _(K07 §6.4, §6.4.1)_
- [ ] Extrair valores numéricos quando possível (nº de sujeitos, efeito, IC), pois são pré-requisito de resumo e meta-análise. _(K07 §6.4.1)_
- [ ] Pilotar o formulário em amostra de estudos com todos os revisores, avaliando completude e usabilidade (clareza das instruções, ordem das perguntas). _(K07 §6.4.1)_
- [ ] Preferir formulários eletrônicos para facilitar a análise. _(K07 §6.4.1)_
- [ ] Incluir no formulário: nome do revisor, data da extração, título/autores/periódico/dados de publicação e espaço para notas. _(K07 §6.4.2)_
- [ ] Registrar quem extraiu e quem conferiu cada estudo (extrator e checador) e usar campos de "notas adicionais" (Tabela 7). _(K07 §6.4.2, Tab. 7)_
- [ ] Sempre que possível, ter extração independente por 2+ pesquisadores, comparar e resolver por consenso ou arbitragem de um terceiro. _(K07 §6.4.3)_
- [ ] Usar um formulário separado para marcar e corrigir erros e discordâncias. _(K07 §6.4.3)_
- [ ] Investigar na análise de sensibilidade os estudos com discordância irresolvida. _(K07 §6.4.3)_
- [ ] Se cada revisor extrai estudos diferentes, fazer todos extraírem uma amostra aleatória comum e medir a consistência entre revisores. _(K07 §6.4.3)_
- [ ] Contatar autores para dados ausentes ou ambíguos. _(K07 §6.4.5)_
- [ ] Em revisões terciárias, extrair e classificar campos como fonte, ano (usar a 1ª data se publicado em vários lugares), tipo, escopo, tema, autores/afiliação, nº de estudos e escore de qualidade; um extrai, outro checa. _(K07 App. 3)_
- [ ] Construir um formulário de extração (item de dado + tipo de valor + pergunta associada): ID, título, autores, ano, área, veículo, e campos específicos do tema. Isso objetiva a extração e permite rever. _(P15 §3.4, Tab. 3, §3.6.1)_
- [ ] Adotar facetas independentes de tópico: venue, tipo de pesquisa e método de pesquisa, para permitir comparar áreas e melhorar os esquemas. "Tipo de contribuição" foi pouco usado e é menos recomendado. _(P15 §4.4.4, §5.1.3)_
- [ ] Para tipo de pesquisa, usar Wieringa et al. (avaliação, validação, proposta de solução, filosófico, opinião, experiência) com a tabela de decisão (Tab. 7) para desambiguar. _(P15 §5.1.3, Tab. 7)_
- [ ] Para método de pesquisa, usar a lista: survey, estudo de caso, experimento controlado, pesquisa-ação, etnografia, simulação, prototipação, análise matemática; manter coerência com o tipo de pesquisa (Fig. 19). _(P15 §5.1.3, Fig. 19)_
- [ ] Para venue, usar a classificação finlandesa de tipos de publicação (Fig. 18); ela também ajuda a decidir fóruns a incluir/excluir. _(P15 §5.1.3, Fig. 18)_
- [ ] Palavras-chave (keywording): extrair conceitos dos resumos, agrupar, refinar e contar artigos por categoria; é análogo à codificação aberta da teoria fundamentada (rotular, estruturar, fundir/renomear códigos). Usar introdução e conclusão se o resumo for fraco. _(P15 §5.1.3)_
- [ ] Projetar um formulário de extração com os campos pertinentes (aqui: título, ano, país, tipo de estudo, guia, critérios, número, propósito, aspecto) e checar se responde às perguntas. _(Z15 §3.4, §6, Tab. 2)_
- [ ] Extrair a informação em três partes: citação geral; tipo de estudo (meta-análise/SLR/mapeamento); detalhes do checklist. _(Z15 §3.4)_
- [ ] Usar a avaliação para classificar estudos (ex.: desenho do estudo conforme hierarquia de Kitchenham; tipo qualitativo/quantitativo/misto/literatura cinzenta). _(Z15 §5.2)_
- [ ] Mesmo modelo de controle: dois extratores independentes por estudo; especialista resolve divergências. _(Z15 §6)_
- [ ] [#1] Ler todos os artigos selecionados com atenção, ao menos uma vez inteira, antes de extrair, para se familiarizar com a profundidade e a amplitude da evidência (imersão); não pular esse passo. _(CD11 §II, Tab. 2 #1)_
- [ ] [#2] Identificar os trechos do texto ligados aos objetivos da síntese (destacar, transferir para formulário ou codificar direto em ferramenta). _(CD11 §II, Tab. 2 #2)_
- [ ] [#3] Extrair de todos os artigos: detalhes de publicação (autores, ano, título, fonte, resumo, objetivos), descrição de contexto (sujeitos, tecnologias, indústria, cenário) e achados (resultados, comportamentos, fenômenos, citações). _(CD11 §II, Tab. 2 #3)_
- [ ] [#4] Fazer outro pesquisador conferir a extração; quando possível, extrair de forma independente com 2+ pesquisadores e comparar. _(CD11 §II, Tab. 2 #4)_
- [ ] Usar uma técnica de leitura estruturada com um modelo de extração: ao menos um contexto por artigo e ao menos um achado por contexto (publicação 1-* contexto 1-* achados). _(CD11 §II, Fig. 2)_
- [ ] Incluir no modelo, além dos campos básicos: tópico e instrumentos e tipo de estudo (contexto), e texto literal, origem e força da evidência (achados). _(CD11 Fig. 2)_
- [ ] Procurar achados nas seções de resultados, análise, discussão e conclusões, e também em tabelas e figuras (relações mostradas só em figuras devem ser traduzidas em texto). _(CD11 §II)_
- [ ] Para decidir se uma frase é um achado, perguntar: relata medições? resume dados brutos? destaca característica dos dados? dá insights sobre tabelas/figuras? resume análises? responde às RQs? reflete o resultado principal? _(CD11 §II)_
- [ ] Quando faltar detalhe no artigo e não houver acordo, extrair em reunião de consenso; incertezas sem acordo entram na análise de sensibilidade ou na avaliação de confiabilidade da síntese. _(CD11 §II)_
- [ ] [#5] Rotular/codificar os trechos importantes (conceitos, categorias, achados, resultados). Código = rótulo descritivo aplicado a um trecho; exige entender o contexto em que o achado foi feito. _(CD11 §III, Tab. 2 #5)_
- [ ] [#6] Codificar todo o conjunto de dados em um nível apropriado às perguntas de pesquisa (dar atenção igual a todos os artigos). _(CD11 §III, Tab. 2 #6)_
- [ ] [#7] Criar a lista de códigos iniciais com definições e frequências e fazer outro pesquisador conferi-la. _(CD11 §III, Tab. 2 #7)_
- [ ] [#8] Fazer verificações de consistência ou de concordância entre avaliadores (inter-rater) para dar credibilidade à codificação. _(CD11 §III, Tab. 2 #8)_
- [ ] [#9] Garantir ligações claras e evidentes entre o texto e os códigos (rastreabilidade). _(CD11 §III, Tab. 2 #9)_
- [ ] Criar definições operacionais claras para cada código, com limites explícitos, para não serem intercambiáveis nem redundantes e para uso consistente por um pesquisador ao longo do tempo ou por vários ao mesmo tempo. _(CD11 §III)_
- [ ] Limitar o escopo dos códigos ao objeto de análise, sem codificar toda frase do texto; refinar os códigos ao longo do trabalho (ninguém acerta a codificação de primeira). _(CD11 §III)_
- [ ] Registrar o processo de codificação conforme o exemplo de Staples & Niazi: dois pesquisadores listam categorias de forma independente, acordam a lista, classificam cada citação independentemente, discutem divergências em reunião (com terceiro como árbitro). _(CD11 §III)_
- [ ] Ext1: planeje extrair também dados descritivos (tipo de estudo, objetivos, contexto, data de publicação, primeiro autor, tipo de publicação). _(G26 Ext1 (Tab. 6 p.21))_
- [ ] Ext2: em mapeamentos que classificam estudos em categorias pré-definidas, use MCC (com extensão para múltiplas categorias/saídas: correto, errado, ausente). _(G26 Ext2 (Tab. 6 p.21); Ap. C.2.2 p.44)_
- [ ] Ext4: para dados quantitativos, meça correção usando como padrão-ouro o valor explicitamente reportado no estudo primário, tanto para humanos quanto para a IA (exceção à regra de comparar com 2 humanos). _(G26 Ext4 (Tab. 6 p.21); Ap. C.2.2 p.44)_
- [ ] Ext5: para extração complexa (ex.: apoio a análise qualitativa), defina quais sub-tarefas serão automatizadas. _(G26 Ext5 (Tab. 6 p.21))_
- [ ] Ext6: defina o ponto de partida do processo automatizado (o que já se sabe sobre os estudos). _(G26 Ext6 (Tab. 6 p.21))_
- [ ] Ext7: especifique como serão comparados e avaliados humanos e IA na extração complexa. _(G26 Ext7 (Tab. 6 p.21))_
- [ ] Se usar IA para sugerir campos do formulário de extração, valide o formulário com humanos; faça piloto do formulário com 2+ pesquisadores em estudos sorteados, discuta divergências e itere até uso consistente. _(G26 Ap. C.2.1-C.2.2 pp.43-44)_
- [ ] Exija da IA o trecho/página de origem para cada valor extraído, para rastreabilidade e verificação. _(G26 Ap. C.2.3 p.45)_
- [ ] Avalie explicitamente: acurácia numérica (correspondência exata), classificação de tipo de estudo (correspondência exata), acurácia de dados textuais (similaridade semântica, difícil de avaliar), tratamento de dados ausentes e risco de alucinação. _(G26 Ap. C.2.2 p.44)_

### CUIDADO

- [ ] Estudos de caso industriais estão presos ao contexto (processos, domínio, equipe); registrar fatores de contexto, mas sem explosão combinatória que torne tudo "incomparável". _(K04 §5.2.2)_
- [ ] O que as pessoas dizem fazer pode diferir do que fazem; considerar ao extrair dados de estudos baseados em auto-relato (surveys, entrevistas). _(E08 §5.3, §5.6, Practical Considerations)_
- [ ] Resumos costumam ser enganosos; estudos podem se rotular "experimento" sem ser. Usar leitura adaptativa. _(P08 §3.2, §4)_
- [ ] Categorias detalhadas exigem leitura profunda; para áreas grandes, manter categorias de alto nível. _(P08 §3.2)_
- [ ] Extrator nunca deve ser coautor do estudo que extrai (cuidado dos exemplos). _(K07 §6.4.3 (exemplo))_
- [ ] Publicações múltiplas dos mesmos dados enviesariam gravemente a síntese; contatar autores, usar a versão mais completa e, se preciso, consultar todas. _(K07 §6.4.4)_
- [ ] Se for preciso recriar dados manipulando os publicados, relatar primeiro como foram publicados e submeter os dados manipulados a análise de sensibilidade. _(K07 §6.4.5)_
- [ ] Ter um leitor extrator e outro checador ajuda quando há muitos artigos; todos devem entender o protocolo e a extração. _(K07 §6.4.6)_
- [ ] Extração é tão sujeita a vieses quanto a seleção, mas menos estudos avaliaram a qualidade da extração do que a da seleção. _(P15 §4.4.4)_
- [ ] Ações de extração observadas: revisor adicional (17 estudos), critérios objetivos (4), teste-reteste (1); ocultar informação que poderia enviesar (autores/venue) aparece nas opções mas não foi aplicada. _(P15 Tab. 8, Tab. B.23, Tab. 5)_
- [ ] Frequência das facetas nos 52 mapas: venue 27, tipo de pesquisa 21, método 17, foco do estudo 11, tipo de contribuição 6. _(P15 Tab. B.24)_
- [ ] Principal confusão: validação × avaliação. Ambas exigem avaliação empírica; avaliação ocorre em contexto industrial real, validação em laboratório. Solução nova "usada na prática" sem avaliação empírica continua proposta de solução. _(P15 §5.1.3, Tab. 7)_
- [ ] O mesmo método pode cair em ambos os tipos (experimento com estudantes = validação; com profissionais = avaliação). _(P15 §5.1.3, Fig. 19)_
- [ ] O processo de "keywording" original foi criticado por não ser claro (Portillo-Rodríguez et al.); descreva os passos usados. _(P15 §5.1.3)_
- [ ] Classes podem não ser disjuntas; classificação em mais de uma categoria pode ser necessária; esclarecer com exemplos. _(P15 §2.2)_
- [ ] Dois mapas com o mesmo esquema classificaram os mesmos artigos de forma diferente (concordância 33%): um esquema bem definido e confiável é preocupação central de mapas. _(P15 §2.2)_
- [ ] Critérios iguais podem aparecer escritos de modos diferentes; ao agregar, unificar por significado (como feito na Tab. 6). _(Z15 §5.3)_
- [ ] Os objetivos dos estudos podem estar pouco claros e exigir trabalho analítico para serem identificados; o contexto é mais difícil de extrair do que os dados de publicação. _(CD11 §II)_
- [ ] Na abordagem dedutiva, cuidado para não forçar os dados nas categorias só porque o código existe; na indutiva o risco é o oposto (perder o foco teórico das RQs). [CONFERIR: o segundo risco é inferência nossa; o texto cita só o 1º] _(CD11 §III)_
- [ ] Erros comuns na codificação: nível geral demais, ver o que se quer ver em vez do que o texto diz, codificar fora do contexto. _(CD11 §III)_
- [ ] O valor reportado no estudo pode estar errado; humanos às vezes percebem valores impossíveis, e a IA talvez não. _(G26 Ap. C.2.2 nota 13, p.44)_
- [ ] Alucinações na extração incluem: inventar valores ou texto que não está no artigo, atribuir informação ao estudo/RQ/condição errada e "confabulação plausível" (texto coerente que não corresponde à fonte). _(G26 Ap. C.2.2 (5), p.44)_
- [ ] Erros de extração são difíceis de detectar depois (um tamanho de efeito errado pode corromper uma meta-análise silenciosamente), e não há tipos de erro "mais graves" por natureza; por isso MCC sem pesos. _(G26 Ap. C.2.3 p.45)_
- [ ] A IA faz erros aritméticos: se a usar para converter unidades, converter medidas de efeito ou derivar estatísticas, verifique manualmente. _(G26 Ap. C.2.4 p.45)_
- [ ] Evidência empírica específica sobre IA em extração para SE é limitada; trate as orientações como preliminares. Também falta estudo que avalie extração e síntese qualitativa separadamente. _(G26 §4.3 p.17; §7 p.27; Ap. C.4.2 p.51)_

### RELATAR

- [ ] Em surveys, taxa de resposta e representatividade; discutir viés de não resposta. _(K02 DC4)_
- [ ] Registrar quem desistiu e se as desistências enviesam; registrar outros desfechos que o tratamento possa afetar. _(K02 DC5, DC6)_
- [ ] Descrever o esquema de classificação, como foi construído (existente/emergente), e o processo de extração com a verificação feita. _(P15 §5.3)_

## F7 — Síntese e análise


### DECISÃO

- [ ] Meta-análise é a forma mais rigorosa de síntese, mas exige réplicas; justificar quando não for possível. _(K04 §4.3)_
- [ ] Considerar **análise cega** para reduzir "pescaria de resultados". _(K02 A2)_
- [ ] Escolher abordagem (clássica x bayesiana; paramétrica x não paramétrica) de acordo com a distribuição; consultar estatístico para bayesiana. _(K02 §5.1)_
- [ ] Escolher o papel da teoria na síntese: verificar teoria (positivista), gerar teoria local (construtivista) ou avaliar utilidade (pragmática). _(E08 §4)_
- [ ] Pode combinar análise temática do mapa e depois RSL mais detalhada. _(P08 §3.2)_
- [ ] Escolher síntese descritiva (narrativa), quantitativa (meta-análise) ou ambas; a descritiva pode ser complementada por resumo quantitativo. _(K07 §6.5)_
- [ ] Escolher a medida de efeito: binários (odds, risco, razão de chances, risco relativo, redução absoluta de risco); contínuos (diferença de médias, DM ponderada, DM padronizada). _(K07 §6.5.2)_
- [ ] Síntese qualitativa: escolher a abordagem de Noblit e Hare (tradução recíproca, síntese refutacional ou linha de argumento). _(K07 §6.5.4)_
- [ ] No mapeamento: análise limitada a totais e resumos, com gráficos de distribuição por classe; sem meta-análise nem síntese narrativa aprofundada. _(K07 §8)_
- [ ] Escolher a visualização: barras, bolhas, pizza, linhas, Venn, mapa de calor. Bolhas e mapa de calor são ideais para cruzar categorias (ex.: tópico × tipo de pesquisa). _(P15 §4.4.5, §5.1.4, Fig. 14)_
- [ ] Em síntese de evidência, escolher entre abordagem simples (checklist com escala) e GRADE (mais precisa, mais difícil). _(Z15 §2.2, §5.4)_
- [ ] Escolher o método de organização dos temas (padrão, elaborativo, longitudinal, focado, axial/teórico) e a representação visual (redes temáticas, tabelas, tree-maps, mapas mentais). _(CD11 §IV)_
- [ ] Classifique sua síntese: para síntese agregativa (ex.: classificar em categorias predefinidas) a IA pode atuar como revisor independente, validada com métricas de concordância como na seleção. _(G26 Ap. C.4.2 p.50)_
- [ ] Para síntese interpretativa/idealista, a IA como "segundo codificador" não agrega e pode atrapalhar; use-a só como método secundário para validar e obter ideias complementares, relatando os vieses da ferramenta. _(G26 Ap. C.4.2 p.50)_

### FAZER

- [ ] Especificar procedimento de **controle de testes múltiplos** (ex.: Bonferroni) ou relatar quantos testes foram feitos. _(K02 A1)_
- [ ] Fazer **análise de sensibilidade** (outliers, observações influentes, colinearidade). _(K02 A3)_
- [ ] Examinar os dados antes de analisar; conferir resultados com outro programa. _(K02 A5)_
- [ ] Usar uma lente teórica explícita para rotular/categorizar ("codificar") dados qualitativos; em métodos quantitativos a lente define quais variáveis isolar. _(E08 §4)_
- [ ] Para desenvolver teoria de forma sistemática a partir de dados qualitativos, considerar a Grounded Theory (começa sem categorias, comparação constante). [CONFERIR] _(E08 §4)_
- [ ] Preferir teorias mais simples ou mais elegantes quando houver várias que explicam as observações. _(E08 §4)_
- [ ] Construir confiança por indução empírica: os resultados precisam se sustentar em vários estudos; a meta-análise compara resultados considerando diferenças de desenho e contexto, mas é difícil em ES. _(E08 Conclusões)_
- [ ] Em métodos mistos, deixar claro a sequência (qual método informa qual) e usar resultados de um para interpretar ou testar o outro. _(E08 §5.6)_
- [ ] Analisar **frequências** por categoria para ver ênfases e lacunas; combinar facetas. _(P08 §2.5)_
- [ ] Visualizar: **gráfico de bolhas** (tamanho = nº de artigos no cruzamento de facetas) e tabelas de frequência por faceta. _(P08 §2.5, Fig. 3, §4)_
- [ ] Especificar as atividades de síntese no protocolo, sabendo que alguns detalhes só se resolvem após ver os dados (ex.: análise de subconjuntos só se houver heterogeneidade). _(K07 §6.5)_
- [ ] Síntese narrativa: tabelar intervenção, população, contexto, tamanho amostral, desfechos e qualidade, de modo a destacar semelhanças e diferenças. _(K07 §6.5.1)_
- [ ] Verificar se os resultados são consistentes (homogêneos) ou inconsistentes (heterogêneos) e tabular o impacto de fontes de heterogeneidade (tipo, qualidade, amostra). _(K07 §6.5.1)_
- [ ] Agrupar tabelas por resultado e ordenar cronologicamente para ver associação com a idade do estudo (técnicas dos exemplos). _(K07 §6.5.1 (exemplo))_
- [ ] Síntese quantitativa: tabelar tamanho amostral por intervenção, tamanho de efeito com erro-padrão, diferença de médias com IC e unidades. _(K07 §6.5.2)_
- [ ] Apresentar resultados quantitativos em forest plot (box proporcional ao nº de sujeitos, linha de erro, resumo no fim, se houver meta-análise). _(K07 §6.5.3)_
- [ ] Em RSL mista, sintetizar quantitativos e qualitativos separadamente e depois integrá-los (qualitativos podem explicar os quantitativos). _(K07 §6.5.5)_
- [ ] Fazer análise de sensibilidade (descritiva ou quantitativa), repetindo em subconjuntos: só alta qualidade, tipos particulares, sem estudos com discordância de dados, por método experimental. _(K07 §6.5.6)_
- [ ] Sem meta-análise, anotar forest plots por qualidade, ordenar estudos por qualidade/hierarquia, marcar estudos duvidosos (cinza x preto). _(K07 §6.5.6)_
- [ ] Na síntese descritiva, avaliar subjetivamente o impacto de excluir estudos ruins ou de certos tipos nas conclusões. _(K07 §6.5.6)_
- [ ] Considerar sensibilidade removendo estudos do autor da teoria (exemplo TAM) ou reportando também só estudos de campo (validade externa). _(K07 §6.5.6 (exemplo))_
- [ ] Avaliar viés de publicação com funnel plot (efeito x 1/variância ou tamanho amostral); assimetria sugere viés e exige cautela. _(K07 §6.5.7)_
- [ ] Tabular e ilustrar os dados extraídos; agrupar estratégias/achados em temas e contar artigos por tema (no estudo, contagem por categoria). _(P15 §3.5, §5.1.3)_
- [ ] Resultados devem permitir identificar tendências, lacunas (categorias com poucos estudos ou sem avaliação) e olhar em detalhe os poucos estudos de uma categoria. _(P15 §2.1, §5.1.1)_
- [ ] Usar os escores de qualidade como apoio à síntese: ponderar estudos (P3) e orientar a interpretação e a força das inferências (P4). _(Z15 §5.2)_
- [ ] Tratar escores baixos como informação para leitores (confiança nas conclusões), não necessariamente razão para excluir (especialmente em áreas imaturas). _(Z15 §5.2)_
- [ ] [#10] Criar os temas a partir de revisão completa, inclusiva e abrangente dos códigos de todos os artigos. _(CD11 §IV, Tab. 2 #10)_
- [ ] [#11] Reduzir a sobreposição entre códigos e agrupar/traduzir os restantes em temas (ordem de grandeza de Fig. 1: muitas páginas, muitos trechos, 30-40 códigos, 15-20 temas, 5-7 temas de ordem superior). _(CD11 §IV, Tab. 2 #11, Fig. 1)_
- [ ] [#12] Conferir os temas entre si e voltar aos dados dos artigos originais. _(CD11 §IV, Tab. 2 #12)_
- [ ] [#13] Garantir que cada tema seja internamente coerente, consistente e distinto dos demais. _(CD11 §IV, Tab. 2 #13)_
- [ ] Usar um mapa temático (tema central, temas de ordem superior, temas, códigos) para organizar visualmente os códigos em temas. _(CD11 §IV, Fig. 5)_
- [ ] [#14] Comparar temas entre estudos, traduzi-los entre si e interpretá-los em temas de ordem superior. _(CD11 §V, Tab. 2 #14)_
- [ ] [#15] Conferir temas de ordem superior e suas relações contra as perguntas de pesquisa da síntese. _(CD11 §V, Tab. 2 #15)_
- [ ] [#16] Descrever com clareza os temas de ordem superior e as relações entre eles. _(CD11 §V, Tab. 2 #16)_
- [ ] [#17] Criar um modelo (taxonomia, mapa temático ou teoria) que mostre as relações entre os temas de ordem superior. _(CD11 §V, Tab. 2 #17)_
- [ ] Passos para temas de ordem superior: (1) revisar cada ramo do mapa com achados e contexto; (2) ligar temas a evidências e contexto; (3) relacionar com teoria e pesquisa prévia; (4) montar o modelo/taxonomia/mapa/teoria. _(CD11 §V)_
- [ ] Se os estudos primários não analisaram a relação entre achados e contexto, usar os dados extraídos para compará-las entre estudos; trabalhoso, mas crítico para a qualidade da síntese. _(CD11 §V)_
- [ ] Explorar a heterogeneidade: variabilidade nos resultados, nos desenhos de estudo e nas populações/intervenções/contextos; usar análise de subgrupos (por temas) quando as fontes forem conhecidas. _(CD11 §V)_
- [ ] Se apresentar frequências dos temas (nº e % de estudos por categoria), tratá-las com cautela, e usar as RQs para discutir os temas mais importantes. _(CD11 §V, §VI)_
- [ ] Syn1: especifique e relate o método de síntese qualitativa e por que é adequado às RQs e aos estudos primários. _(G26 Syn1 (Tab. 6 p.21))_
- [ ] Syn2: especifique e relate os critérios para avaliar o desempenho da IA, dado o método de síntese escolhido. _(G26 Syn2 (Tab. 6 p.21))_
- [ ] Syn3: especifique e relate como a síntese da IA será comparada com a dos humanos e como o desempenho relativo será medido. _(G26 Syn3 (Tab. 6 p.21))_
- [ ] RevA1/RevA2 também valem para síntese: restrinja a IA a validar o trabalho dos humanos e revise toda a saída, assumindo a responsabilidade. _(G26 RevA1-RevA2 (Tab. 6 p.21))_
- [ ] Planeje a síntese em 3 passos: planejar (método, papel dos pesquisadores, forma de validação), conduzir (guardar registro de decisões e resultados intermediários para auditoria), validar (usar critérios definidos no planejamento). _(G26 Ap. C.4.1 p.49)_
- [ ] Use os critérios de uma síntese sólida como base de avaliação: achados fundamentados nos estudos, relevância prática e transferibilidade, ponderação por limitações metodológicas, método adequado e justificado, condução transparente e auditável, tratamento adequado da subjetividade (concordância entre codificadores em abordagens realistas; reflexividade em idealistas). _(G26 Ap. C.4.1 pp.49-50)_
- [ ] Em qualquer caso, humanos examinam os achados da IA antes de entrarem no relatório final. _(G26 Ap. C.4.2 p.50)_

### CUIDADO

- [ ] Evitar confundir **coletar evidência** (revisão) com **empacotar** em diretrizes para públicos específicos (distinção da NHMRC). _(K04 §4.3)_
- [ ] Verificar pressupostos dos testes (distribuição, variâncias); transformar dados se necessário. _(K02 A4)_
- [ ] Distinguir **significância estatística** de **importância prática**; usar intervalos de confiança. Não aumentar alfa depois por baixo poder. _(K02 I2)_
- [ ] Estudo isolado não é conclusivo; evidência se acumula quando estudos posteriores confirmam a teoria ou falham em confirmar teorias rivais. _(E08 §4, §5.2)_
- [ ] Não confundir "evidência de que X é eficiente (como definido)" com "X é melhor"; resultados dependem de como constructos foram definidos. _(E08 §5.1)_
- [ ] Experimentos reduzem a complexidade e podem mascarar interações; resultados podem não generalizar ao mundo real. _(E08 §5.1)_
- [ ] Em estudos de caso, análise e coleta são mais abertas a interpretação e viés; usar framework explícito. _(E08 §5.2)_
- [ ] Em métodos mistos, comparar resultados de duas análises e resolver contradições pode ser difícil; pode exigir nova fonte de evidência ou estudo de acompanhamento. _(E08 §5.6)_
- [ ] Replicações que usam os mesmos dados não dão evidência independente adicional; destacar/excluir da síntese. _(K07 §6.5.1 (exemplo))_
- [ ] Odds são pouco compreendidos por não estatísticos; medidas relativas são mais consistentes, mas tomadores de decisão precisam de valores absolutos. _(K07 §6.5.2)_
- [ ] DM padronizada só é válida se diferenças de desvio padrão refletem escala de medida, não diferenças reais entre populações. _(K07 §6.5.2)_
- [ ] Efeitos muito diferentes entre estudos indicam heterogeneidade: um único resumo tem pouco valor; investigar as razões. _(K07 §6.5.3)_
- [ ] Para evitar "pescar" resultados (post hoc), identificar no protocolo as fontes possíveis de heterogeneidade; sintetizar tipos de estudo separadamente quando fizer sentido. _(K07 §6.5.3)_
- [ ] Em ES, as sínteses tendem a ser qualitativas e a meta-análise pode ser inviável pela variabilidade de relato. _(K07 §6.5.8)_
- [ ] Tabular dados não basta: explicar como os dados agregados respondem às perguntas. _(K07 §6.5.8)_
- [ ] Os mais usados foram gráfico de barras e bolhas; mapa de calor aparece em apenas um estudo, embora mostre bem a quantidade relativa. _(P15 §4.4.5)_
- [ ] Evitar tratar o mapa como evidência sobre eficácia: o produto é um inventário de artigos mapeado em categorias, não síntese da força da evidência. _(P15 §2.1)_
- [ ] Dois propósitos juntos são raros (tabela de matriz): só três estudos cumpriram três propósitos e nenhum mais que três. _(Z15 §5.2, Tab. 5)_
- [ ] Interpretação (P4) é mais comum porque a qualidade complementa a extração e revela a credibilidade das conclusões; deixar isso explícito na discussão. _(Z15 §5.2)_
- [ ] Quem mede qualidade só com escalas aditivas pode superestimar a força da evidência; considerar fatores que a reduzem (inconsistência). _(Z15 §5.4)_
- [ ] Tema é resultado de codificação e reflexão analítica, não algo que já se codifica; a tradução de códigos em temas é iterativa (códigos podem ser fundidos, renomeados ou descartados). Parar quando os temas saturarem. _(CD11 §IV)_
- [ ] Descrever o processo de passar de códigos a temas: a maioria das revisões de ES analisadas não o explicava. _(CD11 §IV)_
- [ ] A exploração da heterogeneidade depende de informação nos estudos primários, que costuma ser mal relatada em ES; a maioria das revisões só descreve temas sem explorar a variabilidade. _(CD11 §V)_
- [ ] Falhas observadas em testes (autoetnográficos): saída plausível porém incorreta, perda de interpretação, sensibilidade a pequenas mudanças de prompt (e mesmo o mesmo prompt dá resultados diferentes), vieses de treinamento, e verificação tão trabalhosa quanto a síntese manual. _(G26 §4.3 p.17; Tab. 3 p.18)_
- [ ] Existem métodos aggregativos (resumem com pouca reinterpretação) e interpretativos (criam novos conceitos); o risco da IA é maior nos interpretativos. _(G26 Ap. C.4 pp.48-49)_

### RELATAR

- [ ] Resultados da síntese: descrição dos estudos primários, resumos quantitativos, meta-análise (se houver) e sensibilidade; resumos não quantitativos em tabela e quantitativos em tabelas/gráficos. _(K07 Tab. 8)_
- [ ] Estruturar a seção de resultados pelas perguntas do mapeamento e incluir discussão/conclusões. _(P15 §5.3)_

## F8 — Validade e ameaças


### DECISÃO

- [ ] Escolher o conjunto de critérios de validade coerente com a postura (positivista: construto, interna, externa, confiabilidade; construtivista: estratégias de Creswell ou credibilidade/transferibilidade/dependabilidade/confirmabilidade; crítica: utilidade e autenticidade). _(E08 §7)_
- [ ] Prefira registrar parâmetros (temperatura baixa, top_p, max tokens etc.) quando a ferramenta permitir; parâmetros podem interagir de forma imprevisível. _(G26 §2.1 item 5 p.3)_
- [ ] Prefira uma ferramenta aberta (versão fixa e arquivada) como baseline para reprodutibilidade; ferramentas proprietárias mudam, podem sumir ou ficar caras. _(G26 PlanE2 (Tab. 5 p.20); Ap. B.1.1 p.35)_

### FAZER

- [ ] Discutir viés do sujeito e do experimentador; técnicas: alocação cega, distribuição cega de material, correção cega, análise cega, coleta cega/automatizada. _(K04 §5.1.1)_
- [ ] Considerar bloqueio, análise de covariáveis ou cross-over para diferenças sistemáticas de habilidade. _(K04 §5.1.1)_
- [ ] Validade de construto: checar se os construtos teóricos são interpretados e medidos corretamente; problema quando a variável medida não corresponde ao significado do termo teórico. _(E08 §7)_
- [ ] Validade interna: checar se os resultados realmente decorrem dos dados; erros típicos: variáveis de confusão mal tratadas e uso indevido de estatística. _(E08 §7)_
- [ ] Validade externa: checar se a generalização é justificada (depende da amostragem); ex.: estudantes como sujeitos exigem argumento analítico de aplicabilidade a profissionais. _(E08 §5.1, §7)_
- [ ] Confiabilidade (reliability): checar se outros pesquisadores obteriam o mesmo resultado; atenção a viés quando o pesquisador tem interesse (ex.: avaliar ferramenta própria). _(E08 §7)_
- [ ] Estratégia construtivista 1, triangulação: usar fontes de dados diferentes para confirmar resultados. _(E08 §7)_
- [ ] Estratégia 2, verificação com membros (member checking): voltar aos participantes para ver se a interpretação faz sentido para eles. [CONFERIR: em RSL, equivale a consultar autores/especialistas] _(E08 §7)_
- [ ] Estratégia 3, descrições ricas e densas do cenário e dos achados. _(E08 §7)_
- [ ] Estratégia 4, esclarecer o viés: ser honesto sobre vieses do pesquisador e usar autorreflexão ao relatar. _(E08 §7)_
- [ ] Estratégia 5, relatar informação discrepante: reportar também resultados que contrariam a teoria emergente. _(E08 §7)_
- [ ] Estratégia 6, contato prolongado com os participantes. [CONFERIR: não se aplica a RSL] _(E08 §7)_
- [ ] Estratégia 7, debriefing por pares: um colega faz perguntas sobre estudo e suposições antes de reportar. _(E08 §7)_
- [ ] Estratégia 8, auditor externo: igual ao debriefing, mas com pessoa fora do círculo do pesquisador que revisa procedimento e achados. _(E08 §7)_
- [ ] Usar análise de sensibilidade como ferramenta geral de robustez (ver F7). _(K07 §6.5.6)_
- [ ] Usar a lista de pontos de controle para testar sua revisão: busca abrangente, qualidade avaliada, sensibilidade, números interpretados com bom senso. _(K07 §5.1 (Greenhalgh))_
- [ ] Discutir validade em subseção própria, usando os tipos de Petersen & Gencel: descritiva, teórica, generalização (interna/externa), interpretativa (e repetibilidade). _(P15 §3.6, §5.3)_
- [ ] Mitigar descritiva: formulário de coleta que objetiva o registro e permite revisitar. _(P15 §3.6.1)_
- [ ] Mitigar teórica: complementar busca com snowballing, criar conjunto de referência, ter outro pesquisador checando seleção/extração. Seleção por um só autor foi a principal ameaça do estudo. _(P15 §3.6.2)_
- [ ] Registrar o recorte temporal e justificar (o estudo ficou nos artigos até 2012 e não incluiu 2013). _(P15 §3.6.2)_
- [ ] Para repetibilidade, relatar o processo em detalhe e as ações para reduzir ameaças. _(P15 §3.6.5)_
- [ ] Discutir ameaças ligadas a: estratégia de busca, critérios de seleção, extração de dados (3 blocos no §6 do artigo). _(Z15 §6)_
- [ ] [#18] Explicitar as suposições e a abordagem específica adotada na síntese temática. _(CD11 §VI, Tab. 2 #18)_
- [ ] [#19] Verificar o ajuste entre o que é afirmado e o que a evidência mostra. _(CD11 §VI, Tab. 2 #19)_
- [ ] [#20] Verificar se a linguagem e os conceitos usados na síntese são consistentes. _(CD11 §VI, Tab. 2 #20)_
- [ ] [#21] Verificar se as perguntas de pesquisa foram respondidas com base na evidência da síntese. _(CD11 §VI, Tab. 2 #21)_
- [ ] Avaliar a confiabilidade (trustworthiness) pelos quatro conceitos: credibilidade, confirmabilidade, dependabilidade e transferibilidade. _(CD11 §VI)_
- [ ] Credibilidade: mostrar que o foco, a seleção de contextos e a busca estão adequados, que códigos e temas cobrem os dados sem excluir relevantes nem incluir irrelevantes; usar trechos representativos e acordo entre co-pesquisadores/especialistas. _(CD11 §VI)_
- [ ] Confirmabilidade: verificar se outros pesquisadores/especialistas concordariam com a forma de codificar e organizar; se possível, o reconhecimento dos autores dos estudos primários. _(CD11 §VI)_
- [ ] Dependabilidade: manter trilha de auditoria (audit trail) que permita a um revisor externo examinar como os dados foram extraídos, codificados e traduzidos em temas; usar métodos de codificação complementares. _(CD11 §VI)_
- [ ] Transferibilidade: descrever com clareza a seleção e as características dos estudos (contexto, cenário), a extração e o processo de síntese; a decisão final de transferir é do leitor. _(CD11 §VI)_
- [ ] Fazer análise de sensibilidade (ex.: por população, local, ano e tipo de estudo) para ver onde os dados podem estar enviesados, como em Beecham et al. _(CD11 §VI)_
- [ ] Apresentar achados de modo que o leitor possa buscar interpretações alternativas; não há um único significado correto, só o mais provável. _(CD11 §VI)_
- [ ] Prefira avaliação prospectiva (durante sua RSL, com dados novos) a retrospectiva (reanalisar RSL antiga) para reduzir contaminação; se usar dados públicos, justifique. _(G26 §4.2 p.15; PlanE4 (Tab. 5 p.20))_
- [ ] Plan4: desenhe a avaliação para detectar erros da ferramenta e minimizar riscos de vieses embutidos e de contaminação por análises repetidas. _(G26 Plan4 (Tab. 5 p.20))_
- [ ] Con1: identifique e relate desvios do plano; Con2: use corretamente os processos de coleta de dados. _(G26 Con1, Con2 (Tab. 5 p.20))_
- [ ] Con3: se fizer estudo de caso de IA dentro da RSL, registre todo o esforço humano necessário para sustentar o uso da IA (prompts, validação, correção). _(G26 Con3 (Tab. 5 p.20))_
- [ ] Humanos que participam da validação devem cronometrar com cuidado o tempo por tarefa (com pausas) e registrar as mesmas justificativas que a IA fornece, mesmo que normalmente não registrassem. _(G26 Ap. B.2.3 p.40; B.1.2 p.36)_

### CUIDADO

- [ ] Replicações devem variar desenho e materiais para evitar viés de causa comum; idealmente por pesquisadores sem interesse no resultado. _(K04 §5.1.1)_
- [ ] Evidência sobre testes parece mais promissora; mais difícil para tecnologias de análise e projeto. _(K04 §6)_
- [ ] Uso de **estudantes** como sujeitos é aceitável se o alvo são novatos; materiais restritos podem não escalar para sistemas industriais. _(K02 I4)_
- [ ] Ao omitir projetos/estudos por dados incompletos, discutir a implicação nas conclusões. _(K02 I4)_
- [ ] Validade em pesquisa construtivista é discutida: alguns rejeitam o conceito; avaliar com estratégias durante a pesquisa em vez de só avaliação a posteriori (Morse et al.). _(E08 §7)_
- [ ] Pesquisa-ação: critérios de qualidade ainda vagos; riscos de política organizacional e de exagero do "caso moral"; reduzir viés por reflexão crítica e replicação. _(E08 §5.5, §7)_
- [ ] Survey: viés de amostragem e baixa taxa de resposta; perguntas ambíguas; auto-relato pode não refletir a prática real. _(E08 §5.3)_
- [ ] Em pesquisa em empresas, o efeito Hawthorne e a perda de controle sobre o que é observado. [CONFERIR: tangencial à RSL] _(E08 Practical Considerations)_
- [ ] Erros de julgamento ao classificar sem avaliar detalhadamente; mitigados por considerar mais artigos. _(P08 §3.2)_
- [ ] Viés ao restringir a poucos fóruns ou só a artigos empíricos. _(P08 §2.2, §3.2)_
- [ ] Viés de seleção: critérios definidos antes e piloto, revisão por mais de uma pessoa, medida de concordância. _(K07 §6.2.1, §6.2.3)_
- [ ] Viés de publicação: ver F3 e funnel plot em F7; resultados negativos tendem a ficar fora. _(K07 §6.1.2, §6.5.7)_
- [ ] Viés do pesquisador: protocolo prévio evita que expectativas guiem seleção e análise. _(K07 §5.4)_
- [ ] Duplicatas inflam resultados; avaliar publicações múltiplas. _(K07 §6.4.4)_
- [ ] Medidas substitutas e estudos com estudantes/tarefas pequenas limitam generalização. _(K07 §5.3.2)_
- [ ] Má qualidade de relato dos estudos primários pode distorcer a avaliação; não confundir "não relatado" com "não feito". _(K07 §6.3.4)_
- [ ] Registrar em detalhe as decisões tomadas durante todo o processo e declarar os desvios do protocolo. _(K07 §7.4)_
- [ ] Em "revisor único", a fragilidade principal é a falta de checagem independente; compensar com técnicas de F4 e F6. _(K07 §9, §6.2.3, §6.4.3)_
- [ ] Ameaças típicas: viés de publicação (resultados negativos/controversos não publicados); formulário de extração mal projetado; viés do pesquisador na seleção e no relato; qualidade da amostra vs. população; generalização; viés na interpretação dos dados. _(P15 §5.1.5)_
- [ ] Análise baseada só no que foi relatado: atividades podem ter sido omitidas ou mal descritas nos artigos analisados. _(P15 §3.6.2)_
- [ ] Viés de interpretação: o primeiro autor também é coautor de uma das diretrizes analisadas; declarar conflitos desse tipo. _(P15 §3.6.4)_
- [ ] A maioria dos estudos relatou ameaças (45 de 52 com pontuação completa; 7 sem descrição). _(P15 Tab. 14, Fig. 15)_
- [ ] Busca: apenas quatro bibliotecas podem deixar estudos de fora, mesmo com QGS; mitigado por snowballing e revisão do supervisor. _(Z15 §6)_
- [ ] Seleção: duplicatas podem inflar frequências; checar duplicatas em duplas. _(Z15 §6)_
- [ ] Extração: viés de extração mitigado por protocolo revisado, formulário padronizado e extração independente em dupla com especialista. _(Z15 §6)_
- [ ] Limitação do artigo: coletou só a afiliação do primeiro autor; análise limitada a estudos que publicaram critérios. [CONFERIR: inferido do §4.2 e §4.1] _(Z15 §4.1, §4.2)_
- [ ] Fatores de qualidade no objeto da tese: se a tese avalia qualidade dos estudos, a validade das conclusões depende de critérios justificados; o artigo observa que a justificativa dos critérios raramente é relatada. _(Z15 Resumo, §7)_
- [ ] Segmentos de texto largos demais (vários parágrafos) são difíceis de manejar; estreitos demais (uma palavra ou linha) fragmentam e podem perder significado. _(CD11 §VI)_
- [ ] Agrupar papéis, países ou períodos diferentes pode apagar detalhes e a variação ao longo do tempo; discutir essa perda como ameaça à síntese. _(CD11 §VI)_
- [ ] Reconhecer ameaças da extração/codificação quando estudos primários têm pouco detalhe de contexto (possíveis imprecisões). _(CD11 §VI)_
- [ ] Contaminação de dados (data leakage): artigos/datasets públicos e testes repetidos podem estar na memória do modelo; resultados "bons demais" devem levantar suspeita, e é muito difícil detectá-la. _(G26 §2.1 item 4 p.3; §6 p.25)_
- [ ] Alucinação: a IA pode inventar conteúdo; mitigação (RAG, checagem de fatos) não elimina o problema. _(G26 §2.1 item 2 p.3)_
- [ ] Inconsistência: a mesma entrada pode gerar saídas diferentes; é você quem distingue variação linguística inofensiva de alucinação. _(G26 §2.1 item 3 p.3)_
- [ ] Alvo móvel: mudanças de versão do modelo e, mais grave, mudanças de infraestrutura (filtros, prompts de sistema, pré-processamento de PDF, limites, interface), que podem ocorrer diariamente sem aviso, prejudicam reprodutibilidade. _(G26 §2.1 item 1 p.3)_
- [ ] Viés da IA: pode subvalorizar estudos não ingleses, de autoras ou de nomes não europeus; o paper trata isso como preocupação a investigar, não achado estabelecido. _(G26 §2.1 item 9 p.4)_
- [ ] Explicabilidade limitada: modelos comerciais ocultam o raciocínio interno; cabe a você exigir via prompt a justificativa e evidências. _(G26 §2.1 item 7 p.4)_
- [ ] Agentes de IA de ponta a ponta nem sempre expõem saídas intermediárias; relatar só os prompts iniciais não basta para reprodutibilidade; relatórios gerados por esses sistemas não são avaliação rigorosa. _(G26 §6 p.26)_

### RELATAR

- [ ] Declarar **limitações**: validade interna (confundidores/viés) e externa (generalização). _(K02 I4)_
- [ ] Definir a **população** a que valem as inferências e modelos preditivos. _(K02 I1)_
- [ ] Incluir uma seção de ameaças à validade nos estudos positivistas: pontos fracos do desenho e tentativas de mitigação, nos quatro critérios. Todo desenho tem falhas. _(E08 §7)_
- [ ] Discutir forças e fraquezas da evidência incluída e da própria revisão, e a validade (vieses da revisão) para o leitor julgar quanto confiar. _(K07 Tab. 8)_
- [ ] Discutir aplicabilidade/generalização, grau de causalidade implicado pelo nível de evidência, benefícios, efeitos adversos, riscos, variações de efeito e suas razões. _(K07 Tab. 8)_
- [ ] Relação com outras revisões, destacando diferenças de qualidade e de resultados. _(K07 Tab. 8)_
- [ ] Declarar conflitos de interesse (ex.: interesse financeiro na tecnologia avaliada). _(K07 Tab. 8)_
- [ ] Discuta nas limitações da sua tese a validade de construto, interna, externa e confiabilidade do uso da IA (o paper modelou essa estrutura na §5). _(G26 §5 pp.23-24)_

## F9 — Relato (texto da tese)


### DECISÃO

- [ ] Preferir resumos estruturados quando existirem; defender seu uso. _(P08 §4)_
- [ ] Planejar a estratégia de disseminação no protocolo (ou na encomenda): para influenciar praticantes, usar também revistas de prática, imprensa, folhetos, pôsteres, páginas web, comunicação direta. _(K07 §7.1)_
- [ ] Definir formatos: relatório técnico ou seção da tese, e artigo de periódico/conferência; o artigo deve referenciar o relatório/tese com todos os detalhes. _(K07 §7.2)_
- [ ] Escolher o veículo: periódicos tiveram mediana maior no checklist que conferências, talvez pelo espaço; os mapas se dividem aproximadamente entre periódicos e conferências/workshops, e IST foi o veículo mais frequente (14). _(P15 §4.3, §5.5, Fig. 21, Tab. 4)_

### FAZER

- [ ] Seguir a estrutura da Tabela 8: título (curto, informativo, indicando RSL), autoria (critérios definidos antes), resumo estruturado (contexto, objetivos, métodos, resultados, conclusões), contexto, perguntas, métodos, incluídos/excluídos, resultados, discussão, conclusões, agradecimentos, conflito de interesse, referências e apêndices. _(K07 §7.2, Tab. 8)_
- [ ] Na tese, omitir os itens marcados com asterisco (título, autoria, resumo estruturado, agradecimentos) conforme a tabela, que não se aplicam. [CONFERIR: o texto diz "provavelmente não relevantes".] _(K07 §7.2, Tab. 8)_
- [ ] Usar apêndices para listar estudos incluídos/excluídos, detalhar a busca e apresentar os dados brutos extraídos. _(K07 Tab. 8)_
- [ ] Submeter o relatório (se não for tese/artigo) a avaliação por pares: o mesmo painel que avaliou o protocolo, ou especialistas no tema/metodologia. _(K07 §7.3)_
- [ ] Avaliar o próprio relatório com os checklists de RSL da §5.1 (CRD/DARE). _(K07 §7.3)_
- [ ] Manter mesma estrutura e estilo de relato entre mapas para facilitar avaliação e comparação. _(P15 §5.3)_
- [ ] Usar o checklist/régua como "guia de bolso" para o autor se auto-avaliar antes de submeter e para revisores. _(P15 §5.4)_
- [ ] RepR1: siga um guia de relato de RSL (SEGRESS para engenharia de software ou PRISMA 2020), que já exige relatar o uso de IA, inclusive treinamento e validação. _(G26 RepR1 (Tab. 5 p.20); Ap. B.2.4 p.40)_

### CUIDADO

- [ ] Gráficos: evitar 2D para dados 1D, pizza, escalas enganosas, omitir outliers, falta de jitter. _(K02 P6)_
- [ ] Conclusões devem decorrer **diretamente** dos resultados; não introduzir material novo nem minimizar achados que contradizem a literatura. _(K02 §7.1)_
- [ ] Relatos de RSL podem ser longos; usar apêndices eletrônicos e repositórios quando o limite de páginas for restritivo. _(K07 §7.4)_
- [ ] Em relatos, evitar incluir a seção de qualidade sem ligá-la ao restante da revisão. _(Z15 §5.2)_

### RELATAR

- [ ] Resultados em forma acessível a praticantes (resumos, publicações para a indústria). _(K04 §4, §6)_
- [ ] Descrever o método de busca e de síntese e fornecer sumário anotado dos estudos revisados. _(K04 §6)_
- [ ] Descrever ou citar todos os procedimentos estatísticos; informar o pacote estatístico. _(K02 P1, P2)_
- [ ] Apresentar resultados quantitativos (tamanho de efeito, limites de confiança, alfa, uni/bicaudal, equação e R² em regressão). _(K02 P3)_
- [ ] Apresentar **dados brutos** ou disponibilizá-los a revisores/auditores em sigilo. _(K02 P4)_
- [ ] Estatística descritiva adequada (n, precisão apropriada, numerador/denominador, desvio-padrão e não erro-padrão, justificar cortes). _(K02 P5)_
- [ ] Incluir informação que permita meta-análise futura. _(K02 §6.1)_
- [ ] Declarar o tipo de pergunta, a postura filosófica e a justificativa dos métodos escolhidos. _(E08 §2, §3, Conclusões)_
- [ ] Declarar o método, a unidade de análise e as técnicas de coleta, e o papel da teoria. _(E08 §5, §6)_
- [ ] Documentar o protocolo planejado e os desvios feitos. _(E08 Practical Considerations)_
- [ ] Incluir ameaças à validade com os critérios coerentes com a postura, e as mitigações adotadas. _(E08 §7)_
- [ ] Reportar resultados discrepantes e vieses do pesquisador (postura construtivista). _(E08 §7)_
- [ ] Reconhecer a limitação de generalização (ex.: tipo de amostra) e a ausência de certeza. _(E08 §5.1, Conclusões)_
- [ ] [CONFERIR] Se houver confidencialidade ou ética em estudos com humanos, declarar. _(E08 Practical Considerations)_
- [ ] Perguntas, string de busca, bases/fóruns, critérios, processo de keywording e esquema final, tabela de extração, frequências e visualizações. _(P08 §2)_
- [ ] Tornar resultados acessíveis; mapas visuais despertam interesse de praticantes, e RSLs devem pensar em formatos mais acessíveis. _(P08 §3.2, §4)_
- [ ] Contexto/justificativa da necessidade da revisão, resumo de revisões anteriores e descrição da técnica estudada e sua importância. _(K07 Tab. 8 (Background))_
- [ ] Os métodos (fontes e busca, seleção, qualidade, extração, síntese) baseados no protocolo, com mudanças reportadas. _(K07 Tab. 8)_
- [ ] Achados principais correspondentes aos discutidos nos resultados; implicações práticas, recomendações, questões não respondidas e implicações para pesquisa futura. _(K07 Tab. 8)_
- [ ] Desvios do protocolo e registro do que ocorreu durante a condução. _(K07 §7.4)_
- [ ] Em mapeamentos, apresentar a distribuição de estudos por categoria, em geral com disseminação mais restrita (órgãos solicitantes e publicações acadêmicas). _(K07 §8)_
- [ ] Estrutura recomendada: Introdução; Trabalhos relacionados; Método (subseções: perguntas, busca, seleção, extração e, se feita, qualidade, análise/classificação, validade); Resultados; Discussão/Conclusões; Apêndice com incluídos e limítrofes excluídos. _(P15 §5.3)_
- [ ] Para a RSL ser avaliada pela régua, relatar de forma explícita cada ação tomada (consulta ao público, estratégias de busca, avaliação da busca, resolução de divergências, esquema de classificação). _(P15 §5.4, Tab. 8–13)_
- [ ] Justificar os critérios de qualidade escolhidos (o artigo observa que pouco se relata sobre essa justificativa). _(Z15 Resumo)_
- [ ] Listar critérios, número, escala, limiar e propósito; publicá-los no texto ou em apêndice/repositório acessível. _(Z15 §4.1, §5)_
- [ ] Reportar distribuição dos escores e decisões tomadas (excluir ou apenas informar). _(Z15 §5.2)_
- [ ] Se for terciário, descrever a distribuição temporal, de venues (IST dominante: 31 de 110), tipos (57 periódicos, 53 conferências/workshops) e geográfica (Europa 56%, 44 estudos). _(Z15 §4.1, §4.2, Fig. 1, Fig. 2)_
- [ ] Declarar a abordagem de síntese, as suposições e o processo seguido em cada passo (extração, codificação, temas, modelo), de modo transparente. _(CD11 §I, §VI, Tab. 2 #18)_
- [ ] Descrever a seleção e as características dos estudos incluídos (contexto, cenário) e o processo de extração. _(CD11 §VI)_
- [ ] Apresentar a lista de códigos com definições e frequências. _(CD11 Tab. 2 #7)_
- [ ] Declarar quantos pesquisadores extraíram/codificaram, como foram resolvidas as discordâncias e os resultados de verificações de concordância. _(CD11 §II, §III, Tab. 2 #4 e #8)_
- [ ] Apresentar o mapa temático/modelo/taxonomia e a descrição dos temas, com citações para dar riqueza à apresentação. _(CD11 §V, §VI, Fig. 5)_
- [ ] Reportar a análise de sensibilidade e as limitações (dados faltantes nos estudos, agrupamentos, frequências a tratar com cautela). _(CD11 §VI)_
- [ ] Expor a trilha de auditoria e a ligação entre texto original, códigos e temas. _(CD11 §VI, Tab. 2 #9)_
- [ ] Responder explicitamente a cada pergunta de pesquisa com base nos temas. _(CD11 Tab. 2 #21)_
- [ ] Explique e justifique o uso de IA e garanta que humanos revisaram todos os resultados assistidos por IA, para evitar conclusões, dados, figuras, citações ou referências fabricados. _(G26 Ap. B.2.4(1)-(2) p.40)_
- [ ] Rep1: reporte a estratégia de prompt, o processo de desenvolvimento, os prompts usados para os resultados e a data da última execução do prompt final. _(G26 Rep1 (Tab. 5 p.20))_
- [ ] Rep2: reporte todas as configurações e parâmetros da ferramenta; reporte também a versão do modelo e valores de parâmetros na seção de métodos. _(G26 Rep2 (Tab. 5 p.20); Ap. B.2.4(4) p.41)_
- [ ] Rep3: reporte todos os custos do uso de IA (financeiros, tokens/chamadas, esforço humano) e a declaração de impacto ambiental/custo computacional, incluindo treinamento e uso, quando possível. _(G26 Rep3 (Tab. 5 p.20); Ap. B.2.4(6) p.41)_
- [ ] Rep4: relate com reprodutibilidade e meta-análise futura em mente; apoie acesso aberto a dados, algoritmos e resultados (pacote de replicação). _(G26 Rep4 (Tab. 5 p.20))_
- [ ] Rep5: relate limitações e quaisquer dúvidas remanescentes sobre a confiabilidade dos resultados da IA. _(G26 Rep5 (Tab. 5 p.20))_
- [ ] RepR2: relate qualquer uso adicional de IA para escrever o relatório da RSL. _(G26 RepR2 (Tab. 5 p.20))_
- [ ] Inclua o teste de validação e seus resultados no relatório ou material suplementar se a IA for adotada. _(G26 Ap. B.2.1 passo 11, p.39)_
- [ ] Reporte conflitos de interesse financeiros ou outros interesses ligados à adoção da ferramenta. _(G26 Ap. B.2.4(7) p.41)_
- [ ] (Avaliador) RepE1-RepE4: explicar integração ao processo de RSL, conformidade com supervisão humana, usos extras de IA na avaliação e interesses financeiros/como evitou viés. _(G26 RepE1-RepE4 (Tab. 5 p.20))_
- [ ] (Avaliador) Relate a justificativa das ferramentas, a descrição das RSLs-fonte, o papel dos humanos, templates de prompt, métricas, confiabilidade intra-ferramenta (rodar prompts várias vezes), eficácia e eficiência, viés e interesses. _(G26 Ap. B.1.3 pp.36-37)_
- [ ] Declare qualquer uso de IA na redação (como feito por Spillias et al.); o paper aceita apenas edição/refino de linguagem sem teste extra, desde que supervisionado por humanos e relatado. _(G26 Ap. B.1.3 p.37; §4.1 p.14; G4 (Tab. 2 p.10))_

## F10 — Uso de IA


### DECISÃO

- [ ] Plan1: justifique por que escolheu cada ferramenta/modelo e avalie-a criticamente (capacidades, riscos, limites) com base em estudos prévios. _(G26 Plan1 (Tab. 5 p.20); Ap. B.2.1 p.38)_
- [ ] Escolha qual modelo e versão usar, e prefira uma ferramenta aberta como baseline (PlanE2). Para seleção detalhada de ferramentas, o paper remete a Thomas et al. [92]. _(G26 Plan1, PlanE2 (Tab. 5 p.20); §3.3 p.11)_
- [ ] Se a tese também avaliar a IA (papel Avaliador), defina objetivos/hipóteses (PlanE1), suposições iniciais (PlanE3), plano de análise e meta-análise (PlanE5) e justifique datasets públicos (PlanE4). _(G26 PlanE1-PlanE5 (Tab. 5 p.20))_

### FAZER

- [ ] G1: seres humanos são responsáveis pela validade dos resultados e pela adesão à ética científica e à lei no uso de IA. Escreva isso como princípio da tese. _(G26 G1 (Tab. 2 p.10))_
- [ ] G2: todo resultado assistido por IA deve ser revisado por humanos. _(G26 G2 (Tab. 2 p.10))_
- [ ] Mantenha um registro versionado de: prompts, saídas, versões dos modelos, parâmetros, datas de execução, medidas de desempenho humanas e da IA. _(G26 Ap. B.1.1 p.35; B.2.2(2) pp.39-40)_
- [ ] O processo é iterativo: planeje -> valide a IA contra níveis aceitáveis -> se falhar, refine prompts ou ative contingência e revalide -> use; reabra a validação se surgirem casos inesperados durante a condução. _(G26 Ap. B.2.5 p.41; Fig. 2 p.42)_
- [ ] Considere tratar sua RSL como estudo de caso prospectivo de IA: rode a IA em paralelo com os humanos para gerar evidência de desempenho. _(G26 §6 p.25; PlanR3 (Tab. 5 p.20))_

### CUIDADO

- [ ] Sem itens: o capítulo (2008) não trata de IA. _(E08)_
- [ ] [CONFERIR] K07 (2007) não trata de IA/LLMs. Os únicos pontos de apoio tecnológico são gerenciadores de referências, formulários eletrônicos e gestão de documentos; qualquer uso de IA deve ser tratado com outras fontes e documentado como desvio/escolha do protocolo. _(K07 §6.1.3, §6.4.1)_
- [ ] O artigo (2015) não trata do uso de IA/LLMs em nenhuma etapa; não há recomendação de P15 sobre isso. Se a tese usar IA para triagem/extração, justificar à parte e mantê-la sujeita às mesmas verificações de confiabilidade (concordância, revisor adicional). [CONFERIR: item é inferência, não do texto] _(P15 (ausência))_
- [ ] O artigo (2015) não aborda IA/LLMs na avaliação de qualidade; não há recomendação a extrair. Se a tese usar IA para pontuar qualidade, tratar como etapa a validar contra revisores humanos. [CONFERIR: inferência, não do texto] _(Z15 (ausência))_
- [ ] Sem itens: o artigo (2011) não trata de IA. A parte de codificação com software qualitativo (§II/§III) é a única ponte e não menciona IA generativa. _(CD11)_
- [ ] G3: não atribua autoria a ferramentas de IA (não as liste como coautoras). _(G26 G3 (Tab. 2 p.10))_
- [ ] G5: a IA não deve criar o texto completo dos relatórios nem criar/alterar/manipular imagens, dados, citações, resultados, conclusões ou recomendações. _(G26 G5 (Tab. 2 p.10))_
- [ ] G6: IA não deve ser usada em revisão por pares; o paper considera G6 restritivo demais se houver salvaguardas (configurar para não reter dados), mas G6 é irrelevante para a condução da RSL. [CONFERIR: na tese, siga a política da sua instituição/periódico.] _(G26 G6 (Tab. 2 p.10); §3.2 p.10)_
- [ ] Não envie dados protegidos por direitos autorais ou sensíveis a APIs comerciais; evite plágio nos resultados assistidos por IA. _(G26 Ap. B.2.4(7) p.41)_
- [ ] Não confie em ensembles como solução mágica: combinar ferramentas reduz erros idiossincráticos, mas não elimina contaminação e aumenta custo. _(G26 §6 p.26)_

### RELATAR

- [ ] G4: relate todo uso de IA, exceto edição e refinamento de texto. _(G26 G4 (Tab. 2 p.10))_
