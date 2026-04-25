import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Phone, MapPin, Wallet, CheckCircle2, Clock } from "lucide-react";
import { getContratsRisques, ContratRisque } from "../services/api";

const fmt = (n: number) => new Intl.NumberFormat("fr-FR").format(n) + " FCFA";

function RiskCard({ r }: { r: ContratRisque }) {
  const taux = r.taux_provisionnement;
  const couleur = taux < 30 ? { bg: "bg-red-50", border: "border-red-200", bar: "#ef4444", badge: "bg-red-100 text-red-700", text: "text-red-600" }
    : taux < 70 ? { bg: "bg-amber-50", border: "border-amber-200", bar: "#f59e0b", badge: "bg-amber-100 text-amber-700", text: "text-amber-600" }
    : { bg: "bg-green-50", border: "border-green-200", bar: "#2ea043", badge: "bg-green-100 text-green-700", text: "text-green-600" };

  const urgence = r.jours_avant_echeance <= 1 ? "URGENT" : r.jours_avant_echeance <= 3 ? "J-" + r.jours_avant_echeance : null;

  return (
    <div className={`bg-white rounded-2xl border ${couleur.border} shadow-sm overflow-hidden`}>
      {/* Header coloré */}
      <div className={`${couleur.bg} px-5 py-3.5 flex items-center justify-between border-b ${couleur.border}`}>
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center shadow-sm">
            <span className="text-xs font-bold text-gray-700">
              {r.locataire_prenom[0]}{r.locataire_nom[0]}
            </span>
          </div>
          <div>
            <p className="font-semibold text-gray-900 text-sm">
              {r.locataire_prenom} {r.locataire_nom}
            </p>
            <div className="flex items-center gap-1 mt-0.5">
              <Phone className="w-3 h-3 text-gray-400" />
              <p className="text-[11px] text-gray-500">{r.locataire_telephone}</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {urgence && (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500 text-white animate-pulse">
              {urgence}
            </span>
          )}
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${couleur.badge}`}>
            {taux}%
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="px-5 py-4 space-y-3">
        <div className="flex items-start gap-2">
          <MapPin className="w-3.5 h-3.5 text-gray-400 mt-0.5 flex-shrink-0" />
          <p className="text-xs text-gray-600 leading-relaxed">{r.bien_adresse}</p>
        </div>

        {/* Barre de progression */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-1.5">
              <Wallet className="w-3 h-3 text-gray-400" />
              <span className="text-gray-500">Wallet :</span>
              <span className="font-semibold text-gray-800">{fmt(r.wallet_solde)}</span>
            </div>
            <span className="text-gray-400">/ {fmt(r.loyer_montant)}</span>
          </div>
          <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{ width: `${Math.min(100, taux)}%`, backgroundColor: couleur.bar }}
            />
          </div>
          <div className="flex items-center justify-between">
            <span className={`text-[11px] font-semibold ${couleur.text}`}>
              {taux >= 100 ? "Wallet suffisant" : `Il manque ${fmt(r.loyer_montant - r.wallet_solde)}`}
            </span>
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3 text-gray-400" />
              <span className="text-[11px] text-gray-500">
                {r.jours_avant_echeance === 0 ? "Échéance aujourd'hui" :
                 r.jours_avant_echeance === 1 ? "Échéance demain" :
                 `J-${r.jours_avant_echeance}`}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function RisquesPage() {
  const { data: risques = [], isLoading } = useQuery({
    queryKey: ["risques"],
    queryFn: getContratsRisques,
    refetchInterval: 60_000,
  });

  const critique = risques.filter((r) => r.taux_provisionnement < 30);
  const attention = risques.filter((r) => r.taux_provisionnement >= 30 && r.taux_provisionnement < 70);
  const suffisant = risques.filter((r) => r.taux_provisionnement >= 70);

  return (
    <div className="p-4 md:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <h1 className="text-base font-semibold text-[#1a3c6e]">Tableau de risques — J-3</h1>
            {risques.length > 0 && (
              <span className="px-2 py-0.5 text-[10px] font-bold bg-red-100 text-red-600 rounded-full">
                {risques.length} locataire{risques.length > 1 ? "s" : ""} à risque
              </span>
            )}
          </div>
          <p className="text-xs text-gray-400">Locataires dont le wallet est insuffisant pour couvrir le loyer</p>
        </div>
        <div className="sm:ml-auto flex gap-3">
          <div className="flex items-center gap-1.5 text-xs text-red-600 font-medium">
            <span className="w-2 h-2 rounded-full bg-red-500" />{critique.length} critique
          </div>
          <div className="flex items-center gap-1.5 text-xs text-amber-600 font-medium">
            <span className="w-2 h-2 rounded-full bg-amber-500" />{attention.length} attention
          </div>
          <div className="flex items-center gap-1.5 text-xs text-green-600 font-medium">
            <span className="w-2 h-2 rounded-full bg-green-500" />{suffisant.length} suffisant
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 h-48 animate-pulse" />
          ))}
        </div>
      ) : risques.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <div className="w-16 h-16 rounded-full bg-green-50 flex items-center justify-center mb-4">
            <CheckCircle2 className="w-8 h-8 text-green-500" />
          </div>
          <h2 className="text-base font-semibold text-gray-700 mb-2">Aucun risque détecté</h2>
          <p className="text-sm text-gray-400 max-w-sm">
            Tous les wallets sont suffisamment provisionnés pour couvrir les loyers à venir.
          </p>
        </div>
      ) : (
        <>
          {critique.length > 0 && (
            <div>
              <h2 className="text-xs font-bold text-red-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                Critique — moins de 30%
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {critique.map((r) => <RiskCard key={r.contrat_id} r={r} />)}
              </div>
            </div>
          )}
          {attention.length > 0 && (
            <div>
              <h2 className="text-xs font-bold text-amber-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                Attention — 30 à 70%
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {attention.map((r) => <RiskCard key={r.contrat_id} r={r} />)}
              </div>
            </div>
          )}
          {suffisant.length > 0 && (
            <div>
              <h2 className="text-xs font-bold text-green-600 uppercase tracking-widest mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                Suffisant — plus de 70%
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {suffisant.map((r) => <RiskCard key={r.contrat_id} r={r} />)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
