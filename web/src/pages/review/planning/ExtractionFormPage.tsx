import { useState, type FormEvent } from "react";
import { Badge, Button, ButtonGroup, Form, Modal, Table } from "react-bootstrap";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { ExtractionField, Planning } from "../../../types";
import { usePlanningMutation } from "./usePlanning";

type Draft = { id?: number; description: string; field_type: ExtractionField["field_type"]; lookups: string };

const EMPTY: Draft = { description: "", field_type: "S", lookups: "" };
const SELECT_TYPES = new Set(["O", "M"]);

function FieldModal({ draft, planning, onHide }: { draft: Draft | null; planning: Planning; onHide: () => void }) {
  const [form, setForm] = useState<Draft>(draft ?? EMPTY);
  const save = usePlanningMutation((base, payload: Draft) => {
    const body = {
      description: payload.description,
      field_type: payload.field_type,
      lookups: payload.lookups.split("\n").map((value) => value.trim()).filter(Boolean),
    };
    return payload.id
      ? api.patch(`${base}/extraction-fields/${payload.id}`, body)
      : api.post(`${base}/extraction-fields`, body);
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate(form, { onSuccess: onHide });
  }

  return (
    <Modal show onHide={onHide}>
      <Form onSubmit={submit}>
        <Modal.Header closeButton>
          <Modal.Title>{form.id ? "Editar campo" : "Novo campo"}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ErrorAlert error={save.error} />
          <Form.Group className="mb-3" controlId="field-description">
            <Form.Label>Descrição</Form.Label>
            <Form.Control autoFocus required maxLength={255} value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })} />
          </Form.Group>
          <Form.Group className="mb-3" controlId="field-type">
            <Form.Label>Tipo</Form.Label>
            <Form.Select value={form.field_type}
              onChange={(event) => setForm({ ...form, field_type: event.target.value as Draft["field_type"] })}>
              {Object.entries(planning.field_types).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </Form.Select>
          </Form.Group>
          {SELECT_TYPES.has(form.field_type) && (
            <Form.Group controlId="field-lookups">
              <Form.Label>Valores (um por linha)</Form.Label>
              <Form.Control as="textarea" rows={5} required value={form.lookups}
                onChange={(event) => setForm({ ...form, lookups: event.target.value })} />
            </Form.Group>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button type="submit" disabled={save.isPending}>Salvar</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

export default function ExtractionFormPage({ planning }: { planning: Planning }) {
  const [draft, setDraft] = useState<Draft | null>(null);
  const [open, setOpen] = useState(false);
  const remove = usePlanningMutation((base, id: number) => api.delete(`${base}/extraction-fields/${id}`));
  const reorder = usePlanningMutation((base, ids: number[]) => api.put(`${base}/extraction-fields/order`, { ids }));
  const fields = planning.data_extraction_fields;

  function openField(field?: ExtractionField) {
    setDraft(field ? {
      id: field.id,
      description: field.description,
      field_type: field.field_type,
      lookups: field.lookups.map((lookup) => lookup.value).join("\n"),
    } : null);
    setOpen(true);
  }

  function move(index: number, delta: number) {
    const ids = fields.map((field) => field.id);
    const [moved] = ids.splice(index, 1);
    ids.splice(index + delta, 0, moved);
    reorder.mutate(ids);
  }

  return (
    <Panel
      title="Formulário de extração de dados"
      actions={<Button size="sm" onClick={() => openField()}><i className="bi bi-plus-lg me-1" />Adicionar campo</Button>}
    >
      <ErrorAlert error={remove.error ?? reorder.error} />
      {fields.length === 0 ? (
        <p className="text-muted mb-0">Defina os campos que serão preenchidos para cada estudo aceito.</p>
      ) : (
        <Table size="sm" className="align-middle">
          <thead>
            <tr><th>Descrição</th><th>Tipo</th><th>Valores</th><th /></tr>
          </thead>
          <tbody>
            {fields.map((field, index) => (
              <tr key={field.id}>
                <td>{field.description}</td>
                <td><Badge bg="light" text="dark">{field.field_type_label}</Badge></td>
                <td className="small">{field.lookups.map((lookup) => lookup.value).join(", ") || "—"}</td>
                <td className="text-end text-nowrap">
                  <ButtonGroup size="sm">
                    <Button variant="outline-secondary" disabled={index === 0} aria-label="Subir" onClick={() => move(index, -1)}>
                      <i className="bi bi-arrow-up" />
                    </Button>
                    <Button variant="outline-secondary" disabled={index === fields.length - 1} aria-label="Descer"
                      onClick={() => move(index, 1)}>
                      <i className="bi bi-arrow-down" />
                    </Button>
                    <Button variant="outline-primary" aria-label="Editar" onClick={() => openField(field)}>
                      <i className="bi bi-pencil" />
                    </Button>
                    <Button variant="outline-danger" aria-label="Remover" onClick={() => remove.mutate(field.id)}>
                      <i className="bi bi-trash" />
                    </Button>
                  </ButtonGroup>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {open && <FieldModal draft={draft} planning={planning} onHide={() => setOpen(false)} />}
    </Panel>
  );
}
