import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, FileText, Search } from "lucide-react";
import { getContrats, getBiens, getLocataires, createContrat, StatutContrat } from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

function StatutBadge({ statut }: { statut: StatutContrat }) {
  const map: Record<StatutContrat, { cls: string; label: string }> = {
    actif: { cls: "bg-green-50 text-green-700", label: "Actif" },
    resilie: { cls: "bg-red-50 text-red-700", label: "Résilié" },
    expire: { cls: "bg-gray-100 text-gray-500", label: "Expiré" },
  };
  const { cls, label } = map[statut];
  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${cls}`}>
      {label}
    </span>
  );
}

const fmt = (n: number) => new Intl.NumberFormat("fr-FR").format(n) + " FCFA";
const fmtDate = (s: string) => new Date(s).toLocaleDateString("fr-FR");

export default function ContratsPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    bien_id: "", locataire_id: "", loyer_montant: "",
    date_debut: "", jour_echeance: "1",
  });

  const { data: rawContrats, isLoading } = useQuery({ queryKey: ["contrats"], queryFn: getContrats });
  const { data: rawBiens } = useQuery({ queryKey: ["biens"], queryFn: getBiens });
  const { data: rawLocataires } = useQuery({ queryKey: ["locataires"], queryFn: getLocataires });
  const contrats = Array.isArray(rawContrats) ? rawContrats : [];
  const biens = Array.isArray(rawBiens) ? rawBiens : [];
  const locataires = Array.isArray(rawLocataires) ? rawLocataires : [];

  const bienMap = Object.fromEntries(biens.map((b) => [b.id, b]));
  const locMap = Object.fromEntries(locataires.map((l) => [l.id, l]));

  const mutation = useMutation({
    mutationFn: createContrat,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contrats"] });
      qc.invalidateQueries({ queryKey: ["biens"] });
      toast.success("Contrat créé");
      setModalOpen(false);
      setForm({ bien_id: "", locataire_id: "", loyer_montant: "", date_debut: "", jour_echeance: "1" });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Erreur"),
  });

  const filtered = contrats.filter((c) => {
    const bien = bienMap[c.bien_id];
    const loc = locMap[c.locataire_id];
    const q = search.toLowerCase();
    return (
      bien?.adresse.toLowerCase().includes(q) ||
      `${loc?.prenom} ${loc?.nom}`.toLowerCase().includes(q)
    );
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      bien_id: form.bien_id,
      locataire_id: form.locataire_id,
      loyer_montant: parseFloat(form.loyer_montant),
      date_debut: form.date_debut,
      jour_echeance: parseInt(form.jour_echeance),
    });
  };

  const biensDisponibles = biens.filter((b) => b.statut === "disponible");

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un contrat…"
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-xl bg-white outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10"
          />
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#2ea043] text-white text-sm font-semibold rounded-xl hover:bg-[#268a38] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Nouveau contrat
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Bien</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Locataire</th>
                <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Loyer</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Début</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fin</th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">J. échéance</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                [...Array(3)].map((_, i) => (
                  <tr key={i}>{[...Array(7)].map((_, j) => (
                    <td key={j} className="px-5 py-4">
                      <div className="h-3 bg-gray-100 rounded animate-pulse w-3/4" />
                    </td>
                  ))}</tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-14 text-center">
                    <FileText className="w-8 h-8 text-gray-200 mx-auto mb-2" />
                    <p className="text-sm text-gray-400">Aucun contrat trouvé</p>
                  </td>
                </tr>
              ) : (
                filtered.map((c) => {
                  const bien = bienMap[c.bien_id];
                  const loc = locMap[c.locataire_id];
                  return (
                    <tr key={c.id} className="hover:bg-gray-50/70 transition-colors">
                      <td className="px-5 py-3.5 font-medium text-gray-800 max-w-[180px]">
                        <p className="truncate text-xs">{bien?.adresse ?? "—"}</p>
                        <p className="text-[10px] text-gray-400 capitalize">{bien?.type_bien}</p>
                      </td>
                      <td className="px-5 py-3.5 text-gray-700">
                        {loc ? `${loc.prenom} ${loc.nom}` : <span className="text-gray-300">—</span>}
                      </td>
                      <td className="px-5 py-3.5 text-right font-medium text-gray-700 whitespace-nowrap">
                        {fmt(c.loyer_montant)}
                      </td>
                      <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">{fmtDate(c.date_debut)}</td>
                      <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                        {c.date_fin ? fmtDate(c.date_fin) : <span className="text-gray-300">—</span>}
                      </td>
                      <td className="px-5 py-3.5 text-center text-gray-600 font-medium">{c.jour_echeance}</td>
                      <td className="px-5 py-3.5"><StatutBadge statut={c.statut} /></td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        {filtered.length > 0 && (
          <div className="px-5 py-3 border-t border-gray-50 text-xs text-gray-400">
            {filtered.length} contrat{filtered.length > 1 ? "s" : ""}
          </div>
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Nouveau contrat de bail" size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Bien (disponible)</label>
            <select required value={form.bien_id} onChange={(e) => {
              const bien = biens.find((b) => b.id === e.target.value);
              setForm({ ...form, bien_id: e.target.value, loyer_montant: bien?.loyer_mensuel.toString() ?? "" });
            }}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white">
              <option value="">Sélectionner un bien disponible</option>
              {biensDisponibles.map((b) => (
                <option key={b.id} value={b.id}>{b.adresse} — {b.type_bien}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Locataire</label>
            <select required value={form.locataire_id} onChange={(e) => setForm({ ...form, locataire_id: e.target.value })}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white">
              <option value="">Sélectionner un locataire</option>
              {locataires.map((l) => (
                <option key={l.id} value={l.id}>{l.prenom} {l.nom} — {l.telephone}</option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Loyer mensuel (FCFA)</label>
              <input required type="number" min="1"
                value={form.loyer_montant}
                onChange={(e) => setForm({ ...form, loyer_montant: e.target.value })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Jour d'échéance (1-28)</label>
              <input required type="number" min="1" max="28"
                value={form.jour_echeance}
                onChange={(e) => setForm({ ...form, jour_echeance: e.target.value })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Date de début</label>
            <input required type="date"
              value={form.date_debut}
              onChange={(e) => setForm({ ...form, date_debut: e.target.value })}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => setModalOpen(false)}
              className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={mutation.isPending}
              className="flex-1 py-2.5 text-sm font-semibold text-white bg-[#2ea043] rounded-lg hover:bg-[#268a38] transition-colors disabled:opacity-60">
              {mutation.isPending ? "Création…" : "Créer le contrat"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
