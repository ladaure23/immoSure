import { useState, useEffect } from "react";
import { NavLink, Outlet, useNavigate, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutDashboard, Building2, Users, FileText, UserCheck,
  AlertTriangle, Ticket, LogOut, Menu, X, ChevronRight,
} from "lucide-react";
import { useAuthStore } from "../../store/authStore";
import { getAgence } from "../../services/api";

const NAV = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Tableau de bord", exact: true },
  { to: "/dashboard/biens", icon: Building2, label: "Biens" },
  { to: "/dashboard/proprietaires", icon: Users, label: "Propriétaires" },
  { to: "/dashboard/contrats", icon: FileText, label: "Contrats" },
  { to: "/dashboard/locataires", icon: UserCheck, label: "Locataires" },
  { to: "/dashboard/risques", icon: AlertTriangle, label: "Risques J-3" },
  { to: "/dashboard/tickets", icon: Ticket, label: "Tickets" },
];

const PAGE_TITLES: Record<string, string> = {
  "/dashboard": "Tableau de bord",
  "/dashboard/biens": "Biens",
  "/dashboard/proprietaires": "Propriétaires",
  "/dashboard/contrats": "Contrats",
  "/dashboard/locataires": "Locataires",
  "/dashboard/risques": "Risques J-3",
  "/dashboard/tickets": "Tickets",
};

function decodeAgenceId(token: string | null): string | null {
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.agence_id ?? null;
  } catch {
    return null;
  }
}

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { token, logout } = useAuthStore();

  const agenceId = decodeAgenceId(token);
  const { data: agence } = useQuery({
    queryKey: ["agence", agenceId],
    queryFn: () => getAgence(agenceId!),
    enabled: !!agenceId,
  });

  const pageTitle = PAGE_TITLES[location.pathname] ?? "ImmoSure";

  useEffect(() => { setSidebarOpen(false); }, [location.pathname]);

  const initials = agence?.raison_sociale
    ? agence.raison_sociale.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase()
    : "AG";

  const handleLogout = () => { logout(); navigate("/"); };

  return (
    <div className="flex h-screen bg-[#f4f5f7] overflow-hidden">

      {/* ── Overlay mobile ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-20 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside
        className={`
          fixed top-0 left-0 h-full z-30 flex flex-col w-60
          bg-[#1a3c6e] transition-transform duration-300 ease-in-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0 md:static md:z-auto
        `}
      >
        {/* Motif décoratif de fond */}
        <div
          className="absolute inset-0 opacity-[0.04] pointer-events-none"
          style={{
            backgroundImage: `repeating-linear-gradient(
              45deg, #fff 0px, #fff 1px, transparent 1px, transparent 32px
            ), repeating-linear-gradient(
              -45deg, #fff 0px, #fff 1px, transparent 1px, transparent 32px
            )`,
          }}
        />

        {/* Logo */}
        <div className="relative z-10 flex items-center justify-between px-5 pt-5 pb-4 border-b border-white/10">
          <img
            src="/photo_2026-04-25_12-43-13.jpg"
            alt="ImmoSure"
            className="h-9 w-auto object-contain"
            style={{ filter: "brightness(0) invert(1)" }}
          />
          <button
            className="md:hidden text-white/60 hover:text-white p-1"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="relative z-10 flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
          {NAV.map(({ to, icon: Icon, label, exact }) => (
            <NavLink
              key={to}
              to={to}
              end={exact}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all group ${
                  isActive
                    ? "bg-[#2ea043]/20 text-white border border-[#2ea043]/40"
                    : "text-white/60 hover:text-white hover:bg-white/8"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "text-[#2ea043]" : ""}`} />
                  <span>{label}</span>
                  {isActive && <ChevronRight className="w-3 h-3 ml-auto text-[#2ea043]" />}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom: agence info + logout */}
        <div className="relative z-10 px-3 pb-4 border-t border-white/10 pt-3">
          <div className="flex items-center gap-3 px-2 py-2 mb-2">
            <div className="w-8 h-8 rounded-lg bg-[#2ea043]/20 border border-[#2ea043]/40 flex items-center justify-center flex-shrink-0">
              <span className="text-[10px] font-bold text-[#2ea043]">{initials}</span>
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold text-white truncate">
                {agence?.raison_sociale ?? "Agence"}
              </p>
              <p className="text-[10px] text-white/40">Commission {agence?.commission_taux ?? 8}%</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2.5 w-full px-3 py-2 rounded-xl text-sm text-white/50 hover:text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-4 h-4" />
            Se déconnecter
          </button>
        </div>
      </aside>

      {/* ── Main content ── */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* Topbar */}
        <header className="bg-white border-b border-gray-100 px-4 md:px-6 h-14 flex items-center gap-4 flex-shrink-0">
          <button
            className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </button>
          <h1 className="text-sm font-semibold text-[#1a3c6e] flex-1">{pageTitle}</h1>
          <div className="flex items-center gap-2">
            <span className="hidden sm:block text-xs text-gray-500">
              {agence?.raison_sociale ?? ""}
            </span>
            <div className="w-8 h-8 rounded-full bg-[#1a3c6e] flex items-center justify-center">
              <span className="text-[10px] font-bold text-white">{initials}</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
