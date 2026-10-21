import { Alert, Col, Row } from "react-bootstrap";
import { Route, Routes } from "react-router-dom";
import SideNav from "../../components/SideNav";
import CodebookPage from "./synthesis/CodebookPage";
import CodingPage from "./synthesis/CodingPage";
import AgreementPage from "./synthesis/AgreementPage";
import ThemesPage from "./synthesis/ThemesPage";
import PhasePage from "./synthesis/PhasePage";
import { useCoding } from "./synthesis/useSynthesis";

export default function SynthesisPage() {
  const coding = useCoding();
  const closed = coding.data?.settings.closed_at;

  return (
    <Row className="g-4">
      <Col md={3}>
        <SideNav
          items={[
            { to: "", label: "1. Codebook", end: true },
            { to: "codificacao", label: "2. Codificação" },
            { to: "concordancia", label: "3. Dupla codificação" },
            { to: "temas", label: "4. Temas" },
            { to: "fechamento", label: "5. Confiabilidade e fechamento" },
          ]}
        />
      </Col>
      <Col md={9}>
        {closed && (
          <Alert variant="secondary" className="py-2 small">
            <i className="bi bi-lock me-1" />Codificação fechada em {new Date(closed).toLocaleString("pt-BR")}. Reabra na etapa 5 para alterar.
          </Alert>
        )}
        <Routes>
          <Route index element={<CodebookPage />} />
          <Route path="codificacao" element={<CodingPage />} />
          <Route path="concordancia" element={<AgreementPage />} />
          <Route path="temas" element={<ThemesPage />} />
          <Route path="fechamento" element={<PhasePage />} />
        </Routes>
      </Col>
    </Row>
  );
}
