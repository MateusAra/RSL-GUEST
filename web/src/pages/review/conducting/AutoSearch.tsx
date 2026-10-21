import { useEffect, useState } from "react";
import { Alert, Badge, Button, Col, Form, Row, Table } from "react-bootstrap";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import ErrorAlert from "../../../components/ErrorAlert";
import type { ApiKeyInfo, ConnectorInfo, SearchRun } from "../../../types";

export function useConnectors() {
  return useQuery({ queryKey: ["search-connectors"], queryFn: () => api.get<ConnectorInfo[]>("/search/connectors"), staleTime: Infinity });
}

const STATUS_VARIANT: Record<SearchRun["status"], string> = { queued: "secondary", running: "info", done: "success", failed: "danger" };

function RunSummary({ run }: { run: SearchRun }) {
  if (run.status === "queued" || run.status === "running") {
    return <span>{run.retrieved.toLocaleString("pt-BR")} registro(s) recebido(s){run.total_reported != null && ` de ${run.total_reported.toLocaleString("pt-BR")}`}…</span>;
  }
  if (run.status === "failed") return <span className="text-danger">{run.error}</span>;
  const total = run.total_reported == null ? "" : `${run.total_reported.toLocaleString("pt-BR")} na base`;
  if (run.mode === "preview") return <span>Prévia: {total}</span>;
  return (
    <span>
      {total}{total && " · "}{run.imported} importado(s)
      {run.skipped_existing > 0 && ` · ${run.skipped_existing} já existiam`}
    </span>
  );
}

