import { useState, type FormEvent } from "react";
import { Button, Card, Form } from "react-bootstrap";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import ErrorAlert from "../components/ErrorAlert";

export default function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ login: "", password: "" });
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);
  const target = (location.state as { from?: string } | null)?.from ?? "/";

  if (user) return <Navigate to={target} replace />;

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(form.login, form.password);
      navigate(target, { replace: true });
    } catch (caught) {
      setError(caught);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="auth-card shadow-sm">
      <Card.Body className="p-4">
        <h1 className="h4 mb-1">Entrar</h1>
        <p className="text-muted mb-4">Acesse suas revisões sistemáticas.</p>
        <ErrorAlert error={error} />
        <Form onSubmit={submit}>
          <Form.Group className="mb-3" controlId="login">
            <Form.Label>Usuário ou e-mail</Form.Label>
            <Form.Control
              autoFocus
              required
              value={form.login}
              onChange={(event) => setForm({ ...form, login: event.target.value })}
            />
          </Form.Group>
          <Form.Group className="mb-4" controlId="password">
            <Form.Label>Senha</Form.Label>
            <Form.Control
              type="password"
              required
              value={form.password}
              onChange={(event) => setForm({ ...form, password: event.target.value })}
            />
          </Form.Group>
          <Button type="submit" className="w-100" disabled={busy}>
            {busy ? "Entrando…" : "Entrar"}
          </Button>
        </Form>
        <p className="text-center mt-4 mb-0">
          Ainda não tem conta? <Link to="/cadastro">Criar conta</Link>
        </p>
      </Card.Body>
    </Card>
  );
}
