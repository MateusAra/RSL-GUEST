"""PRISMA 2020 checklist (27 items and sub-items).

Items follow Page MJ, McKenzie JE, Bossuyt PM et al. "The PRISMA 2020 statement: an updated guideline for
reporting systematic reviews", BMJ 2021;372:n71, distributed under CC BY 4.0. The Portuguese descriptions
below are short adaptations written for this tool, not the official translation.
"""

from __future__ import annotations

PRISMA_ATTRIBUTION = (
    "Checklist baseado no PRISMA 2020 (Page MJ et al., BMJ 2021;372:n71), licença CC BY 4.0. "
    "Descrições adaptadas e resumidas; consulte o texto oficial em prisma-statement.org."
)

# (item, section, topic, description)
PRISMA_ITEMS: list[tuple[str, str, str, str]] = [
    ("1", "Título", "Título", "Identificar o relato como revisão sistemática."),
    ("2", "Resumo", "Resumo", "Apresentar resumo estruturado conforme o checklist PRISMA 2020 para resumos."),
    ("3", "Introdução", "Justificativa", "Descrever a justificativa da revisão no contexto do conhecimento existente."),
    ("4", "Introdução", "Objetivos", "Declarar explicitamente os objetivos ou as perguntas da revisão."),
    ("5", "Métodos", "Critérios de elegibilidade", "Especificar os critérios de inclusão e exclusão e como os estudos foram agrupados para a síntese."),
    ("6", "Métodos", "Fontes de informação", "Listar bases, registros, sites e demais fontes consultadas, com a data da última busca em cada uma."),
    ("7", "Métodos", "Estratégia de busca", "Apresentar as estratégias de busca completas de todas as bases, incluindo filtros e limites."),
    ("8", "Métodos", "Processo de seleção", "Descrever como se decidiu a inclusão: quantos revisores, de forma independente ou não, e ferramentas usadas."),
    ("9", "Métodos", "Processo de coleta de dados", "Descrever como os dados foram extraídos: quantos revisores, independência e confirmação com autores."),
    ("10a", "Métodos", "Itens de dados (desfechos)", "Listar e definir os desfechos buscados e como os resultados compatíveis foram escolhidos."),
    ("10b", "Métodos", "Itens de dados (outras variáveis)", "Listar e definir as demais variáveis extraídas e os pressupostos sobre dados ausentes ou incertos."),
    ("11", "Métodos", "Avaliação do risco de viés", "Especificar o método de avaliação de risco de viés ou qualidade dos estudos, quantos avaliadores e ferramentas."),
    ("12", "Métodos", "Medidas de efeito", "Especificar as medidas de efeito usadas para cada desfecho na síntese ou apresentação."),
    ("13a", "Métodos", "Métodos de síntese (elegibilidade)", "Descrever como se decidiu quais estudos entram em cada síntese."),
    ("13b", "Métodos", "Métodos de síntese (preparação)", "Descrever a preparação dos dados para apresentação ou síntese, como tratamento de dados ausentes."),
    ("13c", "Métodos", "Métodos de síntese (apresentação)", "Descrever os métodos de tabulação ou exibição visual dos resultados."),
    ("13d", "Métodos", "Métodos de síntese (síntese)", "Descrever os métodos de síntese e a justificativa da escolha."),
    ("13e", "Métodos", "Métodos de síntese (heterogeneidade)", "Descrever os métodos usados para explorar causas de heterogeneidade."),
    ("13f", "Métodos", "Métodos de síntese (sensibilidade)", "Descrever as análises de sensibilidade feitas para avaliar a robustez dos resultados."),
    ("14", "Métodos", "Avaliação de viés de relato", "Descrever como foi avaliado o risco de viés por resultados ausentes (viés de publicação)."),
    ("15", "Métodos", "Avaliação da certeza", "Descrever os métodos para avaliar a certeza ou confiança no corpo de evidências."),
    ("16a", "Resultados", "Seleção dos estudos", "Descrever os resultados da busca e da seleção, do total identificado ao incluído, de preferência com fluxograma."),
    ("16b", "Resultados", "Seleção dos estudos (exclusões)", "Citar estudos que pareciam atender aos critérios mas foram excluídos, explicando o motivo."),
    ("17", "Resultados", "Características dos estudos", "Citar cada estudo incluído e apresentar suas características."),
    ("18", "Resultados", "Risco de viés nos estudos", "Apresentar a avaliação de risco de viés ou qualidade de cada estudo incluído."),
    ("19", "Resultados", "Resultados dos estudos individuais", "Apresentar, para cada estudo, os dados ou estatísticas dos desfechos."),
    ("20a", "Resultados", "Resultados das sínteses (características)", "Resumir as características e o risco de viés dos estudos de cada síntese."),
    ("20b", "Resultados", "Resultados das sínteses (resultados)", "Apresentar os resultados de todas as sínteses estatísticas ou qualitativas feitas."),
    ("20c", "Resultados", "Resultados das sínteses (heterogeneidade)", "Apresentar os resultados das investigações de causas de heterogeneidade."),
    ("20d", "Resultados", "Resultados das sínteses (sensibilidade)", "Apresentar os resultados das análises de sensibilidade."),
    ("21", "Resultados", "Vieses de relato", "Apresentar a avaliação do risco de viés por resultados ausentes em cada síntese."),
    ("22", "Resultados", "Certeza da evidência", "Apresentar a avaliação da certeza ou confiança na evidência de cada desfecho."),
    ("23a", "Discussão", "Discussão (interpretação)", "Interpretar os resultados no contexto de outras evidências."),
    ("23b", "Discussão", "Discussão (limitações das evidências)", "Discutir as limitações da evidência incluída na revisão."),
    ("23c", "Discussão", "Discussão (limitações da revisão)", "Discutir as limitações dos processos usados na revisão."),
    ("23d", "Discussão", "Discussão (implicações)", "Discutir as implicações para a prática, as políticas e pesquisas futuras."),
    ("24a", "Outras informações", "Registro", "Informar o registro da revisão (nome e número) ou declarar que não foi registrada."),
    ("24b", "Outras informações", "Protocolo", "Indicar onde o protocolo pode ser acessado ou declarar que não foi preparado."),
    ("24c", "Outras informações", "Alterações do protocolo", "Descrever e justificar alterações em relação ao registro ou ao protocolo."),
    ("25", "Outras informações", "Apoio", "Descrever as fontes de apoio financeiro ou não financeiro e o papel dos financiadores."),
    ("26", "Outras informações", "Conflitos de interesse", "Declarar os conflitos de interesse dos autores."),
    ("27", "Outras informações", "Disponibilidade de dados e materiais", "Informar o que está disponível publicamente (formulários, dados, código, outros materiais) e onde."),
]
PRISMA_KEYS = {item for item, *_ in PRISMA_ITEMS}
PRISMA_STATUSES = {"met": "Atendido", "not_met": "Não atendido", "na": "Não se aplica"}
