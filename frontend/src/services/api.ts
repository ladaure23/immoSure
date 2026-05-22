import axios from "axios";
import { useAuthStore } from "../store/authStore";

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

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = "/";
    }
    return Promise.reject(err);
  }
);

// ── Types ──────────────────────────────────────────────────────────────────
export type TypeBien = "immeuble" | "villa" | "maison" | "appartement" | "studio" | "magasin" | "autre";
export type TypeLocation = "appartement" | "studio" | "chambre" | "villa" | "magasin" | "bureau" | "autre";
export type StatutLocation = "disponible" | "loue";
export type DureeType = "mensuel" | "bimestriel" | "trimestriel" | "semestriel" | "annuel" | "bail" | "indefini";
export type StatutContrat = "actif" | "resilie" | "expire";
export type StatutPaiementLoyer = "en_attente" | "partiel" | "complet";
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
  fedapay_sub_account_ref: string | null;
  statut_partenariat: string;
}

export interface Bien {
  id: string;
  nom: string | null;
  adresse: string;
  type_bien: TypeBien;
  proprietaire_id: string;
  agence_id: string | null;
  created_at: string;
}

export interface Location {
  id: string;
  bien_id: string;
  nom: string;
  type_location: TypeLocation;
  surface_m2: number | null;
  loyer_mensuel: number;
  statut: StatutLocation;
  created_at: string;
}

export interface Proprietaire {
  id: string;
  nom: string;
  prenom: string;
  telephone: string;
  email: string | null;
  fedapay_sub_account_ref: string | null;
  compte_mobile_money: string | null;
  operateur_mobile: OperateurMobile | null;
  localisation: string | null;
  agence_id: string | null;
  created_at: string;
}

export interface Contrat {
  id: string;
  location_id: string;
  locataire_id: string;
  date_debut: string;
  date_fin: string | null;
  loyer_montant: number;
  jour_echeance: number;
  duree_type: DureeType;
  statut: StatutContrat;
  created_at: string;
}

export interface Locataire {
  id: string;
  nom: string;
  prenom: string;
  telephone: string;
  score_fiabilite: number;
  created_at: string;
}

export interface PaiementLoyer {
  id: string;
  contrat_id: string;
  periode_debut: string;
  periode_fin: string;
  loyer_du: number;
  total_paye: number;
  statut: StatutPaiementLoyer;
  created_at: string;
  updated_at: string;
}

export interface InitierPaiementResponse {
  paiement_loyer_id: string;
  fedapay_transaction_id: string;
  payment_url: string;
  montant: number;
  periode_debut: string;
  periode_fin: string;
}

export interface ContratRisque {
  contrat_id: string;
  locataire_nom: string;
  locataire_prenom: string;
  locataire_telephone: string;
  bien_adresse: string;
  location_nom: string;
  loyer_montant: number;
  total_paye: number;
  taux_paiement: number;
  jours_avant_echeance: number;
}

export interface InvitationFedapayResult {
  success: boolean;
  message: string;
  fedapay_ref: string | null;
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
  nom?: string;
  adresse: string;
  type_bien: TypeBien;
  proprietaire_id: string;
}) => http.post<Bien>("/biens", data).then((r) => r.data);
export const updateBien = (id: string, data: Partial<Pick<Bien, "nom" | "adresse" | "type_bien">>) =>
  http.put<Bien>(`/biens/${id}`, data).then((r) => r.data);

// ── Locations ──────────────────────────────────────────────────────────────
export const getLocations = (bien_id: string) =>
  http.get<Location[]>(`/locations?bien_id=${bien_id}`).then((r) => r.data);
export const createLocation = (data: {
  bien_id: string;
  nom: string;
  type_location: TypeLocation;
  surface_m2?: number;
  loyer_mensuel: number;
  statut?: StatutLocation;
}) => http.post<Location>("/locations", data).then((r) => r.data);
export const updateLocation = (id: string, data: Partial<Omit<Location, "id" | "bien_id" | "created_at">>) =>
  http.put<Location>(`/locations/${id}`, data).then((r) => r.data);

// ── Propriétaires ──────────────────────────────────────────────────────────
export const getProprietaires = () =>
  http.get<Proprietaire[]>("/proprietaires").then((r) => r.data);
export const createProprietaire = (data: {
  nom: string;
  prenom: string;
  telephone: string;
  email?: string;
  compte_mobile_money?: string;
  operateur_mobile?: OperateurMobile;
  localisation?: string;
}) => http.post<Proprietaire>("/proprietaires", data).then((r) => r.data);
export const inviterProprietaireFedapay = (id: string) =>
  http.post<InvitationFedapayResult>(`/proprietaires/${id}/inviter-fedapay`).then((r) => r.data);

// ── Contrats ───────────────────────────────────────────────────────────────
export const getContrats = () =>
  http.get<Contrat[]>("/contrats").then((r) => r.data);
export const createContrat = (data: {
  location_id: string;
  locataire_id: string;
  loyer_montant: number;
  date_debut: string;
  jour_echeance: number;
  duree_type?: DureeType;
  date_fin?: string;
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

// ── Paiements loyer ────────────────────────────────────────────────────────
export const getPaiementsLoyer = (contrat_id: string) =>
  http.get<PaiementLoyer[]>(`/paiements/loyer/${contrat_id}`).then((r) => r.data);
export const initierPaiement = (data: {
  contrat_id: string;
  montant: number;
  telephone: string;
}) => http.post<InitierPaiementResponse>("/paiements/initier", data).then((r) => r.data);

// ── Agences FedaPay ────────────────────────────────────────────────────────
export const inviterAgenceFedapay = (id: string) =>
  http.post<InvitationFedapayResult>(`/agences/${id}/inviter-fedapay`).then((r) => r.data);

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
