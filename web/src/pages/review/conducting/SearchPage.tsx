import { useEffect, useState } from "react";
import { Button, Form, Nav, Spinner, Tab } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import BlockedNotice from "../../../components/BlockedNotice";
import type { SearchInfo } from "../../../types";
import { useReview } from "../useReview";

function SourceString({ reviewId, sourceId, initial, base }: { reviewId: number; sourceId: number; initial: string; base: string }) {
  const queryClient = useQueryClient();
  const [value, setValue] = useState(initial);
  useEffect(() => setValue(initial), [initial]);
  const save = useMutation({
    mutationFn: () => api.put(`/reviews/${reviewId}/search/${sourceId}`, { search_string: value }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["search", reviewId] }),
  });

  return (
    <>
      <ErrorAlert error={save.error} />
      <Form.Control as="textarea" rows={5} className="font-monospace small" value={value} aria-label="String da fonte"
        onChange={(event) => setValue(event.target.value)} />
      <div className="mt-2 d-flex gap-2 align-items-center">
        <Button size="sm" disabled={save.isPending} onClick={() => save.mutate()}>Salvar</Button>
        <Button size="sm" variant="outline-secondary" disabled={!base} onClick={() => setValue(base)}>
          Importar a string base
        </Button>
        {save.isSuccess && <span className="text-success small"><i className="bi bi-check2" /> Salvo</span>}
      </div>
      <Form.Text>Adapte a string à sintaxe da fonte antes de executar a busca nela.</Form.Text>
    </>
  );
}

export default function SearchPage() {
  const review = useReview();
  const search = useQuery({ queryKey: ["search", review.id], queryFn: () => api.get<SearchInfo>(`/reviews/${review.id}/search`) });

  if (search.isLoading) return <Spinner animation="border" />;
  if (search.error || !search.data) return <ErrorAlert error={search.error} />;
  if (search.data.sources.length === 0) {
    return (
      <BlockedNotice message="Adicione as fontes da revisão no protocolo antes de registrar as buscas."
        to={`/revisoes/${review.id}/planejamento#fontes`} linkLabel="Ir para Fontes" />
    );
  }

  return (
    <Panel title="Busca">
      <Tab.Container defaultActiveKey="base">
        <Nav variant="tabs" className="mb-3">
          <Nav.Item><Nav.Link eventKey="base">String base</Nav.Link></Nav.Item>
          {search.data.sources.map((item) => (
            <Nav.Item key={item.source.id}>
              <Nav.Link eventKey={String(item.source.id)}>
                {item.source.name}
                {item.search_string && <i className="bi bi-check2 ms-1 text-success" aria-label="string salva" />}
              </Nav.Link>
            </Nav.Item>
          ))}
        </Nav>
        <Tab.Content>
          <Tab.Pane eventKey="base">
            {search.data.base_string ? (
              <pre className="bg-light p-3 rounded small mb-0" style={{ whiteSpace: "pre-wrap" }}>{search.data.base_string}</pre>
            ) : (
              <BlockedNotice message="A string base ainda não foi definida no protocolo."
                to={`/revisoes/${review.id}/planejamento#string`} linkLabel="Definir string" />
            )}
          </Tab.Pane>
          {search.data.sources.map((item) => (
            <Tab.Pane key={item.source.id} eventKey={String(item.source.id)}>
              {item.source.url && (
                <p className="small">
                  Execute a busca em <a href={item.source.url} target="_blank" rel="noreferrer">{item.source.url}</a> e
                  importe o resultado na etapa 2.
                </p>
              )}
              <SourceString reviewId={review.id} sourceId={item.source.id} initial={item.search_string}
                base={search.data.base_string} />
            </Tab.Pane>
          ))}
        </Tab.Content>
      </Tab.Container>
    </Panel>
  );
}
