import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./store/authStore";
import LoginPage from "./pages/LoginPage";
import DashboardLayout from "./components/layout/DashboardLayout";
import DashboardHome from "./pages/DashboardHome";
import BiensPage from "./pages/BiensPage";
import ProprietairesPage from "./pages/ProprietairesPage";
import ContratsPage from "./pages/ContratsPage";
import LocatairesPage from "./pages/LocatairesPage";
import RisquesPage from "./pages/RisquesPage";
import TicketsPage from "./pages/TicketsPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardHome />} />
        <Route path="biens" element={<BiensPage />} />
        <Route path="proprietaires" element={<ProprietairesPage />} />
        <Route path="contrats" element={<ContratsPage />} />
        <Route path="locataires" element={<LocatairesPage />} />
        <Route path="risques" element={<RisquesPage />} />
        <Route path="tickets" element={<TicketsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
