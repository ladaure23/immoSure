import axios from "axios";

const http = axios.create({ baseURL: "/api" });

http.interceptors.request.use((config) => {
  try {
    const stored = localStorage.getItem("immosure-auth");
    if (stored) {
      const { state } = JSON.parse(stored);
      if (state?.token) config.headers.Authorization = `Bearer ${state.token}`;
    }
  } catch {}
  return config;
});

// ── Types ──────────────────────────────────────────────────────────────────
export type TypeBien = "appartement" | "villa" | "studio" | "magasin";
export type StatutBien = "disponible" | "loue";
export type StatutContrat = "actif" | "resilie" | "expire";
export type TypeTicket = "maintenance" | "conflit" | "difficulte_paiement";
export type StatutTicket = "ouvert" | "en_cours" | "ferme";
export type OperateurMobile = "MTN" | "MOOV" | "WAVE";

export interface Agence {
  id: string;
  raison_sociale: string;
  commission_taux: number;
  contact_responsable: string | null;
  telephone: string | null;
  email: string | null;
  statut_partenariat: string;
}

export interface Bien {
  id: string;
  adresse: string;
  type_bien: TypeBien;
  proprietaire_id: string;
  agence_id: string | null;
  loyer_mensuel: number;
  statut: StatutBien;
  created_at: string;
}

export interface Proprietaire {
  id: string;
  nom: string;
  prenom: string;
  telephone: string;
  compte_mobile_money: string | null;
  operateur_mobile: OperateurMobile | null;
  localisation: string | null;
  agence_id: string | null;
  created_at: string;
}

export interface Contrat {
  id: string;
  bien_id: string;
  locataire_id: string;
  date_debut: string;
  date_fin: string | null;
  loyer_montant: number;
  jour_echeance: number;
  statut: StatutContrat;
  created_at: string;
}

export interface Locataire {
  id: string;
  nom: string;
  prenom: string;
  telephone: string;
  wallet_solde: number;
  score_fiabilite: number;
  created_at: string;
}

export interface ContratRisque {
  contrat_id: string;
  locataire_nom: string;
  locataire_prenom: string;
  locataire_telephone: string;
  bien_adresse: string;
  loyer_montant: number;
  wallet_solde: number;
  taux_provisionnement: number;
  jours_avant_echeance: number;
}

export interface DepotWallet {
  id: string;
  locataire_id: string;
  montant: number;
  reference_mtn: string | null;
  created_at: string;
}

export interface WalletInfo {
  locataire_id: string;
  solde: number;
  loyer_mensuel: number | null;
  taux_provisionnement: number;
  historique: DepotWallet[];
}

export interface Ticket {
  id: string;
  contrat_id: string;
  type_ticket: TypeTicket;
  description: string;
  statut: StatutTicket;
  created_at: string;
}

// ── Agences ────────────────────────────────────────────────────────────────
export const getAgence = (id: string) =>
  http.get<Agence>(`/agences/${id}`).then((r) => r.data);

// ── Biens ──────────────────────────────────────────────────────────────────
export const getBiens = () => http.get<Bien[]>("/biens").then((r) => r.data);
export const getBien = (id: string) =>
  http.get<Bien>(`/biens/${id}`).then((r) => r.data);
export const createBien = (data: {
  adresse: string;
  type_bien: TypeBien;
  proprietaire_id: string;
  loyer_mensuel: number;
}) => http.post<Bien>("/biens", data).then((r) => r.data);
export const updateBien = (id: string, data: Partial<Bien>) =>
  http.put<Bien>(`/biens/${id}`, data).then((r) => r.data);

// ── Propriétaires ──────────────────────────────────────────────────────────
export const getProprietaires = () =>
  http.get<Proprietaire[]>("/proprietaires").then((r) => r.data);
export const createProprietaire = (data: {
  nom: string;
  prenom: string;
  telephone: string;
  compte_mobile_money?: string;
  operateur_mobile?: OperateurMobile;
  localisation?: string;
}) => http.post<Proprietaire>("/proprietaires", data).then((r) => r.data);

// ── Contrats ───────────────────────────────────────────────────────────────
export const getContrats = () =>
  http.get<Contrat[]>("/contrats").then((r) => r.data);
export const createContrat = (data: {
  bien_id: string;
  locataire_id: string;
  loyer_montant: number;
  date_debut: string;
  jour_echeance: number;
}) => http.post<Contrat>("/contrats", data).then((r) => r.data);
export const updateContrat = (id: string, data: { statut: StatutContrat }) =>
  http.put<Contrat>(`/contrats/${id}`, data).then((r) => r.data);
export const getContratsRisques = () =>
  http.get<ContratRisque[]>("/contrats/risques").then((r) => r.data);

// ── Locataires ─────────────────────────────────────────────────────────────
export const getLocataires = () =>
  http.get<Locataire[]>("/locataires").then((r) => r.data);
export const createLocataire = (data: {
  nom: string;
  prenom: string;
  telephone: string;
}) => http.post<Locataire>("/locataires", data).then((r) => r.data);
export const getWallet = (id: string) =>
  http.get<WalletInfo>(`/locataires/${id}/wallet`).then((r) => r.data);

// ── Tickets ────────────────────────────────────────────────────────────────
export const getTickets = () =>
  http.get<Ticket[]>("/tickets").then((r) => r.data);
export const createTicket = (data: {
  contrat_id: string;
  type_ticket: TypeTicket;
  description: string;
}) => http.post<Ticket>("/tickets", data).then((r) => r.data);
export const updateTicket = (id: string, statut: StatutTicket) =>
  http.put<Ticket>(`/tickets/${id}`, { statut }).then((r) => r.data);
