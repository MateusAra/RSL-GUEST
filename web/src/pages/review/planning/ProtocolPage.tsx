import { useEffect, useState, type FormEvent } from "react";
import { Alert, Badge, Button, ButtonGroup, Col, Form, ListGroup, Row, Table } from "react-bootstrap";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import InlineEdit from "../../../components/InlineEdit";
import AddInput from "../../../components/AddInput";
import type { KeywordRow, Picoc, Planning, SourceRow } from "../../../types";
import { useConnectors } from "../conducting/AutoSearch";
import { usePlanningMutation } from "./usePlanning";
import { useQuery } from "@tanstack/react-query";
import { useReview } from "../useReview";
import HypothesesSection from "./HypothesesSection";

const RELATED_TO: Record<KeywordRow["related_to"], string> = {
  "": "—",
  P: "População",
  I: "Intervenção",
  C: "Comparação",
  O: "Resultado",
};

const PICOC_FIELDS: { key: keyof Picoc; label: string; help: string }[] = [
  { key: "population", label: "População", help: "Quem ou o quê é estudado" },
  { key: "intervention", label: "Intervenção", help: "Método, técnica ou ferramenta" },
  { key: "comparison", label: "Comparação", help: "Com o que a intervenção é comparada" },
  { key: "outcome", label: "Resultado", help: "Efeitos ou fatores de interesse" },
  { key: "context", label: "Contexto", help: "Onde a comparação acontece" },
];

function SavedNote({ show }: { show: boolean }) {
  return show ? <span className="text-success small ms-2"><i className="bi bi-check2" /> Salvo</span> : null;
}

function Objectives({ planning }: { planning: Planning }) {
  const [objective, setObjective] = useState(planning.objective);
  useEffect(() => setObjective(planning.objective), [planning.objective]);
  const save = usePlanningMutation((base) => api.put(`${base}/objective`, { objective }));

  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate();
  }

  return (
    <Panel id="objetivos" title="Objetivos">
      <ErrorAlert error={save.error} />
      <Form onSubmit={submit}>
        <Form.Control as="textarea" rows={4} maxLength={1000} value={objective} aria-label="Objetivos"
          placeholder="Descreva o objetivo da revisão." onChange={(event) => setObjective(event.target.value)} />
        <div className="mt-2">
          <Button type="submit" size="sm" disabled={save.isPending}>Salvar</Button>
          <SavedNote show={save.isSuccess} />
        </div>
      </Form>
    </Panel>
  );
}

function PicocSection({ planning }: { planning: Planning }) {
  const [picoc, setPicoc] = useState(planning.picoc);
  useEffect(() => setPicoc(planning.picoc), [planning.picoc]);
  const save = usePlanningMutation((base) => api.put(`${base}/picoc`, picoc));

  function submit(event: FormEvent) {
    event.preventDefault();
    save.mutate();
  }

  return (
    <Panel id="picoc" title="PICOC">
      <ErrorAlert error={save.error} />
      <Form onSubmit={submit}>
        {PICOC_FIELDS.map((field) => (
          <Form.Group as={Row} className="mb-2" key={field.key} controlId={`picoc-${field.key}`}>
            <Form.Label column sm={3}>{field.label}</Form.Label>
            <Col sm={9}>
              <Form.Control size="sm" maxLength={200} value={picoc[field.key]} placeholder={field.help}
                onChange={(event) => setPicoc({ ...picoc, [field.key]: event.target.value })} />
            </Col>
          </Form.Group>
        ))}
        <Form.Text className="d-block mb-2">Separe os termos por vírgula para importá-los como palavras-chave.</Form.Text>
        <Button type="submit" size="sm" disabled={save.isPending}>Salvar</Button>
        <SavedNote show={save.isSuccess} />
      </Form>
    </Panel>
  );
}

