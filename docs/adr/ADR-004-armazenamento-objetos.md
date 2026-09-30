# ADR-004 — Armazenamento de objetos
Status: aceita
Data: 2026-09-29

Contexto:
A spec 001 exige armazenamento de objetos para PDFs e raw results, imutabilidade por versão e hash de integridade. O sistema precisa guardar artefatos sem sobrescrita e permitir restauração segura.

Decisão:
MinIO compatível com S3 permanece como backend de objetos para produção. **Decisão complementar do PO (2026-09-29):** para desenvolvimento local e UAT, usar um adaptador de filesystem persistente quando a imagem MinIO não estiver acessível no registry. A aplicação mantém a mesma interface de objetos, hash SHA-256 e versionamento no metadado; o fallback local não é opção de produção.

Alternativas consideradas:
- S3 nativo: melhor para produção crítica, porém pode exigir custos e dependências externas maiores.
- Armazenamento local em disco: simples, mas pouco adequado para versionamento, backup e recuperação estruturada.

Consequências:
- Vantagens: versionamento natural, compatibilidade com APIs de objetos e pronta integração com os requisitos de integridade.
- Desvantagens: exige cuidado com políticas de retenção e backup do bucket.
- Observação: o bucket deve manter hashes e metadados de versão, não apenas o conteúdo bruto.
- UAT local: o volume Docker `rsl_artifact_data` preserva objetos entre reinicializações; selecionar o backend por `OBJECT_STORAGE_BACKEND=filesystem`. Para produção, configurar `OBJECT_STORAGE_BACKEND=minio` e as variáveis `MINIO_*`.
