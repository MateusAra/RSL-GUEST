import { useState, type FormEvent } from "react";
import { Alert, Button, Col, Container, Form, Row } from "react-bootstrap";
import { useMutation } from "@tanstack/react-query";
import { api } from "../api";
import { useAuth } from "../auth";
import Panel from "../components/Panel";
import ErrorAlert from "../components/ErrorAlert";
import type { Me } from "../types";

export default function ProfilePage() {
  const { user, setUser } = useAuth();
  const [profile, setProfile] = useState({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    email: user?.email ?? "",
  });
  const [passwords, setPasswords] = useState({ current_password: "", new_password: "" });

  const saveProfile = useMutation({
    mutationFn: () => api.patch<Me>("/me", profile),
    onSuccess: setUser,
  });
  const savePassword = useMutation({
    mutationFn: () => api.post("/me/password", passwords),
    onSuccess: () => setPasswords({ current_password: "", new_password: "" }),
  });

  function submitProfile(event: FormEvent) {
    event.preventDefault();
    saveProfile.mutate();
  }

  function submitPassword(event: FormEvent) {
    event.preventDefault();
    savePassword.mutate();
  }

  return (
    <Container fluid="lg" className="py-4">
      <h1 className="h3 mb-4">Perfil</h1>
      <Row className="g-4">
        <Col md={6}>
          <Panel title="Dados pessoais">
            <ErrorAlert error={saveProfile.error} />
            {saveProfile.isSuccess && <Alert variant="success" className="py-2">Perfil salvo.</Alert>}
            <Form onSubmit={submitProfile}>
              <Form.Group className="mb-3" controlId="profile-username">
                <Form.Label>Usuário</Form.Label>
                <Form.Control value={user?.username ?? ""} disabled />
              </Form.Group>
              <Row className="g-3 mb-3">
                <Col>
                  <Form.Label htmlFor="profile-first">Nome</Form.Label>
                  <Form.Control id="profile-first" value={profile.first_name}
                    onChange={(event) => setProfile({ ...profile, first_name: event.target.value })} />
                </Col>
                <Col>
                  <Form.Label htmlFor="profile-last">Sobrenome</Form.Label>
                  <Form.Control id="profile-last" value={profile.last_name}
                    onChange={(event) => setProfile({ ...profile, last_name: event.target.value })} />
                </Col>
              </Row>
              <Form.Group className="mb-3" controlId="profile-email">
                <Form.Label>E-mail</Form.Label>
                <Form.Control type="email" required value={profile.email}
                  onChange={(event) => setProfile({ ...profile, email: event.target.value })} />
              </Form.Group>
              <Button type="submit" disabled={saveProfile.isPending}>Salvar</Button>
            </Form>
          </Panel>
        </Col>
        <Col md={6}>
          <Panel title="Alterar senha">
            <ErrorAlert error={savePassword.error} />
            {savePassword.isSuccess && <Alert variant="success" className="py-2">Senha alterada.</Alert>}
            <Form onSubmit={submitPassword}>
              <Form.Group className="mb-3" controlId="current-password">
                <Form.Label>Senha atual</Form.Label>
                <Form.Control type="password" required value={passwords.current_password}
                  onChange={(event) => setPasswords({ ...passwords, current_password: event.target.value })} />
              </Form.Group>
              <Form.Group className="mb-3" controlId="new-password">
                <Form.Label>Nova senha</Form.Label>
                <Form.Control type="password" required minLength={8} value={passwords.new_password}
                  onChange={(event) => setPasswords({ ...passwords, new_password: event.target.value })} />
              </Form.Group>
              <Button type="submit" disabled={savePassword.isPending}>Alterar senha</Button>
            </Form>
          </Panel>
        </Col>
      </Row>
    </Container>
  );
}
