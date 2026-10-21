# Plano do módulo 001 — Fundação

Status: aprovada pelo PO

## 1. Objetivo
Este plano operacionaliza a spec 001 para a camada transversal do sistema: autenticação, papéis, auditoria imutável, armazenamento de artefatos e recuperação de desastres. O escopo aqui é a base sobre a qual os módulos 002–011 se apoiam.

## 2. Decisões técnicas e pendências
A especificação do módulo exige decisões humanas fora do escopo de código. O plano abaixo assume uma abordagem conservadora e não substitui a aprovação do PO.

- Autenticação: cadastro individual por usuário, com email e senha simples armazenados com hash no backend; autenticação por sessão com JWT assinado e refresh token rotativo. A opção SSO institucional foi descartada por enquanto.
- Banco: PostgreSQL relacional com migrações versionadas e escrita otimista por campo `version`.
- Frontend: SPA em React + TypeScript com rotas protegidas por papel.
- Armazenamento: MinIO compatível com S3 para PDFs e raw results.
- Estatística: `krippendorff` + `scikit-learn` para κ/α, com validação manual em ≥ 3 casos antes de uso em produção.
- Hospedagem: proposta inicial de ambiente de desenvolvimento e produção em infraestrutura containerizada institucional ou cloud; a escolha final fica em ADR-006.

## 3. Modelo de dados

### 3.1 Entidades centrais

- `user`
  - id
  - email
  - password_hash
  - status
  - role
  - created_at
  - updated_at
  - version

- `project`
  - id
  - name
  - slug
  - owner_user_id
  - status
  - created_at
  - updated_at
  - version

- `project_member`
  - project_id
  - user_id
  - role
  - created_at
  - version

- `audit_event`
  - id
  - entity_type
  - entity_id
  - action
  - actor_user_id
  - performed_at_utc
  - previous_value
  - new_value
  - ip_address
  - request_id

- `artifact`
  - id
  - project_id
  - file_name
  - object_key
  - content_hash_sha256
  - mime_type
  - version
  - created_by
  - created_at
  - is_deleted

- `backup_job`
  - id
  - started_at
  - finished_at
  - status
  - file_path_or_uri
  - rpo_hours
  - created_by

### 3.2 Regras de integridade
- `audit_event` é append-only; nenhuma linha pode ser atualizada ou apagada pela aplicação.
- `observador` nunca pode receber permissão de escrita em qualquer endpoint.
- `artifact` nunca é sobrescrito; um novo upload cria uma nova versão e preserva a anterior.
- `version` deve ser incrementado em cada escrita para permitir escrita otimista.
- `project_member` deve garantir que o mesmo usuário não seja R1 e R2 no mesmo estudo.

## 4. Contratos de API

### 4.1 Autenticação
- `POST /api/v1/auth/login`
  - body: `{ email, password }`
  - response: `{ access_token, refresh_token, user }`
- `POST /api/v1/auth/refresh`
  - body: `{ refresh_token }`
- `POST /api/v1/auth/logout`
  - requires auth

### 4.2 Administração de usuários e papéis
- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/:id`
- `PATCH /api/v1/users/:id/role`
- `PATCH /api/v1/users/:id/status`

### 4.3 Projetos e membros
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/:id`
- `POST /api/v1/projects/:id/members`
- `DELETE /api/v1/projects/:id/members/:userId`

### 4.4 Auditoria
- `GET /api/v1/audit-events`
  - filtros: `entity_type`, `entity_id`, `actor_user_id`, `from`, `to`
- `GET /api/v1/audit-events/export`
  - exporta JSON/CSV

### 4.5 Arquivos e objetos
- `POST /api/v1/artifacts/upload`
  - multipart/form-data
  - headers: auth token
  - response: `artifact_id`, `object_key`, `sha256`, `version`
- `GET /api/v1/artifacts/:id`
- `GET /api/v1/artifacts/:id/versions`

### 4.6 Backup e restore
- `POST /api/v1/backups/run`
- `GET /api/v1/backups`
- `POST /api/v1/backups/:id/restore`

## 5. Segurança e auditoria
- Toda alteração deve passar pelo contexto de auditoria na mesma transação, com `author`, `performed_at_utc`, `previous_value` e `new_value`.
- Autorização deve ser verificada no servidor em cada endpoint.
- Requisições sem token resultam em `401` e não alcançam a camada de domínio.
- `observador` está limitado a leitura mesmo que a UI tente enviar mudanças por script.

## 6. ADRs previstos
- ADR-001: autenticação e sessões
- ADR-002: stack back-end e banco de dados
- ADR-003: stack front-end
- ADR-004: armazenamento de objetos
- ADR-005: biblioteca de cálculo estatístico para κ e α
- ADR-006: hospedagem e ambiente

## 7. Entregável mínimo do módulo 001
O módulo 001 deve entregar uma base funcional em três frentes:
1. login e papéis com autorização por endpoint;
2. registro de auditoria append-only e exportação;
3. upload de artefatos + backup/restore automatizado em ambiente de teste.

## 8. Riscos e mitigação
- Ausência de decisão do PO sobre SSO vs senha própria: bloquear a implementação do login final até o ADR-001 ser aprovado.
- Contaminação de dados por armazenamento de arquivos sem hash: bloquear qualquer upload sem validação SHA-256.
- Mudanças de schema sem migração: proibir edições manuais em produção e exigir reversão via migração.

## 9. Próximo passo
Com a aprovação do PO, transformar este plano em tarefas executáveis e começar pela suíte de testes dos CA-01 a CA-08 da spec 001.
