import { useState, type FormEvent } from "react";
import { Badge, Button, Col, Container, Form, ListGroup, Modal, Row } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import Panel from "../components/Panel";
import ErrorAlert from "../components/ErrorAlert";
import type { Invite, ReviewSummary } from "../types";

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("pt-BR");
}

function NewReviewModal({ show, onHide }: { show: boolean; onHide: () => void }) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ title: "", description: "" });
  const create = useMutation({
    mutationFn: () => api.post<ReviewSummary>("/reviews", form),
    onSuccess: (review) => {
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
      onHide();
      navigate(`/revisoes/${review.id}`);
    },
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate();
  }

  return (
    <Modal show={show} onHide={onHide}>
      <Form onSubmit={submit}>
        <Modal.Header closeButton>
          <Modal.Title>Nova revisão</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ErrorAlert error={create.error} />
          <Form.Group className="mb-3" controlId="new-title">
            <Form.Label>Título</Form.Label>
            <Form.Control
              autoFocus
              required
              maxLength={255}
              value={form.title}
              onChange={(event) => setForm({ ...form, title: event.target.value })}
            />
          </Form.Group>
          <Form.Group controlId="new-description">
            <Form.Label>Descrição</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              maxLength={500}
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>Cancelar</Button>
          <Button type="submit" disabled={create.isPending}>Criar revisão</Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [showNew, setShowNew] = useState(false);
  const reviews = useQuery({ queryKey: ["reviews"], queryFn: () => api.get<ReviewSummary[]>("/reviews") });
  const invites = useQuery({ queryKey: ["invites"], queryFn: () => api.get<Invite[]>("/invites") });
  const answer = useMutation({
    mutationFn: ({ code, action }: { code: string; action: "accept" | "reject" }) =>
      api.post(`/invites/${code}/${action}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["invites"] });
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
    },
  });

  return (
    <Container fluid="lg" className="py-4">
      <div className="d-flex align-items-center justify-content-between mb-4">
        <h1 className="h3 mb-0">Minhas revisões</h1>
        <Button onClick={() => setShowNew(true)}>
          <i className="bi bi-plus-lg me-1" /> Nova revisão
        </Button>
      </div>
      <Row className="g-4">
        <Col lg={8}>
          <ErrorAlert error={reviews.error} />
          {reviews.data?.length === 0 && (
            <Panel>
              <p className="mb-3">Você ainda não tem revisões.</p>
              <Button variant="outline-primary" onClick={() => setShowNew(true)}>Criar a primeira revisão</Button>
            </Panel>
          )}
          <ListGroup>
            {reviews.data?.map((review) => (
              <ListGroup.Item key={review.id} action as={Link} to={`/revisoes/${review.id}`} className="py-3">
                <div className="d-flex justify-content-between align-items-start gap-3">
                  <div>
                    <div className="fw-semibold">{review.title}</div>
                    {review.description && <div className="text-muted small">{review.description}</div>}
                    <div className="small mt-1">
                      {[review.author, ...review.co_authors].map((person) => person.full_name).join(", ")}
                    </div>
                  </div>
                  <div className="text-end small text-muted text-nowrap">
                    {review.is_owner ? <Badge bg="secondary">Autor principal</Badge> : <Badge bg="info">Coautor</Badge>}
                    <div className="mt-1">Atualizada em {formatDate(review.updated_at)}</div>
                  </div>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Col>
        <Col lg={4}>
          <Panel title="Convites pendentes">
            <ErrorAlert error={answer.error} />
            {invites.data?.length === 0 && <p className="text-muted mb-0">Nenhum convite pendente.</p>}
            {invites.data?.map((invite) => (
              <div key={invite.id} className="border-bottom pb-3 mb-3">
                <div className="fw-semibold">{invite.review.title}</div>
                <div className="small text-muted mb-2">
                  Convite de {invite.invited_by.full_name} em {formatDate(invite.date_sent)}
                </div>
                <Button size="sm" className="me-2" onClick={() => answer.mutate({ code: invite.code, action: "accept" })}>
                  Aceitar
                </Button>
                <Button size="sm" variant="outline-secondary" onClick={() => answer.mutate({ code: invite.code, action: "reject" })}>
                  Recusar
                </Button>
              </div>
            ))}
          </Panel>
        </Col>
      </Row>
      <NewReviewModal show={showNew} onHide={() => setShowNew(false)} />
    </Container>
  );
}
