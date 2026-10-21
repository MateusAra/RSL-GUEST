import { useState, type FormEvent } from "react";
import { Alert, Badge, Button, Card, Col, Form, ListGroup, Row, Spinner } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import BlockedNotice from "../../../components/BlockedNotice";
import type { Code, SegmentRow } from "../../../types";
import { useReview } from "../useReview";
import { codeNames, useCodes, useCoding, useSynthesisMutation } from "./useSynthesis";

function CodePicker({ codes, value, onChange }: { codes: Code[]; value: number[]; onChange: (ids: number[]) => void }) {
  const chosen = new Set(value);
  return (
    <div className="d-flex flex-wrap gap-2">
      {codes.map((code) => (
        <Form.Check key={code.id} inline id={`pick-${code.id}-${value.join("-")}`} className="small me-0" label={code.name}
          checked={chosen.has(code.id)} onChange={(event) => {
            const next = new Set(chosen);
            if (event.target.checked) next.add(code.id); else next.delete(code.id);
            onChange([...next]);
          }} />
      ))}
    </div>
  );
}

function SegmentCard({ segment, activeCodes, names, inSample, locked }: {
  segment: SegmentRow; activeCodes: Code[]; names: Map<number, string>; inSample: boolean; locked: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const current = inSample ? segment.codes.mine ?? [] : segment.codes.final;
  const [draft, setDraft] = useState(current);
  const save = useSynthesisMutation((base, ids: number[]) => api.put(`${base}/segments/${segment.id}/codes`, { code_ids: ids }));
  const remove = useSynthesisMutation((base) => api.delete(`${base}/segments/${segment.id}`));
  const chips = (ids: number[] | undefined, bg = "primary") =>
    (ids ?? []).map((id) => <Badge key={id} bg={bg} className="me-1">{names.get(id) ?? id}</Badge>);

  return (
    <Card className="mb-2">
      <Card.Body className="py-2">
        <blockquote className="mb-1 small">“{segment.text}” <span className="text-muted">(p. {segment.page})</span></blockquote>
        <ErrorAlert error={save.error ?? remove.error} />
        {editing ? (
          <>
            <CodePicker codes={activeCodes} value={draft} onChange={setDraft} />
            <div className="mt-2 d-flex gap-2">
              <Button size="sm" onClick={() => save.mutate(draft, { onSuccess: () => setEditing(false) })}>Salvar códigos</Button>
              <Button size="sm" variant="outline-secondary" onClick={() => setEditing(false)}>Cancelar</Button>
            </div>
          </>
        ) : (
          <div className="d-flex justify-content-between align-items-start gap-2">
            <div className="small">
              {inSample && <span className="text-muted me-1">Meus códigos:</span>}
              {chips(current)}
              {current.length === 0 && <span className="text-muted">sem código</span>}
              {segment.codes.coder_a && (
                <div className="mt-1">
                  <span className="text-muted me-1">Codificador A:</span>{chips(segment.codes.coder_a, "secondary")}
                  <span className="text-muted mx-1">B:</span>{chips(segment.codes.coder_b, "secondary")}
                  {segment.codes.final.length > 0 && <><span className="text-muted mx-1">Final:</span>{chips(segment.codes.final, "success")}</>}
                </div>
              )}
            </div>
            {!locked && (
              <div className="text-nowrap">
                <Button size="sm" variant="link" className="p-0 me-2" onClick={() => { setDraft(current); setEditing(true); }}>Códigos</Button>
                <Button size="sm" variant="link" className="p-0 text-danger" onClick={() => remove.mutate()}>Remover</Button>
              </div>
            )}
          </div>
        )}
      </Card.Body>
    </Card>
  );
}

export default function CodingPage() {
  const review = useReview();
  const coding = useCoding();
  const codes = useCodes();
  const [articleId, setArticleId] = useState<number | null>(null);
  const [form, setForm] = useState<{ text: string; page: string; code_ids: number[] }>({ text: "", page: "", code_ids: [] });
  const current = articleId ?? coding.data?.articles[0]?.id ?? null;
  const segments = useQuery({
    queryKey: ["synthesis", review.id, "segments", current],
    queryFn: () => api.get<SegmentRow[]>(`/reviews/${review.id}/articles/${current}/segments`),
    enabled: current !== null,
  });
  const create = useSynthesisMutation((base, payload: typeof form) => api.post(`${base}/articles/${current}/segments`, payload));
  const done = useSynthesisMutation((base) => api.post(`${base}/coding/sample/${current}/done`));

  if (coding.isLoading || codes.isLoading) return <Spinner animation="border" />;
  if (!coding.data) return <ErrorAlert error={coding.error} />;
  const activeCodes = (codes.data ?? []).filter((code) => code.status === "active");
  const names = codeNames(codes.data);
  const locked = Boolean(coding.data.settings.closed_at);

  if (coding.data.articles.length === 0) {
    return <BlockedNotice message="Nenhum estudo na seleção final ainda." to={`/revisoes/${review.id}/conducao/selecao`} linkLabel="Ir para a seleção" />;
  }
  if (activeCodes.length === 0) {
    return <BlockedNotice message="Ative pelo menos um código no codebook antes de codificar." to={`/revisoes/${review.id}/sintese`} linkLabel="Ir para o codebook" />;
  }

  const article = coding.data.articles.find((item) => item.id === current);
  const sample = coding.data.settings.sample.find((item) => item.article_id === current);
  const inSample = Boolean(article?.in_sample);
  const slot = coding.data.my_slot;
  const myDone = sample && slot ? sample[`coder_${slot}_done` as const] : false;
  const canCode = !locked && (!inSample || (slot !== null && !myDone));

  function submit(event: FormEvent) {
    event.preventDefault();
    create.mutate(form, { onSuccess: () => setForm({ text: "", page: "", code_ids: [] }) });
  }

  return (
    <Row className="g-3">
      <Col lg={4}>
        <ListGroup>
          {coding.data.articles.map((item) => (
            <ListGroup.Item key={item.id} action active={item.id === current} onClick={() => setArticleId(item.id)} className="small">
              <div className="fw-semibold">{item.title}</div>
              <div className={item.id === current ? "" : "text-muted"}>
                {item.segments} trecho(s) {item.in_sample && <Badge bg="info">amostra dupla</Badge>}
              </div>
            </ListGroup.Item>
          ))}
        </ListGroup>
      </Col>
      <Col lg={8}>
        <Panel title={article?.title ?? "Estudo"}>
          {inSample && (
            <Alert variant="info" className="py-2 small">
              Estudo da amostra de dupla codificação: {slot === null ? "só os dois codificadores trabalham aqui." :
                myDone ? "você concluiu; aguardando o outro codificador." :
                  "cada codificador vê apenas os próprios códigos até os dois concluírem."}
              {slot !== null && !myDone && !locked && (
                <Button size="sm" className="ms-2" onClick={() => done.mutate()}>Concluir minha codificação</Button>
              )}
            </Alert>
          )}
          <ErrorAlert error={segments.error ?? create.error ?? done.error} />
          {segments.data?.map((segment) => (
            <SegmentCard key={`${segment.id}-${JSON.stringify(segment.codes)}`} segment={segment} activeCodes={activeCodes}
              names={names} inSample={inSample} locked={!canCode} />
          ))}
          {segments.data?.length === 0 && <p className="text-muted small">Nenhum trecho codificado neste estudo.</p>}
          {canCode && (
            <Form onSubmit={submit} className="border-top pt-3 mt-3">
              <Form.Group className="mb-2" controlId="segment-text">
                <Form.Label className="small mb-1">Trecho exato do estudo</Form.Label>
                <Form.Control as="textarea" rows={3} required value={form.text} onChange={(event) => setForm({ ...form, text: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-2" controlId="segment-page" style={{ maxWidth: 160 }}>
                <Form.Label className="small mb-1">Página</Form.Label>
                <Form.Control required maxLength={20} value={form.page} onChange={(event) => setForm({ ...form, page: event.target.value })} />
              </Form.Group>
              <div className="small fw-semibold mb-1">Códigos</div>
              <CodePicker codes={activeCodes} value={form.code_ids} onChange={(code_ids) => setForm({ ...form, code_ids })} />
              <Button type="submit" size="sm" className="mt-2" disabled={create.isPending}>Adicionar trecho</Button>
            </Form>
          )}
        </Panel>
      </Col>
    </Row>
  );
}
