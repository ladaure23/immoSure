--
-- PostgreSQL database dump
--

\restrict zqVU0f9efDDjE9KQXmpBOR8L4ObrPSrzPYrt2j2nw7Bb90Nn01ozQTMtuQjF0KL

-- Dumped from database version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agences (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    raison_sociale character varying(200) NOT NULL,
    registre_commerce character varying(100),
    commission_taux numeric(5,2) DEFAULT 8.00 NOT NULL,
    contact_responsable character varying(200),
    telephone character varying(20),
    email character varying(200),
    statut_partenariat character varying(50) DEFAULT 'actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    fedapay_sub_account_ref character varying(100)
);


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: biens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.biens (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    adresse character varying(500) NOT NULL,
    type_bien character varying(50) NOT NULL,
    proprietaire_id uuid NOT NULL,
    agence_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    nom character varying(200)
);


--
-- Name: contrats; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contrats (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    locataire_id uuid NOT NULL,
    date_debut date NOT NULL,
    date_fin date,
    loyer_montant numeric(12,2) NOT NULL,
    jour_echeance integer DEFAULT 1 NOT NULL,
    statut character varying(20) DEFAULT 'actif'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    location_id uuid NOT NULL,
    duree_type character varying(20) DEFAULT 'indefini'::character varying NOT NULL
);


