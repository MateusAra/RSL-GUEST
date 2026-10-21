import { useEffect, useState } from "react";
import { Alert, Badge, Button, Col, Form, Modal, Row, Spinner, Table } from "react-bootstrap";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { PrismaChecklistItem, PrismaStatus, ReportVersion } from "../../../types";
import { useReview } from "../useReview";
import { downloadFile } from "../conducting/download";
import PrismaFlowDiagram from "./PrismaFlowDiagram";

function usePrisma() {
  const review = useReview();
  return useQuery({ queryKey: ["prisma", review.id], queryFn: () => api.get<PrismaStatus>(`/reviews/${review.id}/prisma`) });
}

function usePrismaMutation<TArgs>(call: (base: string, args: TArgs) => Promise<unknown>) {
  const review = useReview();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: TArgs) => call(`/reviews/${review.id}`, args),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["prisma", review.id] }),
  });
}

function SectionEditor({ sectionKey, label, value, required, automatic }: {
  sectionKey: string; label: string; value: string; required: boolean; automatic: boolean;
}) {
  const [text, setText] = useState(value);
  useEffect(() => setText(value), [value]);
  const save = usePrismaMutation((base) => api.put(`${base}/prisma/sections/${sectionKey}`, { content: text }));
  return (
    <div className="mb-3">
      <Form.Label htmlFor={`section-${sectionKey}`} className="fw-semibold small mb-1">
        {label} {required && <Badge bg={value.trim() ? "success" : "danger"}>obrigatória</Badge>}
        {automatic && <Badge bg="info" className="ms-1">+ blocos automáticos do sistema</Badge>}
      </Form.Label>
      <ErrorAlert error={save.error} />
      <Form.Control id={`section-${sectionKey}`} as="textarea" rows={sectionKey === "title" ? 1 : 4} value={text}
        onChange={(event) => setText(event.target.value)} onBlur={() => { if (text !== value) save.mutate(undefined); }} />
    </div>
  );
}

function ChecklistRow({ item }: { item: PrismaChecklistItem }) {
  const [form, setForm] = useState({ status: item.status ?? "", location: item.location, justification: item.justification });
  useEffect(() => setForm({ status: item.status ?? "", location: item.location, justification: item.justification }), [item]);
  const save = usePrismaMutation((base) => api.put(`${base}/prisma/checklist/${item.item}`, form));
  const changed = form.status !== (item.status ?? "") || form.location !== item.location || form.justification !== item.justification;
  return (
    <tr>
      <td className="text-nowrap fw-semibold">{item.item}</td>
      <td>
        <div className="fw-semibold">{item.topic}</div>
        <div className="text-muted">{item.description}</div>
        <ErrorAlert error={save.error} />
      </td>
      <td style={{ minWidth: 150 }}>
        <Form.Select size="sm" value={form.status} aria-label={`Situação do item ${item.item}`}
          onChange={(event) => setForm({ ...form, status: event.target.value })}>
          <option value="">Pendente</option>
          <option value="met">Atendido</option>
          <option value="not_met">Não atendido</option>
          <option value="na">Não se aplica</option>
        </Form.Select>
      </td>
      <td style={{ minWidth: 220 }}>
        {form.status === "met" ? (
          <Form.Control size="sm" placeholder="Seção ou página" value={form.location} aria-label={`Localização do item ${item.item}`}
            onChange={(event) => setForm({ ...form, location: event.target.value })} />
        ) : form.status ? (
          <Form.Control size="sm" placeholder="Justificativa" value={form.justification} aria-label={`Justificativa do item ${item.item}`}
            onChange={(event) => setForm({ ...form, justification: event.target.value })} />
        ) : null}
      </td>
      <td><Button size="sm" disabled={!changed || !form.status || save.isPending} onClick={() => save.mutate(undefined)}>Salvar</Button></td>
    </tr>
  );
}

export function PrismaChecklistPage() {
  const prisma = usePrisma();
  if (prisma.isLoading) return <Spinner animation="border" />;
  if (!prisma.data) return <ErrorAlert error={prisma.error} />;
  const done = prisma.data.checklist.filter((item) => item.status).length;
  let currentSection = "";
  return (
    <Panel title="Checklist PRISMA 2020" actions={<span className="small text-muted">{done} de {prisma.data.checklist.length} avaliados</span>}>
      <p className="small text-muted">{prisma.data.attribution} "Atendido" exige a localização no relato; os demais exigem justificativa.</p>
      <Table size="sm" className="small align-middle">
        <tbody>
          {prisma.data.checklist.flatMap((item) => {
            const rows = [];
            if (item.section !== currentSection) {
              currentSection = item.section;
              rows.push(<tr key={`h-${item.section}`} className="table-light"><th colSpan={5}>{item.section}</th></tr>);
            }
            rows.push(<ChecklistRow key={item.item} item={item} />);
            return rows;
          })}
        </tbody>
      </Table>
    </Panel>
  );
}

