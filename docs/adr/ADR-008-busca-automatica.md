# ADR-008 — Busca automática pelas APIs das bases
Status: aceita
Data: 2026-10-21

Contexto:
Até aqui cada busca era feita fora da ferramenta: o pesquisador rodava a string no site da base, exportava BibTeX/RIS/CSV e importava o arquivo. O objetivo é disparar as buscas por dentro da ferramenta, sem perder a importação manual.

Decisão:
- Um conector por API oficial:
  - IEEE Xplore, Scopus, ScienceDirect, Springer Nature e Web of Science Starter, que exigem chave;
  - arXiv, OpenAlex e Semantic Scholar, que não exigem.
  - Cada fonte sugerida vem com o seu conector (`sources.connector`). As fontes próprias podem usar OpenAlex ou Semantic Scholar.
- A string enviada é exatamente a string da fonte salva em Condução › 1, na sintaxe nativa da base. O sistema não traduz nada.
- **ACM Digital Library:** não tem API pública de busca, e raspar o site viola os termos de uso. A busca usa o OpenAlex filtrado pela editora ACM (`publisher_lineage:P4310319798`). A tela e o relato avisam que a sintaxe e os resultados não são idênticos aos do dl.acm.org.
- **Google Scholar:** não tem API, e os termos proíbem a raspagem. Continua só com a importação manual.
- **Chaves de API:**
  - são de cada usuário e ficam cifradas com Fernet (`RSL_SECRET_KEY`), sem nunca voltar para o cliente;
  - a busca usa a chave de quem a dispara, que fica registrada na execução.
- **Execução:**
  - cada execução (`search_runs`) roda em segundo plano, com pausas e novas tentativas conforme a política de cada API;
  - é atômica: se falhar, nada é importado;
  - grava o JSON bruto das respostas como o arquivo do `SearchResult`;
  - ao rodar de novo a mesma fonte, os registros já existentes (DOI ou título normalizado) são ignorados.
- O relato PRISMA ganha a tabela "Estratégia de busca executada": data, forma (API ou arquivo), string exata, anos, total na base e importados (item 7 do PRISMA 2020).

Alternativas consideradas:
- **Raspar o site da ACM e o Google Scholar:** descartado por violar os termos de uso e esbarrar em CAPTCHA.
- **Chave por revisão, compartilhada pela equipe:** descartado. As licenças das APIs são pessoais ou institucionais.
- **Tradução automática da string base para cada sintaxe:** fica para depois. Uma tradução errada mudaria a busca sem que o pesquisador percebesse.

Consequências:
- **Buscas reprodutíveis e registradas**, sem exportar nem importar arquivos à mão.
- **Diferenças de cobertura entre API e site:** algumas APIs devolvem menos campos que a exportação do site, e isso aparece como aviso na execução.
  - O Scopus sem token institucional não traz resumo.
  - O ScienceDirect e a Web of Science Starter não trazem resumo.
- **Cotas:** as cotas diárias das APIs limitam buscas muito grandes; o limite por execução é de 5000 registros.
