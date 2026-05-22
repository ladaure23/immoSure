import { useState, useMemo } from "react";
import { useQuery, useQueries, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ChevronRight, Plus, Building2, Home, Store,
  BedDouble, Search, MapPin, User, Calendar,
  Phone, Clock, Layers, FileText, ShoppingBag, TrendingUp,
} from "lucide-react";
import {
  getBiens, getProprietaires, getLocations, getContrats, getLocataires,
  getPaiementsLoyer, initierPaiement,
  createBien, createLocation, createContrat, updateContrat,
  TypeBien, TypeLocation, DureeType,
  Bien, Location, Contrat, Locataire, Proprietaire, PaiementLoyer,
} from "../services/api";
import Modal from "../components/ui/Modal";
import toast from "react-hot-toast";

// ── Icon maps ──────────────────────────────────────────────────────────────

const BIEN_ICONS: Record<TypeBien, React.ElementType> = {
  immeuble: Building2, villa: Home, maison: Home,
  appartement: BedDouble, studio: BedDouble,
  magasin: Store, autre: MapPin,
};
const LOC_ICONS: Record<TypeLocation, React.ElementType> = {
  appartement: Layers, studio: BedDouble, chambre: BedDouble,
  villa: Home, magasin: ShoppingBag, bureau: FileText, autre: MapPin,
};
const TYPES_BIEN: TypeBien[] = ["immeuble", "villa", "maison", "appartement", "studio", "magasin", "autre"];
const TYPES_LOC: TypeLocation[] = ["appartement", "studio", "chambre", "villa", "magasin", "bureau", "autre"];
const DUREES: { value: DureeType; label: string }[] = [
  { value: "mensuel",     label: "Mensuel (1 mois)" },
  { value: "bimestriel",  label: "Bimestriel (2 mois)" },
  { value: "trimestriel", label: "Trimestriel (3 mois)" },
  { value: "semestriel",  label: "Semestriel (6 mois)" },
  { value: "annuel",      label: "Annuel (12 mois)" },
  { value: "bail",        label: "Bail (durée libre)" },
  { value: "indefini",    label: "Indéfini" },
];
const DUREE_SHORT: Record<string, string> = {
  mensuel: "Mensuel", bimestriel: "2 mois", trimestriel: "3 mois",
  semestriel: "6 mois", annuel: "Annuel", bail: "Bail", indefini: "Indéfini",
};

const fmt = (n: number | string) =>
  new Intl.NumberFormat("fr-FR").format(Number(n)) + " FCFA";