function Questions({ planning }: { planning: Planning }) {
  const add = usePlanningMutation((base, question: string) => api.post(`${base}/questions`, { question }));
  const edit = usePlanningMutation((base, args: { id: number; question: string }) =>
    api.patch(`${base}/questions/${args.id}`, { question: args.question }));
  const remove = usePlanningMutation((base, id: number) => api.delete(`${base}/questions/${id}`));
  const reorder = usePlanningMutation((base, ids: number[]) => api.put(`${base}/questions/order`, { ids }));

  function move(index: number, delta: number) {
    const ids = planning.questions.map((question) => question.id);
    const [moved] = ids.splice(index, 1);
    ids.splice(index + delta, 0, moved);
    reorder.mutate(ids);
  }

  return (
    <Panel id="perguntas" title="Perguntas de pesquisa">
      <ErrorAlert error={add.error ?? edit.error ?? remove.error ?? reorder.error} />
      {planning.questions.length > 0 && (
        <ListGroup variant="flush" className="mb-3">
          {planning.questions.map((question, index) => (
            <ListGroup.Item key={question.id} className="px-0 d-flex align-items-start gap-2">
              <Badge bg="light" text="dark" className="mt-1">RQ{index + 1}</Badge>
              <div className="flex-grow-1">
                <InlineEdit value={question.question} maxLength={500}
                  onSave={(text) => edit.mutate({ id: question.id, question: text })} />
              </div>
              <ButtonGroup size="sm">
                <Button variant="outline-secondary" disabled={index === 0} aria-label="Subir" onClick={() => move(index, -1)}>
                  <i className="bi bi-arrow-up" />
                </Button>
                <Button variant="outline-secondary" disabled={index === planning.questions.length - 1}
                  aria-label="Descer" onClick={() => move(index, 1)}>
                  <i className="bi bi-arrow-down" />
                </Button>
                <Button variant="outline-danger" aria-label="Remover" onClick={() => remove.mutate(question.id)}>
                  <i className="bi bi-trash" />
                </Button>
              </ButtonGroup>
            </ListGroup.Item>
          ))}
        </ListGroup>
      )}
      <AddInput placeholder="Nova pergunta de pesquisa" maxLength={500} onAdd={(text) => add.mutate(text)} />
    </Panel>
  );
}

