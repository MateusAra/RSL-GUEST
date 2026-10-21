import { useEffect, useState } from "react";
import { Button, Col, Form, Modal, Nav, Row, Spinner, Tab } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import ErrorAlert from "../../../components/ErrorAlert";
import StatusBadge, { STATUS_LABELS } from "../../../components/StatusBadge";
import type { Article, ArticleStatus, Planning } from "../../../types";
import { useReview } from "../useReview";
import AssigneeSelect from "./AssigneeSelect";
import Discussion from "./Discussion";

const EDITABLE: { key: keyof Article; label: string; rows?: number }[] = [
  { key: "title", label: "Título" },
  { key: "author", label: "Autores" },
  { key: "journal", label: "Periódico / evento" },
  { key: "year", label: "Ano" },
  { key: "doi", label: "DOI" },
  { key: "url", label: "URL" },
  { key: "keywords", label: "Palavras-chave" },
  { key: "abstract", label: "Resumo", rows: 6 },
];

type ArticleModalProps = {
  articleId: number;
  ids: number[];
  planning?: Planning;
  onNavigate: (articleId: number) => void;
  onHide: () => void;
};

export default function ArticleModal({ articleId, ids, planning, onNavigate, onHide }: ArticleModalProps) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [form, setForm] = useState<Partial<Article>>({});
  const [autoAdvance, setAutoAdvance] = useState(() => {
    try { return localStorage.getItem("rsl.autoAdvance") === "1"; } catch { return false; }
  });
  const article = useQuery({
    queryKey: ["article", review.id, articleId],
    queryFn: () => api.get<Article>(`/reviews/${review.id}/articles/${articleId}`),
  });
  useEffect(() => { if (article.data) setForm(article.data); }, [article.data]);

  const position = ids.indexOf(articleId);
  const previous = position > 0 ? ids[position - 1] : null;
  const next = position >= 0 && position < ids.length - 1 ? ids[position + 1] : null;

  const save = useMutation({
    mutationFn: (changes: Partial<Article>) => api.patch<Article>(`/reviews/${review.id}/articles/${articleId}`, changes),
    onSuccess: (updated) => {
      queryClient.setQueryData(["article", review.id, articleId], updated);
      queryClient.invalidateQueries({ queryKey: ["articles", review.id] });
    },
  });

  function changeStatus(status: ArticleStatus) {
    setForm({ ...form, status });
    if (autoAdvance) {
      save.mutate({ status }, { onSuccess: () => (next !== null ? onNavigate(next) : undefined) });
    }
  }

  function saveAll() {
    const changes: Record<string, unknown> = {};
    for (const field of [...EDITABLE.map((item) => item.key), "status", "comments", "selection_criteria_id"] as const) {
      if (article.data && form[field] !== article.data[field]) changes[field] = form[field];
    }
    save.mutate(changes as Partial<Article>);
  }

  function toggleAutoAdvance(value: boolean) {
    setAutoAdvance(value);
    try { localStorage.setItem("rsl.autoAdvance", value ? "1" : "0"); } catch { /* preference not persisted */ }
  }

  const criteria = form.status === "A" ? planning?.inclusion_criteria : planning?.exclusion_criteria;

  return (
    <Modal show onHide={onHide} size="lg" scrollable>
      <Modal.Header closeButton>
        <Modal.Title className="h6 mb-0">
          Detalhes do artigo {position >= 0 && <span className="text-muted">({position + 1} de {ids.length})</span>}
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <ErrorAlert error={article.error ?? save.error} />
        {article.isLoading || !article.data ? <Spinner animation="border" /> : (
          <Tab.Container defaultActiveKey="details">
            <Nav variant="tabs" className="mb-3">
              <Nav.Item><Nav.Link eventKey="details">Detalhes</Nav.Link></Nav.Item>
              <Nav.Item><Nav.Link eventKey="comments">Comentários</Nav.Link></Nav.Item>
              <Nav.Item><Nav.Link eventKey="discussion">Discussão</Nav.Link></Nav.Item>
            </Nav>
            <Tab.Content>
              <Tab.Pane eventKey="details">
                <div className="mb-3" style={{ maxWidth: 420 }}><AssigneeSelect articleId={articleId} stage="selection" /></div>
                <div className="mb-3 small text-muted">
                  {article.data.source?.name} · {article.data.document_type || "tipo não informado"} · <StatusBadge status={article.data.status} />
                </div>
                {EDITABLE.map((field) => (
                  <Form.Group key={field.key} className="mb-2" controlId={`article-${field.key}`}>
                    <Form.Label className="small mb-1">{field.label}</Form.Label>
                    {field.rows ? (
                      <Form.Control size="sm" as="textarea" rows={field.rows} value={String(form[field.key] ?? "")}
                        onChange={(event) => setForm({ ...form, [field.key]: event.target.value })} />
                    ) : (
                      <Form.Control size="sm" value={String(form[field.key] ?? "")}
                        onChange={(event) => setForm({ ...form, [field.key]: event.target.value })} />
                    )}
                  </Form.Group>
                ))}
              </Tab.Pane>
              <Tab.Pane eventKey="discussion">
                <Discussion articleId={articleId} />
              </Tab.Pane>
              <Tab.Pane eventKey="comments">
                <Form.Control as="textarea" rows={8} maxLength={2000} value={form.comments ?? ""} aria-label="Comentários"
                  placeholder="Anotações sobre a decisão de seleção."
                  onChange={(event) => setForm({ ...form, comments: event.target.value })} />
              </Tab.Pane>
            </Tab.Content>
          </Tab.Container>
        )}
      </Modal.Body>
      <Modal.Footer className="d-block">
        <Row className="g-2 align-items-end">
          <Col sm={4}>
            <Form.Label htmlFor="article-status" className="small mb-1">Status</Form.Label>
            <Form.Select id="article-status" size="sm" value={form.status ?? "U"}
              onChange={(event) => changeStatus(event.target.value as ArticleStatus)}>
              {Object.entries(STATUS_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </Form.Select>
          </Col>
          <Col sm={5}>
            {(form.status === "A" || form.status === "R") && (
              <>
                <Form.Label htmlFor="article-criteria" className="small mb-1">Critério</Form.Label>
                <Form.Select id="article-criteria" size="sm" value={form.selection_criteria_id ?? ""}
                  onChange={(event) => setForm({ ...form, selection_criteria_id: event.target.value ? Number(event.target.value) : null })}>
                  <option value="">—</option>
                  {criteria?.map((item) => <option key={item.id} value={item.id}>{item.description}</option>)}
                </Form.Select>
              </>
            )}
          </Col>
          <Col sm={3} className="text-end">
            <Button size="sm" disabled={save.isPending} onClick={saveAll}>Salvar</Button>
          </Col>
        </Row>
        <div className="d-flex justify-content-between align-items-center mt-3">
          <Form.Check id="auto-advance" type="switch" className="small"
            label="Salvar ao mudar o status e ir para o próximo"
            checked={autoAdvance} onChange={(event) => toggleAutoAdvance(event.target.checked)} />
          <div className="d-flex gap-2">
            <Button size="sm" variant="outline-secondary" disabled={previous === null} onClick={() => previous !== null && onNavigate(previous)}>
              <i className="bi bi-chevron-left" /> Anterior
            </Button>
            <Button size="sm" variant="outline-secondary" disabled={next === null} onClick={() => next !== null && onNavigate(next)}>
              Próximo <i className="bi bi-chevron-right" />
            </Button>
          </div>
        </div>
      </Modal.Footer>
    </Modal>
  );
}
