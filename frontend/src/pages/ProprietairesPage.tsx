import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Users, Search, Phone, MapPin } from "lucide-react";
import { getProprietaires, getBiens, createProprietaire, OperateurMobile } from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

const OPERATEURS: OperateurMobile[] = ["MTN", "MOOV", "WAVE"];

const OPERATEUR_COLORS: Record<string, string> = {
  MTN: "bg-yellow-100 text-yellow-700",
  MOOV: "bg-blue-100 text-blue-700",
  WAVE: "bg-teal-100 text-teal-700",
};

export default function ProprietairesPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState({
    nom: "", prenom: "", telephone: "",
    compte_mobile_money: "", operateur_mobile: "" as OperateurMobile | "",
    localisation: "",
  });

  const { data: proprietaires = [], isLoading } = useQuery({ queryKey: ["proprietaires"], queryFn: getProprietaires });
  const { data: biens = [] } = useQuery({ queryKey: ["biens"], queryFn: getBiens });

  const mutation = useMutation({
    mutationFn: createProprietaire,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["proprietaires"] });
      toast.success("Propriétaire ajouté");
      setModalOpen(false);
      setForm({ nom: "", prenom: "", telephone: "", compte_mobile_money: "", operateur_mobile: "", localisation: "" });
    },
    onError: () => toast.error("Erreur lors de l'ajout"),
  });

  const biensByProprio = biens.reduce<Record<string, number>>((acc, b) => {
    acc[b.proprietaire_id] = (acc[b.proprietaire_id] ?? 0) + 1;
    return acc;
  }, {});

  const filtered = proprietaires.filter((p) =>
    `${p.nom} ${p.prenom} ${p.telephone}`.toLowerCase().includes(search.toLowerCase())
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      nom: form.nom, prenom: form.prenom, telephone: form.telephone,
      compte_mobile_money: form.compte_mobile_money || undefined,
      operateur_mobile: (form.operateur_mobile || undefined) as OperateurMobile | undefined,
      localisation: form.localisation || undefined,
    });
  };

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher un propriétaire…"
            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-xl bg-white outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10"
          />
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#1a3c6e] text-white text-sm font-semibold rounded-xl hover:bg-[#132d54] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Ajouter un propriétaire
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Propriétaire</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Téléphone</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Mobile Money</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Localisation</th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Biens</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {isLoading ? (
                [...Array(3)].map((_, i) => (
                  <tr key={i}>{[...Array(5)].map((_, j) => (
                    <td key={j} className="px-5 py-4">
                      <div className="h-3 bg-gray-100 rounded animate-pulse w-3/4" />
                    </td>
                  ))}</tr>
                ))
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-5 py-14 text-center">
                    <Users className="w-8 h-8 text-gray-200 mx-auto mb-2" />
                    <p className="text-sm text-gray-400">Aucun propriétaire</p>
                  </td>
                </tr>
              ) : (
                filtered.map((p) => (
                  <tr key={p.id} className="hover:bg-gray-50/70 transition-colors">
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-[#1a3c6e]/10 flex items-center justify-center flex-shrink-0">
                          <span className="text-[10px] font-bold text-[#1a3c6e]">
                            {p.prenom[0]}{p.nom[0]}
                          </span>
                        </div>
                        <div>
                          <p className="font-semibold text-gray-800">{p.prenom} {p.nom}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-1.5 text-gray-600">
                        <Phone className="w-3 h-3 text-gray-400" />
                        {p.telephone}
                      </div>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-2">
                        {p.operateur_mobile && (
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${OPERATEUR_COLORS[p.operateur_mobile]}`}>
                            {p.operateur_mobile}
                          </span>
                        )}
                        {p.compte_mobile_money && (
                          <span className="text-xs text-gray-500">{p.compte_mobile_money}</span>
                        )}
                        {!p.compte_mobile_money && <span className="text-gray-300 text-xs">—</span>}
                      </div>
                    </td>
                    <td className="px-5 py-3.5 text-gray-500">
                      {p.localisation ? (
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3 text-gray-400" />
                          <span className="text-xs">{p.localisation}</span>
                        </div>
                      ) : <span className="text-gray-300">—</span>}
                    </td>
                    <td className="px-5 py-3.5 text-center">
                      <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-[#1a3c6e]/10 text-[#1a3c6e] text-xs font-bold">
                        {biensByProprio[p.id] ?? 0}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        {filtered.length > 0 && (
          <div className="px-5 py-3 border-t border-gray-50 text-xs text-gray-400">
            {filtered.length} propriétaire{filtered.length > 1 ? "s" : ""}
          </div>
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Ajouter un propriétaire">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Prénom</label>
              <input required value={form.prenom} onChange={(e) => setForm({ ...form, prenom: e.target.value })}
                placeholder="Jean" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Nom</label>
              <input required value={form.nom} onChange={(e) => setForm({ ...form, nom: e.target.value })}
                placeholder="Dupont" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Téléphone</label>
            <input required value={form.telephone} onChange={(e) => setForm({ ...form, telephone: e.target.value })}
              placeholder="+229 97 00 00 00" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">Opérateur Mobile</label>
              <select value={form.operateur_mobile} onChange={(e) => setForm({ ...form, operateur_mobile: e.target.value as OperateurMobile | "" })}
                className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white">
                <option value="">Sélectionner</option>
                {OPERATEURS.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1.5">N° Mobile Money</label>
              <input value={form.compte_mobile_money} onChange={(e) => setForm({ ...form, compte_mobile_money: e.target.value })}
                placeholder="229 97 00 00 00" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Localisation</label>
            <input value={form.localisation} onChange={(e) => setForm({ ...form, localisation: e.target.value })}
              placeholder="Cotonou, Cadjehoun" className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10" />
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
