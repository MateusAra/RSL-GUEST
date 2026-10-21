import { useEffect, useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import ErrorAlert from "../../../components/ErrorAlert";
import type { Hypothesis, VerdictKey, Verdicts } from "../../../types";
import { useReview } from "../useReview";

export const VERDICT_LABELS: Record<VerdictKey, string> = {
  supports: "Suporta",
  partial: "Suporta parcialmente",
  refutes: "Refuta",
  inconclusive: "Inconclusivo",
};

function VerdictRow({ articleId, hypothesis, current }: {
  articleId: number; hypothesis: Hypothesis; current?: { verdict: VerdictKey; justification: string };
}) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ verdict: current?.verdict ?? "", justification: current?.justification ?? "" });
  useEffect(() => setForm({ verdict: current?.verdict ?? "", justification: current?.justification ?? "" }), [current]);
  const save = useMutation({
    mutationFn: () => api.put(`/reviews/${review.id}/articles/${articleId}/verdicts/${hypothesis.id}`,
      { verdict: form.verdict || null, justification: form.justification }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["verdicts", review.id] }),
  });
  const changed = form.verdict !== (current?.verdict ?? "") || form.justification !== (current?.justification ?? "");

  return (
    <div className="mb-2">
      <div className="small"><strong>{hypothesis.code}</strong>: {hypothesis.statement}</div>
      <ErrorAlert error={save.error} />
      <div className="d-flex gap-2">
        <Form.Select size="sm" style={{ maxWidth: 210 }} value={form.verdict} aria-label={`Veredito para ${hypothesis.code}`}
          onChange={(event) => setForm({ ...form, verdict: event.target.value })}>
          <option value="">— sem veredito —</option>
          {Object.entries(VERDICT_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </Form.Select>
        <Form.Control size="sm" placeholder="Justificativa com base no estudo" value={form.justification}
          aria-label={`Justificativa para ${hypothesis.code}`} onChange={(event) => setForm({ ...form, justification: event.target.value })} />
        <Button size="sm" disabled={!changed || save.isPending} onClick={() => save.mutate()}>Salvar</Button>
      </div>
    </div>
  );
}

export default function VerdictEditor({ articleId, hypotheses, verdicts }: { articleId: number; hypotheses: Hypothesis[]; verdicts?: Verdicts }) {
  if (hypotheses.length === 0) return null;
  return (
    <div className="border-top pt-3 mt-3">
      <div className="fw-semibold small mb-2">Vereditos das hipóteses</div>
      {hypotheses.map((hypothesis) => (
        <VerdictRow key={hypothesis.id} articleId={articleId} hypothesis={hypothesis}
          current={verdicts?.[String(articleId)]?.[String(hypothesis.id)]} />
      ))}
    </div>
  );
}
