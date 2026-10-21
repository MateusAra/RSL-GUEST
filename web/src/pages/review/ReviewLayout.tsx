import { Container, Nav, Spinner } from "react-bootstrap";
import { NavLink, Outlet } from "react-router-dom";
import ErrorAlert from "../../components/ErrorAlert";
import { useReviewQuery } from "./useReview";

const TABS = [
  { to: "", label: "Revisão", end: true },
  { to: "planejamento", label: "Planejamento" },
  { to: "conducao", label: "Condução" },
  { to: "sintese", label: "Síntese" },
  { to: "relatorio", label: "Relatório" },
];

export default function ReviewLayout() {
  const review = useReviewQuery();

  if (review.isLoading) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" />
      </div>
    );
  }
  if (review.error || !review.data) {
    return (
      <Container fluid="lg" className="py-4">
        <ErrorAlert error={review.error ?? "Revisão não encontrada."} />
      </Container>
    );
  }

  return (
    <>
      <div className="review-header">
        <Container fluid="lg" className="pt-3">
          <div className="small text-muted">{review.data.author.full_name}</div>
          <h1>{review.data.title}</h1>
          <Nav variant="tabs" className="review-tabs border-0 mt-2">
            {TABS.map((tab) => (
              <Nav.Item key={tab.label}>
                <Nav.Link as={NavLink} to={tab.to} end={tab.end}>
                  {tab.label}
                </Nav.Link>
              </Nav.Item>
            ))}
          </Nav>
        </Container>
      </div>
      <Container fluid="lg" className="py-4">
        <Outlet context={review.data} />
      </Container>
    </>
  );
}
