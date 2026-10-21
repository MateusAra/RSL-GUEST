import { useState, type FormEvent } from "react";
import { Accordion, Badge, Button, Form, Modal, Spinner } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { ThemeRow } from "../../../types";
import { useReview } from "../useReview";
import { useCodes, useSynthesisMutation } from "./useSynthesis";
import ThemeMap from "./ThemeMap";

function ThemeModal({ themes, onHide }: { themes: ThemeRow[]; onHide: () => void }) {
  const codes = useCodes();
  const [form, setForm] = useState({ name: "", description: "", justification: "" });
  const [codeIds, setCodeIds] = useState<Set<number>>(new Set());
  const [childIds, setChildIds] = useState<Set<number>>(new Set());
  const create = useSynthesisMutation((base) => api.post(`${base}/themes`, {
    ...form, code_ids: [...codeIds], child_theme_ids: [...childIds] }));
  const toggle = (set: Set<number>, update: (next: Set<number>) => void, id: number, value: boolean) => {
    const next = new Set(set);
    if (value) next.add(id); else next.delete(id);
    update(next);
  };

  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate(undefined, { onSuccess: onHide });
  }

  return (
    <Modal show onHide={onHide} size="lg">
      <Form onSubmit={submit}>
        <Modal.Header closeButton><Modal.Title className="h6 mb-0">Novo tema</Modal.Title></Modal.Header>
        <Modal.Body>
          <ErrorAlert error={create.error} />
          <Form.Group className="mb-2" controlId="theme-name">
            <Form.Label className="small mb-1">Nome</Form.Label>
            <Form.Control required maxLength={200} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} />
          </Form.Group>
          <Form.Group className="mb-3" controlId="theme-description">
            <Form.Label className="small mb-1">Descrição</Form.Label>
            <Form.Control as="textarea" rows={2} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} />
          </Form.Group>
          <div className="small fw-semibold mb-1">Códigos</div>
          <div className="d-flex flex-wrap gap-2 mb-3">
            {(codes.data ?? []).filter((code) => code.status === "active").map((code) => (
              <Form.Check key={code.id} inline className="me-0 small" id={`theme-code-${code.id}`} label={`${code.name} (${code.segments})`}
                checked={codeIds.has(code.id)} onChange={(event) => toggle(codeIds, setCodeIds, code.id, event.target.checked)} />
            ))}
          </div>
          {themes.length > 0 && (
            <>
              <div className="small fw-semibold mb-1">Ou agrupe temas existentes (tema de ordem superior)</div>
              <div className="d-flex flex-wrap gap-2 mb-3">
                {themes.map((theme) => (
                  <Form.Check key={theme.id} inline className="me-0 small" id={`theme-child-${theme.id}`} label={theme.name}
                    checked={childIds.has(theme.id)} onChange={(event) => toggle(childIds, setChildIds, theme.id, event.target.checked)} />
                ))}
              </div>
            </>
          )}
          <Form.Group controlId="theme-justification">
            <Form.Label className="small mb-1">Justificativa (se algum código já estiver em outro tema)</Form.Label>
            <Form.Control value={form.justification} onChange={(event) => setForm({ ...form, justification: event.target.value })} />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button type="submit" disabled={create.isPending}>Criar tema</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

export default function ThemesPage() {
  const review = useReview();
  const [creating, setCreating] = useState(false);
  const themes = useQuery({ queryKey: ["synthesis", review.id, "themes"], queryFn: () => api.get<ThemeRow[]>(`/reviews/${review.id}/themes`) });
  const remove = useSynthesisMutation((base, id: number) => api.delete(`${base}/themes/${id}`));
  const removeCode = useSynthesisMutation((base, args: { theme: number; code: number }) =>
    api.delete(`${base}/themes/${args.theme}/codes/${args.code}`));

  if (themes.isLoading) return <Spinner animation="border" />;
  const list = themes.data ?? [];
  const byId = new Map(list.map((theme) => [theme.id, theme]));

  return (
    <>
      <Panel title="Mapa temático">
        {list.length === 0 ? <p className="text-muted mb-0">Crie temas a partir dos códigos para ver o mapa.</p> : <ThemeMap themes={list} />}
      </Panel>
      <Panel title="Temas" actions={<Button size="sm" onClick={() => setCreating(true)}><i className="bi bi-plus-lg me-1" />Novo tema</Button>}>
        <ErrorAlert error={themes.error ?? remove.error ?? removeCode.error} />
        <Accordion alwaysOpen>
          {list.map((theme) => {
            const children = list.filter((item) => item.parent_id === theme.id);
            return (
              <Accordion.Item key={theme.id} eventKey={String(theme.id)}>
                <Accordion.Header>
                  <span className="fw-semibold me-2">{theme.name}</span>
                  {children.length > 0 && <Badge bg="dark" className="me-1">ordem superior</Badge>}
                  {theme.parent_id && <Badge bg="light" text="dark">em {byId.get(theme.parent_id)?.name}</Badge>}
                </Accordion.Header>
                <Accordion.Body className="small">
                  {theme.description && <p>{theme.description}</p>}
                  {children.length > 0 && <p>Agrupa: {children.map((child) => child.name).join(", ")}</p>}
                  {theme.codes.map((code) => (
                    <div key={code.id} className="mb-3">
                      <div className="d-flex justify-content-between">
                        <span><Badge bg="primary">{code.name}</Badge> <span className="text-muted">{code.evidence.length} trecho(s)</span>
                          {code.justification && <span className="text-muted"> · {code.justification}</span>}</span>
                        <Button size="sm" variant="link" className="p-0 text-danger"
                          onClick={() => removeCode.mutate({ theme: theme.id, code: code.id })}>Tirar do tema</Button>
                      </div>
                      {code.evidence.map((item) => (
                        <blockquote key={item.id} className="border-start ps-2 mt-1 mb-1">
                          “{item.text}” <span className="text-muted">— {item.article_title}, p. {item.page}</span>
                        </blockquote>
                      ))}
                    </div>
                  ))}
                  <Button size="sm" variant="outline-danger" onClick={() => remove.mutate(theme.id)}>Remover tema</Button>
                </Accordion.Body>
              </Accordion.Item>
            );
          })}
        </Accordion>
      </Panel>
      {creating && <ThemeModal themes={list} onHide={() => setCreating(false)} />}
    </>
  );
}