--
-- Name: depots_wallet; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.depots_wallet (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    locataire_id uuid NOT NULL,
    montant numeric(12,2) NOT NULL,
    reference_provider character varying(200),
    provider character varying(50) NOT NULL,
    statut character varying(20) DEFAULT 'en_attente'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: locataires; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locataires (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    telephone character varying(20) NOT NULL,
    telegram_chat_id character varying(100),
    whatsapp_id character varying(100),
    score_fiabilite integer DEFAULT 100 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: locations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.locations (
    id uuid NOT NULL,
    bien_id uuid NOT NULL,
    nom character varying(200) NOT NULL,
    type_location character varying(50) NOT NULL,
    surface_m2 numeric(8,2),
    loyer_mensuel numeric(12,2) NOT NULL,
    statut character varying(20) DEFAULT 'disponible'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.notifications (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    destinataire_id uuid NOT NULL,
    type_destinataire character varying(20) NOT NULL,
    canal character varying(20) NOT NULL,
    type_notif character varying(20) NOT NULL,
    message text NOT NULL,
    statut_envoi character varying(20) DEFAULT 'en_attente'::character varying NOT NULL,
    contrat_id uuid,
    tentatives integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: paiement_loyer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.paiement_loyer (
    id uuid NOT NULL,
    contrat_id uuid NOT NULL,
    periode_debut date NOT NULL,
    periode_fin date NOT NULL,
    loyer_du numeric(12,2) NOT NULL,
    total_paye numeric(12,2) DEFAULT '0'::numeric NOT NULL,
    statut character varying(20) DEFAULT 'en_attente'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: proprietaires; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.proprietaires (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    nom character varying(100) NOT NULL,
    prenom character varying(100) NOT NULL,
    telephone character varying(20) NOT NULL,
    compte_mobile_money character varying(20),
    operateur_mobile character varying(20),
    whatsapp_id character varying(100),
    telegram_chat_id character varying(100),
    localisation character varying(300),
    agence_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    email character varying(200),
    fedapay_sub_account_ref character varying(100)
);


--
-- Name: tickets; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tickets (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    contrat_id uuid NOT NULL,
    type_ticket character varying(50) NOT NULL,
    description text NOT NULL,
    statut character varying(20) DEFAULT 'ouvert'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    contrat_id uuid NOT NULL,
    montant_total numeric(12,2) NOT NULL,
    part_proprietaire numeric(12,2) NOT NULL,
    part_agence numeric(12,2) NOT NULL,
    part_plateforme numeric(12,2) NOT NULL,
    statut character varying(20) DEFAULT 'en_attente'::character varying NOT NULL,
    reference_paiement character varying(200),
    provider character varying(50),
    mois_concerne date NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    fedapay_transaction_id character varying(100),
    montant_net numeric(12,2),
    frais_fedapay numeric(12,2)
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    email character varying(200) NOT NULL,
    password_hash character varying(200) NOT NULL,
    role character varying(20) DEFAULT 'agence'::character varying NOT NULL,
    agence_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Data for Name: agences; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agences (id, raison_sociale, registre_commerce, commission_taux, contact_responsable, telephone, email, statut_partenariat, created_at, fedapay_sub_account_ref) FROM stdin;
7c52e1f3-0c44-4928-a2a5-89a3f1a46105	ImmoSure Cotonou	RC-BEN-2024-001	8.00	Adjonou Kévin	+229 97 11 22 33	contact@immosure.bj	actif	2026-04-25 14:51:32.667731+00	acc_0292158558
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
004
\.


--
-- Data for Name: biens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.biens (id, adresse, type_bien, proprietaire_id, agence_id, created_at, nom) FROM stdin;
f6a5b71b-ed08-4300-bed3-712263c37748	Lot 45 Rue des Cocotiers, Cadjehoun, Cotonou	appartement	e999f4ac-eb12-477c-8f07-abc4dc0f5009	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	\N
7139eeb9-9a59-444d-ac6a-7168973b85ac	Villa 12 Résidence Bel Air, Fidjrossè, Cotonou	villa	e999f4ac-eb12-477c-8f07-abc4dc0f5009	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	\N
eb4eb980-5f2d-44d4-b0e5-d49b85ad9fcf	Studio B4 Immeuble Soleil, Haie Vive, Cotonou	studio	0878e17d-30ae-4b09-a186-affac86dfa4b	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	\N
74361bda-2c24-4383-88c8-23a089d6142d	Magasin 3 Marché Dantokpa, Zone Commerciale	magasin	0878e17d-30ae-4b09-a186-affac86dfa4b	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	\N
355bde82-99b5-4f30-858a-c46c58cd4279	Appartement 2A Résidence du Lac, Porto-Novo	appartement	f1888fc2-37db-447a-875f-714585aa88b3	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	\N
b21fc83c-b32b-4b60-9e2f-4553e03db558	juiueizbfibi	villa	e999f4ac-eb12-477c-8f07-abc4dc0f5009	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-26 13:23:09.2093+00	\N
\.


--
-- Data for Name: contrats; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contrats (id, locataire_id, date_debut, date_fin, loyer_montant, jour_echeance, statut, created_at, location_id, duree_type) FROM stdin;
e02f2631-cd7b-4f23-a8e1-4f40fa1c847e	42a57843-5b97-41d8-b5f4-8a5f22ec2088	2025-01-01	\N	120000.00	5	actif	2026-04-25 14:51:32.667731+00	254aebfd-eb98-4d0a-94a4-cdbe934d8e32	indefini
ff1168b1-44b3-4d93-9568-679e195672b3	0260bc00-654e-4bd6-9846-b0e98b68a697	2025-03-01	\N	250000.00	1	actif	2026-04-25 14:51:32.667731+00	1378d893-65be-4b7d-823f-3e56c40526b4	indefini
5f120d58-e5f9-49ce-b20f-e51b645582c8	35d06ff0-e9cc-45ae-8a74-75b99989c0d0	2025-06-01	\N	75000.00	10	actif	2026-04-25 14:51:32.667731+00	34cda33c-fe9d-4ac3-8595-0aee30fe6b05	indefini
5e64c867-6da5-4c84-8213-4dcea7cd89b4	d58452ce-705a-4fc0-b77c-1b36ca7e8c37	2025-09-01	\N	180000.00	3	actif	2026-04-25 14:51:32.667731+00	06359cca-66f5-4c50-8c8d-1f3418f339a4	indefini
6181e8d8-f7bd-4238-9c72-0d96d1b04e6e	42a57843-5b97-41d8-b5f4-8a5f22ec2088	2026-04-26	2026-07-26	25000.00	1	actif	2026-04-26 12:48:26.149544+00	f99ea1ae-350c-493d-bb59-331a3ffd5057	trimestriel
fa4c778a-937b-4269-a9d3-eb490cd37e30	2baa98e1-4d67-4ac9-9c5c-fbdbac826741	2026-01-01	\N	95000.00	5	actif	2026-04-27 13:15:40.877937+00	fee1a655-1eb4-410f-8aca-15bc1004ca8a	mensuel
\.


--
-- Data for Name: depots_wallet; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.depots_wallet (id, locataire_id, montant, reference_provider, provider, statut, created_at) FROM stdin;
\.


--
-- Data for Name: locataires; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.locataires (id, nom, prenom, telephone, telegram_chat_id, whatsapp_id, score_fiabilite, created_at) FROM stdin;
42a57843-5b97-41d8-b5f4-8a5f22ec2088	Mensah	Kofi	+229 97 10 20 30	\N	\N	92	2026-04-25 14:51:32.667731+00
0260bc00-654e-4bd6-9846-b0e98b68a697	Amoussou	Félicité	+229 96 40 50 60	\N	\N	85	2026-04-25 14:51:32.667731+00
35d06ff0-e9cc-45ae-8a74-75b99989c0d0	Gbaguidi	Romuald	+229 95 70 80 90	\N	\N	61	2026-04-25 14:51:32.667731+00
d58452ce-705a-4fc0-b77c-1b36ca7e8c37	Ahlonsou	Diane	+229 97 01 23 45	\N	\N	38	2026-04-25 14:51:32.667731+00
2baa98e1-4d67-4ac9-9c5c-fbdbac826741	BOSSOU	JEAN	0167130339	878644775	\N	75	2026-04-27 13:15:40.877937+00
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.locations (id, bien_id, nom, type_location, surface_m2, loyer_mensuel, statut, created_at) FROM stdin;
254aebfd-eb98-4d0a-94a4-cdbe934d8e32	f6a5b71b-ed08-4300-bed3-712263c37748	Principal	appartement	\N	120000.00	loue	2026-04-25 23:41:25.061337+00
1378d893-65be-4b7d-823f-3e56c40526b4	7139eeb9-9a59-444d-ac6a-7168973b85ac	Principal	villa	\N	250000.00	loue	2026-04-25 23:41:25.061337+00
34cda33c-fe9d-4ac3-8595-0aee30fe6b05	eb4eb980-5f2d-44d4-b0e5-d49b85ad9fcf	Principal	studio	\N	75000.00	loue	2026-04-25 23:41:25.061337+00
06359cca-66f5-4c50-8c8d-1f3418f339a4	74361bda-2c24-4383-88c8-23a089d6142d	Principal	magasin	\N	180000.00	loue	2026-04-25 23:41:25.061337+00
f99ea1ae-350c-493d-bb59-331a3ffd5057	7139eeb9-9a59-444d-ac6a-7168973b85ac	AS	appartement	25.00	25000.00	loue	2026-04-26 12:47:47.78228+00
7a060b6e-7d88-4a70-aef9-405ad57d33a9	b21fc83c-b32b-4b60-9e2f-4553e03db558	Appart A	chambre	25.00	12000.00	disponible	2026-04-26 13:23:42.815258+00
fee1a655-1eb4-410f-8aca-15bc1004ca8a	355bde82-99b5-4f30-858a-c46c58cd4279	Principal	appartement	\N	95000.00	loue	2026-04-25 23:41:25.061337+00
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.notifications (id, destinataire_id, type_destinataire, canal, type_notif, message, statut_envoi, contrat_id, tentatives, created_at) FROM stdin;
\.


--
-- Data for Name: paiement_loyer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.paiement_loyer (id, contrat_id, periode_debut, periode_fin, loyer_du, total_paye, statut, created_at, updated_at) FROM stdin;
f4807d14-5e42-4de6-8097-dcf92fb79e3c	e02f2631-cd7b-4f23-a8e1-4f40fa1c847e	2026-04-01	2026-05-01	120000.00	50000.00	partiel	2026-04-26 18:35:56.776387+00	2026-04-26 18:44:18.729074+00
65c69dfb-00d0-4995-8489-a199e5003686	fa4c778a-937b-4269-a9d3-eb490cd37e30	2026-04-01	2026-05-01	95000.00	0.00	en_attente	2026-04-27 13:33:16.844408+00	2026-04-27 13:33:16.844408+00
44433a3f-6ef3-4a72-adc0-59bf7c0003f1	fa4c778a-937b-4269-a9d3-eb490cd37e30	2026-05-01	2026-06-01	95000.00	0.00	en_attente	2026-05-05 17:51:41.482912+00	2026-05-05 17:51:41.482912+00
\.


--
-- Data for Name: proprietaires; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.proprietaires (id, nom, prenom, telephone, compte_mobile_money, operateur_mobile, whatsapp_id, telegram_chat_id, localisation, agence_id, created_at, email, fedapay_sub_account_ref) FROM stdin;
e999f4ac-eb12-477c-8f07-abc4dc0f5009	Adjovi	Barnabé	+229 96 00 11 22	22996001122	MTN	\N	\N	Cotonou, Cadjehoun	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	barnabe.adjovi@test.bj	\N
0878e17d-30ae-4b09-a186-affac86dfa4b	Dossou	Euphrasie	+229 97 33 44 55	22997334455	MOOV	\N	\N	Cotonou, Fidjrossè	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	euphrasie.dossou@test.bj	\N
f1888fc2-37db-447a-875f-714585aa88b3	Hounsa	Gildas	+229 95 66 77 88	22995667788	WAVE	\N	\N	Porto-Novo, Stade	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00	gildas.hounsa@test.bj	acc_3947386110
\.


--
-- Data for Name: tickets; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tickets (id, contrat_id, type_ticket, description, statut, created_at) FROM stdin;
900e1731-1021-4b54-8474-6a29492978c3	5f120d58-e5f9-49ce-b20f-e51b645582c8	maintenance	Fuite d'eau au plafond de la salle de bain depuis 3 jours.	ouvert	2026-04-25 14:51:32.667731+00
d04e52e4-c422-4ab9-a632-9039ec212a9b	5e64c867-6da5-4c84-8213-4dcea7cd89b4	difficulte_paiement	Locataire signale une difficulté de paiement ce mois — en attente de virement Mobile Money.	en_cours	2026-04-25 14:51:32.667731+00
d087f4fa-64a0-442e-96da-3e19ffc8d968	e02f2631-cd7b-4f23-a8e1-4f40fa1c847e	conflit	czdcdzc	en_cours	2026-04-26 12:37:35.559198+00
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.transactions (id, contrat_id, montant_total, part_proprietaire, part_agence, part_plateforme, statut, reference_paiement, provider, mois_concerne, created_at, fedapay_transaction_id, montant_net, frais_fedapay) FROM stdin;
87102738-054b-4db0-a58f-0e2aeace293a	e02f2631-cd7b-4f23-a8e1-4f40fa1c847e	50000.00	0.00	0.00	49100.00	complete	\N	fedapay	2026-04-01	2026-04-26 18:44:18.729074+00	434628	49100.00	900.00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, email, password_hash, role, agence_id, created_at) FROM stdin;
b9c3179e-d8d4-4a73-8807-0a78a4333342	admin@immosure.bj	$2b$12$tHorO8cJTQcH7.BoCl4xAuA6Au4wSRERqrXQspubhLlG/HvlQQHDi	agence	7c52e1f3-0c44-4928-a2a5-89a3f1a46105	2026-04-25 14:51:32.667731+00
\.


--
-- Name: agences agences_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agences
    ADD CONSTRAINT agences_pkey PRIMARY KEY (id);


--
-- Name: agences agences_registre_commerce_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agences
    ADD CONSTRAINT agences_registre_commerce_key UNIQUE (registre_commerce);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: biens biens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.biens
    ADD CONSTRAINT biens_pkey PRIMARY KEY (id);


--
-- Name: contrats contrats_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contrats
    ADD CONSTRAINT contrats_pkey PRIMARY KEY (id);


--
-- Name: depots_wallet depots_wallet_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.depots_wallet
    ADD CONSTRAINT depots_wallet_pkey PRIMARY KEY (id);


--
-- Name: locataires locataires_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locataires
    ADD CONSTRAINT locataires_pkey PRIMARY KEY (id);


--
-- Name: locataires locataires_telephone_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locataires
    ADD CONSTRAINT locataires_telephone_key UNIQUE (telephone);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: paiement_loyer paiement_loyer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.paiement_loyer
    ADD CONSTRAINT paiement_loyer_pkey PRIMARY KEY (id);


--
-- Name: proprietaires proprietaires_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proprietaires
    ADD CONSTRAINT proprietaires_pkey PRIMARY KEY (id);


--
-- Name: proprietaires proprietaires_telephone_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proprietaires
    ADD CONSTRAINT proprietaires_telephone_key UNIQUE (telephone);


--
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_contrats_locataire_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contrats_locataire_id ON public.contrats USING btree (locataire_id);


--
-- Name: ix_contrats_statut; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contrats_statut ON public.contrats USING btree (statut);


--
-- Name: ix_depots_wallet_locataire_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_depots_wallet_locataire_id ON public.depots_wallet USING btree (locataire_id);


--
-- Name: ix_locations_bien_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_locations_bien_id ON public.locations USING btree (bien_id);


--
-- Name: ix_notifications_destinataire; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_destinataire ON public.notifications USING btree (destinataire_id, type_destinataire);


--
-- Name: ix_notifications_statut_envoi; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_notifications_statut_envoi ON public.notifications USING btree (statut_envoi);


--
-- Name: ix_paiement_loyer_contrat_periode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_paiement_loyer_contrat_periode ON public.paiement_loyer USING btree (contrat_id, periode_debut);


--
-- Name: ix_transactions_contrat_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_contrat_id ON public.transactions USING btree (contrat_id);


--
-- Name: ix_transactions_mois_concerne; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_transactions_mois_concerne ON public.transactions USING btree (mois_concerne);


--
-- Name: biens biens_agence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.biens
    ADD CONSTRAINT biens_agence_id_fkey FOREIGN KEY (agence_id) REFERENCES public.agences(id);


--
-- Name: biens biens_proprietaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.biens
    ADD CONSTRAINT biens_proprietaire_id_fkey FOREIGN KEY (proprietaire_id) REFERENCES public.proprietaires(id);


--
-- Name: contrats contrats_locataire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contrats
    ADD CONSTRAINT contrats_locataire_id_fkey FOREIGN KEY (locataire_id) REFERENCES public.locataires(id);


--
-- Name: depots_wallet depots_wallet_locataire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.depots_wallet
    ADD CONSTRAINT depots_wallet_locataire_id_fkey FOREIGN KEY (locataire_id) REFERENCES public.locataires(id);


--
-- Name: contrats fk_contrats_location_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contrats
    ADD CONSTRAINT fk_contrats_location_id FOREIGN KEY (location_id) REFERENCES public.locations(id);


--
-- Name: locations locations_bien_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_bien_id_fkey FOREIGN KEY (bien_id) REFERENCES public.biens(id);


--
-- Name: notifications notifications_contrat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_contrat_id_fkey FOREIGN KEY (contrat_id) REFERENCES public.contrats(id);


--
-- Name: paiement_loyer paiement_loyer_contrat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.paiement_loyer
    ADD CONSTRAINT paiement_loyer_contrat_id_fkey FOREIGN KEY (contrat_id) REFERENCES public.contrats(id);


--
-- Name: proprietaires proprietaires_agence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proprietaires
    ADD CONSTRAINT proprietaires_agence_id_fkey FOREIGN KEY (agence_id) REFERENCES public.agences(id);


--
-- Name: tickets tickets_contrat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_contrat_id_fkey FOREIGN KEY (contrat_id) REFERENCES public.contrats(id);


--
-- Name: transactions transactions_contrat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_contrat_id_fkey FOREIGN KEY (contrat_id) REFERENCES public.contrats(id);


--
-- Name: users users_agence_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_agence_id_fkey FOREIGN KEY (agence_id) REFERENCES public.agences(id);


--
-- PostgreSQL database dump complete
--

\unrestrict zqVU0f9efDDjE9KQXmpBOR8L4ObrPSrzPYrt2j2nw7Bb90Nn01ozQTMtuQjF0KL

