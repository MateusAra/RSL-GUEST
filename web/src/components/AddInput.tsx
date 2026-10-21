import { useState, type FormEvent } from "react";
import { Button, Form, InputGroup } from "react-bootstrap";

type AddInputProps = {
  placeholder: string;
  buttonLabel?: string;
  onAdd: (value: string) => void;
  maxLength?: number;
  disabled?: boolean;
};

/** Text input that adds an item on Enter or on the button, then clears itself. */
export default function AddInput({ placeholder, buttonLabel = "Adicionar", onAdd, maxLength, disabled }: AddInputProps) {
  const [value, setValue] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    const text = value.trim();
    if (!text) return;
    onAdd(text);
    setValue("");
  }

  return (
    <Form onSubmit={submit}>
      <InputGroup size="sm">
        <Form.Control value={value} placeholder={placeholder} maxLength={maxLength} aria-label={placeholder}
          onChange={(event) => setValue(event.target.value)} />
        <Button type="submit" disabled={disabled}>
          <i className="bi bi-plus-lg me-1" />
          {buttonLabel}
        </Button>
      </InputGroup>
    </Form>
  );
}
