import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Ticket, Wrench, MessageCircle, CreditCard, Clock, CheckCircle2, AlertCircle } from "lucide-react";
import { getTickets, getContrats, getBiens, getLocataires, createTicket, updateTicket, TypeTicket, StatutTicket } from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

const TYPE_CONFIG: Record<TypeTicket, { label: string; icon: React.ElementType; color: string }> = {
  maintenance: { label: "Maintenance", icon: Wrench, color: "bg-blue-50 text-blue-700" },
  conflit: { label: "Conflit", icon: MessageCircle, color: "bg-red-50 text-red-700" },
  difficulte_paiement: { label: "Difficulté paiement", icon: CreditCard, color: "bg-amber-50 text-amber-700" },
};

const STATUT_CONFIG: Record<StatutTicket, { label: string; icon: React.ElementType; color: string }> = {
  ouvert: { label: "Ouvert", icon: AlertCircle, color: "bg-red-50 text-red-700" },
  en_cours: { label: "En cours", icon: Clock, color: "bg-amber-50 text-amber-700" },
  ferme: { label: "Fermé", icon: CheckCircle2, color: "bg-green-50 text-green-700" },
};

const fmtDate = (s: string) =>
  new Date(s).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric" });

export default function TicketsPage() {
  const qc = useQueryClient();
  const [modalOpen, setModalOpen] = useState(false);
  const [filterStatut, setFilterStatut] = useState<StatutTicket | "">("");
  const [form, setForm] = useState({
    contrat_id: "", type_ticket: "maintenance" as TypeTicket, description: "",
  });

  const { data: rawTickets, isLoading } = useQuery({ queryKey: ["tickets"], queryFn: getTickets });
  const { data: rawContrats } = useQuery({ queryKey: ["contrats"], queryFn: getContrats });
  const { data: rawBiens } = useQuery({ queryKey: ["biens"], queryFn: getBiens });
  const { data: rawLocataires } = useQuery({ queryKey: ["locataires"], queryFn: getLocataires });
  const tickets = Array.isArray(rawTickets) ? rawTickets : [];
  const contrats = Array.isArray(rawContrats) ? rawContrats : [];
  const biens = Array.isArray(rawBiens) ? rawBiens : [];
  const locataires = Array.isArray(rawLocataires) ? rawLocataires : [];

  const bienMap = Object.fromEntries(biens.map((b) => [b.id, b]));
  const locMap = Object.fromEntries(locataires.map((l) => [l.id, l]));
  const contratMap = Object.fromEntries(contrats.map((c) => [c.id, c]));

  const createMutation = useMutation({
    mutationFn: createTicket,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tickets"] });
      toast.success("Ticket créé");
      setModalOpen(false);
      setForm({ contrat_id: "", type_ticket: "maintenance", description: "" });
    },
    onError: () => toast.error("Erreur lors de la création"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, statut }: { id: string; statut: StatutTicket }) => updateTicket(id, statut),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tickets"] });
      toast.success("Statut mis à jour");
    },
  });

  const filtered = tickets.filter((t) =>
    filterStatut ? t.statut === filterStatut : true
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(form);
  };

  const STATUTS: StatutTicket[] = ["ouvert", "en_cours", "ferme"];

  return (
    <div className="p-4 md:p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="flex gap-2 flex-1">
          <button
            onClick={() => setFilterStatut("")}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              filterStatut === "" ? "bg-[#1a3c6e] text-white" : "bg-white text-gray-500 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            Tous ({tickets.length})
          </button>
          {STATUTS.map((s) => {
            const { label, color } = STATUT_CONFIG[s];
            const count = tickets.filter((t) => t.statut === s).length;
            return (
              <button
                key={s}
                onClick={() => setFilterStatut(filterStatut === s ? "" : s)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                  filterStatut === s ? `${color} ring-2 ring-offset-1 ring-current/30` : "bg-white text-gray-500 border border-gray-200 hover:bg-gray-50"
                }`}
              >
                {label} ({count})
              </button>
            );
          })}
        </div>
        <button
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-[#1a3c6e] text-white text-sm font-semibold rounded-xl hover:bg-[#132d54] transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          Nouveau ticket
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 h-24 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <Ticket className="w-10 h-10 text-gray-200 mx-auto mb-3" />
          <p className="text-sm text-gray-400">Aucun ticket</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((t) => {
            const contrat = contratMap[t.contrat_id];
            const bien = contrat ? bienMap[contrat.bien_id] : null;
            const loc = contrat ? locMap[contrat.locataire_id] : null;
            const typeConf = TYPE_CONFIG[t.type_ticket];
            const statutConf = STATUT_CONFIG[t.statut];
            const TypeIcon = typeConf.icon;
            const StatutIcon = statutConf.icon;

            return (
              <div key={t.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
                <div className="flex items-start gap-4">
                  <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${typeConf.color}`}>
                    <TypeIcon className="w-4 h-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1.5">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${typeConf.color}`}>
                        {typeConf.label}
                      </span>
                      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${statutConf.color}`}>
                        <StatutIcon className="w-3 h-3" />
                        {statutConf.label}
                      </span>
                      <span className="text-[11px] text-gray-400 ml-auto">{fmtDate(t.created_at)}</span>
                    </div>
                    {bien && (
                      <p className="text-xs font-semibold text-gray-700 mb-0.5 truncate">{bien.adresse}</p>
                    )}
                    {loc && (
                      <p className="text-[11px] text-gray-500 mb-2">{loc.prenom} {loc.nom}</p>
                    )}
                    <p className="text-sm text-gray-600 leading-relaxed">{t.description}</p>
                  </div>
                  {t.statut !== "ferme" && (
                    <div className="flex flex-col gap-1.5 flex-shrink-0">
                      {t.statut === "ouvert" && (
                        <button
                          onClick={() => updateMutation.mutate({ id: t.id, statut: "en_cours" })}
                          disabled={updateMutation.isPending}
                          className="px-3 py-1.5 text-[11px] font-medium text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-lg transition-colors"
                        >
                          Prendre en charge
                        </button>
                      )}
                      <button
                        onClick={() => updateMutation.mutate({ id: t.id, statut: "ferme" })}
                        disabled={updateMutation.isPending}
                        className="px-3 py-1.5 text-[11px] font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
                      >
                        Fermer
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="Nouveau ticket">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Contrat concerné</label>
            <select required value={form.contrat_id} onChange={(e) => setForm({ ...form, contrat_id: e.target.value })}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white">
              <option value="">Sélectionner un contrat</option>
              {contrats.filter((c) => c.statut === "actif").map((c) => {
                const bien = bienMap[c.bien_id];
                const loc = locMap[c.locataire_id];
                return (
                  <option key={c.id} value={c.id}>
                    {bien?.adresse ?? "?"} — {loc ? `${loc.prenom} ${loc.nom}` : "?"}
                  </option>
                );
              })}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Type de ticket</label>
            <select value={form.type_ticket} onChange={(e) => setForm({ ...form, type_ticket: e.target.value as TypeTicket })}
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 bg-white">
              {Object.entries(TYPE_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1.5">Description</label>
            <textarea required rows={3} value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Décrivez le problème en détail…"
              className="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 resize-none" />
          </div>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={() => setModalOpen(false)}
              className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={createMutation.isPending}
              className="flex-1 py-2.5 text-sm font-semibold text-white bg-[#1a3c6e] rounded-lg hover:bg-[#132d54] transition-colors disabled:opacity-60">
              {createMutation.isPending ? "Création…" : "Créer le ticket"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
