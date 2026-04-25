import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Building2, Search } from "lucide-react";
import { getBiens, getProprietaires, createBien, TypeBien } from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

const TYPES: TypeBien[] = ["appartement", "villa", "studio", "magasin"];

const fmt = (n: number) => new Intl.NumberFormat("fr-FR").format(n) + " FCFA";

function StatutBadge({ statut }: { statut: string }) {
  return statut === "loue" ? (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium">
      <span className="w-1.5 h-1.5 rounded-full bg-green-500" />Loué
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-100 text-gray-500 text-xs font-medium">
      <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />Disponible
    </span>
  );
}

export default function BiensPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    adresse: "", type_bien: "appartement" as TypeBien,
    proprietaire_id: "", loyer_mensuel: "",
  });

  const { data: biens = [], isLoading } = useQuery({ queryKey: ["biens"], queryFn: getBiens });
  const { data: proprietaires = [] } = useQuery({ queryKey: ["proprietaires"], queryFn: getProprietaires });

  const mutation = useMutation({
    mutationFn: createBien,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["biens"] });
      toast.success("Bien ajouté");
      setModalOpen(false);
      setForm({ adresse: "", type_bien: "appartement", proprietaire_id: "", loyer_mensuel: "" });
    },
    onError: () => toast.error("Erreur lors de l'ajout"),
  });

  const proprioMap = Object.fromEntries(proprietaires.map((p) => [p.id, p]));

  const filtered = biens.filter(
    (b) => b.adresse.toLowerCase().includes(search.toLowerCase()) ||
           b.type_bien.toLowerCase().includes(search.toLowerCase())
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.proprietaire_id) return toast.error("Sélectionnez un propriétaire");
    mutation.mutate({
      adresse: form.adresse,
      type_bien: form.type_bien,
      proprietaire_id: form.proprietaire_id,
      loyer_mensuel: parseFloat(form.loyer_mensuel),
    });
  };

  return (
    <div className="p-4 md:p-6 space-y-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un bien…"
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-xl bg-white outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10"
          />
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#1a3c6e] text-white text-sm font-semibold rounded-xl hover:bg-[#132d54] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Ajouter un bien
        </button>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Adresse</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Type</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Propriétaire</th>
                <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Loyer / mois</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Statut</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                [...Array(4)].map((_, i) => (
                  <tr key={i}>
                    {[...Array(5)].map((_, j) => (
                      <td key={j} className="px-5 py-4">
                        <div className="h-3 bg-gray-100 rounded animate-pulse" style={{ width: `${60 + Math.random() * 30}%` }} />
                      </td>
                    ))}
                  </tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-14 text-center">
                    <Building2 className="w-8 h-8 text-gray-200 mx-auto mb-2" />
                    <p className="text-sm text-gray-400">Aucun bien trouvé</p>
                  </td>
                </tr>
              ) : (
                filtered.map((b) => {
                  const proprio = proprioMap[b.proprietaire_id];
                  return (
                    <tr key={b.id} className="hover:bg-gray-50/70 transition-colors cursor-default">
                      <td className="px-5 py-3.5 font-medium text-gray-800 max-w-[220px]">
                        <p className="truncate">{b.adresse}</p>
                      </td>
                      <td className="px-5 py-3.5 text-gray-500 capitalize">{b.type_bien}</td>
                      <td className="px-5 py-3.5 text-gray-600">
                        {proprio ? `${proprio.prenom} ${proprio.nom}` : <span className="text-gray-300">—</span>}
                      </td>
                      <td className="px-5 py-3.5 text-right font-medium text-gray-700">{fmt(b.loyer_mensuel)}</td>
                      <td className="px-5 py-3.5"><StatutBadge statut={b.statut} /></td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        {filtered.length > 0 && (
          <div className="px-5 py-3 border-t border-gray-50 text-xs text-gray-400">
            {filtered.length} bien{filtered.length > 1 ? "s" : ""}
          </div>
        )}
      </div>

      {/* Modal ajout */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Ajouter un bien">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Adresse</label>
            <input
              required
              value={form.adresse}
              onChange={(e) => setForm({ ...form, adresse: e.target.value })}
              placeholder="123 rue exemple, Cotonou"
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Type de bien</label>
              <select
                value={form.type_bien}
                onChange={(e) => setForm({ ...form, type_bien: e.target.value as TypeBien })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white capitalize"
              >
                {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Loyer mensuel (FCFA)</label>
              <input
                required type="number" min="1"
                value={form.loyer_mensuel}
                onChange={(e) => setForm({ ...form, loyer_mensuel: e.target.value })}
                placeholder="150000"
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10"
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Propriétaire</label>
            <select
              required
              value={form.proprietaire_id}
              onChange={(e) => setForm({ ...form, proprietaire_id: e.target.value })}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white"
            >
              <option value="">Sélectionner un propriétaire</option>
              {proprietaires.map((p) => (
                <option key={p.id} value={p.id}>{p.prenom} {p.nom} — {p.telephone}</option>
              ))}
            </select>
          </div>
          <div className="flex gap-3 pt-2">
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
