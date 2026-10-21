import { useMemo, useState, type FormEvent } from "react";
import { Alert, Badge, Button, Col, Form, Nav, Row, Spinner, Tab, Table } from "react-bootstrap";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from "chart.js";
import { Bar } from "react-chartjs-2";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { AnalysisData, AnalysisWeighting, Crosstab, HypothesisSynthesis, InsightFilters, Insights, Ranked, Snapshot } from "../../../types";
import { useReview } from "../useReview";
import { usePlanning } from "../planning/usePlanning";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const COLORS = ["#2c3e50", "#198754", "#2f80ed", "#fd7e14", "#6f42c1"];
const CATEGORIES: Record<string, string> = {
  journal: "Periódico", conference: "Evento", preprint: "Pré-print", thesis: "Tese ou dissertação", book: "Livro ou capítulo", other: "Outro",
};
const EMPTY_FILTERS: InsightFilters = { min_quality_pct: null, year_from: null, year_to: null, source_ids: [], categories: [] };

function query(filters: InsightFilters) {
  const params = new URLSearchParams();
  if (filters.min_quality_pct !== null) params.set("min_quality_pct", String(filters.min_quality_pct));
  if (filters.year_from) params.set("year_from", String(filters.year_from));
  if (filters.year_to) params.set("year_to", String(filters.year_to));
  if (filters.source_ids.length) params.set("source_ids", filters.source_ids.join(","));
  if (filters.categories.length) params.set("categories", filters.categories.join(","));
  return params.toString();
}

