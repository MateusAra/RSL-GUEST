import { useEffect, useState, type KeyboardEvent } from "react";
import { Button, Form, InputGroup } from "react-bootstrap";

type InlineEditProps = {
  value: string;
  onSave: (value: string) => void;
  placeholder?: string;
  maxLength?: number;
};

/** Text shown as-is; click "editar" to change it in place (Enter saves, Esc cancels). */
export default function InlineEdit({ value, onSave, placeholder, maxLength }: InlineEditProps) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value);

  useEffect(() => setDraft(value), [value]);

  function save() {
    const next = draft.trim();
    if (next && next !== value) onSave(next);
    setEditing(false);
  }

  function keyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault();
      save();
    } else if (event.key === "Escape") {
      setDraft(value);
      setEditing(false);
    }
  }

  if (!editing) {
    return (
      <span className="d-inline-flex align-items-center gap-2">
        <span>{value || <span className="text-muted">{placeholder}</span>}</span>
        <Button variant="link" size="sm" className="p-0" aria-label="Editar" onClick={() => setEditing(true)}>
          <i className="bi bi-pencil" />
        </Button>
      </span>
    );
  }

  return (
    <InputGroup size="sm">
      <Form.Control autoFocus value={draft} maxLength={maxLength} placeholder={placeholder}
        onChange={(event) => setDraft(event.target.value)} onKeyDown={keyDown} />
      <Button size="sm" onClick={save}>Salvar</Button>
      <Button size="sm" variant="outline-secondary" onClick={() => { setDraft(value); setEditing(false); }}>
        Cancelar
      </Button>
    </InputGroup>
  );
}
