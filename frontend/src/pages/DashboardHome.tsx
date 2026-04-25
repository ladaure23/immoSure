import { useQuery } from "@tanstack/react-query";
import {
  Building2, FileText, UserCheck, TrendingUp,
  AlertTriangle, Wallet, ArrowUpRight,
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { getBiens, getContrats, getLocataires, getContratsRisques } from "../services/api";

const MOIS = ["Nov", "Déc", "Jan", "Fév", "Mar", "Avr"];
const CHART_DATA = MOIS.map((m, i) => ({
  mois: m,
  collecté: [820000, 910000, 875000, 1020000, 980000, 1150000][i],
}));

function KpiCard({
  label, value, icon: Icon, color, sub,
}: {
  label: string; value: string | number; icon: React.ElementType;
  color: string; sub?: string;
}) {
  return (
    <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-start gap-4">
      <div className={`w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 ${color}`}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-xs text-gray-500 font-medium mb-0.5">{label}</p>
        <p className="text-2xl font-bold text-[#1a3c6e] leading-none">{value}</p>
        {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
      </div>
    </div>
  );
}

function StatutDot({ statut, wallet, loyer }: { statut: string; wallet: number; loyer: number }) {
  if (statut === "disponible") return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-100 text-gray-500 text-xs font-medium">
      <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />
      Disponible
    </span>
  );
  const taux = loyer > 0 ? (wallet / loyer) * 100 : 0;
  if (taux >= 100) return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium">
      <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
      Payé
    </span>
  );
  if (taux >= 30) return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-50 text-amber-700 text-xs font-medium">
      <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
      En cours
    </span>
  );
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-50 text-red-700 text-xs font-medium">
      <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
      À risque
    </span>
  );
}

const fmt = (n: number) =>
  new Intl.NumberFormat("fr-FR").format(n) + " FCFA";

export default function DashboardHome() {
  const { data: rawBiens } = useQuery({ queryKey: ["biens"], queryFn: getBiens });
  const { data: rawContrats } = useQuery({ queryKey: ["contrats"], queryFn: getContrats });
  const { data: rawLocataires } = useQuery({ queryKey: ["locataires"], queryFn: getLocataires });
  const { data: rawRisques } = useQuery({ queryKey: ["risques"], queryFn: getContratsRisques });

  const biens = Array.isArray(rawBiens) ? rawBiens : [];
  const contrats = Array.isArray(rawContrats) ? rawContrats : [];
  const locataires = Array.isArray(rawLocataires) ? rawLocataires : [];
  const risques = Array.isArray(rawRisques) ? rawRisques : [];

  const contratsActifs = contrats.filter((c) => c.statut === "actif").length;
  const biensLoues = biens.filter((b) => b.statut === "loue").length;

  const locataireMap = Object.fromEntries(locataires.map((l) => [l.id, l]));
  const biensAvecStatut = biens.map((b) => {
    const contrat = contrats.find((c) => c.bien_id === b.id && c.statut === "actif");
    const locataire = contrat ? locataireMap[contrat.locataire_id] : null;
    return {
      ...b,
      wallet: locataire?.wallet_solde ?? 0,
      loyer: contrat?.loyer_montant ?? b.loyer_mensuel,
    };
  });

  const tauxRecouvrement =
    risques.length === 0
      ? 100
      : Math.round(
          (risques.filter((r) => r.taux_provisionnement >= 100).length / risques.length) * 100
        );

  return (
    <div className="p-4 md:p-6 space-y-6">

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Biens gérés"
          value={biens.length}
          icon={Building2}
          color="bg-blue-50 text-[#1a3c6e]"
          sub={`${biensLoues} loués`}
        />
        <KpiCard
          label="Contrats actifs"
          value={contratsActifs}
          icon={FileText}
          color="bg-green-50 text-[#2ea043]"
          sub={`${contrats.length} au total`}
        />
        <KpiCard
          label="Locataires"
          value={locataires.length}
          icon={UserCheck}
          color="bg-purple-50 text-purple-600"
        />
        <KpiCard
          label="Taux de recouvrement"
          value={`${tauxRecouvrement}%`}
          icon={TrendingUp}
          color="bg-amber-50 text-amber-600"
          sub="Ce mois-ci"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">

        {/* Graphe collectes */}
        <div className="xl:col-span-2 bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-sm font-semibold text-[#1a3c6e]">Collectes mensuelles</h2>
              <p className="text-xs text-gray-400 mt-0.5">6 derniers mois · FCFA</p>
            </div>
            <span className="flex items-center gap-1 text-xs text-[#2ea043] font-medium">
              <ArrowUpRight className="w-3.5 h-3.5" /> +17% vs an passé
            </span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={CHART_DATA} barSize={32}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
              <XAxis dataKey="mois" tick={{ fontSize: 11, fill: "#9ca3af" }} axisLine={false} tickLine={false} />
              <YAxis
                tick={{ fontSize: 10, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(v: number) => [fmt(v), "Collecté"]}
                contentStyle={{ borderRadius: 8, border: "none", boxShadow: "0 4px 20px rgba(0,0,0,.08)", fontSize: 12 }}
              />
              <Bar dataKey="collecté" fill="#1a3c6e" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Risques */}
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <h2 className="text-sm font-semibold text-[#1a3c6e]">Risques du mois</h2>
            {risques.length > 0 && (
              <span className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-red-100 text-red-600">
                {risques.length}
              </span>
            )}
          </div>
          {risques.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <div className="w-10 h-10 rounded-full bg-green-50 flex items-center justify-center mb-3">
                <TrendingUp className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-sm font-medium text-gray-700">Aucun risque</p>
              <p className="text-xs text-gray-400 mt-1">Tous les wallets sont suffisants</p>
            </div>
          ) : (
            <div className="space-y-3">
              {risques.slice(0, 4).map((r) => {
                const taux = r.taux_provisionnement;
                const color = taux < 30 ? "#ef4444" : taux < 70 ? "#f59e0b" : "#2ea043";
                return (
                  <div key={r.contrat_id} className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs font-semibold text-gray-800">
                          {r.locataire_prenom} {r.locataire_nom}
                        </p>
                        <p className="text-[10px] text-gray-400 truncate max-w-[150px]">{r.bien_adresse}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        <Wallet className="w-3 h-3 text-gray-400" />
                        <span className="text-[10px] font-bold" style={{ color }}>{taux}%</span>
                      </div>
                    </div>
                    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700"
                        style={{ width: `${taux}%`, backgroundColor: color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Tableau biens */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-[#1a3c6e]">État du parc immobilier</h2>
          <span className="text-xs text-gray-400">{biens.length} biens</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Adresse</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Type</th>
                <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Loyer</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {biensAvecStatut.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-5 py-10 text-center text-sm text-gray-400">
                    Aucun bien enregistré
                  </td>
                </tr>
              ) : (
                biensAvecStatut.slice(0, 8).map((b) => (
                  <tr key={b.id} className="hover:bg-gray-50/70 transition-colors">
                    <td className="px-5 py-3.5 font-medium text-gray-800 max-w-[200px] truncate">{b.adresse}</td>
                    <td className="px-5 py-3.5 text-gray-500 capitalize">{b.type_bien}</td>
                    <td className="px-5 py-3.5 text-right text-gray-700 font-medium">{fmt(b.loyer_mensuel)}</td>
                    <td className="px-5 py-3.5">
                      <StatutDot statut={b.statut} wallet={b.wallet} loyer={b.loyer} />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
