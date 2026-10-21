import { useState, type FormEvent } from "react";
import { Button, Col, Form, ListGroup, Row } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { Hypothesis } from "../../../types";
import { useReview } from "../useReview";

const EMPTY = { code: "", statement: "", independent_variables: "", dependent_variables: "", operational_criteria: "" };

/** Optional protocol section: hypotheses whose verdicts are recorded per study in the extraction step. */
export default function HypothesesSection() {
  const review = useReview();
  const queryClient = useQueryClient();
  const key = ["hypotheses", review.id];
  const hypotheses = useQuery({ queryKey: key, queryFn: () => api.get<Hypothesis[]>(`/reviews/${review.id}/hypotheses`) });
  const [form, setForm] = useState<typeof EMPTY & { id?: number }>(EMPTY);
  const refresh = () => queryClient.invalidateQueries({ queryKey: key });
  const save = useMutation({
    mutationFn: () => form.id
      ? api.patch(`/reviews/${review.id}/hypotheses/${form.id}`, form)
      : api.post(`/reviews/${review.id}/hypotheses`, form),
    onSuccess: () => { setForm(EMPTY); refresh(); },
  });
  const remove = useMutation({ mutationFn: (id: number) => api.delete(`/reviews/${review.id}/hypotheses/${id}`), onSuccess: refresh });

  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate();
  }

  const field = (name: keyof typeof EMPTY, label: string) => (
    <Form.Group className="mb-2" controlId={`hyp-${name}`}>
      <Form.Label className="small mb-1">{label}</Form.Label>
      <Form.Control size="sm" required={name === "code" || name === "statement"} value={form[name]}
        onChange={(event) => setForm({ ...form, [name]: event.target.value })} />
    </Form.Group>
  );

  return (
    <Panel id="hipoteses" title="Hipóteses (opcional)">
      <p className="small text-muted">Se a revisão testa hipóteses, cadastre-as aqui. Os vereditos são dados estudo a estudo na extração de dados.</p>
      <ErrorAlert error={hypotheses.error ?? save.error ?? remove.error} />
      <ListGroup variant="flush" className="mb-3">
        {hypotheses.data?.map((item) => (
          <ListGroup.Item key={item.id} className="px-0 small d-flex justify-content-between gap-2">
            <div>
              <strong>{item.code}</strong>: {item.statement}
              {(item.independent_variables || item.dependent_variables) && (
                <div className="text-muted">VI: {item.independent_variables || "—"} · VD: {item.dependent_variables || "—"}</div>
              )}
              {item.operational_criteria && <div className="text-muted">Critério: {item.operational_criteria}</div>}
            </div>
            <div className="text-nowrap">
              <Button size="sm" variant="link" className="p-0 me-2" onClick={() => setForm({ ...item })}>Editar</Button>
              <Button size="sm" variant="link" className="p-0 text-danger" onClick={() => remove.mutate(item.id)}>Remover</Button>
            </div>
          </ListGroup.Item>
        ))}
      </ListGroup>
      <Form onSubmit={submit}>
        <Row className="g-2">
          <Col sm={3}>{field("code", "Identificador")}</Col>
          <Col sm={9}>{field("statement", "Enunciado")}</Col>
          <Col sm={6}>{field("independent_variables", "Variáveis independentes")}</Col>
          <Col sm={6}>{field("dependent_variables", "Variáveis dependentes")}</Col>
          <Col sm={12}>{field("operational_criteria", "Critério operacional dos vereditos")}</Col>
        </Row>
        <Button type="submit" size="sm" disabled={save.isPending}>{form.id ? "Salvar hipótese" : "Adicionar hipótese"}</Button>
        {form.id && <Button size="sm" variant="link" onClick={() => setForm(EMPTY)}>Cancelar</Button>}
      </Form>
    </Panel>
  );
}
