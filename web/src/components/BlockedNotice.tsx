import { Alert } from "react-bootstrap";
import { Link } from "react-router-dom";

/** Prerequisite notice with a direct link to what is missing (as Parsifal's blocked steps). */
export default function BlockedNotice({ message, to, linkLabel }: { message: string; to: string; linkLabel: string }) {
  return (
    <Alert variant="warning" className="d-flex align-items-center justify-content-between gap-3">
      <span><i className="bi bi-lock me-2" />{message}</span>
      <Link to={to} className="btn btn-sm btn-outline-dark text-nowrap">{linkLabel}</Link>
    </Alert>
  );
}
