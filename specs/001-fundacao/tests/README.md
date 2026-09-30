# Testes do módulo 001

Os casos de teste a seguir devem ser implementados antes da codificação funcional (TDD), seguindo a rastreabilidade da spec 001.

- CT-FND-01: acesso de `observador` em escrita
- CT-FND-02: `revisor` sem acesso a administrador
- CT-FND-03: auditoria de alteração de dado
- CT-FND-04: auditoria append-only no banco
- CT-FND-05: requisição sem token retorna 401
- CT-FND-06: upload de artefato cria nova versão
- CT-FND-07: restore com perda de no máximo 24h
- CT-FND-08: matriz papel x endpoint com 403 em não permitidos

Todos os testes devem ser vinculados a um `CA-##` da spec e executados na CI antes de liberar a build.
