# ADR-001 — Autenticação e sessões
Status: aceita
Data: 2026-09-29

Contexto:
A constituição exige autenticação obrigatória para todo acesso e papéis diferenciados (`admin`, `revisor`, `terceiro_revisor`, `observador`). A spec 001 define login e autorização por endpoint, mas não fixa o mecanismo exato.

Decisão:
O sistema usará cadastro individual por usuário, com email e senha simples, armazenados com hash no backend. A autenticação será feita por sessão com token JWT e refresh token rotativo. A solução foi escolhida por ser simples de operar, segura o suficiente no escopo da RSL e compatível com a arquitetura proposta.

Alternativas consideradas:
- SSO institucional: bom para governança, porém depende de integrações externas e de políticas de identidade da instituição.
- Cadastro por equipe ou credenciais compartilhadas: descartado por quebrar rastreabilidade e auditoria individual.
- Sessões server-side somente: mais simples de revogar, porém menos apropriado para API REST e front SPA.

Consequências:
- Vantagens: controle individual de acesso, rastreabilidade clara, gestão simples de papéis e compatibilidade com API REST.
- Desvantagens: exige cuidado com hash de senha, expiração de token e revogação de sessão.
- Observação: a implementação deve registrar cada usuário de forma individual e manter a auditoria de ações por pessoa.
