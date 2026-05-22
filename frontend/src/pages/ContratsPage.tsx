import { useState } from "react";
import { useQuery, useQueries, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, FileText, Search } from "lucide-react";
import {
  getContrats, getBiens, getLocataires, getLocations, createContrat,
  StatutContrat, DureeType, Location,
} from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

const DUREE_LABELS: Record<DureeType, string> = {
  mensuel: "Mensuel (1 mois)",
  bimestriel: "Bimestriel (2 mois)",
  trimestriel: "Trimestriel (3 mois)",
  semestriel: "Semestriel (6 mois)",
  annuel: "Annuel (12 mois)",
  bail: "Bail (durée libre)",
  indefini: "Indéfini",
};

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
  const [selectedBienId, setSelectedBienId] = useState("");
  const [form, setForm] = useState({
    location_id: "", locataire_id: "", loyer_montant: "",
    date_debut: "", jour_echeance: "1",
    duree_type: "indefini" as DureeType, date_fin: "",
  });

  const { data: rawContrats, isLoading } = useQuery({ queryKey: ["contrats"], queryFn: getContrats });
  const { data: rawBiens } = useQuery({ queryKey: ["biens"], queryFn: getBiens });
  const { data: rawLocataires } = useQuery({ queryKey: ["locataires"], queryFn: getLocataires });
  const contrats = Array.isArray(rawContrats) ? rawContrats : [];
  const biens = Array.isArray(rawBiens) ? rawBiens : [];
  const locataires = Array.isArray(rawLocataires) ? rawLocataires : [];

  // Load all locations for all biens (for the table display)
  const locationQueries = useQueries({
    queries: biens.map((b) => ({
      queryKey: ["locations", b.id],
      queryFn: () => getLocations(b.id),
    })),
  });
  const allLocations: Location[] = locationQueries.flatMap((q) => Array.isArray(q.data) ? q.data : []);
  const locationMap = Object.fromEntries(allLocations.map((l) => [l.id, l]));
  const bienMap = Object.fromEntries(biens.map((b) => [b.id, b]));
  const locMap = Object.fromEntries(locataires.map((l) => [l.id, l]));

  // Locations for selected bien in modal
  const locationsForBien = allLocations.filter((l) => l.bien_id === selectedBienId && l.statut === "disponible");

  const mutation = useMutation({
    mutationFn: createContrat,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contrats"] });
      qc.invalidateQueries({ queryKey: ["locations"] });
      toast.success("Contrat créé");
      setModalOpen(false);
      setSelectedBienId("");
      setForm({ location_id: "", locataire_id: "", loyer_montant: "", date_debut: "", jour_echeance: "1", duree_type: "indefini", date_fin: "" });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Erreur"),
  });

  const filtered = contrats.filter((c) => {
    const loc = locationMap[c.location_id];
    const bien = loc ? bienMap[loc.bien_id] : undefined;
    const locataire = locMap[c.locataire_id];
    const q = search.toLowerCase();
    return (
      bien?.adresse.toLowerCase().includes(q) ||
      loc?.nom.toLowerCase().includes(q) ||
      `${locataire?.prenom} ${locataire?.nom}`.toLowerCase().includes(q)
    );
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload: Parameters<typeof createContrat>[0] = {
      location_id: form.location_id,
      locataire_id: form.locataire_id,
      loyer_montant: parseFloat(form.loyer_montant),
      date_debut: form.date_debut,
      jour_echeance: parseInt(form.jour_echeance),
      duree_type: form.duree_type,
    };
    if (form.duree_type === "bail") {
      if (!form.date_fin) return toast.error("La date de fin est requise pour un bail");
      payload.date_fin = form.date_fin;
    }
    mutation.mutate(payload);
  };

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
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Location</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Locataire</th>
                <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Loyer</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Durée</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Début</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fin</th>
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
                  const loc = locationMap[c.location_id];
                  const bien = loc ? bienMap[loc.bien_id] : undefined;
                  const locataire = locMap[c.locataire_id];
                  return (
                    <tr key={c.id} className="hover:bg-gray-50/70 transition-colors">
                      <td className="px-5 py-3.5 max-w-[200px]">
                        <p className="font-medium text-gray-800 truncate text-xs">{loc?.nom ?? "—"}</p>
                        <p className="text-[10px] text-gray-400 truncate">{bien?.adresse}</p>
                      </td>
                      <td className="px-5 py-3.5 text-gray-700">
                        {locataire ? `${locataire.prenom} ${locataire.nom}` : <span className="text-gray-300">—</span>}
                      </td>
                      <td className="px-5 py-3.5 text-right font-medium text-gray-700 whitespace-nowrap">
                        {fmt(c.loyer_montant)}
                      </td>
                      <td className="px-5 py-3.5 text-gray-500 text-xs capitalize">{c.duree_type}</td>
                      <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">{fmtDate(c.date_debut)}</td>
                      <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                        {c.date_fin ? fmtDate(c.date_fin) : <span className="text-gray-300">—</span>}
                      </td>
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

      <Modal open={modalOpen} onClose={() => { setModalOpen(false); setSelectedBienId(""); }} title="Nouveau contrat de bail" size="md">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Step 1: Select bien */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Bien</label>
            <select
              required
              value={selectedBienId}
              onChange={(e) => {
                setSelectedBienId(e.target.value);
                setForm({ ...form, location_id: "" });
              }}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] bg-white"
            >
              <option value="">Sélectionner un bien</option>
              {biens.map((b) => <option key={b.id} value={b.id}>{b.adresse}</option>)}
            </select>
          </div>

          {/* Step 2: Select location (disponible) */}
          {selectedBienId && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Location (unité)</label>
              <select
                required
                value={form.location_id}
                onChange={(e) => {
                  const loc = allLocations.find((l) => l.id === e.target.value);
                  setForm({ ...form, location_id: e.target.value, loyer_montant: loc ? String(loc.loyer_mensuel) : form.loyer_montant });
                }}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] bg-white"
              >
                <option value="">Sélectionner une location disponible</option>
                {locationsForBien.map((l) => (
                  <option key={l.id} value={l.id}>{l.nom} — {l.type_location} {l.surface_m2 ? `(${l.surface_m2} m²)` : ""}</option>
                ))}
              </select>
              {locationsForBien.length === 0 && (
                <p className="text-xs text-orange-500 mt-1">Aucune location disponible pour ce bien.</p>
              )}
            </div>
          )}

          {/* Locataire */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Locataire</label>
            <select required value={form.locataire_id} onChange={(e) => setForm({ ...form, locataire_id: e.target.value })}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] bg-white">
              <option value="">Sélectionner un locataire</option>
              {locataires.map((l) => <option key={l.id} value={l.id}>{l.prenom} {l.nom} — {l.telephone}</option>)}
            </select>
          </div>

          {/* Loyer + Jour échéance */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Loyer (FCFA)</label>
              <input required type="number" min="1" value={form.loyer_montant}
                onChange={(e) => setForm({ ...form, loyer_montant: e.target.value })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e]" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Jour d'échéance (1-28)</label>
              <input required type="number" min="1" max="28" value={form.jour_echeance}
                onChange={(e) => setForm({ ...form, jour_echeance: e.target.value })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e]" />
            </div>
          </div>

          {/* Date début + Durée */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Date de début</label>
              <input required type="date" value={form.date_debut}
                onChange={(e) => setForm({ ...form, date_debut: e.target.value })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e]" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Type de durée</label>
              <select value={form.duree_type} onChange={(e) => setForm({ ...form, duree_type: e.target.value as DureeType, date_fin: "" })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] bg-white">
                {(Object.keys(DUREE_LABELS) as DureeType[]).map((k) => (
                  <option key={k} value={k}>{DUREE_LABELS[k]}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Date fin (bail only) */}
          {form.duree_type === "bail" && (
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Date de fin (obligatoire pour bail)</label>
              <input required type="date" value={form.date_fin}
                onChange={(e) => setForm({ ...form, date_fin: e.target.value })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e]" />
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={() => { setModalOpen(false); setSelectedBienId(""); }}
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
