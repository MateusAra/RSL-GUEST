import { useState } from "react";
import { Accordion, Badge, Form, Spinner, Table } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import BlockedNotice from "../../../components/BlockedNotice";
import type { QualityAssessmentData } from "../../../types";
import { useReview } from "../useReview";
import { useMyAssignments } from "../team/useAssignments";

export default function QualityAssessmentPage() {
  const review = useReview();
  const mine = useMyAssignments("quality");
  const [onlyMine, setOnlyMine] = useState(false);
  const queryClient = useQueryClient();
  const key = ["quality-assessment", review.id];
  const data = useQuery({ queryKey: key, queryFn: () => api.get<QualityAssessmentData>(`/reviews/${review.id}/quality-assessment`) });
  const save = useMutation({
    mutationFn: ({ articleId, questionId, answerId }: { articleId: number; questionId: number; answerId: number }) =>
      api.put(`/reviews/${review.id}/articles/${articleId}/quality`, { question_id: questionId, answer_id: answerId }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: key }),
  });

  if (data.isLoading) return <Spinner animation="border" />;
  if (data.error || !data.data) return <ErrorAlert error={data.error} />;
  const { questions, answers, articles } = data.data;
  if (questions.length === 0 || answers.length === 0) {
    return (
      <BlockedNotice message="Cadastre as perguntas e as respostas do checklist de qualidade antes desta etapa."
        to={`/revisoes/${review.id}/planejamento/qualidade`} linkLabel="Ir para o checklist" />
    );
  }
  if (articles.length === 0) {
    return (
      <BlockedNotice message="Nenhum estudo aceito ainda. Aceite estudos na seleção para avaliá-los."
        to={`/revisoes/${review.id}/conducao/selecao`} linkLabel="Ir para a seleção" />
    );
  }

  const assessed = articles.filter((article) => article.complete).length;
  const visible = onlyMine && mine ? articles.filter((article) => mine.has(article.id)) : articles;

  return (
    <Panel title="Avaliação de qualidade"
      actions={<span className="small text-muted"><Form.Check type="switch" id="only-mine" className="small d-inline-block me-3" label="Atribuídos a mim"
          checked={onlyMine} onChange={(event) => setOnlyMine(event.target.checked)} />{assessed} de {articles.length} avaliados · corte {data.data.cutoff_score} de {data.data.max_score}</span>}>
      <ErrorAlert error={save.error} />
      <Accordion alwaysOpen>
        {visible.map((article) => (
          <Accordion.Item key={article.id} eventKey={String(article.id)}>
            <Accordion.Header>
              <div className="d-flex w-100 justify-content-between align-items-center pe-3 gap-2">
                <span>
                  <span className="fw-semibold">{article.title}</span>
                  <span className="small text-muted d-block">{article.author} · {article.year}</span>
                </span>
                <span className="text-nowrap">
                  <Badge bg={article.passed ? "success" : "secondary"}>
                    {article.score.toLocaleString("pt-BR")} / {data.data.max_score.toLocaleString("pt-BR")}
                  </Badge>{" "}
                  {!article.complete && <Badge bg="warning" text="dark">incompleta</Badge>}
                </span>
              </div>
            </Accordion.Header>
            <Accordion.Body>
              <Table size="sm" className="align-middle small mb-0">
                <thead>
                  <tr>
                    <th>Pergunta</th>
                    {answers.map((answer) => <th key={answer.id} className="text-center">{answer.description} ({answer.weight})</th>)}
                  </tr>
                </thead>
                <tbody>
                  {questions.map((question) => (
                    <tr key={question.id}>
                      <td>{question.description}</td>
                      {answers.map((answer) => (
                        <td key={answer.id} className="text-center">
                          <Form.Check type="radio" name={`qa-${article.id}-${question.id}`}
                            aria-label={`${question.description}: ${answer.description}`}
                            checked={article.answers[String(question.id)] === answer.id}
                            onChange={() => save.mutate({ articleId: article.id, questionId: question.id, answerId: answer.id })} />
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Accordion.Body>
          </Accordion.Item>
        ))}
      </Accordion>
    </Panel>
  );
}
