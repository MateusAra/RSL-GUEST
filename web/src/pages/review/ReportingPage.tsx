import { useEffect, useMemo, useState } from "react";
import { Button, Col, Form, Row, Spinner } from "react-bootstrap";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "../../api";
import Panel from "../../components/Panel";
import ErrorAlert from "../../components/ErrorAlert";
import { downloadFile } from "./conducting/download";
import { useReview } from "./useReview";

type Section = { key: string; group: string; label: string };

export default function ReportingPage() {
  const review = useReview();
  const sections = useQuery({ queryKey: ["report-sections"], queryFn: () => api.get<Section[]>("/report/sections") });
  const [chosen, setChosen] = useState<Set<string>>(new Set());
  useEffect(() => {
    if (sections.data) setChosen(new Set(sections.data.map((section) => section.key)));
  }, [sections.data]);

  const groups = useMemo(() => {
    const result = new Map<string, Section[]>();
    for (const section of sections.data ?? []) result.set(section.group, [...(result.get(section.group) ?? []), section]);
    return [...result.entries()];
  }, [sections.data]);

  const download = useMutation({
    mutationFn: () => {
      const keys = (sections.data ?? []).filter((section) => chosen.has(section.key)).map((section) => section.key);
      return downloadFile(`/reviews/${review.id}/report.docx?sections=${keys.join(",")}`, `${review.name}.docx`);
    },
  });

  function toggle(keys: string[], value: boolean) {
    const next = new Set(chosen);
    for (const key of keys) {
      if (value) next.add(key); else next.delete(key);
    }
    setChosen(next);
  }

  if (sections.isLoading) return <Spinner animation="border" />;
  const all = (sections.data ?? []).map((section) => section.key);

  return (
    <Panel
      title="Exportar relatório"
      actions={
        <Form.Check id="toggle-all" label="Marcar todos" checked={chosen.size === all.length}
          onChange={(event) => toggle(all, event.target.checked)} />
      }
    >
      <ErrorAlert error={sections.error ?? download.error} />
      <p className="small text-muted">Escolha as seções que entram no documento do Word.</p>
      <Row className="g-4 mb-3">
        {groups.map(([group, items]) => {
          const keys = items.map((item) => item.key);
          return (
            <Col md={4} key={group}>
              <Form.Check id={`group-${group}`} className="fw-semibold mb-2" label={group}
                checked={keys.every((key) => chosen.has(key))} onChange={(event) => toggle(keys, event.target.checked)} />
              {items.map((item) => (
                <Form.Check key={item.key} id={`section-${item.key}`} className="ms-3 small" label={item.label}
                  checked={chosen.has(item.key)} onChange={(event) => toggle([item.key], event.target.checked)} />
              ))}
            </Col>
          );
        })}
      </Row>
      <Button disabled={chosen.size === 0 || download.isPending} onClick={() => download.mutate()}>
        <i className="bi bi-file-earmark-word me-1" />
        {download.isPending ? "Gerando…" : "Baixar .docx"}
      </Button>
    </Panel>
  );
}
