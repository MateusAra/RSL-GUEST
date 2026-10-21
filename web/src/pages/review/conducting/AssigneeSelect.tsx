import { useState } from "react";
import { Button, Form, InputGroup } from "react-bootstrap";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import ErrorAlert from "../../../components/ErrorAlert";
import type { Stage } from "../../../types";
import { useReview } from "../useReview";
import { useAssignments } from "../team/useAssignments";

/** Who is responsible for the study in a stage; changing an existing assignee asks for a justification. */
export default function AssigneeSelect({ articleId, stage }: { articleId: number; stage: Stage }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const assignments = useAssignments(stage);
  const current = assignments.data?.assignments[String(articleId)]?.user_id ?? null;
  const [target, setTarget] = useState<string | null>(null);
  const [justification, setJustification] = useState("");
  const save = useMutation({
    mutationFn: () => api.put(`/reviews/${review.id}/articles/${articleId}/assignment`, {
      stage, user_id: target ? Number(target) : null, justification }),
    onSuccess: () => { setTarget(null); setJustification(""); queryClient.invalidateQueries({ queryKey: ["assignments", review.id] }); },
  });
  const value = target ?? (current === null ? "" : String(current));
  const changing = target !== null && target !== (current === null ? "" : String(current));

  return (
    <div>
      <Form.Label htmlFor={`assignee-${articleId}`} className="small mb-1">Responsável</Form.Label>
      <ErrorAlert error={save.error} />
      <InputGroup size="sm">
        <Form.Select id={`assignee-${articleId}`} value={value} onChange={(event) => setTarget(event.target.value)}>
          <option value="">— ninguém —</option>
          {[review.author, ...review.co_authors].map((member) => <option key={member.id} value={member.id}>{member.full_name}</option>)}
        </Form.Select>
        {changing && current !== null && (
          <Form.Control placeholder="Justificativa" value={justification} aria-label="Justificativa da reatribuição"
            onChange={(event) => setJustification(event.target.value)} />
        )}
        {changing && <Button disabled={save.isPending} onClick={() => save.mutate()}>Atribuir</Button>}
      </InputGroup>
    </div>
  );
}
