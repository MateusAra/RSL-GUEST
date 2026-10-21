import { useState, type FormEvent } from "react";
import { Alert, Badge, Button, ButtonGroup, Dropdown, Form, Modal, Spinner, Table } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { Code, CodeEvent } from "../../../types";
import { useReview } from "../useReview";
import { downloadFile } from "../conducting/download";
import { useCodes, useSynthesisMutation } from "./useSynthesis";

const STATUS_BG: Record<Code["status"], string> = { draft: "warning", active: "success", merged: "secondary", removed: "dark" };
const ACTIONS: Record<string, string> = {
  created: "criado", imported: "importado", activated: "ativado", renamed: "renomeado", redefined: "redefinido",
  merged: "fundido", created_by_merge: "criado por fusão", removed: "removido",
};

type Draft = { id?: number; name: string; definition: string; limits: string; justification: string; active: boolean };

function CodeModal({ draft, onHide }: { draft: Draft; onHide: () => void }) {
  const [form, setForm] = useState(draft);
  const save = useSynthesisMutation((base, value: Draft) => value.id
    ? api.patch(`${base}/codes/${value.id}`, { name: value.name, definition: value.definition, limits: value.limits, justification: value.justification })
    : api.post(`${base}/codes`, { name: value.name, definition: value.definition, limits: value.limits }));

  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate(form, { onSuccess: onHide });
  }

  return (
    <Modal show onHide={onHide}>
      <Form onSubmit={submit}>
        <Modal.Header closeButton><Modal.Title className="h6 mb-0">{form.id ? "Editar código" : "Novo código"}</Modal.Title></Modal.Header>
        <Modal.Body>
          <ErrorAlert error={save.error} />
          <Form.Group className="mb-2" controlId="code-name">
            <Form.Label className="small mb-1">Nome</Form.Label>
            <Form.Control required maxLength={200} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          </Form.Group>
          <Form.Group className="mb-2" controlId="code-definition">
            <Form.Label className="small mb-1">Definição</Form.Label>
            <Form.Control as="textarea" rows={3} value={form.definition} onChange={(event) => setForm({ ...form, definition: event.target.value })} />
          </Form.Group>
          <Form.Group className="mb-2" controlId="code-limits">
            <Form.Label className="small mb-1">Limites (o que não entra neste código)</Form.Label>
            <Form.Control as="textarea" rows={2} value={form.limits} onChange={(event) => setForm({ ...form, limits: event.target.value })} />
          </Form.Group>
          {form.active && (
            <Form.Group controlId="code-justification">
              <Form.Label className="small mb-1">Justificativa da alteração</Form.Label>
              <Form.Control required value={form.justification} onChange={(event) => setForm({ ...form, justification: event.target.value })} />
            </Form.Group>
          )}
          <Form.Text>Defina limites explícitos para que os códigos não se sobreponham.</Form.Text>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button type="submit" disabled={save.isPending}>Salvar</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

function MergeModal({ codes, onHide }: { codes: Code[]; onHide: () => void }) {
  const [form, setForm] = useState({ name: codes[0]?.name ?? "", definition: "", limits: "", justification: "" });
  const merge = useSynthesisMutation((base) => api.post(`${base}/codes/merge`, { ...form, code_ids: codes.map((code) => code.id) }));
  return (
    <Modal show onHide={onHide}>
      <Form onSubmit={(event) => { event.preventDefault(); merge.mutate(undefined, { onSuccess: onHide }); }}>
        <Modal.Header closeButton><Modal.Title className="h6 mb-0">Fundir {codes.length} códigos</Modal.Title></Modal.Header>
        <Modal.Body>
          <ErrorAlert error={merge.error} />
          <p className="small">{codes.map((code) => code.name).join(" + ")}. Os trechos migram para o novo código e a origem fica no histórico.</p>
          {(["name", "definition", "limits", "justification"] as const).map((field) => (
            <Form.Group key={field} className="mb-2" controlId={`merge-${field}`}>
              <Form.Label className="small mb-1">
                {{ name: "Nome do novo código", definition: "Definição", limits: "Limites", justification: "Justificativa" }[field]}
              </Form.Label>
              <Form.Control required value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })} />
            </Form.Group>
          ))}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button type="submit" disabled={merge.isPending}>Fundir</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

