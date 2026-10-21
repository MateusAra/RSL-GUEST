import { useState, type FormEvent } from "react";
import { Badge, Button, Col, Form, Row, Spinner } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";
import Panel from "../components/Panel";
import ErrorAlert from "../components/ErrorAlert";
import type { ApiKeyInfo } from "../types";

function ProviderKey({ info }: { info: ApiKeyInfo }) {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({ key: "", extra: "" });
  const refresh = () => queryClient.invalidateQueries({ queryKey: ["api-keys"] });
  const save = useMutation({
    mutationFn: () => api.put(`/me/api-keys/${info.provider}`, form),
    onSuccess: () => { setForm({ key: "", extra: "" }); refresh(); },
  });
  const remove = useMutation({ mutationFn: () => api.delete(`/me/api-keys/${info.provider}`), onSuccess: refresh });
  const test = useMutation({ mutationFn: () => api.post<{ ok: boolean; total: number | null }>(`/me/api-keys/${info.provider}/test`) });

  function submit(event: FormEvent) {
    event.preventDefault();
    test.reset();
    save.mutate();
  }

  return (
    <div className="border rounded p-3 h-100">
      <div className="d-flex justify-content-between align-items-start mb-1">
        <div className="fw-semibold">{info.label}</div>
        {info.configured
          ? <Badge bg="success">configurada ···{info.last_four}</Badge>
          : <Badge bg={info.required ? "secondary" : "light"} text={info.required ? undefined : "dark"}>{info.required ? "sem chave" : "opcional"}</Badge>}
      </div>
      <div className="small text-muted mb-2">
        Usada em: {info.connectors.join(", ")}. <a href={info.url} target="_blank" rel="noreferrer">Obter a chave</a>
      </div>
      <ErrorAlert error={save.error ?? remove.error ?? test.error} />
      {test.isSuccess && (
        <div className="small text-success mb-2">
          <i className="bi bi-check2" /> Chave aceita{test.data.total != null && ` (${test.data.total.toLocaleString("pt-BR")} resultados na consulta de teste)`}.
        </div>
      )}
      <Form onSubmit={submit}>
        <Form.Control size="sm" type="password" autoComplete="off" className="mb-2" required minLength={4}
          placeholder={info.configured ? "Nova chave (substitui a atual)" : "Chave de API"} aria-label={`Chave de ${info.label}`}
          value={form.key} onChange={(event) => setForm({ ...form, key: event.target.value })} />
        {info.extra_label && (
          <Form.Control size="sm" type="password" autoComplete="off" className="mb-2" placeholder={info.extra_label}
            aria-label={info.extra_label} value={form.extra} onChange={(event) => setForm({ ...form, extra: event.target.value })} />
        )}
        <div className="d-flex gap-2">
          <Button size="sm" type="submit" disabled={save.isPending || !form.key}>Salvar</Button>
          {info.configured && (
            <>
              <Button size="sm" variant="outline-secondary" disabled={test.isPending} onClick={() => test.mutate()}>
                {test.isPending ? "Testando…" : "Testar"}
              </Button>
              <Button size="sm" variant="outline-danger" disabled={remove.isPending} onClick={() => { test.reset(); remove.mutate(); }}>
                Remover
              </Button>
            </>
          )}
        </div>
      </Form>
    </div>
  );
}

/** The user's own API keys for the automated searches (stored encrypted, never shown back). */
export default function ApiKeysPanel() {
  const keys = useQuery({ queryKey: ["api-keys"], queryFn: () => api.get<ApiKeyInfo[]>("/me/api-keys") });
  return (
    <Panel title="Chaves de API das bases">
      <p className="small text-muted">
        As buscas automáticas usam a chave de quem as executa. As chaves ficam criptografadas no servidor e nunca são
        exibidas de volta. arXiv e ACM (via OpenAlex) funcionam sem chave.
      </p>
      {keys.isLoading ? <Spinner animation="border" size="sm" /> : <ErrorAlert error={keys.error} />}
      <Row className="g-3">
        {keys.data?.map((info) => <Col md={6} lg={4} key={info.provider}><ProviderKey info={info} /></Col>)}
      </Row>
    </Panel>
  );
}