export default function PrismaReportPage() {
  const review = useReview();
  const queryClient = useQueryClient();
  const prisma = usePrisma();
  const versions = useQuery({ queryKey: ["prisma-versions", review.id], queryFn: () => api.get<ReportVersion[]>(`/reviews/${review.id}/prisma/versions`) });
  const [confirm, setConfirm] = useState<"docx" | "latex" | null>(null);
  const style = usePrismaMutation((base, value: string) => api.put(`${base}/prisma/style`, { reference_style: value }));
  const exportReport = useMutation({
    mutationFn: (format: "docx" | "latex") => downloadFile(`/reviews/${review.id}/prisma/export`,
      `${review.name}-relato.${format === "docx" ? "docx" : "zip"}`, { format }),
    onSuccess: () => { setConfirm(null); queryClient.invalidateQueries({ queryKey: ["prisma-versions", review.id] }); },
  });
  const references = useMutation({
    mutationFn: (format: "bibtex" | "ris") => downloadFile(`/reviews/${review.id}/references?format=${format}`,
      `${review.name}-referencias.${format === "bibtex" ? "bib" : "ris"}`),
  });
  const downloadVersion = useMutation({
    mutationFn: (version: ReportVersion) => downloadFile(`/reviews/${review.id}/prisma/versions/${version.id}/download`, version.file_name),
  });

  if (prisma.isLoading) return <Spinner animation="border" />;
  if (!prisma.data) return <ErrorAlert error={prisma.error} />;
  const data = prisma.data;

  function startExport(format: "docx" | "latex") {
    if (data.warnings.length) setConfirm(format);
    else exportReport.mutate(format);
  }

  return (
    <>
      <Panel title="Fluxograma PRISMA 2020"><PrismaFlowDiagram flow={data.flow} /></Panel>
      <Panel title="Esqueleto do relato">
        <p className="small text-muted">
          O texto é escrito pelos pesquisadores; o sistema não redige conteúdo. Métodos e Resultados recebem, na exportação, os
          blocos com o protocolo, o fluxograma e as tabelas de qualidade, extração, temas e hipóteses.
        </p>
        {Object.entries(data.section_labels).map(([key, label]) => (
          <SectionEditor key={key} sectionKey={key} label={label} value={data.sections[key]} required={data.required.includes(key)}
            automatic={key === "methods" || key === "results"} />
        ))}
      </Panel>
      <Panel title="Exportação">
        <ErrorAlert error={style.error ?? exportReport.error ?? references.error ?? downloadVersion.error} />
        <Row className="g-3 align-items-end">
          <Col sm={4}>
            <Form.Label htmlFor="reference-style" className="small mb-1">Estilo das referências</Form.Label>
            <Form.Select id="reference-style" size="sm" value={data.reference_style} onChange={(event) => style.mutate(event.target.value)}>
              {Object.entries(data.reference_styles).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </Form.Select>
          </Col>
          <Col sm="auto" className="d-flex flex-wrap gap-2">
            <Button size="sm" disabled={exportReport.isPending} onClick={() => startExport("docx")}><i className="bi bi-file-earmark-word me-1" />Word (.docx)</Button>
            <Button size="sm" disabled={exportReport.isPending} onClick={() => startExport("latex")}><i className="bi bi-filetype-tex me-1" />LaTeX (.zip)</Button>
            <Button size="sm" variant="outline-secondary" onClick={() => references.mutate("bibtex")}>Referências .bib</Button>
            <Button size="sm" variant="outline-secondary" onClick={() => references.mutate("ris")}>Referências .ris</Button>
          </Col>
        </Row>
        <Form.Text>O mesmo estilo é usado no Word e no LaTeX. No LaTeX, as citações usam as chaves BibTeX dos estudos.</Form.Text>
      </Panel>
      <Panel title="Versões geradas">
        {versions.data?.length === 0 ? <p className="text-muted mb-0 small">Nenhuma versão gerada ainda.</p> : (
          <Table size="sm" className="small">
            <thead><tr><th>Data</th><th>Formato</th><th>Estilo</th><th>Incluídos</th><th /></tr></thead>
            <tbody>
              {versions.data?.map((version) => (
                <tr key={version.id}>
                  <td>{new Date(version.created_at).toLocaleString("pt-BR")}</td>
                  <td>{version.format === "docx" ? "Word" : "LaTeX"}</td>
                  <td>{data.reference_styles[version.reference_style]}</td>
                  <td>{version.numbers.included}</td>
                  <td className="text-end"><Button size="sm" variant="link" className="p-0" onClick={() => downloadVersion.mutate(version)}>Baixar</Button></td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Panel>
      <Modal show={confirm !== null} onHide={() => setConfirm(null)}>
        <Modal.Header closeButton><Modal.Title className="h6 mb-0">Exportar mesmo assim?</Modal.Title></Modal.Header>
        <Modal.Body>
          <Alert variant="warning" className="small mb-0"><ul className="mb-0 ps-3">{data.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul></Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={() => setConfirm(null)}>Voltar</Button>
          <Button disabled={exportReport.isPending} onClick={() => confirm && exportReport.mutate(confirm)}>Exportar</Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}
