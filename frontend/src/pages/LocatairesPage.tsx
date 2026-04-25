import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, UserCheck, Search, Wallet } from "lucide-react";
import { getLocataires, getContrats, createLocataire } from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

const fmt = (n: number) => new Intl.NumberFormat("fr-FR").format(n) + " FCFA";

function ScoreBadge({ score }: { score: number }) {
  const color =
    score >= 80 ? "bg-green-50 text-green-700" :
    score >= 50 ? "bg-amber-50 text-amber-700" :
    "bg-red-50 text-red-700";
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${color}`}>
      {score}/100
    </span>
  );
}

export default function LocatairesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({ nom: "", prenom: "", telephone: "" });

  const { data: rawLocataires, isLoading } = useQuery({ queryKey: ["locataires"], queryFn: getLocataires });
  const { data: rawContrats } = useQuery({ queryKey: ["contrats"], queryFn: getContrats });
  const locataires = Array.isArray(rawLocataires) ? rawLocataires : [];
  const contrats = Array.isArray(rawContrats) ? rawContrats : [];

  const mutation = useMutation({
    mutationFn: createLocataire,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["locataires"] });
      toast.success("Locataire ajouté");
      setModalOpen(false);
      setForm({ nom: "", prenom: "", telephone: "" });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Erreur"),
  });

  const contratsActifsByLoc = contrats
    .filter((c) => c.statut === "actif")
    .reduce<Record<string, { count: number; loyer: number }>>((acc, c) => {
      if (!acc[c.locataire_id]) acc[c.locataire_id] = { count: 0, loyer: 0 };
      acc[c.locataire_id].count++;
      acc[c.locataire_id].loyer += c.loyer_montant;
      return acc;
    }, {});

  const filtered = locataires.filter((l) =>
    `${l.nom} ${l.prenom} ${l.telephone}`.toLowerCase().includes(search.toLowerCase())
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un locataire…"
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-xl bg-white outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10"
          />
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#1a3c6e] text-white text-sm font-semibold rounded-xl hover:bg-[#132d54] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Ajouter un locataire
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Locataire</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Téléphone</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide w-52">Wallet</th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Score</th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Contrats</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                [...Array(4)].map((_, i) => (
                  <tr key={i}>{[...Array(5)].map((_, j) => (
                    <td key={j} className="px-5 py-4">
                      <div className="h-3 bg-gray-100 rounded animate-pulse w-3/4" />
                    </td>
                  ))}</tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-14 text-center">
                    <UserCheck className="w-8 h-8 text-gray-200 mx-auto mb-2" />
                    <p className="text-sm text-gray-400">Aucun locataire</p>
                  </td>
                </tr>
              ) : (
                filtered.map((l) => {
                  const info = contratsActifsByLoc[l.id];
                  const loyer = info?.loyer ?? 0;
                  const taux = loyer > 0 ? Math.min(100, Math.round((l.wallet_solde / loyer) * 100)) : 0;
                  const barColor = taux >= 100 ? "#2ea043" : taux >= 30 ? "#f59e0b" : "#ef4444";

                  return (
                    <tr key={l.id} className="hover:bg-gray-50/70 transition-colors">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-[#2ea043]/10 flex items-center justify-center flex-shrink-0">
                            <span className="text-[10px] font-bold text-[#2ea043]">
                              {l.prenom[0]}{l.nom[0]}
                            </span>
                          </div>
                          <p className="font-semibold text-gray-800">{l.prenom} {l.nom}</p>
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-gray-500">{l.telephone}</td>
                      <td className="px-5 py-3.5">
                        <div className="space-y-1.5">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1">
                              <Wallet className="w-3 h-3 text-gray-400" />
                              <span className="text-xs font-medium text-gray-700">{fmt(l.wallet_solde)}</span>
                            </div>
                            {loyer > 0 && (
                              <span className="text-[10px] font-bold" style={{ color: barColor }}>
                                {taux}%
                              </span>
                            )}
                          </div>
                          {loyer > 0 && (
                            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden w-40">
                              <div
                                className="h-full rounded-full transition-all duration-500"
                                style={{ width: `${taux}%`, backgroundColor: barColor }}
                              />
                            </div>
                          )}
                          {loyer > 0 && (
                            <p className="text-[10px] text-gray-400">Loyer : {fmt(loyer)}</p>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-center">
                        <ScoreBadge score={l.score_fiabilite} />
                      </td>
                      <td className="px-5 py-3.5 text-center">
                        <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-[#1a3c6e]/10 text-[#1a3c6e] text-xs font-bold">
                          {info?.count ?? 0}
                        </span>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        {filtered.length > 0 && (
          <div className="px-5 py-3 border-t border-gray-50 text-xs text-gray-400">
            {filtered.length} locataire{filtered.length > 1 ? "s" : ""}
          </div>
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Ajouter un locataire">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Prénom</label>
              <input required value={form.prenom} onChange={(e) => setForm({ ...form, prenom: e.target.value })}
                placeholder="Kofi" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Nom</label>
              <input required value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
                placeholder="Mensah" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Téléphone (identifiant unique)</label>
            <input required value={form.telephone} onChange={(e) => setForm({ ...form, telephone: e.target.value })}
              placeholder="+229 97 00 00 00" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
          </div>
          <p className="text-xs text-gray-400 bg-blue-50 rounded-lg px-3 py-2">
            Le locataire pourra accéder au bot Telegram avec ce numéro pour gérer son wallet.
          </p>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={() => setModalOpen(false)}
              className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={mutation.isPending}
              className="flex-1 py-2.5 text-sm font-semibold text-white bg-[#1a3c6e] rounded-lg hover:bg-[#132d54] transition-colors disabled:opacity-60">
              {mutation.isPending ? "Enregistrement…" : "Ajouter"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
