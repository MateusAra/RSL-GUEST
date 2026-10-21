import { useEffect, useMemo, useState } from "react";
import { Badge, Button, ButtonGroup, Dropdown, Form, InputGroup, Nav, Pagination, Spinner, Table, ToggleButton } from "react-bootstrap";
import { keepPreviousData, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import BlockedNotice from "../../../components/BlockedNotice";
import StatusBadge, { STATUS_LABELS } from "../../../components/StatusBadge";
import type { ArticleList, ArticleStatus } from "../../../types";
import { useReview } from "../useReview";
import { usePlanning } from "../planning/usePlanning";
import ArticleModal from "./ArticleModal";
import DuplicatesModal from "./DuplicatesModal";
import { downloadFile } from "./download";

type SortKey = "title" | "author" | "year" | "journal" | "status";
const BULK_ACTIONS = {
  accept: "Aceitar",
  reject: "Rejeitar",
  duplicated: "Marcar como duplicado",
  unclassify: "Marcar como não classificado",
  remove: "Remover da revisão",
} as const;

export default function SelectionPage() {
  const review = useReview();
  const queryClient = useQueryClient();
  const planning = usePlanning();
  const [source, setSource] = useState<number | null>(null);
  const [status, setStatus] = useState<ArticleStatus | "">("");
  const [search, setSearch] = useState("");
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<SortKey>("title");
  const [order, setOrder] = useState<"asc" | "desc">("asc");
  const [page, setPage] = useState(1);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [bulk, setBulk] = useState<keyof typeof BULK_ACTIONS>("accept");
  const [detail, setDetail] = useState<number | null>(null);
  const [showDuplicates, setShowDuplicates] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => { setQ(search); setPage(1); }, 300);
    return () => clearTimeout(timer);
  }, [search]);
  useEffect(() => setSelected(new Set()), [source, status, q, page]);

  const params = useMemo(() => {
    const query = new URLSearchParams({ sort, order, page: String(page), page_size: "25" });
    if (source !== null) query.set("source_id", String(source));
    if (status) query.set("status", status);
    if (q) query.set("q", q);
    return query.toString();
  }, [source, status, q, sort, order, page]);

  const articles = useQuery({
    queryKey: ["articles", review.id, params],
    queryFn: () => api.get<ArticleList>(`/reviews/${review.id}/articles?${params}`),
    placeholderData: keepPreviousData,
  });
  const applyBulk = useMutation({
    mutationFn: () => api.post(`/reviews/${review.id}/articles/bulk`, { ids: [...selected], action: bulk }),
    onSuccess: () => {
      setSelected(new Set());
      queryClient.invalidateQueries({ queryKey: ["articles", review.id] });
    },
  });
  const exportArticles = useMutation({
    mutationFn: (format: "bibtex" | "csv") => {
      const query = new URLSearchParams({ format });
      if (source !== null) query.set("source_id", String(source));
      if (status) query.set("status", status);
      return downloadFile(`/reviews/${review.id}/articles-export?${query}`, `${review.name}.${format === "bibtex" ? "bib" : "csv"}`);
    },
  });

  if (planning.data && planning.data.sources.length === 0) {
    return (
      <BlockedNotice message="Adicione fontes e importe estudos antes da seleção."
        to={`/revisoes/${review.id}/planejamento#fontes`} linkLabel="Ir para Fontes" />
    );
  }

  const data = articles.data;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;
  const allOnPage = data?.items.length ? data.items.every((item) => selected.has(item.id)) : false;
  const sources = planning.data?.sources ?? [];
  const totalArticles = data ? Object.values(data.source_counts).reduce((sum, value) => sum + value, 0) : 0;

  function sortBy(key: SortKey) {
    if (sort === key) setOrder(order === "asc" ? "desc" : "asc");
    else { setSort(key); setOrder("asc"); }
  }

  function header(key: SortKey, label: string) {
    const icon = sort !== key ? "bi-arrow-down-up opacity-25" : order === "asc" ? "bi-sort-up" : "bi-sort-down";
    return (
      <th role="button" onClick={() => sortBy(key)} className="text-nowrap user-select-none">
        {label} <i className={`bi ${icon}`} />
      </th>
    );
  }

  return (
    <Panel
      title="Seleção de estudos"
      actions={
        <div className="d-flex gap-2">
          <Button size="sm" variant="outline-primary" onClick={() => setShowDuplicates(true)}>
            <i className="bi bi-files me-1" />Encontrar duplicados
          </Button>
          <Dropdown>
            <Dropdown.Toggle size="sm" variant="outline-secondary">Exportar</Dropdown.Toggle>
            <Dropdown.Menu align="end">
              <Dropdown.Item onClick={() => exportArticles.mutate("bibtex")}>BibTeX (.bib)</Dropdown.Item>
              <Dropdown.Item onClick={() => exportArticles.mutate("csv")}>Planilha (.csv)</Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </div>
      }
    >
      <ErrorAlert error={articles.error ?? applyBulk.error ?? exportArticles.error} />
      <Nav variant="tabs" className="mb-3" activeKey={source === null ? "all" : String(source)}
        onSelect={(key) => { setSource(key === "all" || !key ? null : Number(key)); setPage(1); }}>
        <Nav.Item><Nav.Link eventKey="all">Todas as fontes <Badge bg="light" text="dark">{totalArticles}</Badge></Nav.Link></Nav.Item>
        {sources.map((item) => (
          <Nav.Item key={item.id}>
            <Nav.Link eventKey={String(item.id)}>
              {item.name} <Badge bg="light" text="dark">{data?.source_counts[String(item.id)] ?? 0}</Badge>
            </Nav.Link>
          </Nav.Item>
        ))}
      </Nav>

      <div className="d-flex flex-wrap gap-2 align-items-center mb-3">
        <ButtonGroup size="sm">
          {(["", "U", "A", "R", "D"] as const).map((value) => (
            <ToggleButton key={value || "all"} id={`status-${value || "all"}`} type="radio" variant="outline-secondary"
              value={value} checked={status === value} onChange={() => { setStatus(value); setPage(1); }}>
              {value ? STATUS_LABELS[value] : "Todos"}{" "}
              <Badge bg="secondary">
                {data ? (value ? data.status_counts[value] : Object.values(data.status_counts).reduce((a, b) => a + b, 0)) : 0}
              </Badge>
            </ToggleButton>
          ))}
        </ButtonGroup>
        <InputGroup size="sm" className="ms-auto" style={{ maxWidth: 280 }}>
          <InputGroup.Text><i className="bi bi-search" /></InputGroup.Text>
          <Form.Control placeholder="Buscar título, autor, resumo" aria-label="Buscar estudos" value={search}
            onChange={(event) => setSearch(event.target.value)} />
        </InputGroup>
      </div>

      {articles.isLoading ? <Spinner animation="border" /> : data && data.total === 0 ? (
        <p className="text-muted">Nenhum estudo neste filtro.</p>
      ) : data && (
        <>
          <Table hover size="sm" className="table-articles align-middle small">
            <thead>
              <tr>
                <th style={{ width: 32 }}>
                  <Form.Check aria-label="Selecionar todos da página" checked={allOnPage}
                    onChange={(event) => setSelected(event.target.checked ? new Set(data.items.map((item) => item.id)) : new Set())} />
                </th>
                {header("title", "Título")}
                {header("author", "Autores")}
                {header("journal", "Periódico")}
                {header("year", "Ano")}
                <th>Fonte</th>
                {header("status", "Status")}
              </tr>
            </thead>
            <tbody>
              {data.items.map((article) => (
                <tr key={article.id} onClick={() => setDetail(article.id)}>
                  <td onClick={(event) => event.stopPropagation()}>
                    <Form.Check aria-label={`Selecionar ${article.title}`} checked={selected.has(article.id)}
                      onChange={(event) => {
                        const next = new Set(selected);
                        if (event.target.checked) next.add(article.id); else next.delete(article.id);
                        setSelected(next);
                      }} />
                  </td>
                  <td className="fw-semibold">{article.title}</td>
                  <td className="text-truncate" style={{ maxWidth: 180 }}>{article.author}</td>
                  <td className="text-truncate" style={{ maxWidth: 160 }}>{article.journal}</td>
                  <td>{article.year}</td>
                  <td>{article.source?.name}</td>
                  <td><StatusBadge status={article.status} /></td>
                </tr>
              ))}
            </tbody>
          </Table>
          <div className="d-flex flex-wrap justify-content-between align-items-center gap-2">
            <InputGroup size="sm" style={{ maxWidth: 380 }}>
              <InputGroup.Text>{selected.size} selecionado(s)</InputGroup.Text>
              <Form.Select aria-label="Ação em massa" value={bulk} onChange={(event) => setBulk(event.target.value as keyof typeof BULK_ACTIONS)}>
                {Object.entries(BULK_ACTIONS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </Form.Select>
              <Button disabled={selected.size === 0 || applyBulk.isPending} onClick={() => applyBulk.mutate()}>Aplicar</Button>
            </InputGroup>
            <Pagination size="sm" className="mb-0">
              <Pagination.Prev disabled={page === 1} onClick={() => setPage(page - 1)} />
              <Pagination.Item active>{page} / {totalPages}</Pagination.Item>
              <Pagination.Next disabled={page >= totalPages} onClick={() => setPage(page + 1)} />
            </Pagination>
          </div>
        </>
      )}

      {detail !== null && data && (
        <ArticleModal articleId={detail} ids={data.ids} planning={planning.data}
          onNavigate={setDetail} onHide={() => setDetail(null)} />
      )}
      {showDuplicates && <DuplicatesModal onHide={() => setShowDuplicates(false)} />}
    </Panel>
  );
}
