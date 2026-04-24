import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./store/authStore";
import LoginPage from "./pages/LoginPage";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <>{children}</> : <Navigate to="/" replace />;
}

function DashboardPlaceholder() {
  const logout = useAuthStore((s) => s.logout);
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#f4f5f7]">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-[#1a3c6e] mb-2">Dashboard</h1>
        <p className="text-gray-500 mb-6">En cours de construction — étape 8</p>
        <button
          onClick={logout}
          className="px-4 py-2 bg-[#1a3c6e] text-white rounded-lg text-sm hover:bg-[#132d54] transition-colors"
        >
          Se déconnecter
        </button>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPlaceholder />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
