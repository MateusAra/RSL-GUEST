import { useEffect, useState } from "react";
import { Alert, Badge, Button, Form, Spinner } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { SynthesisChecklist } from "../../../types";
import { useReview } from "../useReview";
import { useCoding, useSynthesisMutation } from "./useSynthesis";

function ChecklistItem({ item }: { item: SynthesisChecklist["items"][number] }) {
  const [form, setForm] = useState({ met: item.met ?? true, justification: item.justification });
  useEffect(() => setForm({ met: item.met ?? true, justification: item.justification }), [item]);
  const save = useSynthesisMutation((base) => api.put(`${base}/synthesis-checklist/${item.item}`, form));
  return (
    <div className="border-bottom pb-3 mb-3">
      <div className="fw-semibold small mb-1">
        {item.item}. {item.text} {item.justification && <Badge bg={item.met ? "success" : "warning"} text={item.met ? undefined : "dark"}>{item.met ? "atendido" : "não atendido"}</Badge>}
      </div>
      <ErrorAlert error={save.error} />
      <div className="d-flex gap-2 align-items-center">
        <Form.Select size="sm" style={{ maxWidth: 150 }} value={form.met ? "1" : "0"} aria-label={`Item ${item.item}`}
          onChange={(event) => setForm({ ...form, met: event.target.value === "1" })}>
          <option value="1">Atendido</option>
          <option value="0">Não atendido</option>
        </Form.Select>
        <Form.Control size="sm" placeholder="Justificativa (obrigatória)" value={form.justification} aria-label={`Justificativa do item ${item.item}`}
          onChange={(event) => setForm({ ...form, justification: event.target.value })} />
        <Button size="sm" disabled={!form.justification.trim() || save.isPending} onClick={() => save.mutate()}>Salvar</Button>
      </div>
    </div>
  );
}

export default function PhasePage() {
  const review = useReview();
  const coding = useCoding();
  const checklist = useQuery({
    queryKey: ["synthesis", review.id, "checklist"],
    queryFn: () => api.get<SynthesisChecklist>(`/reviews/${review.id}/synthesis-checklist`),
  });
  const [justification, setJustification] = useState("");
  const verify = useSynthesisMutation((base) => api.post(`${base}/coding/verify-codebook`));
  const close = useSynthesisMutation((base) => api.post(`${base}/coding/close`, { justification }));
  const reopen = useSynthesisMutation((base) => api.post(`${base}/coding/reopen`));

  if (coding.isLoading || checklist.isLoading) return <Spinner animation="border" />;
  const settings = coding.data?.settings;
  const members = new Map([review.author, ...review.co_authors].map((member) => [member.id, member.full_name]));

  return (
    <>
      <Panel title="Conferência do codebook">
        <ErrorAlert error={verify.error} />
        {settings?.codebook_verified_at ? (
          <p className="small mb-0"><i className="bi bi-check2-circle text-success me-1" />
            Conferido por {members.get(settings.codebook_verified_by_id ?? -1) ?? "membro removido"} em {new Date(settings.codebook_verified_at).toLocaleString("pt-BR")}.</p>
        ) : (
          <>
            <p className="small">Outro membro, que não criou os códigos, confere a lista (definições, limites e frequências) antes de fechar a fase.</p>
            <Button size="sm" onClick={() => verify.mutate()} disabled={verify.isPending}>Marcar codebook como conferido</Button>
          </>
        )}
      </Panel>

      <Panel title="Fechamento da codificação">
        <ErrorAlert error={close.error ?? reopen.error} />
        {settings?.closed_at ? (
          <>
            <Alert variant="secondary" className="py-2 small mb-2">
              Fechada em {new Date(settings.closed_at).toLocaleString("pt-BR")}.
              {settings.close_justification && <> Justificativa: {settings.close_justification}</>}
            </Alert>
            {review.is_owner && <Button size="sm" variant="outline-secondary" onClick={() => reopen.mutate()}>Reabrir codificação</Button>}
          </>
        ) : (
          <>
            <p className="small">Fechar exige o codebook conferido e, com dupla codificação, a amostra concluída, as divergências resolvidas e concordância ≥ 0,6. Sem isso, registre uma justificativa.</p>
            <div className="d-flex gap-2">
              <Form.Control size="sm" placeholder="Justificativa (só se houver pendências)" value={justification}
                onChange={(event) => setJustification(event.target.value)} aria-label="Justificativa do fechamento" />
              <Button size="sm" className="text-nowrap" onClick={() => close.mutate()} disabled={close.isPending}>Fechar codificação</Button>
            </div>
          </>
        )}
      </Panel>

      <Panel title="Checklist de confiabilidade da síntese"
        actions={checklist.data?.evaluated ? <Badge bg="success">síntese avaliada</Badge> : <Badge bg="secondary">pendente</Badge>}>
        <p className="small text-muted">Itens 18–21 de Cruzes & Dybå (2011). Cada item é avaliado pelo pesquisador, com justificativa.</p>
        {checklist.data?.items.map((item) => <ChecklistItem key={item.item} item={item} />)}
      </Panel>
    </>
  );
}
