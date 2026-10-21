import { useRef, useState } from "react";
import { Alert, Button, Form, Modal, Spinner, Table } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import BlockedNotice from "../../../components/BlockedNotice";
import type { ImportSummary } from "../../../types";
import { useReview } from "../useReview";

type ImportReport = { file_name: string; imported: number; total: number; skipped_without_title: number; encoding: string };

function ManualArticleModal({ sourceId, onHide }: { sourceId: number; onHide: () => void }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ title: "", author: "", journal: "", year: "", doi: "", abstract: "" });
  const create = useMutation({
    mutationFn: () => api.post(`/reviews/${review.id}/articles`, { ...form, source_id: sourceId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["imports", review.id] });
      queryClient.invalidateQueries({ queryKey: ["articles", review.id] });
      onHide();
    },
  });
  const field = (name: keyof typeof form, label: string) => (
    <Form.Group className="mb-2" controlId={`manual-${name}`}>
      <Form.Label className="small mb-1">{label}</Form.Label>
      {name === "abstract" ? (
        <Form.Control size="sm" as="textarea" rows={4} value={form[name]}
          onChange={(event) => setForm({ ...form, [name]: event.target.value })} />
      ) : (
        <Form.Control size="sm" required={name === "title"} value={form[name]}
          onChange={(event) => setForm({ ...form, [name]: event.target.value })} />
      )}
    </Form.Group>
  );

  return (
    <Modal show onHide={onHide}>
      <Form onSubmit={(event) => { event.preventDefault(); create.mutate(); }}>
        <Modal.Header closeButton><Modal.Title>Novo artigo</Modal.Title></Modal.Header>
        <Modal.Body>
          <ErrorAlert error={create.error} />
          {field("title", "Título")}
          {field("author", "Autores")}
          {field("journal", "Periódico / evento")}
          {field("year", "Ano")}
          {field("doi", "DOI")}
          {field("abstract", "Resumo")}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button type="submit" disabled={create.isPending}>Adicionar</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

export default function ImportPage() {
  const review = useReview();
  const queryClient = useQueryClient();
  const inputs = useRef<Record<number, HTMLInputElement | null>>({});
  const [report, setReport] = useState<ImportReport | null>(null);
  const [manualSource, setManualSource] = useState<number | null>(null);
  const summary = useQuery({ queryKey: ["imports", review.id], queryFn: () => api.get<ImportSummary>(`/reviews/${review.id}/imports`) });
  const upload = useMutation({
    mutationFn: ({ sourceId, file }: { sourceId: number; file: File }) => {
      const form = new FormData();
      form.append("file", file);
      return api.upload<ImportReport>(`/reviews/${review.id}/sources/${sourceId}/import`, form);
    },
    onSuccess: (data) => {
      setReport(data);
      queryClient.invalidateQueries({ queryKey: ["imports", review.id] });
      queryClient.invalidateQueries({ queryKey: ["articles", review.id] });
    },
  });

  if (summary.isLoading) return <Spinner animation="border" />;
  if (summary.error || !summary.data) return <ErrorAlert error={summary.error} />;
  if (summary.data.length === 0) {
    return (
      <BlockedNotice message="Adicione as fontes da revisão no protocolo para importar estudos."
        to={`/revisoes/${review.id}/planejamento#fontes`} linkLabel="Ir para Fontes" />
    );
  }

  return (
    <Panel title="Importar estudos">
      <p className="small text-muted">Envie o arquivo exportado de cada fonte em BibTeX (.bib), RIS (.ris) ou CSV.</p>
      <ErrorAlert error={upload.error} />
      {report && (
        <Alert variant="success" className="py-2 small" dismissible onClose={() => setReport(null)}>
          <strong>{report.file_name}</strong>: {report.imported} estudo(s) importado(s)
          {report.skipped_without_title > 0 && `, ${report.skipped_without_title} ignorado(s) por não ter título`}.
          {report.encoding === "latin-1" && " Arquivo lido como Latin-1: confira os acentos."}
        </Alert>
      )}
      <Table className="align-middle">
        <thead>
          <tr><th>Fonte</th><th className="text-end">Estudos</th><th>Arquivos importados</th><th /></tr>
        </thead>
        <tbody>
          {summary.data.map((item) => (
            <tr key={item.source.id}>
              <td className="fw-semibold">{item.source.name}</td>
              <td className="text-end">{item.articles}</td>
              <td className="small">
                {item.files.length === 0 ? <span className="text-muted">—</span> : item.files.map((file) => (
                  <div key={file.id}>{file.file_name} <span className="text-muted">({file.imported_count})</span></div>
                ))}
              </td>
              <td className="text-end text-nowrap">
                <input type="file" accept=".bib,.bibtex,.ris,.csv,.txt" hidden
                  ref={(element) => { inputs.current[item.source.id] = element; }}
                  onChange={(event) => {
                    const file = event.target.files?.[0];
                    if (file) upload.mutate({ sourceId: item.source.id, file });
                    event.target.value = "";
                  }} />
                <Button size="sm" className="me-2" disabled={upload.isPending}
                  onClick={() => inputs.current[item.source.id]?.click()}>
                  <i className="bi bi-upload me-1" />Importar
                </Button>
                <Button size="sm" variant="outline-secondary" onClick={() => setManualSource(item.source.id)}>
                  Novo artigo
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      {manualSource !== null && <ManualArticleModal sourceId={manualSource} onHide={() => setManualSource(null)} />}
    </Panel>
  );
}
