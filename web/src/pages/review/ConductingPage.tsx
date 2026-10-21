import { Col, Row } from "react-bootstrap";
import { Route, Routes } from "react-router-dom";
import SideNav from "../../components/SideNav";
import SearchPage from "./conducting/SearchPage";
import ImportPage from "./conducting/ImportPage";
import SelectionPage from "./conducting/SelectionPage";
import QualityAssessmentPage from "./conducting/QualityAssessmentPage";
import DataExtractionPage from "./conducting/DataExtractionPage";
import DataAnalysisPage from "./conducting/DataAnalysisPage";

export default function ConductingPage() {
  return (
    <Row className="g-4">
      <Col md={3}>
        <SideNav
          items={[
            { to: "", label: "1. Busca", end: true },
            { to: "importar", label: "2. Importar estudos" },
            { to: "selecao", label: "3. Seleção de estudos" },
            { to: "qualidade", label: "4. Avaliação de qualidade" },
            { to: "extracao", label: "5. Extração de dados" },
            { to: "analise", label: "6. Análise de dados" },
          ]}
        />
      </Col>
      <Col md={9}>
        <Routes>
          <Route index element={<SearchPage />} />
          <Route path="importar" element={<ImportPage />} />
          <Route path="selecao" element={<SelectionPage />} />
          <Route path="qualidade" element={<QualityAssessmentPage />} />
          <Route path="extracao" element={<DataExtractionPage />} />
          <Route path="analise" element={<DataAnalysisPage />} />
        </Routes>
      </Col>
    </Row>
  );
}
