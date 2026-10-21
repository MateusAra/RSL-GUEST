import { useState } from "react";
import { Badge, Button, Form } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import ErrorAlert from "../../../components/ErrorAlert";
import type { CommentRow } from "../../../types";
import { useReview } from "../useReview";

/** Discussion thread of a study. Messages are never deleted; a resolution records the study status at that moment. */
export default function Discussion({ articleId }: { articleId: number }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const key = ["comments", review.id, articleId];
  const comments = useQuery({ queryKey: key, queryFn: () => api.get<CommentRow[]>(`/reviews/${review.id}/articles/${articleId}/comments`) });
  const [body, setBody] = useState("");
  const [resolution, setResolution] = useState(false);
  const send = useMutation({
    mutationFn: () => api.post(`/reviews/${review.id}/articles/${articleId}/comments`, { body, is_resolution: resolution }),
    onSuccess: () => { setBody(""); setResolution(false); queryClient.invalidateQueries({ queryKey: key }); },
  });

  return (
    <>
      <ErrorAlert error={comments.error ?? send.error} />
      {comments.data?.length === 0 && <p className="small text-muted">Nenhuma mensagem ainda.</p>}
      {comments.data?.map((item) => (
        <div key={item.id} className={`small border-start ps-2 mb-2 ${item.is_resolution ? "border-success" : ""}`}>
          <strong>{item.user?.full_name ?? "Membro removido"}</strong>{" "}
          <span className="text-muted">{new Date(item.created_at).toLocaleString("pt-BR")}</span>
          {item.is_resolution && <Badge bg="success" className="ms-2">resolução · {item.resolution_status}</Badge>}
          <div style={{ whiteSpace: "pre-wrap" }}>{item.body}</div>
        </div>
      ))}
      <Form.Control as="textarea" rows={3} className="mt-2" value={body} aria-label="Nova mensagem" placeholder="Escreva para os coautores…"
        onChange={(event) => setBody(event.target.value)} />
      <div className="d-flex justify-content-between align-items-center mt-2">
        <Form.Check id={`resolution-${articleId}`} className="small" label="Registrar como resolução (guarda o status atual do estudo)"
          checked={resolution} onChange={(event) => setResolution(event.target.checked)} />
        <Button size="sm" disabled={!body.trim() || send.isPending} onClick={() => send.mutate()}>Enviar</Button>
      </div>
    </>
  );
}
