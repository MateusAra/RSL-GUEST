import { Alert } from "react-bootstrap";

export default function ErrorAlert({ error }: { error: unknown }) {
  if (!error) return null;
  const message = error instanceof Error ? error.message : String(error);
  return (
    <Alert variant="danger" className="py-2">
      {message}
    </Alert>
  );
}