function RemoveModal({ code, codes, onHide }: { code: Code; codes: Code[]; onHide: () => void }) {
  const [form, setForm] = useState({ migrate_to_id: "", justification: "" });
  const remove = useSynthesisMutation((base) => api.post(`${base}/codes/${code.id}/remove`, {
    migrate_to_id: form.migrate_to_id ? Number(form.migrate_to_id) : null, justification: form.justification }));
  return (
    <Modal show onHide={onHide}>
      <Form onSubmit={(event) => { event.preventDefault(); remove.mutate(undefined, { onSuccess: onHide }); }}>
        <Modal.Header closeButton><Modal.Title className="h6 mb-0">Remover "{code.name}"</Modal.Title></Modal.Header>
        <Modal.Body>
          <ErrorAlert error={remove.error} />
          {code.segments > 0 && <p className="small">Este código tem {code.segments} trecho(s). Migre-os ou justifique o descarte.</p>}
          <Form.Group className="mb-2" controlId="remove-target">
            <Form.Label className="small mb-1">Migrar trechos para</Form.Label>
            <Form.Select value={form.migrate_to_id} onChange={(event) => setForm({ ...form, migrate_to_id: event.target.value })}>
              <option value="">— descartar os trechos —</option>
              {codes.filter((item) => item.status === "active" && item.id !== code.id).map((item) => (
                <option key={item.id} value={item.id}>{item.name}</option>
              ))}
            </Form.Select>
          </Form.Group>
          <Form.Group controlId="remove-justification">
            <Form.Label className="small mb-1">Justificativa</Form.Label>
            <Form.Control value={form.justification} onChange={(event) => setForm({ ...form, justification: event.target.value })} />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button variant="danger" type="submit" disabled={remove.isPending}>Remover</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

function HistoryModal({ code, onHide }: { code: Code; onHide: () => void }) {
  const review = useReview();
  const history = useQuery({
    queryKey: ["synthesis", review.id, "history", code.id],
    queryFn: () => api.get<CodeEvent[]>(`/reviews/${review.id}/codes/${code.id}/history`),
  });
  return (
    <Modal show onHide={onHide} size="lg">
      <Modal.Header closeButton><Modal.Title className="h6 mb-0">Histórico de "{code.name}"</Modal.Title></Modal.Header>
      <Modal.Body>
        {history.isLoading ? <Spinner animation="border" /> : (
          <Table size="sm" className="small">
            <thead><tr><th>#</th><th>Data</th><th>Quem</th><th>Ação</th><th>Antes → depois</th><th>Justificativa</th></tr></thead>
            <tbody>
              {history.data?.map((event) => (
                <tr key={event.sequence}>
                  <td>{event.sequence}</td>
                  <td className="text-nowrap">{new Date(event.created_at).toLocaleString("pt-BR")}</td>
                  <td>{event.user}</td>
                  <td>{ACTIONS[event.action] ?? event.action}</td>
                  <td>
                    {event.previous && "name" in event.previous && event.new && "name" in event.new && event.previous.name !== event.new.name
                      ? `${String(event.previous.name)} → ${String(event.new.name)}`
                      : event.action === "created_by_merge" && event.previous
                        ? `absorveu: ${(event.previous.absorbed as string[]).join(", ")}` : ""}
                  </td>
                  <td>{event.justification}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Modal.Body>
    </Modal>
  );
}

export default function CodebookPage() {
  const review = useReview();
  const codes = useCodes();
  const [editing, setEditing] = useState<Draft | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [merging, setMerging] = useState(false);
  const [removing, setRemoving] = useState<Code | null>(null);
  const [history, setHistory] = useState<Code | null>(null);
  const importList = useSynthesisMutation((base) => api.post<{ created: number }>(`${base}/codes/import-start-list`));
  const activate = useSynthesisMutation((base, id: number) => api.post(`${base}/codes/${id}/activate`));
  const exportEvents = useSynthesisMutation((_, format: "csv" | "json") =>
    downloadFile(`/reviews/${review.id}/coding/events?format=${format}`, `${review.name}-codificacao.${format}`));

  if (codes.isLoading) return <Spinner animation="border" />;
  const list = codes.data ?? [];
  const selectedCodes = list.filter((code) => selected.has(code.id));

  return (
    <Panel
      title="Codebook"
      actions={
        <div className="d-flex gap-2">
          <Button size="sm" onClick={() => setEditing({ name: "", definition: "", limits: "", justification: "", active: false })}>
            <i className="bi bi-plus-lg me-1" />Novo código
          </Button>
          <Button size="sm" variant="outline-primary" onClick={() => importList.mutate()}>Importar lista inicial</Button>
          <Dropdown>
            <Dropdown.Toggle size="sm" variant="outline-secondary">Histórico</Dropdown.Toggle>
            <Dropdown.Menu align="end">
              <Dropdown.Item onClick={() => exportEvents.mutate("csv")}>Exportar CSV</Dropdown.Item>
              <Dropdown.Item onClick={() => exportEvents.mutate("json")}>Exportar JSON</Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      }
    >
      <ErrorAlert error={codes.error ?? importList.error ?? activate.error ?? exportEvents.error} />
      {importList.isSuccess && (
        <Alert variant="info" className="py-2 small">
          {importList.data.created} código(s) dedutivo(s) importado(s) dos campos de seleção do formulário de extração.
        </Alert>
      )}
      <p className="small text-muted">
        Códigos nascem como rascunho e só são aplicados depois de ativados, com definição e limites. A lista inicial vem dos
        valores dos campos de seleção do formulário de extração.
      </p>
      {list.length === 0 ? <p className="text-muted mb-0">Nenhum código ainda.</p> : (
        <Table size="sm" className="align-middle small">
          <thead>
            <tr><th /><th>Código</th><th>Tipo</th><th>Status</th><th>Definição / limites</th><th className="text-end">Trechos</th><th /></tr>
          </thead>
          <tbody>
            {list.map((code) => (
              <tr key={code.id} className={code.status === "merged" || code.status === "removed" ? "text-muted" : undefined}>
                <td>
                  {code.status === "active" && (
                    <Form.Check aria-label={`Selecionar ${code.name}`} checked={selected.has(code.id)} onChange={(event) => {
                      const next = new Set(selected);
                      if (event.target.checked) next.add(code.id); else next.delete(code.id);
                      setSelected(next);
                    }} />
                  )}
                </td>
                <td className="fw-semibold">{code.name}</td>
                <td>{code.kind_label}</td>
                <td><Badge bg={STATUS_BG[code.status]}>{code.status_label}</Badge></td>
                <td style={{ maxWidth: 280 }}>
                  <div>{code.definition || <span className="text-muted">sem definição</span>}</div>
                  {code.limits && <div className="text-muted">Limites: {code.limits}</div>}
                </td>
                <td className="text-end">{code.segments}</td>
                <td className="text-end text-nowrap">
                  <ButtonGroup size="sm">
                    {code.status === "draft" && (
                      <Button variant="outline-success" onClick={() => activate.mutate(code.id)}>Ativar</Button>
                    )}
                    {(code.status === "draft" || code.status === "active") && (
                      <>
                        <Button variant="outline-primary" aria-label="Editar" onClick={() => setEditing({
                          id: code.id, name: code.name, definition: code.definition, limits: code.limits, justification: "",
                          active: code.status === "active" })}>
                          <i className="bi bi-pencil" />
                        </Button>
                        <Button variant="outline-danger" aria-label="Remover" onClick={() => setRemoving(code)}>
                          <i className="bi bi-trash" />
                        </Button>
                      </>
                    )}
                    <Button variant="outline-secondary" aria-label="Histórico" onClick={() => setHistory(code)}>
                      <i className="bi bi-clock-history" />
                    </Button>
                  </ButtonGroup>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      <Button size="sm" variant="outline-secondary" disabled={selectedCodes.length < 2} onClick={() => setMerging(true)}>
        <i className="bi bi-intersect me-1" />Fundir selecionados ({selectedCodes.length})
      </Button>
      {editing && <CodeModal draft={editing} onHide={() => setEditing(null)} />}
      {merging && <MergeModal codes={selectedCodes} onHide={() => { setMerging(false); setSelected(new Set()); }} />}
      {removing && <RemoveModal code={removing} codes={list} onHide={() => setRemoving(null)} />}
      {history && <HistoryModal code={history} onHide={() => setHistory(null)} />}
    </Panel>
  );
}