function Keywords({ planning }: { planning: Planning }) {
  const [newKeyword, setNewKeyword] = useState<{ description: string; related_to: KeywordRow["related_to"] }>({
    description: "",
    related_to: "",
  });
  const importPicoc = usePlanningMutation((base) => api.post<{ created: number }>(`${base}/keywords/import-picoc`));
  const add = usePlanningMutation((base, payload: { description: string; related_to?: string; synonym_of_id?: number }) =>
    api.post(`${base}/keywords`, payload));
  const edit = usePlanningMutation((base, args: { id: number; description?: string; related_to?: string }) =>
    api.patch(`${base}/keywords/${args.id}`, args));
  const remove = usePlanningMutation((base, id: number) => api.delete(`${base}/keywords/${id}`));

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!newKeyword.description.trim()) return;
    add.mutate(newKeyword, { onSuccess: () => setNewKeyword({ description: "", related_to: "" }) });
  }

  return (
    <Panel
      id="palavras-chave"
      title="Palavras-chave e sinônimos"
      actions={
        <Button size="sm" variant="outline-primary" disabled={importPicoc.isPending} onClick={() => importPicoc.mutate()}>
          Importar termos do PICOC
        </Button>
      }
    >
      <ErrorAlert error={importPicoc.error ?? add.error ?? edit.error ?? remove.error} />
      {importPicoc.isSuccess && (
        <Alert variant="info" className="py-2 small">{importPicoc.data.created} termo(s) importado(s) do PICOC.</Alert>
      )}
      <Table size="sm" responsive className="align-middle">
        <thead>
          <tr>
            <th style={{ width: "30%" }}>Palavra-chave</th>
            <th>Sinônimos</th>
            <th style={{ width: "18%" }}>Relacionada a</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {planning.keywords.map((keyword) => (
            <tr key={keyword.id}>
              <td>
                <InlineEdit value={keyword.description} maxLength={200}
                  onSave={(description) => edit.mutate({ id: keyword.id, description })} />
              </td>
              <td>
                <div className="d-flex flex-wrap gap-1 mb-1">
                  {keyword.synonyms.map((synonym) => (
                    <Badge key={synonym.id} bg="secondary" className="d-inline-flex align-items-center gap-1">
                      {synonym.description}
                      <button type="button" className="btn-close btn-close-white" style={{ fontSize: "0.5rem" }}
                        aria-label={`Remover ${synonym.description}`} onClick={() => remove.mutate(synonym.id)} />
                    </Badge>
                  ))}
                </div>
                <AddInput placeholder="Novo sinônimo" buttonLabel="" maxLength={200}
                  onAdd={(description) => add.mutate({ description, synonym_of_id: keyword.id })} />
              </td>
              <td>
                <Form.Select size="sm" value={keyword.related_to} aria-label="Relacionada a"
                  onChange={(event) => edit.mutate({ id: keyword.id, related_to: event.target.value })}>
                  {Object.entries(RELATED_TO).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </Form.Select>
              </td>
              <td className="text-end">
                <Button size="sm" variant="outline-danger" aria-label="Remover palavra-chave" onClick={() => remove.mutate(keyword.id)}>
                  <i className="bi bi-trash" />
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <Form onSubmit={submit} className="d-flex gap-2">
        <Form.Control size="sm" placeholder="Nova palavra-chave" value={newKeyword.description} maxLength={200}
          aria-label="Nova palavra-chave" onChange={(event) => setNewKeyword({ ...newKeyword, description: event.target.value })} />
        <Form.Select size="sm" style={{ maxWidth: 180 }} value={newKeyword.related_to} aria-label="Relacionada a"
          onChange={(event) => setNewKeyword({ ...newKeyword, related_to: event.target.value as KeywordRow["related_to"] })}>
          {Object.entries(RELATED_TO).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </Form.Select>
        <Button type="submit" size="sm" className="text-nowrap"><i className="bi bi-plus-lg me-1" />Adicionar</Button>
      </Form>
    </Panel>
  );
}

function SearchString({ planning }: { planning: Planning }) {
  const [value, setValue] = useState(planning.search_string);
  useEffect(() => setValue(planning.search_string), [planning.search_string]);
  const generate = usePlanningMutation((base) => api.post<{ search_string: string }>(`${base}/search-string/generate`));
  const save = usePlanningMutation((base) => api.put(`${base}/search-string`, { search_string: value }));

  return (
    <Panel id="string" title="String de busca">
      <ErrorAlert error={generate.error ?? save.error} />
      <Form.Control as="textarea" rows={4} value={value} className="font-monospace small" aria-label="String de busca"
        placeholder='("multi-agent system" OR MAS) AND (explainability OR XAI)'
        onChange={(event) => setValue(event.target.value)} />
      <div className="mt-2 d-flex gap-2 align-items-center">
        <Button size="sm" disabled={save.isPending} onClick={() => save.mutate()}>Salvar</Button>
        <Button size="sm" variant="outline-secondary" disabled={generate.isPending}
          onClick={() => generate.mutate(undefined, { onSuccess: (data) => setValue(data.search_string) })}>
          Gerar a partir das palavras-chave
        </Button>
        <SavedNote show={save.isSuccess} />
      </div>
      <Form.Text>A string gerada é só um ponto de partida: revise antes de salvar.</Form.Text>
    </Panel>
  );
}

const CUSTOM_CONNECTORS = ["openalex", "semantic_scholar"];

function Sources({ planning }: { planning: Planning }) {
  const review = useReview();
  const [custom, setCustom] = useState({ name: "", url: "", connector: "" });
  const connectors = useConnectors();
  const connectorLabel = (key?: string | null) => connectors.data?.find((item) => item.key === key)?.label;
  const suggested = useQuery({
    queryKey: ["suggested-sources", review.id, planning.sources.length],
    queryFn: () => api.get<SourceRow[]>(`/reviews/${review.id}/sources/suggested`),
  });
  const add = usePlanningMutation((base, payload: { source_id?: number; name?: string; url?: string; connector?: string | null }) =>
    api.post(`${base}/sources`, payload));
  const setConnector = usePlanningMutation((base, source: SourceRow & { connector: string | null }) =>
    api.patch(`${base}/sources/${source.id}`, { name: source.name, url: source.url, connector: source.connector }));
  const remove = usePlanningMutation((base, id: number) => api.delete(`${base}/sources/${id}`));

  function submit(event: FormEvent) {
    event.preventDefault();
    add.mutate({ ...custom, connector: custom.connector || null }, { onSuccess: () => setCustom({ name: "", url: "", connector: "" }) });
  }

  return (
    <Panel id="fontes" title="Fontes">
      <ErrorAlert error={add.error ?? remove.error ?? setConnector.error} />
      {planning.sources.length > 0 && (
        <Table size="sm" className="align-middle">
          <thead>
            <tr><th>Nome</th><th>URL</th><th>Busca automática</th><th /></tr>
          </thead>
          <tbody>
            {planning.sources.map((source) => (
              <tr key={source.id}>
                <td>{source.name}</td>
                <td>{source.url && <a href={source.url} target="_blank" rel="noreferrer">{source.url}</a>}</td>
                <td className="small">
                  {source.is_default ? (connectorLabel(source.connector) ?? <span className="text-muted">só importação de arquivo</span>) : (
                    <Form.Select size="sm" value={source.connector ?? ""} aria-label={`Busca automática de ${source.name}`}
                      onChange={(event) => setConnector.mutate({ ...source, connector: event.target.value || null })}>
                      <option value="">Só importação de arquivo</option>
                      {CUSTOM_CONNECTORS.map((key) => <option key={key} value={key}>{connectorLabel(key) ?? key}</option>)}
                    </Form.Select>
                  )}
                </td>
                <td className="text-end">
                  <Button size="sm" variant="outline-danger" aria-label={`Remover ${source.name}`} onClick={() => remove.mutate(source.id)}>
                    <i className="bi bi-trash" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
      {suggested.data && suggested.data.length > 0 && (
        <div className="mb-3">
          <div className="small fw-semibold mb-1">Bibliotecas digitais sugeridas</div>
          <div className="d-flex flex-wrap gap-2">
            {suggested.data.map((source) => (
              <Button key={source.id} size="sm" variant="outline-primary" onClick={() => add.mutate({ source_id: source.id })}>
                <i className="bi bi-plus-lg me-1" />{source.name}
              </Button>
            ))}
          </div>
        </div>
      )}
      <Form onSubmit={submit} className="d-flex gap-2">
        <Form.Control size="sm" placeholder="Outra fonte" required maxLength={100} value={custom.name} aria-label="Nome da fonte"
          onChange={(event) => setCustom({ ...custom, name: event.target.value })} />
        <Form.Control size="sm" placeholder="URL (opcional)" maxLength={200} value={custom.url} aria-label="URL da fonte"
          onChange={(event) => setCustom({ ...custom, url: event.target.value })} />
        <Form.Select size="sm" value={custom.connector} aria-label="Busca automática da nova fonte" style={{ maxWidth: 220 }}
          onChange={(event) => setCustom({ ...custom, connector: event.target.value })}>
          <option value="">Só importação de arquivo</option>
          {CUSTOM_CONNECTORS.map((key) => <option key={key} value={key}>Busca via {connectorLabel(key) ?? key}</option>)}
        </Form.Select>
        <Button type="submit" size="sm" className="text-nowrap"><i className="bi bi-plus-lg me-1" />Adicionar</Button>
      </Form>
    </Panel>
  );
}

function Criteria({ planning }: { planning: Planning }) {
  const add = usePlanningMutation((base, payload: { criteria_type: "I" | "E"; description: string }) =>
    api.post(`${base}/criteria`, payload));
  const remove = usePlanningMutation((base, id: number) => api.delete(`${base}/criteria/${id}`));

  const column = (type: "I" | "E", title: string, items: Planning["inclusion_criteria"]) => (
    <Col md={6}>
      <div className="fw-semibold mb-2">{title}</div>
      <ListGroup className="mb-2">
        {items.map((item) => (
          <ListGroup.Item key={item.id} className="d-flex justify-content-between align-items-center small">
            {item.description}
            <Button size="sm" variant="link" className="text-danger p-0" aria-label={`Remover ${item.description}`}
              onClick={() => remove.mutate(item.id)}>
              <i className="bi bi-x-lg" />
            </Button>
          </ListGroup.Item>
        ))}
        {items.length === 0 && <ListGroup.Item className="text-muted small">Nenhum critério.</ListGroup.Item>}
      </ListGroup>
      <AddInput placeholder={`Novo critério de ${type === "I" ? "inclusão" : "exclusão"}`} maxLength={200}
        onAdd={(description) => add.mutate({ criteria_type: type, description })} />
    </Col>
  );

  return (
    <Panel id="criterios" title="Critérios de seleção">
      <ErrorAlert error={add.error ?? remove.error} />
      <Row className="g-4">
        {column("I", "Critérios de inclusão", planning.inclusion_criteria)}
        {column("E", "Critérios de exclusão", planning.exclusion_criteria)}
      </Row>
    </Panel>
  );
}

export default function ProtocolPage({ planning }: { planning: Planning }) {
  return (
    <>
      <Objectives planning={planning} />
      <PicocSection planning={planning} />
      <Questions planning={planning} />
      <HypothesesSection />
      <Keywords planning={planning} />
      <SearchString planning={planning} />
      <Sources planning={planning} />
      <Criteria planning={planning} />
    </>
  );
}
