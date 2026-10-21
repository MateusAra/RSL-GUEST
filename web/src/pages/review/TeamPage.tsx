import { useState } from "react";
import { Alert, Badge, Button, Card, Col, Form, ProgressBar, Row, Spinner, Table } from "react-bootstrap";
import { Route, Routes } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api";
import Panel from "../../components/Panel";
import SideNav from "../../components/SideNav";
import ErrorAlert from "../../components/ErrorAlert";
import type { Dashboard, EvidenceChain, Planning, Stage, ThemeRow } from "../../types";
import { useReview } from "./useReview";
import { STAGE_LABELS, useAssignments } from "./team/useAssignments";
import { usePlanning } from "./planning/usePlanning";

function Progress({ label, done, total }: { label: string; done: number; total: number }) {
  return (
    <div className="mb-3">
      <div className="d-flex justify-content-between small"><span>{label}</span><span>{done} de {total}</span></div>
      <ProgressBar now={total ? (done / total) * 100 : 0} variant={done === total && total > 0 ? "success" : undefined} />
    </div>
  );
}

function ProgressPage() {
  const review = useReview();
  const data = useQuery({ queryKey: ["dashboard", review.id], queryFn: () => api.get<Dashboard>(`/reviews/${review.id}/dashboard`) });
  if (data.isLoading) return <Spinner animation="border" />;
  if (!data.data) return <ErrorAlert error={data.error} />;
  const { selection, quality, extraction, coding, members } = data.data;
  const imported = Object.values(selection).reduce((a, b) => a + b, 0);
  return (
    <>
      <Panel title="Progresso por etapa">
        <Progress label="Seleção (classificados)" done={imported - selection.U} total={imported} />
        <Progress label="Avaliação de qualidade (completas)" done={quality.complete} total={quality.accepted} />
        <Progress label="Extração (concluídas)" done={extraction.finished} total={extraction.final} />
        <Progress label="Codificação (estudos com trechos)" done={coding.studies_coded} total={coding.final} />
        <div className="small text-muted">
          {coding.segments} trecho(s) codificado(s).
          {coding.agreement !== null && (
            <> Concordância da dupla codificação ({coding.agreement_metric === "kappa" ? "κ" : "α"}):{" "}
              <Badge bg={coding.agreement >= coding.agreement_threshold ? "success" : "warning"} text={coding.agreement >= coding.agreement_threshold ? undefined : "dark"}>
                {coding.agreement.toFixed(3)}</Badge></>
          )}
        </div>
      </Panel>
      <Panel title="Pendências por membro">
        <Table size="sm" className="small">
          <thead><tr><th>Membro</th>{(Object.keys(STAGE_LABELS) as Stage[]).map((stage) => <th key={stage}>{STAGE_LABELS[stage]}</th>)}</tr></thead>
          <tbody>
            {members.map((member) => (
              <tr key={member.user.id}>
                <td>{member.user.full_name}</td>
                {(Object.keys(STAGE_LABELS) as Stage[]).map((stage) => {
                  const bucket = member.stages[stage];
                  return <td key={stage}>{bucket ? <>{bucket.pending} pendente(s) de {bucket.assigned}</> : <span className="text-muted">—</span>}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </Table>
      </Panel>
    </>
  );
}

function AssignmentsPage() {
  const review = useReview();
  const queryClient = useQueryClient();
  const [stage, setStage] = useState<Stage>("selection");
  const members = [review.author, ...review.co_authors];
  const [chosen, setChosen] = useState<Set<number>>(new Set(members.map((member) => member.id)));
  const assignments = useAssignments(stage);
  const distribute = useMutation({
    mutationFn: () => api.post<{ assigned: Record<string, number> }>(`/reviews/${review.id}/assignments/distribute`, { stage, user_ids: [...chosen] }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assignments", review.id] });
      queryClient.invalidateQueries({ queryKey: ["dashboard", review.id] });
    },
  });
  const counts = new Map<number, number>();
  Object.values(assignments.data?.assignments ?? {}).forEach((item) => counts.set(item.user_id, (counts.get(item.user_id) ?? 0) + 1));
  const total = distribute.data ? Object.values(distribute.data.assigned).reduce((a, b) => a + b, 0) : null;

  return (
    <Panel title="Distribuir estudos">
      <ErrorAlert error={distribute.error} />
      {total !== null && <Alert variant="success" className="py-2 small">{total} estudo(s) sem responsável foram distribuídos.</Alert>}
      <Row className="g-3 align-items-end mb-3">
        <Col sm={4}>
          <Form.Label htmlFor="stage" className="small mb-1">Etapa</Form.Label>
          <Form.Select id="stage" size="sm" value={stage} onChange={(event) => setStage(event.target.value as Stage)}>
            {(Object.keys(STAGE_LABELS) as Stage[]).map((item) => <option key={item} value={item}>{STAGE_LABELS[item]}</option>)}
          </Form.Select>
        </Col>
        <Col sm={8}>
          <div className="small fw-semibold mb-1">Entre</div>
          {members.map((member) => (
            <Form.Check key={member.id} inline id={`member-${member.id}`} label={`${member.full_name} (${counts.get(member.id) ?? 0})`}
              checked={chosen.has(member.id)} onChange={(event) => {
                const next = new Set(chosen);
                if (event.target.checked) next.add(member.id); else next.delete(member.id);
                setChosen(next);
              }} />
          ))}
        </Col>
      </Row>
      <Button size="sm" disabled={chosen.size === 0 || distribute.isPending} onClick={() => distribute.mutate()}>
        Distribuir os estudos sem responsável
      </Button>
      <Form.Text className="d-block mt-2">
        A distribuição equilibra a carga atual (rodízio) e não mexe em quem já tem responsável. Para trocar o responsável
        de um estudo, use o modal do estudo na seleção; a troca pede justificativa.
      </Form.Text>
    </Panel>
  );
}

function LinksEditor({ chain, planning, themes }: { chain: EvidenceChain[number]; planning?: Planning; themes: ThemeRow[] }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [fields, setFields] = useState(new Set(chain.field_ids));
  const [linked, setLinked] = useState(new Set(chain.theme_ids));
  const [conclusion, setConclusion] = useState(chain.conclusion);
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["evidence", review.id] });
  const saveLinks = useMutation({
    mutationFn: () => api.put(`/reviews/${review.id}/questions/${chain.question_id}/links`, { field_ids: [...fields], theme_ids: [...linked] }),
    onSuccess: refresh,
  });
  const saveConclusion = useMutation({
    mutationFn: () => api.put(`/reviews/${review.id}/questions/${chain.question_id}/conclusion`, { conclusion }),
    onSuccess: refresh,
  });
  const toggle = (set: Set<number>, update: (next: Set<number>) => void, id: number) => {
    const next = new Set(set);
    if (next.has(id)) next.delete(id); else next.add(id);
    update(next);
  };
  return (
    <div className="small">
      <ErrorAlert error={saveLinks.error ?? saveConclusion.error} />
      <div className="fw-semibold">Campos de extração</div>
      {(planning?.data_extraction_fields ?? []).map((field) => (
        <Form.Check key={field.id} inline id={`q${chain.question_id}-f${field.id}`} label={field.description}
          checked={fields.has(field.id)} onChange={() => toggle(fields, setFields, field.id)} />
      ))}
      <div className="fw-semibold mt-2">Temas</div>
      {themes.map((theme) => (
        <Form.Check key={theme.id} inline id={`q${chain.question_id}-t${theme.id}`} label={theme.name}
          checked={linked.has(theme.id)} onChange={() => toggle(linked, setLinked, theme.id)} />
      ))}
      <div><Button size="sm" className="mt-2" onClick={() => saveLinks.mutate()} disabled={saveLinks.isPending}>Salvar ligações</Button></div>
      <Form.Label htmlFor={`conclusion-${chain.question_id}`} className="fw-semibold mt-3 mb-1">Conclusão (escrita pelos pesquisadores)</Form.Label>
      <Form.Control id={`conclusion-${chain.question_id}`} as="textarea" rows={3} value={conclusion} onChange={(event) => setConclusion(event.target.value)} />
      <Button size="sm" className="mt-2" onClick={() => saveConclusion.mutate()} disabled={saveConclusion.isPending}>Salvar conclusão</Button>
    </div>
  );
}

function EvidencePage() {
  const review = useReview();
  const planning = usePlanning();
  const chain = useQuery({ queryKey: ["evidence", review.id], queryFn: () => api.get<EvidenceChain>(`/reviews/${review.id}/evidence`) });
  const themes = useQuery({ queryKey: ["synthesis", review.id, "themes"], queryFn: () => api.get<ThemeRow[]>(`/reviews/${review.id}/themes`) });
  if (chain.isLoading) return <Spinner animation="border" />;
  if (!chain.data) return <ErrorAlert error={chain.error} />;
  if (chain.data.length === 0) return <Panel><p className="text-muted mb-0">Cadastre as perguntas de pesquisa no protocolo para montar a cadeia de evidência.</p></Panel>;

  return (
    <>
      {chain.data.map((item, index) => (
        <Panel key={item.question_id} title={`RQ${index + 1}: ${item.question}`}>
          <Row className="g-3">
            <Col lg={5}><LinksEditor key={JSON.stringify([item.field_ids, item.theme_ids, item.conclusion])} chain={item} planning={planning.data} themes={themes.data ?? []} /></Col>
            <Col lg={7}>
              {item.gaps.length > 0 && (
                <Alert variant="warning" className="py-2 small">
                  <strong>Lacunas</strong>
                  <ul className="mb-0 ps-3">{item.gaps.map((gap) => <li key={gap}>{gap}</li>)}</ul>
                </Alert>
              )}
              {item.studies.map((study) => (
                <Card key={study.article_id} className="mb-2">
                  <Card.Body className="py-2 small">
                    <div className="fw-semibold">{study.title}</div>
                    {study.fields.map((field) => (
                      <div key={field.field}>{field.field}: {field.value || <span className="text-danger">sem valor</span>}</div>
                    ))}
                    {study.segments.map((segment) => (
                      <blockquote key={`${segment.segment_id}-${segment.code}`} className="border-start ps-2 my-1">
                        “{segment.text}” <span className="text-muted">(p. {segment.page}) · {segment.code} → {segment.theme}</span>
                      </blockquote>
                    ))}
                  </Card.Body>
                </Card>
              ))}
              {item.conclusion && <div className="small"><strong>Conclusão:</strong> {item.conclusion}</div>}
            </Col>
          </Row>
        </Panel>
      ))}
    </>
  );
}

export default function TeamPage() {
  return (
    <Row className="g-4">
      <Col md={3}>
        <SideNav items={[
          { to: "", label: "Progresso", end: true },
          { to: "atribuicoes", label: "Atribuições" },
          { to: "evidencias", label: "Cadeia de evidência" },
        ]} />
      </Col>
      <Col md={9}>
        <Routes>
          <Route index element={<ProgressPage />} />
          <Route path="atribuicoes" element={<AssignmentsPage />} />
          <Route path="evidencias" element={<EvidencePage />} />
        </Routes>
      </Col>
    </Row>
  );
}
