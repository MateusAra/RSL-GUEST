import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Spinner } from "react-bootstrap";
import type { ReactNode } from "react";
import { useAuth } from "./auth";
import AppNavbar from "./components/AppNavbar";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DashboardPage from "./pages/DashboardPage";
import ProfilePage from "./pages/ProfilePage";
import ReviewLayout from "./pages/review/ReviewLayout";
import ReviewHomePage from "./pages/review/ReviewHomePage";
import PlanningPage from "./pages/review/PlanningPage";
import ConductingPage from "./pages/review/ConductingPage";
import ReportingPage from "./pages/review/ReportingPage";
import SynthesisPage from "./pages/review/SynthesisPage";

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" />
      </div>
    );
  }
  if (!user) return <Navigate to="/entrar" state={{ from: location.pathname }} replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <>
      <AppNavbar />
      <Routes>
        <Route path="/entrar" element={<LoginPage />} />
        <Route path="/cadastro" element={<SignupPage />} />
        <Route path="/" element={<RequireAuth><DashboardPage /></RequireAuth>} />
        <Route path="/perfil" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/revisoes/:reviewId" element={<RequireAuth><ReviewLayout /></RequireAuth>}>
          <Route index element={<ReviewHomePage />} />
          <Route path="planejamento/*" element={<PlanningPage />} />
          <Route path="conducao/*" element={<ConductingPage />} />
          <Route path="sintese/*" element={<SynthesisPage />} />
          <Route path="relatorio" element={<ReportingPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
