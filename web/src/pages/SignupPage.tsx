import { useState, type FormEvent } from "react";
import { Button, Card, Col, Form, Row } from "react-bootstrap";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import ErrorAlert from "../components/ErrorAlert";

export default function SignupPage() {
  const { user, signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ first_name: "", last_name: "", username: "", email: "", password: "" });
  const [error, setError] = useState<unknown>(null);
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const field = (name: keyof typeof form) => ({
    value: form[name],
    onChange: (event: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [name]: event.target.value }),
  });

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await signup(form);
      navigate("/", { replace: true });
    } catch (caught) {
      setError(caught);
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="auth-card shadow-sm">
      <Card.Body className="p-4">
        <h1 className="h4 mb-1">Criar conta</h1>
        <p className="text-muted mb-4">
          Crie sua conta para começar uma revisão ou aceitar convites de coautoria.
        </p>
        <ErrorAlert error={error} />
        <Form onSubmit={submit}>
          <Row className="g-3 mb-3">
            <Col>
              <Form.Label htmlFor="first_name">Nome</Form.Label>
              <Form.Control id="first_name" {...field("first_name")} />
            </Col>
            <Col>
              <Form.Label htmlFor="last_name">Sobrenome</Form.Label>
              <Form.Control id="last_name" {...field("last_name")} />
            </Col>
          </Row>
          <Form.Group className="mb-3" controlId="username">
            <Form.Label>Usuário</Form.Label>
            <Form.Control required minLength={3} {...field("username")} />
            <Form.Text>Letras, números, ponto, hífen e sublinhado.</Form.Text>
          </Form.Group>
          <Form.Group className="mb-3" controlId="email">
            <Form.Label>E-mail</Form.Label>
            <Form.Control type="email" required {...field("email")} />
            <Form.Text>Use o e-mail em que você recebeu um convite, se for o caso.</Form.Text>
          </Form.Group>
          <Form.Group className="mb-4" controlId="password">
            <Form.Label>Senha</Form.Label>
            <Form.Control type="password" required minLength={8} {...field("password")} />
            <Form.Text>Pelo menos 8 caracteres.</Form.Text>
          </Form.Group>
          <Button type="submit" className="w-100" disabled={busy}>
            {busy ? "Criando…" : "Criar conta"}
          </Button>
        </Form>
        <p className="text-center mt-4 mb-0">
          Já tem conta? <Link to="/entrar">Entrar</Link>
        </p>
      </Card.Body>
    </Card>
  );
}
