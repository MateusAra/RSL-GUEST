import { Col, Row, Spinner } from "react-bootstrap";
import { Route, Routes } from "react-router-dom";
import SideNav from "../../components/SideNav";
import ErrorAlert from "../../components/ErrorAlert";
import ProtocolPage from "./planning/ProtocolPage";
import QualityChecklistPage from "./planning/QualityChecklistPage";
import ExtractionFormPage from "./planning/ExtractionFormPage";
import { usePlanning } from "./planning/usePlanning";

const PROTOCOL_SECTIONS = [
  { href: "#objetivos", label: "Objetivos" },
  { href: "#picoc", label: "PICOC" },
  { href: "#perguntas", label: "Perguntas de pesquisa" },
  { href: "#palavras-chave", label: "Palavras-chave e sinônimos" },
  { href: "#string", label: "String de busca" },
  { href: "#fontes", label: "Fontes" },
  { href: "#criterios", label: "Critérios de seleção" },
];

export default function PlanningPage() {
  const planning = usePlanning();

  return (
    <Row className="g-4">
      <Col md={3}>
        <SideNav
          items={[
            { to: "", label: "Protocolo", end: true, children: PROTOCOL_SECTIONS },
            { to: "qualidade", label: "Checklist de qualidade" },
            { to: "extracao", label: "Formulário de extração" },
          ]}
        />
      </Col>
      <Col md={9}>
        <ErrorAlert error={planning.error} />
        {planning.isLoading && <Spinner animation="border" />}
        {planning.data && (
          <Routes>
            <Route index element={<ProtocolPage planning={planning.data} />} />
            <Route path="qualidade" element={<QualityChecklistPage planning={planning.data} />} />
            <Route path="extracao" element={<ExtractionFormPage planning={planning.data} />} />
          </Routes>
        )}
      </Col>
    </Row>
  );
}