/** Automated search of one source through its API, next to the source's search string. */
export default function AutoSearch({ reviewId, sourceId, connectorKey, hasString }: {
  reviewId: number; sourceId: number; connectorKey: string; hasString: boolean;
}) {
  const queryClient = useQueryClient();
  const connectors = useConnectors();
  const keys = useQuery({ queryKey: ["api-keys"], queryFn: () => api.get<ApiKeyInfo[]>("/me/api-keys") });
  const [form, setForm] = useState({ year_from: "", year_to: "", max_records: "1000" });
  const runs = useQuery({
    queryKey: ["search-runs", reviewId, sourceId],
    queryFn: () => api.get<SearchRun[]>(`/reviews/${reviewId}/search-runs?source_id=${sourceId}`),
    refetchInterval: (query) => (query.state.data?.some((run) => run.status === "queued" || run.status === "running") ? 2000 : false),
  });
  const start = useMutation({
    mutationFn: (mode: "preview" | "import") => api.post<SearchRun>(`/reviews/${reviewId}/sources/${sourceId}/search-runs`, {
      mode,
      year_from: form.year_from ? Number(form.year_from) : null,
      year_to: form.year_to ? Number(form.year_to) : null,
      max_records: Number(form.max_records) || 1000,
    }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["search-runs", reviewId, sourceId] }),
  });

  const latest = runs.data?.[0];
  const importedRun = latest?.mode === "import" && latest.status === "done" ? latest.id : null;
  useEffect(() => {
    if (importedRun === null) return;
    queryClient.invalidateQueries({ queryKey: ["imports", reviewId] });
    queryClient.invalidateQueries({ queryKey: ["articles", reviewId] });
  }, [importedRun, reviewId, queryClient]);

  const connector = connectors.data?.find((item) => item.key === connectorKey);
  if (!connector) return null;
  const key = keys.data?.find((item) => item.provider === connector.provider);
  const missingKey = connector.key_required && key !== undefined && !key.configured;
  const busy = start.isPending || latest?.status === "queued" || latest?.status === "running";

  return (
    <div className="border rounded p-3 mt-3">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <div className="fw-semibold"><i className="bi bi-lightning-charge me-1" />Busca automática — {connector.label}</div>
        {connector.provider && key && (
          key.configured
            ? <Badge bg="success">chave ···{key.last_four}</Badge>
            : <Badge bg={connector.key_required ? "warning" : "light"} text="dark">{connector.key_required ? "chave necessária" : "sem chave (opcional)"}</Badge>
        )}
      </div>
      {connector.notice && <Alert variant="info" className="small py-2">{connector.notice}</Alert>}
      <p className="small text-muted mb-2">
        A string salva acima é enviada exatamente como está. {connector.syntax_help}
      </p>
      {missingKey && (
        <Alert variant="warning" className="small py-2">
          Cadastre sua chave em <Link to="/perfil">Perfil › Chaves de API</Link> para buscar no {connector.label}.
        </Alert>
      )}
      <ErrorAlert error={start.error} />
      <Row className="g-2 align-items-end mb-2">
        <Col xs={4} md={2}>
          <Form.Label htmlFor={`from-${sourceId}`} className="small mb-1">Ano de</Form.Label>
          <Form.Control id={`from-${sourceId}`} size="sm" type="number" min={1900} max={2100} value={form.year_from}
            onChange={(event) => setForm({ ...form, year_from: event.target.value })} />
        </Col>
        <Col xs={4} md={2}>
          <Form.Label htmlFor={`to-${sourceId}`} className="small mb-1">até</Form.Label>
          <Form.Control id={`to-${sourceId}`} size="sm" type="number" min={1900} max={2100} value={form.year_to}
            onChange={(event) => setForm({ ...form, year_to: event.target.value })} />
        </Col>
        <Col xs={4} md={2}>
          <Form.Label htmlFor={`limit-${sourceId}`} className="small mb-1">Limite</Form.Label>
          <Form.Control id={`limit-${sourceId}`} size="sm" type="number" min={1} max={connector.max_records} value={form.max_records}
            onChange={(event) => setForm({ ...form, max_records: event.target.value })} />
        </Col>
        <Col className="d-flex gap-2">
          <Button size="sm" variant="outline-primary" disabled={busy || !hasString || missingKey} onClick={() => start.mutate("preview")}>
            Prévia
          </Button>
          <Button size="sm" disabled={busy || !hasString || missingKey} onClick={() => start.mutate("import")}>
            <i className="bi bi-cloud-download me-1" />Buscar e importar
          </Button>
        </Col>
      </Row>
      {!hasString && <div className="small text-muted mb-2">Salve a string desta fonte para habilitar a busca.</div>}

      {latest?.mode === "preview" && latest.status === "done" && latest.preview && (
        <div className="mb-3">
          <div className="small fw-semibold mb-1">
            Prévia: {latest.total_reported?.toLocaleString("pt-BR") ?? "?"} resultado(s) na base; primeiros {latest.preview.length}:
          </div>
          <ol className="small mb-0 ps-3">
            {latest.preview.map((item, index) => (
              <li key={index}>{item.title} <span className="text-muted">— {item.author.split(";")[0]}{item.year && `, ${item.year}`}{item.journal && ` · ${item.journal}`}</span></li>
            ))}
          </ol>
        </div>
      )}
      {latest?.warnings.map((warning) => <Alert key={warning} variant="warning" className="small py-2">{warning}</Alert>)}

      {runs.data && runs.data.length > 0 && (
        <Table size="sm" className="small mb-0">
          <thead><tr><th>Data</th><th>Tipo</th><th>Anos</th><th>Situação</th><th>Resultado</th></tr></thead>
          <tbody>
            {runs.data.slice(0, 8).map((run) => (
              <tr key={run.id}>
                <td className="text-nowrap">{new Date(run.created_at).toLocaleString("pt-BR")}</td>
                <td>{run.mode === "preview" ? "Prévia" : "Importação"}</td>
                <td className="text-nowrap">{run.year_from || run.year_to ? `${run.year_from ?? "…"}–${run.year_to ?? "…"}` : "—"}</td>
                <td><Badge bg={STATUS_VARIANT[run.status]}>{run.status_label}</Badge></td>
                <td><RunSummary run={run} /></td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
}