function ChartWithTable({ title, rows, columns, series }: {
  title: string; rows: string[]; columns: string[]; series: { label: string; data: number[] }[];
}) {
  return (
    <Panel title={title}>
      {rows.length === 0 ? <p className="text-muted mb-0">Sem dados.</p> : (
        <Row className="g-3 align-items-center">
          <Col lg={7}>
            <Bar aria-label={title}
              data={{ labels: rows, datasets: series.map((item, index) => ({ label: item.label, data: item.data, backgroundColor: COLORS[index % COLORS.length] })) }}
              options={{ responsive: true, plugins: { legend: { display: series.length > 1 } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }} />
          </Col>
          <Col lg={5}>
            <Table size="sm" className="small mb-0">
              <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
              <tbody>{rows.map((row, index) => <tr key={row}><td>{row}</td>{series.map((item) => <td key={item.label}>{item.data[index]}</td>)}</tr>)}</tbody>
            </Table>
          </Col>
        </Row>
      )}
    </Panel>
  );
}

function RankedChart({ title, data, column }: { title: string; data: Ranked; column: string }) {
  return <ChartWithTable title={title} rows={data.map((item) => item.label)} columns={[column, "Estudos"]}
    series={[{ label: "Estudos", data: data.map((item) => item.count) }]} />;
}

function FiltersBar({ filters, onApply }: { filters: InsightFilters; onApply: (filters: InsightFilters) => void }) {
  const planning = usePlanning();
  const [draft, setDraft] = useState(filters);
  const toggle = (list: (number | string)[], value: number | string) =>
    list.includes(value) ? list.filter((item) => item !== value) : [...list, value];

  function submit(event: FormEvent) {
    event.preventDefault();
    onApply(draft);
  }

  return (
    <Panel title="Sensibilidade">
      <Form onSubmit={submit}>
        <Row className="g-2 align-items-end">
          <Col sm={3}>
            <Form.Label htmlFor="min-quality" className="small mb-1">Qualidade mínima (% do máximo)</Form.Label>
            <Form.Control id="min-quality" size="sm" type="number" min={0} max={100} value={draft.min_quality_pct ?? ""}
              onChange={(event) => setDraft({ ...draft, min_quality_pct: event.target.value === "" ? null : Number(event.target.value) })} />
          </Col>
          <Col sm={2}>
            <Form.Label htmlFor="year-from" className="small mb-1">Ano de</Form.Label>
            <Form.Control id="year-from" size="sm" type="number" value={draft.year_from ?? ""}
              onChange={(event) => setDraft({ ...draft, year_from: event.target.value ? Number(event.target.value) : null })} />
          </Col>
          <Col sm={2}>
            <Form.Label htmlFor="year-to" className="small mb-1">até</Form.Label>
            <Form.Control id="year-to" size="sm" type="number" value={draft.year_to ?? ""}
              onChange={(event) => setDraft({ ...draft, year_to: event.target.value ? Number(event.target.value) : null })} />
          </Col>
          <Col sm="auto" className="d-flex gap-2">
            <Button type="submit" size="sm">Aplicar</Button>
            <Button size="sm" variant="outline-secondary" onClick={() => { setDraft(EMPTY_FILTERS); onApply(EMPTY_FILTERS); }}>Limpar</Button>
          </Col>
        </Row>
        <div className="small mt-2">
          <span className="fw-semibold me-2">Fontes:</span>
          {(planning.data?.sources ?? []).map((source) => (
            <Form.Check key={source.id} inline id={`filter-source-${source.id}`} label={source.name}
              checked={draft.source_ids.includes(source.id)}
              onChange={() => setDraft({ ...draft, source_ids: toggle(draft.source_ids, source.id) as number[] })} />
          ))}
        </div>
        <div className="small">
          <span className="fw-semibold me-2">Canal:</span>
          {Object.entries(CATEGORIES).map(([value, label]) => (
            <Form.Check key={value} inline id={`filter-cat-${value}`} label={label} checked={draft.categories.includes(value)}
              onChange={() => setDraft({ ...draft, categories: toggle(draft.categories, value) as string[] })} />
          ))}
        </div>
        <Form.Text>Os filtros só reaplicam as análises; nenhum dado é alterado.</Form.Text>
      </Form>
    </Panel>
  );
}

function HypothesisTable({ item, comparison }: { item: HypothesisSynthesis; comparison?: HypothesisSynthesis }) {
  return (
    <div className="mb-4">
      <div className="fw-semibold">{item.code}: {item.statement}</div>
      <div className="small text-muted mb-1">{item.rated} estudo(s) com veredito · {item.missing} sem veredito</div>
      <Table size="sm" className="small">
        <thead>
          <tr><th>Veredito</th><th>Estudos</th><th>%</th><th>Peso</th><th>% ponderado</th><th>Faixa moderada</th>{comparison && <th>% no corpus completo</th>}</tr>
        </thead>
        <tbody>
          {item.verdicts.map((verdict) => (
            <tr key={verdict.verdict}>
              <td>{verdict.label}</td><td>{verdict.count}</td><td>{verdict.pct}</td><td>{verdict.weighted}</td><td>{verdict.weighted_pct}</td>
              <td>{verdict.moderate_band}</td>
              {comparison && <td>{comparison.verdicts.find((other) => other.verdict === verdict.verdict)?.pct}</td>}
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );
}

function WeightingForm({ settings }: { settings: AnalysisWeighting }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [form, setForm] = useState(settings);
  const save = useMutation({
    mutationFn: () => api.put(`/reviews/${review.id}/analysis-settings`, form),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["insights", review.id] }),
  });
  const field = (name: keyof AnalysisWeighting, label: string) => (
    <Col sm>
      <Form.Label htmlFor={name} className="small mb-1">{label}</Form.Label>
      <Form.Control id={name} size="sm" type="number" step="any" value={form[name]}
        onChange={(event) => setForm({ ...form, [name]: Number(event.target.value) })} />
    </Col>
  );
  return (
    <Panel title="Ponderação pela qualidade">
      <ErrorAlert error={save.error} />
      <Row className="g-2 align-items-end">
        {field("high_min_pct", "Faixa alta a partir de (%)")}
        {field("high_weight", "Peso alto")}
        {field("moderate_min_pct", "Faixa moderada a partir de (%)")}
        {field("moderate_weight", "Peso moderado")}
        {field("author_concentration_pct", "Concentração de autoria (%)")}
        <Col sm="auto"><Button size="sm" disabled={!review.is_owner || save.isPending} onClick={() => save.mutate()}>Salvar</Button></Col>
      </Row>
      <Form.Text>Estudos abaixo da faixa moderada pesam 0. Sem checklist de qualidade, todos pesam 1. Só o autor principal altera.</Form.Text>
    </Panel>
  );
}

function CrosstabPanel({ insights, filters }: { insights: Insights; filters: InsightFilters }) {
  const review = useReview();
  const [pair, setPair] = useState({ a: "", b: "" });
  const table = useQuery({
    queryKey: ["insights", review.id, "crosstab", pair, filters],
    queryFn: () => api.get<Crosstab>(`/reviews/${review.id}/insights/crosstab?field_a=${pair.a}&field_b=${pair.b}&${query(filters)}`),
    enabled: Boolean(pair.a && pair.b && pair.a !== pair.b),
  });
  return (
    <Panel title="Cruzamento de campos">
      <Row className="g-2 mb-3">
        {(["a", "b"] as const).map((key) => (
          <Col sm={6} key={key}>
            <Form.Select size="sm" aria-label={`Campo ${key.toUpperCase()}`} value={pair[key]} onChange={(event) => setPair({ ...pair, [key]: event.target.value })}>
              <option value="">Campo {key === "a" ? "das linhas" : "das colunas"}</option>
              {insights.fields.map((field) => <option key={field.field_id} value={field.field_id}>{field.field}</option>)}
            </Form.Select>
          </Col>
        ))}
      </Row>
      <ErrorAlert error={table.error} />
      {table.data && (
        <Table size="sm" bordered className="small">
          <thead><tr><th>{table.data.field_a} \ {table.data.field_b}</th>{table.data.columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
          <tbody>
            {table.data.rows.map((row, index) => (
              <tr key={row}><th>{row}</th>{table.data!.matrix[index].map((value, column) => <td key={column}>{value}</td>)}</tr>
            ))}
          </tbody>
        </Table>
      )}
    </Panel>
  );
}

function SnapshotsPanel({ filters }: { filters: InsightFilters }) {
  const review = useReview();
  const queryClient = useQueryClient();
  const [label, setLabel] = useState("");
  const [open, setOpen] = useState<number | null>(null);
  const list = useQuery({ queryKey: ["insights", review.id, "snapshots"], queryFn: () => api.get<Snapshot[]>(`/reviews/${review.id}/insights/snapshots`) });
  const detail = useQuery({
    queryKey: ["insights", review.id, "snapshot", open],
    queryFn: () => api.get<Snapshot>(`/reviews/${review.id}/insights/snapshots/${open}`),
    enabled: open !== null,
  });
  const create = useMutation({
    mutationFn: () => api.post(`/reviews/${review.id}/insights/snapshots`, { label, filters }),
    onSuccess: () => { setLabel(""); queryClient.invalidateQueries({ queryKey: ["insights", review.id, "snapshots"] }); },
  });
  return (
    <Panel title="Instantâneos">
      <p className="small text-muted">Um instantâneo guarda os filtros, a ponderação e os resultados de agora. Ele não muda depois, mesmo que os dados mudem.</p>
      <ErrorAlert error={create.error} />
      <div className="d-flex gap-2 mb-3">
        <Form.Control size="sm" placeholder="Nome do instantâneo" value={label} onChange={(event) => setLabel(event.target.value)} aria-label="Nome do instantâneo" />
        <Button size="sm" className="text-nowrap" disabled={create.isPending} onClick={() => create.mutate()}>Salvar instantâneo</Button>
      </div>
      <Table size="sm" hover className="small">
        <thead><tr><th>Data</th><th>Nome</th><th>Estudos</th><th>Filtros</th></tr></thead>
        <tbody>
          {list.data?.map((item) => (
            <tr key={item.id} role="button" onClick={() => setOpen(item.id)}>
              <td>{new Date(item.created_at).toLocaleString("pt-BR")}</td><td>{item.label || "—"}</td><td>{item.corpus}</td>
              <td className="text-muted">{query(item.filters) || "corpus completo"}</td>
            </tr>
          ))}
        </tbody>
      </Table>
      {detail.data?.results && (
        <Alert variant="light" className="small">
          <strong>{detail.data.label || "Instantâneo"}</strong>: {detail.data.results.corpus} estudo(s).{" "}
          {detail.data.results.hypotheses.map((item) => `${item.code}: ${item.verdicts.map((v) => `${v.label} ${v.pct}%`).join(", ")}`).join(" · ")}
        </Alert>
      )}
    </Panel>
  );
}

export default function DataAnalysisPage() {
  const review = useReview();
  const [filters, setFilters] = useState<InsightFilters>(EMPTY_FILTERS);
  const params = useMemo(() => query(filters), [filters]);
  const status = useQuery({ queryKey: ["analysis", review.id], queryFn: () => api.get<AnalysisData>(`/reviews/${review.id}/analysis`) });
  const insights = useQuery({
    queryKey: ["insights", review.id, params],
    queryFn: () => api.get<Insights>(`/reviews/${review.id}/insights?${params}`),
    placeholderData: keepPreviousData,
  });

  if (status.isLoading || insights.isLoading) return <Spinner animation="border" />;
  if (!status.data || !insights.data) return <ErrorAlert error={status.error ?? insights.error} />;
  const { per_source, status_totals } = status.data;
  const data = insights.data;
  const biblio = data.bibliometrics;

  return (
    <>
      <Row className="g-3 mb-4 text-center">
        {[["Importados", Object.values(status_totals).reduce((a, b) => a + b, 0)], ["Aceitos", status_totals.A],
          ["Rejeitados", status_totals.R], ["Duplicados", status_totals.D], ["Seleção final", data.final_total],
          ["No filtro", data.corpus]].map(([label, value]) => (
          <Col key={label} xs={6} md>
            <div className="panel p-3"><div className="fs-4 fw-semibold">{value}</div><div className="small text-muted">{label}</div></div>
          </Col>
        ))}
      </Row>
      <FiltersBar filters={filters} onApply={setFilters} />
      <Tab.Container defaultActiveKey="biblio">
        <Nav variant="tabs" className="mb-3">
          <Nav.Item><Nav.Link eventKey="biblio">Bibliometria</Nav.Link></Nav.Item>
          <Nav.Item><Nav.Link eventKey="fields">Campos de extração</Nav.Link></Nav.Item>
          <Nav.Item><Nav.Link eventKey="hypotheses">Hipóteses</Nav.Link></Nav.Item>
          <Nav.Item><Nav.Link eventKey="snapshots">Instantâneos</Nav.Link></Nav.Item>
        </Nav>
        <Tab.Content>
          <Tab.Pane eventKey="biblio">
            <ChartWithTable title="Estudos importados e aceitos por fonte" rows={per_source.map((item) => item.source)} columns={["Fonte", "Estudos", "Aceitos"]}
              series={[{ label: "Estudos", data: per_source.map((item) => item.total) }, { label: "Aceitos", data: per_source.map((item) => item.accepted) }]} />
            <RankedChart title="Por ano" data={biblio.per_year} column="Ano" />
            <RankedChart title="Por canal de publicação" data={biblio.per_category} column="Canal" />
            <RankedChart title="Por veículo" data={biblio.per_venue} column="Veículo" />
            <RankedChart title="Palavras-chave mais frequentes" data={biblio.top_keywords} column="Palavra-chave" />
            <Row className="g-3">
              <Col md={6}><Panel title="Autores mais recorrentes">
                <Table size="sm" className="small mb-0"><tbody>{biblio.top_authors.map((item) => <tr key={item.label}><td>{item.label}</td><td>{item.count}</td></tr>)}</tbody></Table>
              </Panel></Col>
              <Col md={6}><Panel title="Coautorias mais frequentes">
                <Table size="sm" className="small mb-0"><tbody>{biblio.coauthor_pairs.map((item) => <tr key={item.label}><td>{item.label}</td><td>{item.count}</td></tr>)}</tbody></Table>
              </Panel></Col>
            </Row>
            {biblio.author_concentration.length > 0 && (
              <Alert variant="warning" className="small">
                <i className="bi bi-exclamation-triangle me-1" />Concentração de autoria acima de {data.settings.author_concentration_pct}%:{" "}
                {biblio.author_concentration.map((item) => `${item.author} (${item.count} estudos, ${item.pct}%)`).join("; ")}.
              </Alert>
            )}
          </Tab.Pane>
          <Tab.Pane eventKey="fields">
            {data.fields.length === 0 ? <p className="text-muted">Nenhum campo de seleção ou booleano no formulário de extração.</p> : (
              <>
                {data.fields.map((field) => (
                  <ChartWithTable key={field.field_id} title={`${field.field}${field.unanswered ? ` (${field.unanswered} sem resposta)` : ""}`}
                    rows={field.values.map((item) => item.label)} columns={["Valor", "Estudos"]}
                    series={[{ label: "Estudos", data: field.values.map((item) => item.count) }]} />
                ))}
                <CrosstabPanel insights={data} filters={filters} />
              </>
            )}
          </Tab.Pane>
          <Tab.Pane eventKey="hypotheses">
            <WeightingForm key={JSON.stringify(data.settings)} settings={data.settings} />
            <Panel title="Síntese dos vereditos"
              actions={<span className="small text-muted">faixas: <Badge bg="success">{data.quality_bands.high} alta</Badge>{" "}
                <Badge bg="warning" text="dark">{data.quality_bands.moderate} moderada</Badge>{" "}
                <Badge bg="secondary">{data.quality_bands.low} baixa</Badge></span>}>
              {data.hypotheses.length === 0 ? <p className="text-muted mb-0">Nenhuma hipótese no protocolo.</p> : data.hypotheses.map((item) => (
                <HypothesisTable key={item.id} item={item} comparison={data.comparison?.hypotheses.find((other) => other.id === item.id)} />
              ))}
            </Panel>
          </Tab.Pane>
          <Tab.Pane eventKey="snapshots"><SnapshotsPanel filters={filters} /></Tab.Pane>
        </Tab.Content>
      </Tab.Container>
    </>
  );
}
