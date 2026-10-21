import { useEffect, useState, type FormEvent } from "react";
import { Alert, Badge, Button, Col, Form, InputGroup, ListGroup, Modal, Row } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api";
import Panel from "../../components/Panel";
import ErrorAlert from "../../components/ErrorAlert";
import type { Activity, Invite, ReviewSummary } from "../../types";
import { useReview } from "./useReview";

const INVITE_STATUS: Record<Invite["status"], { label: string; bg: string }> = {
  pending: { label: "Pendente", bg: "warning" },
  accepted: { label: "Aceito", bg: "success" },
  rejected: { label: "Recusado", bg: "secondary" },
};

export default function ReviewHomePage() {
  const review = useReview();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [details, setDetails] = useState({ title: review.title, description: review.description });
  const [email, setEmail] = useState("");
  const [confirm, setConfirm] = useState<"delete" | "leave" | null>(null);

  useEffect(() => setDetails({ title: review.title, description: review.description }), [review]);

  const refresh = () => {
    queryClient.invalidateQueries({ queryKey: ["review", String(review.id)] });
    queryClient.invalidateQueries({ queryKey: ["reviews"] });
    queryClient.invalidateQueries({ queryKey: ["review-invites", review.id] });
    queryClient.invalidateQueries({ queryKey: ["activities", review.id] });
  };

  const invites = useQuery({
    queryKey: ["review-invites", review.id],
    queryFn: () => api.get<Invite[]>(`/reviews/${review.id}/invites`),
    enabled: review.is_owner,
  });
  const activities = useQuery({
    queryKey: ["activities", review.id],
    queryFn: () => api.get<Activity[]>(`/reviews/${review.id}/activities`),
  });

  const saveDetails = useMutation({
    mutationFn: () => api.patch<ReviewSummary>(`/reviews/${review.id}`, details),
    onSuccess: refresh,
  });
  const invite = useMutation({
    mutationFn: () => api.post<Invite & { has_account: boolean }>(`/reviews/${review.id}/invites`, { email }),
    onSuccess: () => {
      setEmail("");
      refresh();
    },
  });
  const cancelInvite = useMutation({
    mutationFn: (inviteId: number) => api.delete(`/reviews/${review.id}/invites/${inviteId}`),
    onSuccess: refresh,
  });
  const removeCoauthor = useMutation({
    mutationFn: (userId: number) => api.delete(`/reviews/${review.id}/coauthors/${userId}`),
    onSuccess: refresh,
  });
  const destroy = useMutation({
    mutationFn: () =>
      confirm === "delete" ? api.delete(`/reviews/${review.id}`) : api.post(`/reviews/${review.id}/leave`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["reviews"] });
      navigate("/");
    },
  });

  function submitDetails(event: FormEvent) {
    event.preventDefault();
    saveDetails.mutate();
  }

  function submitInvite(event: FormEvent) {
    event.preventDefault();
    invite.mutate();
  }

  const pendingInvites = invites.data?.filter((item) => item.status === "pending") ?? [];

  return (
    <Row className="g-4">
      <Col lg={8}>
        <Panel title="Revisão">
          <ErrorAlert error={saveDetails.error} />
          {saveDetails.isSuccess && <Alert variant="success" className="py-2">Alterações salvas.</Alert>}
          <Form onSubmit={submitDetails}>
            <Form.Group className="mb-3" controlId="review-title">
              <Form.Label>Título</Form.Label>
              <Form.Control required maxLength={255} value={details.title}
                onChange={(event) => setDetails({ ...details, title: event.target.value })} />
            </Form.Group>
            <Form.Group className="mb-3" controlId="review-description">
              <Form.Label>Descrição</Form.Label>
              <Form.Control as="textarea" rows={4} maxLength={500} value={details.description}
                onChange={(event) => setDetails({ ...details, description: event.target.value })} />
            </Form.Group>
            <Button type="submit" disabled={saveDetails.isPending}>Salvar</Button>
          </Form>
        </Panel>

        <Panel title="Atividade recente">
          {activities.data?.length === 0 && <p className="text-muted mb-0">Nenhuma atividade ainda.</p>}
          <ListGroup variant="flush">
            {activities.data?.map((item, index) => (
              <ListGroup.Item key={index} className="px-0 small">
                <strong>{item.user.full_name}</strong> {item.verb}
                {item.target && <> <em>{item.target}</em></>}
                <span className="text-muted"> · {new Date(item.created_at).toLocaleString("pt-BR")}</span>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Panel>
      </Col>

      <Col lg={4}>
        <Panel title="Autores">
          <ErrorAlert error={removeCoauthor.error} />
          <ListGroup variant="flush" className="mb-3">
            <ListGroup.Item className="px-0 d-flex justify-content-between align-items-center">
              <span>
                {review.author.full_name} <span className="text-muted small">@{review.author.username}</span>
              </span>
              <Badge bg="secondary">Autor principal</Badge>
            </ListGroup.Item>
            {review.co_authors.map((coauthor) => (
              <ListGroup.Item key={coauthor.id} className="px-0 d-flex justify-content-between align-items-center">
                <span>
                  {coauthor.full_name} <span className="text-muted small">@{coauthor.username}</span>
                </span>
                {review.is_owner && (
                  <Button size="sm" variant="link" className="text-danger p-0"
                    onClick={() => removeCoauthor.mutate(coauthor.id)}>
                    Remover
                  </Button>
                )}
              </ListGroup.Item>
            ))}
          </ListGroup>

          {review.is_owner && (
            <>
              <ErrorAlert error={invite.error} />
              {invite.isSuccess && (
                <Alert variant="success" className="py-2 small">
                  Convite criado.{" "}
                  {invite.data?.has_account
                    ? "A pessoa verá o convite no painel dela."
                    : "Quando a pessoa criar a conta com esse e-mail, verá o convite no painel."}
                </Alert>
              )}
              <Form onSubmit={submitInvite}>
                <Form.Label htmlFor="invite-email" className="small fw-semibold">Adicionar autor</Form.Label>
                <InputGroup>
                  <Form.Control id="invite-email" type="email" required placeholder="email@exemplo.com"
                    value={email} onChange={(event) => setEmail(event.target.value)} />
                  <Button type="submit" disabled={invite.isPending}>Convidar</Button>
                </InputGroup>
              </Form>
              {pendingInvites.length > 0 && (
                <div className="mt-3">
                  <div className="small fw-semibold mb-1">Convites pendentes</div>
                  {pendingInvites.map((item) => (
                    <div key={item.id} className="d-flex justify-content-between align-items-center small py-1">
                      <span>
                        {item.invitee_email} <Badge bg={INVITE_STATUS[item.status].bg}>{INVITE_STATUS[item.status].label}</Badge>
                      </span>
                      <Button size="sm" variant="link" className="p-0" onClick={() => cancelInvite.mutate(item.id)}>
                        Cancelar
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </Panel>

        <Panel title={review.is_owner ? "Excluir revisão" : "Sair da revisão"}>
          <p className="small text-muted">
            {review.is_owner
              ? "Remove a revisão e todos os seus dados para todos os autores."
              : "Você deixará de ter acesso a esta revisão."}
          </p>
          <Button variant="outline-danger" size="sm" onClick={() => setConfirm(review.is_owner ? "delete" : "leave")}>
            {review.is_owner ? "Excluir revisão" : "Sair da revisão"}
          </Button>
        </Panel>
      </Col>

      <Modal show={confirm !== null} onHide={() => setConfirm(null)}>
        <Modal.Header closeButton>
          <Modal.Title>{confirm === "delete" ? "Excluir revisão?" : "Sair da revisão?"}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <ErrorAlert error={destroy.error} />
          {confirm === "delete"
            ? `"${review.title}" e todos os estudos, avaliações e extrações serão apagados. Isso não pode ser desfeito.`
            : `Você perderá o acesso a "${review.title}" até ser convidado de novo.`}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={() => setConfirm(null)}>Cancelar</Button>
          <Button variant="danger" disabled={destroy.isPending} onClick={() => destroy.mutate()}>
            {confirm === "delete" ? "Excluir" : "Sair"}
          </Button>
        </Modal.Footer>
      </Modal>
    </Row>
  );
}
