import { useEffect, useState } from "react";
import { Accordion, Badge, Button, Form, Spinner } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import BlockedNotice from "../../../components/BlockedNotice";
import type { DataExtractionData, ExtractionValue, Hypothesis, Verdicts } from "../../../types";
import { useReview } from "../useReview";
import { downloadFile } from "./download";
import VerdictEditor from "./VerdictEditor";

type Field = DataExtractionData["fields"][number];

function FieldInput({ field, value, onSave }: { field: Field; value: ExtractionValue; onSave: (value: ExtractionValue) => void }) {
  const [draft, setDraft] = useState(value ?? "");
  useEffect(() => setDraft(value ?? ""), [value]);
  const id = `field-${field.id}`;

  switch (field.field_type) {
    case "B":
      return (
        <Form.Select id={id} size="sm" value={String(value ?? "")} onChange={(event) => onSave(event.target.value)}>
          <option value="">—</option>
          <option value="True">Sim</option>
          <option value="False">Não</option>
        </Form.Select>
      );
    case "O":
      return (
        <Form.Select id={id} size="sm" value={value === null || value === undefined ? "" : String(value)}
          onChange={(event) => onSave(event.target.value ? Number(event.target.value) : null)}>
          <option value="">—</option>
          {field.lookups.map((lookup) => <option key={lookup.id} value={lookup.id}>{lookup.value}</option>)}
        </Form.Select>
      );
    case "M": {
      const chosen = new Set(Array.isArray(value) ? value : []);
      return (
        <div id={id}>
          {field.lookups.map((lookup) => (
            <Form.Check key={lookup.id} inline id={`${id}-${lookup.id}`} label={lookup.value} checked={chosen.has(lookup.id)}
              onChange={(event) => {
                const next = new Set(chosen);
                if (event.target.checked) next.add(lookup.id); else next.delete(lookup.id);
                onSave([...next]);
              }} />
          ))}
        </div>
      );
    }
    default:
      return (
        <Form.Control id={id} size="sm" type={field.field_type === "D" ? "date" : "text"}
          inputMode={field.field_type === "F" || field.field_type === "I" ? "decimal" : undefined}
          value={String(draft)} onChange={(event) => setDraft(event.target.value)}
          onBlur={() => { if (String(draft) !== String(value ?? "")) onSave(String(draft)); }} />
      );
  }
}

export default function DataExtractionPage() {
  const review = useReview();
  const queryClient = useQueryClient();
  const key = ["data-extraction", review.id];
  const data = useQuery({ queryKey: key, queryFn: () => api.get<DataExtractionData>(`/reviews/${review.id}/data-extraction`) });
  const hypotheses = useQuery({ queryKey: ["hypotheses", review.id], queryFn: () => api.get<Hypothesis[]>(`/reviews/${review.id}/hypotheses`) });
  const verdicts = useQuery({ queryKey: ["verdicts", review.id], queryFn: () => api.get<Verdicts>(`/reviews/${review.id}/verdicts`) });
  const save = useMutation({
    mutationFn: ({ articleId, fieldId, value }: { articleId: number; fieldId: number; value: ExtractionValue }) =>
      api.put(`/reviews/${review.id}/articles/${articleId}/extraction`, { field_id: fieldId, value }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: key }),
  });
  const finish = useMutation({
    mutationFn: ({ articleId, finished }: { articleId: number; finished: boolean }) =>
      api.put(`/reviews/${review.id}/articles/${articleId}/extraction-status`, { finished }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: key }),
  });
  const exportData = useMutation({
    mutationFn: () => downloadFile(`/reviews/${review.id}/data-extraction/export`, `${review.name}-extracao.csv`),
  });

  const exportButton = (
    <Button size="sm" variant="outline-secondary" onClick={() => exportData.mutate()}>
      <i className="bi bi-download me-1" />Exportar dados
    </Button>
  );

  if (data.isLoading) return <Spinner animation="border" />;
  if (data.error || !data.data) return <ErrorAlert error={data.error} />;
  if (data.data.fields.length === 0) {
    return (
      <BlockedNotice message="Monte o formulário de extração no planejamento antes desta etapa."
        to={`/revisoes/${review.id}/planejamento/extracao`} linkLabel="Ir para o formulário" />
    );
  }

  const done = data.data.articles.filter((article) => article.finished_data_extraction).length;

  return (
    <Panel title="Extração de dados" actions={exportButton}>
      <ErrorAlert error={save.error ?? finish.error ?? exportData.error} />
      {data.data.articles.length === 0 ? (
        <BlockedNotice message="Nenhum estudo aceito acima da nota de corte da avaliação de qualidade."
          to={`/revisoes/${review.id}/conducao/qualidade`} linkLabel="Ir para a avaliação" />
      ) : (
        <>
          <p className="small text-muted">{done} de {data.data.articles.length} estudos com extração concluída.</p>
          <Accordion alwaysOpen>
            {data.data.articles.map((article) => (
              <Accordion.Item key={article.id} eventKey={String(article.id)}>
                <Accordion.Header>
                  <div className="d-flex w-100 justify-content-between align-items-center pe-3 gap-2">
                    <span>
                      <span className="fw-semibold">{article.title}</span>
                      <span className="small text-muted d-block">{article.author} · {article.year}</span>
                    </span>
                    {article.finished_data_extraction
                      ? <Badge bg="success"><i className="bi bi-check2 me-1" />Concluída</Badge>
                      : <Badge bg="secondary">Em andamento</Badge>}
                  </div>
                </Accordion.Header>
                <Accordion.Body>
                  {data.data.fields.map((field) => (
                    <Form.Group key={field.id} className="mb-2">
                      <Form.Label htmlFor={`field-${field.id}`} className="small mb-1">{field.description}</Form.Label>
                      <FieldInput field={field} value={article.values[String(field.id)] ?? null}
                        onSave={(value) => save.mutate({ articleId: article.id, fieldId: field.id, value })} />
                    </Form.Group>
                  ))}
                  <VerdictEditor articleId={article.id} hypotheses={hypotheses.data ?? []} verdicts={verdicts.data} />
                  <Form.Check type="switch" id={`finished-${article.id}`} className="mt-3" label="Extração concluída"
                    checked={article.finished_data_extraction}
                    onChange={(event) => finish.mutate({ articleId: article.id, finished: event.target.checked })} />
                </Accordion.Body>
              </Accordion.Item>
            ))}
          </Accordion>
        </>
      )}
    </Panel>
  );
}
