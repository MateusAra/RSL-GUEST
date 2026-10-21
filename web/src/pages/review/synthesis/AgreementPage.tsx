import { useEffect, useState } from "react";
import { Alert, Badge, Button, Card, Col, Form, Row, Spinner } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { Agreement } from "../../../types";
import { useReview } from "../useReview";
import { codeNames, useCodes, useCoding, useSynthesisMutation } from "./useSynthesis";

function Resolution({ divergence, names }: { divergence: Agreement["divergences"][number]; names: Map<number, string> }) {
  const codes = useCodes();
  const [chosen, setChosen] = useState<Set<number>>(new Set(divergence.final.length ? divergence.final : divergence.coder_a));
  const [justification, setJustification] = useState("");
  const resolve = useSynthesisMutation((base) => api.post(`${base}/segments/${divergence.segment_id}/resolve`, {
    code_ids: [...chosen], justification }));
  const label = (ids: number[]) => ids.map((id) => names.get(id) ?? id).join(", ") || "nenhum";

  return (
    <Card className="mb-2">
      <Card.Body className="py-2 small">
        <blockquote className="mb-1">“{divergence.text}” <span className="text-muted">(p. {divergence.page})</span></blockquote>
        <div>A: {label(divergence.coder_a)} · B: {label(divergence.coder_b)}
          {divergence.resolved && <Badge bg="success" className="ms-2">Resolvido: {label(divergence.final)}</Badge>}
        </div>
        <ErrorAlert error={resolve.error} />
        <div className="d-flex flex-wrap gap-2 mt-2">
          {(codes.data ?? []).filter((code) => code.status === "active").map((code) => (
            <Form.Check key={code.id} inline id={`resolve-${divergence.segment_id}-${code.id}`} className="me-0" label={code.name}
              checked={chosen.has(code.id)} onChange={(event) => {
                const next = new Set(chosen);
                if (event.target.checked) next.add(code.id); else next.delete(code.id);
                setChosen(next);
              }} />
          ))}
        </div>
        <div className="d-flex gap-2 mt-2">
          <Form.Control size="sm" placeholder="Justificativa da resolução" value={justification}
            onChange={(event) => setJustification(event.target.value)} aria-label="Justificativa da resolução" />
          <Button size="sm" disabled={!justification.trim() || resolve.isPending} onClick={() => resolve.mutate()}>Resolver</Button>
        </div>
      </Card.Body>
    </Card>
  );
}

export default function AgreementPage() {
  const review = useReview();
  const coding = useCoding();
  const codes = useCodes();
  const agreement = useQuery({
    queryKey: ["synthesis", review.id, "agreement"],
    queryFn: () => api.get<Agreement>(`/reviews/${review.id}/coding/agreement`),
  });
  const members = [review.author, ...review.co_authors];
  const [form, setForm] = useState({ dual_enabled: false, sample_percent: 20, coder_a_id: "", coder_b_id: "" });
  useEffect(() => {
    const settings = coding.data?.settings;
    if (settings) setForm({ dual_enabled: settings.dual_enabled, sample_percent: settings.sample_percent,
      coder_a_id: settings.coder_a_id ? String(settings.coder_a_id) : "", coder_b_id: settings.coder_b_id ? String(settings.coder_b_id) : "" });
  }, [coding.data?.settings]);
  const save = useSynthesisMutation((base) => api.put(`${base}/coding/settings`, {
    dual_enabled: form.dual_enabled, sample_percent: Number(form.sample_percent),
    coder_a_id: form.coder_a_id ? Number(form.coder_a_id) : null, coder_b_id: form.coder_b_id ? Number(form.coder_b_id) : null }));

  if (coding.isLoading || agreement.isLoading) return <Spinner animation="border" />;
  const data = agreement.data;
  const names = codeNames(codes.data);
  const sampleSize = coding.data?.settings.sample.length ?? 0;
  const format = (value: number | null) => (value === null ? "—" : value.toFixed(3));

  return (
    <>
      <Panel title="Configuração">
        <ErrorAlert error={save.error} />
        {review.is_owner ? (
          <Row className="g-2 align-items-end">
            <Col sm={12}>
              <Form.Check type="switch" id="dual-enabled" label="Dupla codificação numa amostra sorteada"
                checked={form.dual_enabled} onChange={(event) => setForm({ ...form, dual_enabled: event.target.checked })} />
            </Col>
            {form.dual_enabled && (
              <>
                <Col sm={3}>
                  <Form.Label htmlFor="sample-percent" className="small mb-1">Amostra (%)</Form.Label>
                  <Form.Control id="sample-percent" type="number" min={1} max={100} size="sm" value={form.sample_percent}
                    disabled={sampleSize > 0} onChange={(event) => setForm({ ...form, sample_percent: Number(event.target.value) })} />
                </Col>
                {(["coder_a_id", "coder_b_id"] as const).map((field, index) => (
                  <Col sm={4} key={field}>
                    <Form.Label htmlFor={field} className="small mb-1">Codificador {index === 0 ? "A" : "B"}</Form.Label>
                    <Form.Select id={field} size="sm" value={form[field]} onChange={(event) => setForm({ ...form, [field]: event.target.value })}>
                      <option value="">—</option>
                      {members.map((member) => <option key={member.id} value={member.id}>{member.full_name}</option>)}
                    </Form.Select>
                  </Col>
                ))}
              </>
            )}
            <Col sm="auto"><Button size="sm" onClick={() => save.mutate()} disabled={save.isPending}>Salvar</Button></Col>
          </Row>
        ) : <p className="small text-muted mb-0">Só o autor principal configura a dupla codificação.</p>}
        {sampleSize > 0 && (
          <p className="small text-muted mt-2 mb-0">O sistema sorteou {sampleSize} estudo(s) da seleção final para a amostra.</p>
        )}
      </Panel>

      {data?.enabled && (
        <Panel title="Concordância">
          {data.articles_done === 0 ? <p className="text-muted mb-0">Nenhum estudo da amostra com os dois codificadores concluídos.</p> : (
            <>
              <Row className="g-3 text-center mb-3">
                {[["α de Krippendorff", format(data.alpha)], ["κ de Cohen", format(data.kappa)],
                  ["Trechos", String(data.segments)], ["Concordantes", String(data.agreed_segments)]].map(([label, value]) => (
                  <Col key={label} xs={6} md={3}><div className="panel p-2"><div className="fs-5 fw-semibold">{value}</div><div className="small text-muted">{label}</div></div></Col>
                ))}
              </Row>
              {data.below_threshold
                ? <Alert variant="warning" className="py-2 small">A concordância ({data.metric === "kappa" ? "κ" : "α"}) está abaixo de {data.threshold}. Discuta as divergências antes de fechar a fase.</Alert>
                : <Alert variant="success" className="py-2 small">Concordância acima de {data.threshold}.</Alert>}
              <div className="small text-muted mb-2">
                {data.metric === "kappa" ? "κ usado porque cada trecho recebeu um único código." : "α usado porque há trechos com mais de um código."}
              </div>
              <h6 className="mt-3">Divergências ({data.divergences.length})</h6>
              {data.divergences.map((divergence) => <Resolution key={divergence.segment_id} divergence={divergence} names={names} />)}
            </>
          )}
        </Panel>
      )}
    </>
  );
}
