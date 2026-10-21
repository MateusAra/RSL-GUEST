import { Col, Row, Spinner, Table } from "react-bootstrap";
import { useQuery } from "@tanstack/react-query";
import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from "chart.js";
import { Bar } from "react-chartjs-2";
import { api } from "../../../api";
import Panel from "../../../components/Panel";
import ErrorAlert from "../../../components/ErrorAlert";
import type { AnalysisData } from "../../../types";
import { useReview } from "../useReview";

ChartJS.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend);

const COLORS = { total: "#2c3e50", accepted: "#198754", final: "#2f80ed" };

function ChartWithTable({ title, labels, series, columns }: {
  title: string;
  labels: string[];
  series: { label: string; data: number[]; color: string }[];
  columns: string[];
}) {
  return (
    <Panel title={title}>
      {labels.length === 0 ? <p className="text-muted mb-0">Sem dados ainda.</p> : (
        <Row className="g-3 align-items-center">
          <Col lg={7}>
            <Bar
              aria-label={title}
              data={{ labels, datasets: series.map((item) => ({ label: item.label, data: item.data, backgroundColor: item.color })) }}
              options={{ responsive: true, plugins: { legend: { display: series.length > 1 } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }}
            />
          </Col>
          <Col lg={5}>
            <Table size="sm" className="small mb-0">
              <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead>
              <tbody>
                {labels.map((label, index) => (
                  <tr key={label}>
                    <td>{label}</td>
                    {series.map((item) => <td key={item.label}>{item.data[index]}</td>)}
                  </tr>
                ))}
              </tbody>
            </Table>
          </Col>
        </Row>
      )}
    </Panel>
  );
}

export default function DataAnalysisPage() {
  const review = useReview();
  const data = useQuery({ queryKey: ["analysis", review.id], queryFn: () => api.get<AnalysisData>(`/reviews/${review.id}/analysis`) });

  if (data.isLoading) return <Spinner animation="border" />;
  if (data.error || !data.data) return <ErrorAlert error={data.error} />;
  const { per_source, final_per_year, status_totals, final_total } = data.data;
  const sources = per_source.map((item) => item.source);

  return (
    <>
      <Row className="g-3 mb-4 text-center">
        {[
          ["Importados", Object.values(status_totals).reduce((a, b) => a + b, 0)],
          ["Aceitos", status_totals.A],
          ["Rejeitados", status_totals.R],
          ["Duplicados", status_totals.D],
          ["Seleção final", final_total],
        ].map(([label, value]) => (
          <Col key={label} xs={6} md>
            <div className="panel p-3">
              <div className="fs-4 fw-semibold">{value}</div>
              <div className="small text-muted">{label}</div>
            </div>
          </Col>
        ))}
      </Row>
      <ChartWithTable title="Estudos por fonte" labels={sources} columns={["Fonte", "Estudos", "Aceitos"]}
        series={[
          { label: "Estudos", data: per_source.map((item) => item.total), color: COLORS.total },
          { label: "Aceitos", data: per_source.map((item) => item.accepted), color: COLORS.accepted },
        ]} />
      <ChartWithTable title="Seleção final por ano" labels={final_per_year.map((item) => item.year)} columns={["Ano", "Estudos"]}
        series={[{ label: "Estudos", data: final_per_year.map((item) => item.count), color: COLORS.final }]} />
    </>
  );
}
