import { useEffect, useState, type FormEvent } from "react";
import { Button, ButtonGroup, Col, Form, InputGroup, ListGroup, Row, Table } from "react-bootstrap";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import InlineEdit from "../../../components/InlineEdit";
import AddInput from "../../../components/AddInput";
import type { Planning } from "../../../types";
import { usePlanningMutation } from "./usePlanning";

export default function QualityChecklistPage({ planning }: { planning: Planning }) {
  const [answer, setAnswer] = useState({ description: "", weight: "" });
  const [cutoff, setCutoff] = useState(String(planning.quality_cutoff_score));
  useEffect(() => setCutoff(String(planning.quality_cutoff_score)), [planning.quality_cutoff_score]);

  const addQuestion = usePlanningMutation((base, description: string) => api.post(`${base}/quality-questions`, { description }));
  const editQuestion = usePlanningMutation((base, args: { id: number; description: string }) =>
    api.patch(`${base}/quality-questions/${args.id}`, { description: args.description }));
  const removeQuestion = usePlanningMutation((base, id: number) => api.delete(`${base}/quality-questions/${id}`));
  const reorder = usePlanningMutation((base, ids: number[]) => api.put(`${base}/quality-questions/order`, { ids }));
  const addAnswer = usePlanningMutation((base, payload: { description: string; weight: number }) =>
    api.post(`${base}/quality-answers`, payload));
  const suggested = usePlanningMutation((base) => api.post(`${base}/quality-answers/suggested`));
  const editAnswer = usePlanningMutation((base, args: { id: number; description: string; weight: number }) =>
    api.patch(`${base}/quality-answers/${args.id}`, args));
  const removeAnswer = usePlanningMutation((base, id: number) => api.delete(`${base}/quality-answers/${id}`));
  const saveCutoff = usePlanningMutation((base) =>
    api.put(`${base}/quality-cutoff`, { quality_cutoff_score: Number(cutoff.replace(",", ".")) }));

  function move(index: number, delta: number) {
    const ids = planning.quality_questions.map((question) => question.id);
    const [moved] = ids.splice(index, 1);
    ids.splice(index + delta, 0, moved);
    reorder.mutate(ids);
  }

  function submitAnswer(event: FormEvent) {
    event.preventDefault();
    addAnswer.mutate(
      { description: answer.description, weight: Number(answer.weight.replace(",", ".")) },
      { onSuccess: () => setAnswer({ description: "", weight: "" }) },
    );
  }

  function submitCutoff(event: FormEvent) {
    event.preventDefault();
    saveCutoff.mutate();
  }

  const error = addQuestion.error ?? editQuestion.error ?? removeQuestion.error ?? reorder.error ?? addAnswer.error
    ?? suggested.error ?? editAnswer.error ?? removeAnswer.error ?? saveCutoff.error;

  return (
    <>
      <ErrorAlert error={error} />
      <Panel title="Perguntas">
        <ListGroup variant="flush" className="mb-3">
          {planning.quality_questions.map((question, index) => (
            <ListGroup.Item key={question.id} className="px-0 d-flex align-items-start gap-2">
              <span className="text-muted small mt-1">Q{index + 1}</span>
              <div className="flex-grow-1">
                <InlineEdit value={question.description} maxLength={255}
                  onSave={(description) => editQuestion.mutate({ id: question.id, description })} />
              </div>
              <ButtonGroup size="sm">
                <Button variant="outline-secondary" disabled={index === 0} aria-label="Subir" onClick={() => move(index, -1)}>
                  <i className="bi bi-arrow-up" />
                </Button>
                <Button variant="outline-secondary" disabled={index === planning.quality_questions.length - 1}
                  aria-label="Descer" onClick={() => move(index, 1)}>
                  <i className="bi bi-arrow-down" />
                </Button>
                <Button variant="outline-danger" aria-label="Remover" onClick={() => removeQuestion.mutate(question.id)}>
                  <i className="bi bi-trash" />
                </Button>
              </ButtonGroup>
            </ListGroup.Item>
          ))}
          {planning.quality_questions.length === 0 && (
            <ListGroup.Item className="px-0 text-muted">Nenhuma pergunta de qualidade.</ListGroup.Item>
          )}
        </ListGroup>
        <AddInput placeholder="Nova pergunta de qualidade" maxLength={255} onAdd={(text) => addQuestion.mutate(text)} />
      </Panel>

      <Panel
        title="Respostas"
        actions={
          <Button size="sm" variant="outline-primary" onClick={() => suggested.mutate()}>
            Adicionar respostas sugeridas
          </Button>
        }
      >
        <Table size="sm" className="align-middle">
          <thead>
            <tr><th>Descrição</th><th style={{ width: 140 }}>Peso</th><th /></tr>
          </thead>
          <tbody>
            {planning.quality_answers.map((item) => (
              <tr key={item.id}>
                <td>
                  <InlineEdit value={item.description} maxLength={255}
                    onSave={(description) => editAnswer.mutate({ id: item.id, description, weight: item.weight })} />
                </td>
                <td>
                  <InlineEdit value={String(item.weight)}
                    onSave={(weight) => editAnswer.mutate({ id: item.id, description: item.description,
                      weight: Number(weight.replace(",", ".")) })} />
                </td>
                <td className="text-end">
                  <Button size="sm" variant="outline-danger" aria-label="Remover resposta" onClick={() => removeAnswer.mutate(item.id)}>
                    <i className="bi bi-trash" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
        <Form onSubmit={submitAnswer} className="d-flex gap-2">
          <Form.Control size="sm" placeholder="Nova resposta" required maxLength={255} value={answer.description}
            aria-label="Nova resposta" onChange={(event) => setAnswer({ ...answer, description: event.target.value })} />
          <Form.Control size="sm" placeholder="Peso" required inputMode="decimal" style={{ maxWidth: 110 }}
            aria-label="Peso" value={answer.weight} onChange={(event) => setAnswer({ ...answer, weight: event.target.value })} />
          <Button type="submit" size="sm" className="text-nowrap"><i className="bi bi-plus-lg me-1" />Adicionar</Button>
        </Form>
      </Panel>

      <Panel title="Pontuação">
        <Row className="g-3 align-items-end">
          <Col sm={6}>
            <div className="small text-muted">Pontuação máxima</div>
            <div className="fs-4 fw-semibold">{planning.quality_max_score.toLocaleString("pt-BR")}</div>
            <div className="small text-muted">nº de perguntas × maior peso de resposta</div>
          </Col>
          <Col sm={6}>
            <Form onSubmit={submitCutoff}>
              <Form.Label htmlFor="cutoff" className="small">Nota de corte</Form.Label>
              <InputGroup size="sm">
                <Form.Control id="cutoff" inputMode="decimal" value={cutoff} onChange={(event) => setCutoff(event.target.value)} />
                <Button type="submit" disabled={saveCutoff.isPending}>Salvar</Button>
              </InputGroup>
              <Form.Text>Estudos com pontuação abaixo do corte não seguem para a extração.</Form.Text>
            </Form>
          </Col>
        </Row>
      </Panel>
    </>
  );
}
