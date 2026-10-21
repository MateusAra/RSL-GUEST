import { Container, Nav, Navbar, NavDropdown } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import NotificationBell from "./NotificationBell";

export default function AppNavbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <Navbar variant="dark" expand="md" className="navbar-rsl">
      <Container fluid="lg">
        <Navbar.Brand as={Link} to="/">
          <i className="bi bi-journal-text me-2" />
          RSL
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="main-nav" />
        <Navbar.Collapse id="main-nav">
          {user ? (
            <Nav className="ms-auto align-items-md-center">
              <NotificationBell />
              <Nav.Link as={Link} to="/">Minhas revisões</Nav.Link>
              <NavDropdown title={user.full_name} align="end">
                <NavDropdown.Item as={Link} to="/perfil">Perfil e senha</NavDropdown.Item>
                <NavDropdown.Divider />
                <NavDropdown.Item
                  onClick={async () => {
                    await logout();
                    navigate("/entrar");
                  }}
                >
                  Sair
                </NavDropdown.Item>
              </NavDropdown>
            </Nav>
          ) : (
            <Nav className="ms-auto">
              <Nav.Link as={Link} to="/entrar">Entrar</Nav.Link>
              <Nav.Link as={Link} to="/cadastro">Criar conta</Nav.Link>
            </Nav>
          )}
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