const fmtShort = (n: number | string) => {
  const v = Number(n);
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M FCFA`;
  if (v >= 1_000)     return `${Math.round(v / 1_000)}k FCFA`;
  return `${v} FCFA`;
};
const fmtDate = (s: string) =>
  new Date(s).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "2-digit" });

// ── Collapse animation wrapper ─────────────────────────────────────────────

function Collapse({ open, children }: { open: boolean; children: React.ReactNode }) {
  return (
    <div
      style={{
        display: "grid",
        gridTemplateRows: open ? "1fr" : "0fr",
        transition: "grid-template-rows 280ms cubic-bezier(0.4, 0, 0.2, 1)",
      }}
    >
      <div style={{ overflow: "hidden" }}>{children}</div>
    </div>
  );
}

// ── Level 3 : ContratRow ───────────────────────────────────────────────────

function ContratRow({
  contrat, locataire, paiementLoyer, onResilier, resilierPending, onDemanderPaiement,
}: {
  contrat: Contrat;
  locataire?: Locataire;
  paiementLoyer?: PaiementLoyer;
  onResilier: () => void;
  resilierPending: boolean;
  onDemanderPaiement: (contrat: Contrat) => void;
}) {
  const loyer = Number(contrat.loyer_montant);
  const totalPaye = Number(paiementLoyer?.total_paye ?? 0);
  const taux = loyer > 0 ? Math.min(100, Math.round((totalPaye / loyer) * 100)) : 0;
  const payColor = taux >= 100 ? "#2ea043" : taux >= 30 ? "#f59e0b" : "#ef4444";
  const initiales = locataire
    ? `${locataire.prenom[0]}${locataire.nom[0]}`.toUpperCase()
    : "??";

  const statutCls =
    contrat.statut === "actif"   ? "bg-green-50 text-green-700 border-green-200" :
    contrat.statut === "resilie" ? "bg-red-50 text-red-700 border-red-200" :
                                   "bg-gray-50 text-gray-500 border-gray-200";

  return (
    <div className="mt-2 ml-5 sm:ml-7">
      <div className="border-l-[3px] border-[#2ea043]/30 pl-3 sm:pl-4">
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          {/* Colour accent */}
          <div className="h-0.5" style={{ backgroundColor: payColor, opacity: 0.5 }} />

          <div className="p-3 sm:p-4">
            {/* Header */}
            <div className="flex items-start gap-3">
              {/* Avatar */}
              <div
                className="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center text-white text-xs font-bold"
                style={{ background: "linear-gradient(135deg, #1a3c6e 0%, #2ea043 100%)" }}
              >
                {initiales}
              </div>

              <div className="flex-1 min-w-0">
                {/* Name + badges */}
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="font-semibold text-gray-800 text-sm leading-tight">
                    {locataire ? `${locataire.prenom} ${locataire.nom}` : "Locataire inconnu"}
                  </span>
                  <span className={`inline-flex items-center text-[10px] px-1.5 py-0.5 rounded border font-medium ${statutCls}`}>
                    {contrat.statut}
                  </span>
                  <span className="inline-flex items-center text-[10px] px-1.5 py-0.5 rounded bg-blue-50 border border-blue-100 text-[#1a3c6e] font-medium">
                    {DUREE_SHORT[contrat.duree_type] ?? contrat.duree_type}
                  </span>
                </div>
                {locataire?.telephone && (
                  <p className="text-[11px] text-gray-400 mt-0.5 flex items-center gap-1">
                    <Phone className="w-2.5 h-2.5" /> {locataire.telephone}
                  </p>
                )}
              </div>

              {/* Loyer / echéance */}
              <div className="text-right flex-shrink-0">
                <p className="text-sm font-bold text-gray-800">{fmtShort(loyer)}</p>
                <p className="text-[10px] text-gray-400 flex items-center gap-1 justify-end mt-0.5">
                  <Clock className="w-2.5 h-2.5" /> J-{contrat.jour_echeance}
                </p>
              </div>
            </div>

            {/* Dates */}
            <div className="mt-2 flex items-center gap-1.5 text-[10px] text-gray-400">
              <Calendar className="w-3 h-3 flex-shrink-0" />
              <span>{fmtDate(contrat.date_debut)}</span>
              <span className="text-gray-300">→</span>
              <span>{contrat.date_fin ? fmtDate(contrat.date_fin) : "indéfini"}</span>
            </div>

            {/* Barre de paiement du mois */}
            <div className="mt-3 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-gray-400 flex items-center gap-1">
                  <TrendingUp className="w-2.5 h-2.5" />
                  {paiementLoyer ? `${fmtShort(totalPaye)} payé` : "Aucun paiement ce mois"}
                </span>
                <span className="text-[10px] font-bold" style={{ color: payColor }}>
                  {taux}%
                </span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${taux}%`, backgroundColor: payColor }}
                />
              </div>
            </div>

            {/* Actions */}
            {contrat.statut === "actif" && (
              <div className="mt-3 flex items-center justify-between gap-2">
                <button
                  onClick={() => onDemanderPaiement(contrat)}
                  className="flex items-center gap-1 text-[11px] px-3 py-1.5 rounded-lg bg-[#1a3c6e] text-white font-medium hover:bg-[#132d54] transition-colors"
                >
                  <Plus className="w-3 h-3" />
                  Demander paiement
                </button>
                <button
                  onClick={onResilier}
                  disabled={resilierPending}
                  className="text-[11px] px-3 py-1.5 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 font-medium transition-all border border-transparent hover:border-red-200 disabled:opacity-40"
                >
                  Résilier
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Level 2 : LocationRow ──────────────────────────────────────────────────

function LocationRow({
  location, contrats, locataireMap, paiementsByContrat, onAddContrat,
  isExpanded, onToggle, onResilier, resilierPending, onDemanderPaiement,
}: {
  location: Location;
  contrats: Contrat[];
  locataireMap: Record<string, Locataire>;
  paiementsByContrat: Record<string, PaiementLoyer>;
  onAddContrat: (loc: Location) => void;
  isExpanded: boolean;
  onToggle: () => void;
  onResilier: (id: string) => void;
  resilierPending: boolean;
  onDemanderPaiement: (c: Contrat) => void;
}) {
  const Icon = LOC_ICONS[location.type_location] ?? MapPin;
  const locContrats = contrats.filter((c) => c.location_id === location.id);
  const canExpand = locContrats.length > 0;
  const isLoue = location.statut === "loue";

  return (
    <div className="mt-1.5 ml-4 sm:ml-6">
      <div className="border-l-2 border-[#1a3c6e]/12 pl-3 sm:pl-4">
        {/* Location header */}
        <div
          onClick={canExpand ? onToggle : undefined}
          className={`
            flex items-center gap-2 sm:gap-3 py-2.5 px-3 sm:px-4 rounded-xl
            border border-gray-100 bg-white transition-colors duration-150
            ${canExpand ? "cursor-pointer hover:bg-slate-50 active:bg-slate-100" : "cursor-default"}
          `}
        >
          {/* Chevron placeholder */}
          <div className="w-3.5 h-3.5 flex-shrink-0">
            {canExpand && (
              <ChevronRight
                className="w-3.5 h-3.5 text-gray-300 transition-transform duration-200"
                style={{ transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)" }}
              />
            )}
          </div>

          {/* Icon */}
          <div className={`w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 ${
            isLoue ? "bg-green-50 text-green-600" : "bg-gray-50 text-gray-400"
          }`}>
            <Icon className="w-3.5 h-3.5" />
          </div>

          {/* Name + meta */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="font-semibold text-gray-700 text-sm">{location.nom}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 text-gray-500 capitalize leading-none">
                {location.type_location}
              </span>
              {location.surface_m2 && (
                <span className="text-[10px] text-gray-400 hidden sm:inline">{location.surface_m2} m²</span>
              )}
            </div>
            {/* Loyer on mobile below name */}
            <p className="text-[11px] text-gray-400 sm:hidden mt-0.5">{fmtShort(location.loyer_mensuel)}</p>
          </div>

          {/* Right */}
          <div className="flex items-center gap-1.5 sm:gap-2.5 flex-shrink-0">
            {/* Loyer desktop */}
            <span className="text-xs font-semibold text-gray-600 hidden sm:block whitespace-nowrap">
              {fmt(location.loyer_mensuel)}
            </span>

            {/* Statut */}
            {isLoue ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-green-100 text-green-700 text-[10px] font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500 flex-shrink-0" />
                <span className="hidden sm:inline">Loué</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-gray-100 text-gray-500 text-[10px] font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-gray-400 flex-shrink-0" />
                <span className="hidden sm:inline">Disponible</span>
              </span>
            )}

            {/* Add contrat button */}
            {!isLoue && (
              <button
                onClick={(e) => { e.stopPropagation(); onAddContrat(location); }}
                className="flex items-center gap-1 px-2 sm:px-2.5 py-1 rounded-lg bg-[#2ea043] text-white text-[10px] font-bold hover:bg-[#268a38] transition-colors shadow-sm whitespace-nowrap"
              >
                <Plus className="w-3 h-3" />
                <span className="hidden sm:inline">Contrat</span>
              </button>
            )}
          </div>
        </div>

        {/* Level 3 — contrats */}
        <Collapse open={canExpand && isExpanded}>
          <div className="pb-2">
            {locContrats.map((c) => (
              <ContratRow
                key={c.id}
                contrat={c}
                locataire={locataireMap[c.locataire_id]}
                paiementLoyer={paiementsByContrat[c.id]}
                onResilier={() => onResilier(c.id)}
                resilierPending={resilierPending}
                onDemanderPaiement={onDemanderPaiement}
              />
            ))}
          </div>
        </Collapse>
      </div>
    </div>
  );
}

// ── Level 1 : BienCard ─────────────────────────────────────────────────────

function BienCard({
  bien, proprietaire, locations, locsLoading, contrats, locataireMap,
  paiementsByContrat, isExpanded, onToggle, onAddLocation, onAddContrat,
  onResilier, resilierPending, onDemanderPaiement,
}: {
  bien: Bien;
  proprietaire?: Proprietaire;
  locations: Location[];
  locsLoading: boolean;
  contrats: Contrat[];
  locataireMap: Record<string, Locataire>;
  paiementsByContrat: Record<string, PaiementLoyer>;
  isExpanded: boolean;
  onToggle: () => void;
  onAddLocation: (b: Bien) => void;
  onAddContrat: (l: Location) => void;
  onResilier: (id: string) => void;
  resilierPending: boolean;
  onDemanderPaiement: (c: Contrat) => void;
}) {
  const [expandedLocs, setExpandedLocs] = useState<Set<string>>(new Set());
  const Icon = BIEN_ICONS[bien.type_bien] ?? Building2;
  const louees = locations.filter((l) => l.statut === "loue").length;

  const pillCls =
    locations.length === 0     ? "bg-gray-100 text-gray-400" :
    louees === locations.length ? "bg-green-100 text-green-700" :
    louees > 0                  ? "bg-amber-100 text-amber-700" :
                                  "bg-gray-100 text-gray-500";

  const toggleLoc = (id: string) =>
    setExpandedLocs((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      {/* Bien header — level 1 */}
      <div
        onClick={onToggle}
        className="flex items-center gap-3 sm:gap-4 px-4 sm:px-5 py-4 cursor-pointer select-none group transition-colors duration-150 hover:bg-gray-50/60"
      >
        {/* Chevron */}
        <ChevronRight
          className="w-4 h-4 text-gray-300 group-hover:text-gray-500 flex-shrink-0 transition-transform duration-250"
          style={{ transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)" }}
        />

        {/* Icon */}
        <div className="w-10 h-10 rounded-xl bg-[#eef2f8] flex items-center justify-center flex-shrink-0 text-[#1a3c6e]">
          <Icon className="w-5 h-5" />
        </div>

        {/* Main info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="font-bold text-gray-900 text-sm sm:text-[15px] leading-tight truncate">
              {bien.nom ?? bien.adresse}
            </p>
            <span className="text-[10px] sm:text-xs px-2 py-0.5 rounded-full bg-[#1a3c6e]/10 text-[#1a3c6e] font-semibold capitalize flex-shrink-0">
              {bien.type_bien}
            </span>
          </div>
          <p className="text-[11px] text-gray-400 mt-0.5 flex items-center gap-1 truncate">
            <MapPin className="w-3 h-3 flex-shrink-0" /> {bien.adresse}
          </p>
          {proprietaire && (
            <p className="text-[11px] text-gray-400 flex items-center gap-1 truncate">
              <User className="w-3 h-3 flex-shrink-0" />
              {proprietaire.prenom} {proprietaire.nom}
            </p>
          )}
        </div>

        {/* Right: pill + add button */}
        <div className="flex items-center gap-1.5 sm:gap-2.5 flex-shrink-0">
          <span className={`text-[10px] sm:text-xs px-2 sm:px-2.5 py-1 rounded-full font-semibold whitespace-nowrap ${pillCls}`}>
            <span className="sm:hidden">{louees}/{locations.length}</span>
            <span className="hidden sm:inline">
              {locations.length} loc{locations.length > 1 ? "s" : ""} · {louees} louée{louees > 1 ? "s" : ""}
            </span>
          </span>
          <button
            onClick={(e) => { e.stopPropagation(); onAddLocation(bien); }}
            className="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1.5 rounded-xl bg-[#1a3c6e] text-white text-[10px] sm:text-xs font-bold hover:bg-[#132d54] transition-colors shadow-sm whitespace-nowrap"
          >
            <Plus className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
            <span className="hidden sm:inline">Location</span>
          </button>
        </div>
      </div>

      {/* Separator */}
      {isExpanded && <div className="h-px bg-gray-50 mx-4 sm:mx-5" />}

      {/* Locations subtree */}
      <Collapse open={isExpanded}>
        <div className="px-4 sm:px-5 pb-4 pt-3">
          {locsLoading ? (
            <div className="ml-4 sm:ml-6 space-y-2">
              {[1, 2].map((i) => (
                <div key={i} className="flex items-center gap-3 border-l-2 border-gray-100 pl-4 ml-3 py-2.5">
                  <div className="w-7 h-7 rounded-lg bg-gray-100 animate-pulse flex-shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-3 bg-gray-100 rounded animate-pulse w-1/3" />
                    <div className="h-2 bg-gray-100 rounded animate-pulse w-1/5" />
                  </div>
                </div>
              ))}
            </div>
          ) : locations.length === 0 ? (
            <div className="ml-6 py-5 text-center">
              <p className="text-sm text-gray-400 mb-1.5">Aucune location pour ce bien</p>
              <button
                onClick={() => onAddLocation(bien)}
                className="text-xs font-semibold text-[#1a3c6e] hover:underline"
              >
                + Ajouter la première location
              </button>
            </div>
          ) : (
            <div>
              {locations.map((loc) => (
                <LocationRow
                  key={loc.id}
                  location={loc}
                  contrats={contrats}
                  locataireMap={locataireMap}
                  paiementsByContrat={paiementsByContrat}
                  onAddContrat={onAddContrat}
                  isExpanded={expandedLocs.has(loc.id)}
                  onToggle={() => toggleLoc(loc.id)}
                  onResilier={onResilier}
                  resilierPending={resilierPending}
                  onDemanderPaiement={onDemanderPaiement}
                />
              ))}
            </div>
          )}
        </div>
      </Collapse>
    </div>
  );
}

// ── Form field helper ──────────────────────────────────────────────────────

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-600 mb-1.5">{label}</label>
      {children}
    </div>
  );
}
const inputCls = "w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 transition-all";
const selectCls = `${inputCls} bg-white`;

// ── Main page ──────────────────────────────────────────────────────────────

export default function BiensPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [expandedBiens, setExpandedBiens] = useState<Set<string>>(new Set());

  // Modal states
  const [bienModal, setBienModal] = useState(false);
  const [locModal, setLocModal] = useState(false);
  const [contratModal, setContratModal] = useState(false);
  const [paiementModal, setPaiementModal] = useState(false);
  const [paiementForm, setPaiementForm] = useState({ contrat_id: "", telephone: "", montant: "" });
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null);

  // Form states
  const [bienForm, setBienForm] = useState<{ nom: string; adresse: string; type_bien: TypeBien; proprietaire_id: string }>({
    nom: "", adresse: "", type_bien: "villa", proprietaire_id: "",
  });
  const [locForm, setLocForm] = useState<{
    bien_id: string; nom: string; type_location: TypeLocation; surface_m2: string; loyer_mensuel: string;
  }>({ bien_id: "", nom: "", type_location: "appartement", surface_m2: "", loyer_mensuel: "" });
  const [contratForm, setContratForm] = useState<{
    location_id: string; locataire_id: string; loyer_montant: string;
    date_debut: string; jour_echeance: string; duree_type: DureeType; date_fin: string;
  }>({ location_id: "", locataire_id: "", loyer_montant: "", date_debut: "", jour_echeance: "1", duree_type: "indefini", date_fin: "" });

  // ── Queries ─────────────────────────────────────────────────────────────
  const { data: rawBiens, isLoading: biensLoading } = useQuery({ queryKey: ["biens"], queryFn: getBiens });
  const { data: rawProprietaires } = useQuery({ queryKey: ["proprietaires"], queryFn: getProprietaires });
  const { data: rawContrats } = useQuery({ queryKey: ["contrats"], queryFn: getContrats });
  const { data: rawLocataires } = useQuery({ queryKey: ["locataires"], queryFn: getLocataires });

  const biens: Bien[]         = Array.isArray(rawBiens)         ? rawBiens         : [];
  const proprietaires: Proprietaire[] = Array.isArray(rawProprietaires) ? rawProprietaires : [];
  const contrats: Contrat[]   = Array.isArray(rawContrats)      ? rawContrats      : [];
  const locataires: Locataire[] = Array.isArray(rawLocataires)  ? rawLocataires    : [];

  const proprioMap    = Object.fromEntries(proprietaires.map((p) => [p.id, p]));
  const locataireMap  = Object.fromEntries(locataires.map((l) => [l.id, l]));

  // Load ALL locations for all biens (needed for search + pills)
  const locationQueries = useQueries({
    queries: biens.map((b) => ({
      queryKey: ["locations", b.id],
      queryFn: () => getLocations(b.id),
    })),
  });

  // Load paiements loyer for all active contrats
  const activeContrats = useMemo(
    () => contrats.filter((c) => c.statut === "actif"),
    [contrats]
  );
  const paiementQueries = useQueries({
    queries: activeContrats.map((c) => ({
      queryKey: ["paiements-loyer", c.id],
      queryFn: () => getPaiementsLoyer(c.id),
      staleTime: 30_000,
    })),
  });
  const paiementsByContrat: Record<string, PaiementLoyer> = useMemo(() => {
    const now = new Date();
    const m = now.getMonth();
    const y = now.getFullYear();
    const map: Record<string, PaiementLoyer> = {};
    activeContrats.forEach((c, i) => {
      const list = paiementQueries[i]?.data;
      if (Array.isArray(list)) {
        const current = list.find((p) => {
          const d = new Date(p.periode_debut);
          return d.getMonth() === m && d.getFullYear() === y;
        });
        if (current) map[c.id] = current;
      }
    });
    return map;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeContrats, paiementQueries]);

  const locationsByBien: Record<string, Location[]> = useMemo(() => {
    const map: Record<string, Location[]> = {};
    biens.forEach((b, i) => {
      const d = locationQueries[i]?.data;
      map[b.id] = Array.isArray(d) ? d : [];
    });
    return map;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [biens, locationQueries]);

  const allLocations = useMemo(
    () => Object.values(locationsByBien).flat(),
    [locationsByBien]
  );

  // ── Search + auto-expand ─────────────────────────────────────────────────
  const { filteredBiens, autoExpanded } = useMemo(() => {
    if (!search.trim()) return { filteredBiens: biens, autoExpanded: new Set<string>() };
    const q = search.toLowerCase();
    const auto = new Set<string>();
    const filtered = biens.filter((b) => {
      const bMatch = b.adresse.toLowerCase().includes(q) || b.type_bien.toLowerCase().includes(q) || (b.nom ?? "").toLowerCase().includes(q);
      const lMatch = (locationsByBien[b.id] ?? []).some(
        (l) => l.nom.toLowerCase().includes(q) || l.type_location.toLowerCase().includes(q)
      );
      if (lMatch) auto.add(b.id);
      return bMatch || lMatch;
    });
    return { filteredBiens: filtered, autoExpanded: auto };
  }, [search, biens, locationsByBien]);

  const effectiveExpanded = useMemo(
    () => new Set([...expandedBiens, ...autoExpanded]),
    [expandedBiens, autoExpanded]
  );

  const toggleBien = (id: string) =>
    setExpandedBiens((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  // ── Mutations ────────────────────────────────────────────────────────────
  const mutBien = useMutation({
    mutationFn: createBien,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["biens"] });
      toast.success("Bien ajouté");
      setBienModal(false);
      setBienForm({ nom: "", adresse: "", type_bien: "villa", proprietaire_id: "" });
    },
    onError: () => toast.error("Erreur lors de l'ajout"),
  });

  const mutLoc = useMutation({
    mutationFn: createLocation,
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["locations", data.bien_id] });
      toast.success("Location créée");
      setLocModal(false);
      setLocForm({ bien_id: "", nom: "", type_location: "appartement", surface_m2: "", loyer_mensuel: "" });
    },
    onError: () => toast.error("Erreur lors de la création"),
  });

  const mutContrat = useMutation({
    mutationFn: createContrat,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contrats"] });
      qc.invalidateQueries({ queryKey: ["locations"] });
      toast.success("Contrat créé");
      setContratModal(false);
      setContratForm({ location_id: "", locataire_id: "", loyer_montant: "", date_debut: "", jour_echeance: "1", duree_type: "indefini", date_fin: "" });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Erreur"),
  });

  const mutResilier = useMutation({
    mutationFn: (id: string) => updateContrat(id, { statut: "resilie" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["contrats"] });
      qc.invalidateQueries({ queryKey: ["locations"] });
      toast.success("Contrat résilié");
    },
    onError: () => toast.error("Erreur lors de la résiliation"),
  });

  const mutPaiement = useMutation({
    mutationFn: initierPaiement,
    onSuccess: (data) => {
      setPaymentUrl(data.payment_url);
      qc.invalidateQueries({ queryKey: ["paiements-loyer", paiementForm.contrat_id] });
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail ?? "Erreur lors de l'initiation du paiement"),
  });

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleDemanderPaiement = (contrat: Contrat) => {
    setPaiementForm({ contrat_id: contrat.id, telephone: "", montant: String(contrat.loyer_montant) });
    setPaymentUrl(null);
    setPaiementModal(true);
  };

  const handleAddLocation = (bien: Bien) => {
    setLocForm((f) => ({ ...f, bien_id: bien.id }));
    setLocModal(true);
  };
  const handleAddContrat = (loc: Location) => {
    setContratForm((f) => ({ ...f, location_id: loc.id, loyer_montant: String(loc.loyer_mensuel) }));
    setContratModal(true);
  };

  // ── Stats ─────────────────────────────────────────────────────────────────
  const totalLocs = allLocations.length;
  const totalLouees = allLocations.filter((l) => l.statut === "loue").length;

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="p-4 md:p-6 min-h-full">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-5">
        <div className="flex-1 min-w-0">
          <h1 className="text-lg font-bold text-[#1a3c6e]">Parc immobilier</h1>
          <p className="text-xs text-gray-400 mt-0.5">
            {biens.length} bien{biens.length > 1 ? "s" : ""}
            {totalLocs > 0 && ` · ${totalLocs} location${totalLocs > 1 ? "s" : ""} · ${totalLouees} louée${totalLouees > 1 ? "s" : ""}`}
          </p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Rechercher…"
              className="pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-xl bg-white outline-none focus:border-[#1a3c6e] focus:ring-2 focus:ring-[#1a3c6e]/10 w-36 sm:w-52 transition-all"
            />
          </div>
          {/* New bien */}
          <button
            onClick={() => setBienModal(true)}
            className="flex items-center gap-1.5 px-3 sm:px-4 py-2 bg-[#1a3c6e] text-white text-sm font-bold rounded-xl hover:bg-[#132d54] transition-colors shadow-sm whitespace-nowrap"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Nouveau bien</span>
            <span className="sm:hidden">Bien</span>
          </button>
        </div>
      </div>

      {/* Treeview */}
      {biensLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5 animate-pulse">
              <div className="flex items-center gap-4">
                <div className="w-4 h-4 rounded bg-gray-100" />
                <div className="w-10 h-10 rounded-xl bg-gray-100" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-100 rounded w-2/3" />
                  <div className="h-3 bg-gray-100 rounded w-1/4" />
                </div>
                <div className="w-20 h-7 rounded-full bg-gray-100" />
              </div>
            </div>
          ))}
        </div>
      ) : filteredBiens.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mb-4">
            <Building2 className="w-7 h-7 text-gray-300" />
          </div>
          <p className="text-gray-500 font-medium text-sm">
            {search ? "Aucun résultat pour cette recherche" : "Aucun bien enregistré"}
          </p>
          {!search && (
            <button
              onClick={() => setBienModal(true)}
              className="mt-3 text-sm font-semibold text-[#1a3c6e] hover:underline"
            >
              + Ajouter le premier bien
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filteredBiens.map((bien) => {
            const idx = biens.findIndex((b) => b.id === bien.id);
            return (
              <BienCard
                key={bien.id}
                bien={bien}
                proprietaire={proprioMap[bien.proprietaire_id]}
                locations={locationsByBien[bien.id] ?? []}
                locsLoading={locationQueries[idx]?.isLoading ?? false}
                contrats={contrats}
                locataireMap={locataireMap}
                paiementsByContrat={paiementsByContrat}
                isExpanded={effectiveExpanded.has(bien.id)}
                onToggle={() => toggleBien(bien.id)}
                onAddLocation={handleAddLocation}
                onAddContrat={handleAddContrat}
                onResilier={(id) => mutResilier.mutate(id)}
                resilierPending={mutResilier.isPending}
                onDemanderPaiement={handleDemanderPaiement}
              />
            );
          })}
        </div>
      )}

      {/* ── Modal : Nouveau bien ── */}
      <Modal open={bienModal} onClose={() => setBienModal(false)} title="Nouveau bien">
        <form
          onSubmit={(e) => {
            e.preventDefault();
                    if (!bienForm.proprietaire_id) return toast.error("Sélectionnez un propriétaire");
            mutBien.mutate(bienForm);
          }}
          className="space-y-4"
        >
          <Field label="Nom du bien">
            <input
              required value={bienForm.nom}
              onChange={(e) => setBienForm({ ...bienForm, nom: e.target.value })}
              placeholder="Villa Bel Air, Résidence Fidjrossè…"
              className={inputCls}
            />
          </Field>
          <Field label="Adresse">
            <input
              required value={bienForm.adresse}
              onChange={(e) => setBienForm({ ...bienForm, adresse: e.target.value })}
              placeholder="Rue 12, Fidjrossè, Cotonou"
              className={inputCls}
            />
          </Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Type de bien">
              <select
                value={bienForm.type_bien}
                onChange={(e) => setBienForm({ ...bienForm, type_bien: e.target.value as TypeBien })}
                className={selectCls}
              >
                {TYPES_BIEN.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </Field>
            <Field label="Propriétaire">
              <select
                required value={bienForm.proprietaire_id}
                onChange={(e) => setBienForm({ ...bienForm, proprietaire_id: e.target.value })}
                className={selectCls}
              >
                <option value="">Choisir…</option>
                {proprietaires.map((p) => (
                  <option key={p.id} value={p.id}>{p.prenom} {p.nom}</option>
                ))}
              </select>
            </Field>
          </div>
          <div className="flex gap-3 pt-1">
            <button type="button" onClick={() => setBienModal(false)}
              className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={mutBien.isPending}
              className="flex-1 py-2.5 text-sm font-bold text-white bg-[#1a3c6e] rounded-lg hover:bg-[#132d54] transition-colors disabled:opacity-60">
              {mutBien.isPending ? "Enregistrement…" : "Créer le bien"}
            </button>
          </div>
        </form>
      </Modal>

      {/* ── Modal : Nouvelle location ── */}
      <Modal open={locModal} onClose={() => setLocModal(false)} title="Nouvelle location">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutLoc.mutate({
              bien_id: locForm.bien_id,
              nom: locForm.nom,
              type_location: locForm.type_location,
              surface_m2: locForm.surface_m2 ? parseFloat(locForm.surface_m2) : undefined,
              loyer_mensuel: parseFloat(locForm.loyer_mensuel),
            });
          }}
          className="space-y-4"
        >
          {/* Bien parent */}
          {locForm.bien_id ? (
            <div className="flex items-start gap-2 px-3 py-2.5 bg-[#eef2f8] rounded-lg border border-[#1a3c6e]/15">
              <MapPin className="w-3.5 h-3.5 text-[#1a3c6e] mt-0.5 flex-shrink-0" />
              <div className="text-xs text-[#1a3c6e]">
                <p className="font-semibold">{biens.find((b) => b.id === locForm.bien_id)?.adresse}</p>
                <button
                  type="button"
                  onClick={() => setLocForm((f) => ({ ...f, bien_id: "" }))}
                  className="text-[#1a3c6e]/60 hover:text-[#1a3c6e] mt-0.5 underline"
                >
                  Changer
                </button>
              </div>
            </div>
          ) : (
            <Field label="Bien parent">
              <select
                required value={locForm.bien_id}
                onChange={(e) => setLocForm({ ...locForm, bien_id: e.target.value })}
                className={selectCls}
              >
                <option value="">Sélectionner un bien</option>
                {biens.map((b) => <option key={b.id} value={b.id}>{b.adresse}</option>)}
              </select>
            </Field>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Field label="Nom de l'unité">
              <input
                required value={locForm.nom}
                onChange={(e) => setLocForm({ ...locForm, nom: e.target.value })}
                placeholder="Appartement A"
                className={inputCls}
              />
            </Field>
            <Field label="Type">
              <select
                value={locForm.type_location}
                onChange={(e) => setLocForm({ ...locForm, type_location: e.target.value as TypeLocation })}
                className={selectCls}
              >
                {TYPES_LOC.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Surface (m²) — optionnel">
              <input
                type="number" min="1" value={locForm.surface_m2}
                onChange={(e) => setLocForm({ ...locForm, surface_m2: e.target.value })}
                placeholder="65"
                className={inputCls}
              />
            </Field>
            <Field label="Loyer mensuel (FCFA)">
              <input
                required type="number" min="1" value={locForm.loyer_mensuel}
                onChange={(e) => setLocForm({ ...locForm, loyer_mensuel: e.target.value })}
                placeholder="120 000"
                className={inputCls}
              />
            </Field>
          </div>

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={() => setLocModal(false)}
              className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={mutLoc.isPending}
              className="flex-1 py-2.5 text-sm font-bold text-white bg-[#2ea043] rounded-lg hover:bg-[#268a38] transition-colors disabled:opacity-60">
              {mutLoc.isPending ? "Création…" : "Créer la location"}
            </button>
          </div>
        </form>
      </Modal>

      {/* ── Modal : Demander paiement ── */}
      <Modal open={paiementModal} onClose={() => { setPaiementModal(false); setPaymentUrl(null); }} title="Demander un paiement">
        {paymentUrl ? (
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-3 py-4">
              <div className="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-green-500" />
              </div>
              <p className="text-sm font-semibold text-gray-800">Lien de paiement généré</p>
              <p className="text-xs text-gray-500 text-center">Partagez ce lien avec le locataire ou ouvrez-le directement.</p>
              <a
                href={paymentUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full text-center py-2.5 px-4 rounded-lg bg-[#2ea043] text-white text-sm font-bold hover:bg-[#268a38] transition-colors"
              >
                Ouvrir le lien FedaPay
              </a>
              <button
                onClick={() => { navigator.clipboard.writeText(paymentUrl); toast.success("Lien copié"); }}
                className="w-full py-2 px-4 rounded-lg border border-gray-200 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
              >
                Copier le lien
              </button>
            </div>
            <button
              onClick={() => { setPaiementModal(false); setPaymentUrl(null); }}
              className="w-full py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Fermer
            </button>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!paiementForm.telephone) return toast.error("Entrez le numéro de téléphone du locataire");
              mutPaiement.mutate({
                contrat_id: paiementForm.contrat_id,
                montant: parseFloat(paiementForm.montant),
                telephone: paiementForm.telephone,
              });
            }}
            className="space-y-4"
          >
            <Field label="Montant (FCFA)">
              <input
                required type="number" min="1"
                value={paiementForm.montant}
                onChange={(e) => setPaiementForm({ ...paiementForm, montant: e.target.value })}
                className={inputCls}
              />
            </Field>
            <Field label="Téléphone Mobile Money du locataire">
              <input
                required type="tel"
                value={paiementForm.telephone}
                onChange={(e) => setPaiementForm({ ...paiementForm, telephone: e.target.value })}
                placeholder="96XXXXXX (MTN) ou 67XXXXXX (MOOV)"
                className={inputCls}
              />
            </Field>
            <p className="text-[11px] text-gray-400">
              MTN : 96/97 · MOOV : 61–67. Le locataire recevra une demande de paiement FedaPay.
            </p>
            <div className="flex gap-3 pt-1">
              <button type="button" onClick={() => setPaiementModal(false)}
                className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                Annuler
              </button>
              <button type="submit" disabled={mutPaiement.isPending}
                className="flex-1 py-2.5 text-sm font-bold text-white bg-[#1a3c6e] rounded-lg hover:bg-[#132d54] transition-colors disabled:opacity-60">
                {mutPaiement.isPending ? "Génération…" : "Générer le lien"}
              </button>
            </div>
          </form>
        )}
      </Modal>

      {/* ── Modal : Nouveau contrat ── */}
      <Modal open={contratModal} onClose={() => setContratModal(false)} title="Nouveau contrat" size="md">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (contratForm.duree_type === "bail" && !contratForm.date_fin)
              return toast.error("La date de fin est requise pour un bail");
            mutContrat.mutate({
              location_id: contratForm.location_id,
              locataire_id: contratForm.locataire_id,
              loyer_montant: parseFloat(contratForm.loyer_montant),
              date_debut: contratForm.date_debut,
              jour_echeance: parseInt(contratForm.jour_echeance),
              duree_type: contratForm.duree_type,
              ...(contratForm.duree_type === "bail" ? { date_fin: contratForm.date_fin } : {}),
            });
          }}
          className="space-y-4"
        >
          {/* Location display */}
          {(() => {
            const loc = allLocations.find((l) => l.id === contratForm.location_id);
            const bien = loc ? biens.find((b) => b.id === loc.bien_id) : null;
            return loc ? (
              <div className="px-3 py-2.5 bg-green-50 rounded-lg border border-green-100">
                <p className="text-xs font-bold text-green-800">{loc.nom}</p>
                <p className="text-[11px] text-green-600">{bien?.adresse}</p>
                <p className="text-[11px] text-green-600 mt-0.5">Loyer suggéré : {fmt(loc.loyer_mensuel)}</p>
              </div>
            ) : null;
          })()}

          {/* Locataire */}
          <Field label="Locataire">
            <select
              required value={contratForm.locataire_id}
              onChange={(e) => setContratForm({ ...contratForm, locataire_id: e.target.value })}
              className={selectCls}
            >
              <option value="">Sélectionner un locataire</option>
              {locataires.map((l) => (
                <option key={l.id} value={l.id}>{l.prenom} {l.nom} — {l.telephone}</option>
              ))}
            </select>
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Loyer mensuel (FCFA)">
              <input
                required type="number" min="1" value={contratForm.loyer_montant}
                onChange={(e) => setContratForm({ ...contratForm, loyer_montant: e.target.value })}
                className={inputCls}
              />
            </Field>
            <Field label="Jour d'échéance (1-28)">
              <input
                required type="number" min="1" max="28" value={contratForm.jour_echeance}
                onChange={(e) => setContratForm({ ...contratForm, jour_echeance: e.target.value })}
                className={inputCls}
              />
            </Field>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Date de début">
              <input
                required type="date" value={contratForm.date_debut}
                onChange={(e) => setContratForm({ ...contratForm, date_debut: e.target.value })}
                className={inputCls}
              />
            </Field>
            <Field label="Type de durée">
              <select
                value={contratForm.duree_type}
                onChange={(e) => setContratForm({ ...contratForm, duree_type: e.target.value as DureeType, date_fin: "" })}
                className={selectCls}
              >
                {DUREES.map((d) => <option key={d.value} value={d.value}>{d.label}</option>)}
              </select>
            </Field>
          </div>

          {contratForm.duree_type === "bail" && (
            <Field label="Date de fin (obligatoire)">
              <input
                required type="date" value={contratForm.date_fin}
                onChange={(e) => setContratForm({ ...contratForm, date_fin: e.target.value })}
                className={inputCls}
              />
            </Field>
          )}

          <div className="flex gap-3 pt-1">
            <button type="button" onClick={() => setContratModal(false)}
              className="flex-1 py-2.5 text-sm font-medium text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              Annuler
            </button>
            <button type="submit" disabled={mutContrat.isPending}
              className="flex-1 py-2.5 text-sm font-bold text-white bg-[#2ea043] rounded-lg hover:bg-[#268a38] transition-colors disabled:opacity-60">
              {mutContrat.isPending ? "Création…" : "Créer le contrat"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
