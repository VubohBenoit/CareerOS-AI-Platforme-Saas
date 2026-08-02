# CareerOS AI — Specification complète

**Version:** 0.1 | **Date:** 2026-08-02 | **Statut:** En cours de validation

## 1. Vue d'ensemble du produit

### Définition
CareerOS AI est une plateforme SaaS qui automatise et optimise le parcours de recherche d'emploi. Elle aide les candidats à :
- Construire un profil professionnel complet
- Découvrir les offres pertinentes automatiquement
- Adapter leur candidature à chaque position
- Suivre intelligemment chaque application
- Préparer efficacement les entretiens

### Valeur unique
Contrairement aux outils existants :
- **Pas d'invention** : aucune expérience fictive n'est créée
- **Automatisation éthique** : l'humain valide avant chaque envoi
- **Intelligence contextuelle** : analyse profonde des postes + recommandations
- **Suivi complet** : tableau de bord holistique avec prédictions
- **Coaching actif** : préparation d'entretien conversationnelle

---

## 2. Personas et contextes d'utilisation

### Persona 1 : Léa - Développeuse en transition
**Profil** 
- Âge : 28 ans
- Expérience : 4 ans en backend (Python/Django)
- Situation : Changement de secteur (du fintech aux deeptech)
- Défi : Au même niveau technique mais manque de portfolio visibilité

**Besoins**
- Trouver 20-30 postes pertinents par semaine
- Adapter son CV pour mettre en avant les projets OpenSource
- Optimiser pour les mots-clés des annonces
- Relancer intelligemment après 7 jours (pas de spam)
- Préparer entretiens techniques sur des domaines neufs (ML, infra cloud)

**Objectif** : Décrocher 3-5 entretiens/semaine → 1 offre viable en 4-6 semaines

---

### Persona 2 : Marc - Cadre expérimenté
**Profil**
- Âge : 42 ans
- Expérience : 15 ans, plusieurs postes de management
- Situation : Licenciement économique, recherche haut de gamme
- Défi : Repositionnement, secteur trop général

**Besoins**
- Filtrer rigoureusement (seulement postes C-suite/direction)
- Lettres de motivation très personnalisées par entreprise
- Analyse de l'entreprise (culture, financiers, croissance)
- Suivi de 10-15 candidatures max (qualité vs. quantité)
- Préparer questions stratégiques avant entretiens

**Objectif** : 2-3 offres sérieuses en 3-4 mois

---

### Persona 3 : Aminata - Entrante sans expérience
**Profil**
- Âge : 23 ans, fraîchement diplômée (Master Data Science)
- Situation : Première recherche d'emploi, compétitions fiables
- Défi : Pas d'expérience "réelle", manque de confiance

**Besoins**
- Candidatures massives (100+/semaine possible)
- Modèles de lettres génériques + professionnels
- Questions entretien junior + préparation
- Feedback sur forces/faiblesses dans ses réponses
- Suivi de toutes les candidatures pour apprendre

**Objectif** : 1ère offre en 2-3 mois, CDI

---

## 3. Cas d'utilisation critiques

### UC1 : Configuration du profil initial
**Acteur** : Léa (première connexion)

1. Léa se connecte et crée son profil
2. Elle importe un CV PDF (parsed automatiquement)
3. Elle valide/complète les infos extraites :
   - Expériences (dates, descriptions, technologies)
   - Diplômes et certifications
   - Compétences (manuelles + détectées du CV)
   - Langues, liens (GitHub, LinkedIn, portfolio)
4. Elle configure ses préférences :
   - Type de contrat souhaité (CDI, freelance, stage)
   - Localisations (télétravail partiel accepté ?)
   - Salaire minimum acceptable
   - Disponibilité
5. Système vérifie complétude et propose optimisations
6. Profil enregistré et prêt pour recherche

**Résultat** : Profil validé, 0% de données fictives

---

### UC2 : Recherche et découverte d'offres
**Acteur** : Léa (quotidien)

1. Léa accède au dashboard
2. Elle lance une recherche sauvegardée ("Backend Python – Deeptech")
3. CareerOS interroge :
   - LinkedIn API (job search)
   - Indeed (via scraping respectueux)
   - Flux RSS d'entreprises
   - Welcome To The Jungle, FlexJobs, etc.
4. Système filtre et classe :
   - Exclude doublons
   - Score compatibilité vs. profil
   - Alertes nouveautés
5. Léa voit 15 nouvelles offres, trie par score
6. Elle clique sur une offre pour analyse détaillée

**Résultat** : 15-30 offres/jour, pas de spam

---

### UC3 : Analyse intelligente d'une annonce
**Acteur** : Léa (sur 1 offre)

1. Léa ouvre une offre : "Sr. Backend Engineer – Python/FastAPI"
2. CareerOS analyse :
   - Compétences requises (parsing NLP)
   - Technologies (Python, FastAPI, PostgreSQL, Docker, Kubernetes)
   - Niveau demandé (senior = 5+ ans)
   - Salaire (si visible, ou estimation par ML)
   - Mots-clés ATS (keywords importants)
   - Responsabilités principales
3. Système calcule un **score de compatibilité** :
   - Léa : 4 ans expérience → "Niveau Senior attendu"
   - Mots-clés matchés : 8/12 → 67%
   - Localisation : Remote OK, elle est en Paris → Match
   - Score final : 78% (Bon match)
4. Interface affiche :
   - Analyse structurée
   - Points forts / points faibles
   - Recommandations ("Mettre en avant Docker, Kubernetes")
   - Bouton "Préparer candidature"

**Résultat** : Décision éclairée en 30 secondes

---

### UC4 : Préparation et envoi de candidature
**Acteur** : Léa (75 offres/mois)

1. Léa clique "Préparer candidature" sur l'offre
2. CareerOS crée une **candidature brouillon** :
   - CV adapté (réorganisé pour offre spécifique)
   - Lettre de motivation esquisse
   - Email d'envoi template
3. Léa voit le **rapport ATS** :
   - Sections du CV réordonnées (mots-clés en haut)
   - Mots-clés manquants suggérés
   - Avant/après comparaison
4. Elle valide et **peut éditer** :
   - CV : OK tel quel (ou faire des tweaks)
   - Lettre : personnalise les détails (1-2 paragraphes custom)
   - Email : ajoute contexte personnel si souhaité
5. Avant envoi, elle **aperçu complet** :
   - CV en PDF preview
   - Lettre entière
   - Email sujet + corps
6. Elle clique "Envoyer candidature"
7. Système enregistre :
   - Email tracé (ouverte ?)
   - Dates d'envoi
   - Documents versionnés
   - Candidature = "Envoyée"

**Résultat** : 3 candidatures solides/jour max, 0% d'erreurs

---

### UC5 : Relance intelligente
**Acteur** : Système (planification)

1. Candidature envoyée le 2 août, pas de réponse
2. 7 jours après (9 août, jeudi) :
   - Système génère relance personnalisée
   - Email template = "Relance cordiale" (ton pro)
   - Message = "Avez-vous pu examiner ma candidature ?"
   - Contient lien GitHub / portfolio (credibilité)
3. Avant envoi, Léa **doit valider** :
   - Elle voit email proposé
   - Approuve ou modifie
   - Peut reporter la relance
4. Si réponse reçue = relance annulée automatiquement
5. Après 2 relances (2 semaines) = candidature marquée "Dormante"

**Résultat** : Suivi passif, zéro spam, 100% contrôle humain

---

### UC6 : Préparation d'entretien
**Acteur** : Léa (avant entretien RH)

1. Léa a un entretien prévu le 15 août (9h30)
2. Elle clique "Préparer entretien" sur la candidature
3. CareerOS affiche **fiche candidature** :
   - Entreprise : TechCorp
   - Poste : Sr. Backend Engineer
   - Recruteur : Jean Dupont (LinkedIn profile)
   - Offre originale + analyse
4. **Coach IA lance module d'entraînement** :
   - Présentation TechCorp (secteur, CA, équipe)
   - Culture (LinkedIn, Glassdoor parsing)
   - Résumé offre + points clés
5. **Simulation entretien** :
   - Léa : "Présentez-vous en 2 min"
   - Coach : enregistre réponse (text ou audio?)
   - Analyse : clarté, confiance, keywords-match
   - Feedback : "Bien → ajouter impact metrics"
   - 5-7 questions itératives
6. **Questions probables** :
   - "Décrivez un projet Python complexe"
   - "Comment gérez-vous les migrations DB ?"
   - "Questions techniques" (généré depuis skill match)
7. **Résultat** : Rapport notes + conseils

**Résultat** : Préparation 30 min → confiance +40%

---

## 4. Chemins utilisateur détaillés

### Jour 1 : Onboarding
- Sign-up → Email confirm
- Import CV → Parsing
- Complétion profil (15 min)
- Créer 1ère recherche sauvegardée

### Jour 2-7 : Configuration
- Affinage profil
- Import docs (versions CV, lettres)
- Préférences recherche
- 1ère candidature (validation manuelle du flow)

### Semaine 2+ : Routine
- **Lundi** : Lancer recherche, voir 20-30 offres
- **Mardi-Jeudi** : Préparer 3-5 candidatures/jour
- **Vendredi** : Relances + suivi
- **Semaine 2+** : Entretiens → préparation

---

## 5. Fonctionnalités détaillées

### 5.1 Gestion du profil
**Données stockées** :
- Identité (nom, email, téléphone, addresse)
- Expériences (titre, entreprise, dates, description, technologies, impact metrics)
- Diplômes (établissement, diplôme, année, spécialité)
- Certifications (nom, issuer, date, expiration)
- Compétences (technique, niveau, endorsements)
- Langues (langue, niveau parlé/écrit)
- Liens (LinkedIn URL, GitHub, portfolio, site perso)
- Préférences (contrat, localisations, salaire_min, disponibilité, visa_required)
- Documents (versions de CV, lettres type)

**Validations** :
- Aucun champ ne peut être vide sans raison
- Dates cohérentes (date_fin > date_debut)
- Email validé (confirmation)
- Au moins 2 ans d'expérience OU diplôme universitaire
- Au moins 3 compétences relevantes

**Versioning** :
- Chaque modification enregistrée
- Historique accessible
- Restaurer version antérieure possible

---

### 5.2 Recherche d'offres
**Sources** :
- LinkedIn (API officielle si possible, sinon web scraping éthique)
- Indeed (API + scraping)
- Welcome To The Jungle (API)
- Flux RSS custom (user-provided)
- Job boards sectoriels (Angellist, PythoJobs, etc.)

**Filtres** :
- Localisation (multi-select)
- Contrat (CDI, freelance, stage, alternance)
- Secteur (si dans skills)
- Exp. requise (range)
- Salaire (min/max)
- Entreprise (include/exclude list)
- Mots-clés (include/exclude)

**Classement** :
- Score compatibilité (80-100%)
- Date publication (nouvelles en haut)
- Popularité (# applications)

**Alertes** :
- Email 1x/jour avec top offres
- Push notif (app mobile future)
- Webhook possible (Slack intégration)

---

### 5.3 Analyse intelligente des annonces
**Extraction NLP** :
- Compétences techniques (regex + ML)
- Technologies (parsing structured)
- Niveau demandé (seniority classifier)
- Responsabilités (text summarization)
- Mots-clés ATS (frequency analysis)

**Scoring** :
```
score = (
  0.3 * skill_match +
  0.2 * experience_fit +
  0.2 * location_match +
  0.15 * contract_fit +
  0.15 * other_factors
)
```

**Rapport d'analyse** :
- Compétences match (✓ avez-vous, ✗ manquant)
- Niveau (junior/mid/senior/lead + years required)
- Salaire (fourchette si visible)
- Entreprise (description, taille, financials)
- Culture (Glassdoor sentiments)
- Recommandations ATS

---

### 5.4 Optimisation ATS
**Inputs** :
- CV utilisateur (base de référence)
- Annonce cible

**Traitement** :
1. Parsing du CV (sections, contenu)
2. Extraction mots-clés annonce
3. Réordonnancement sections (keywords en haut)
4. Reformulation descriptions (langage + keywords)
5. Comparaison avant/après
6. Génération rapport modifications

**Sorties** :
- CV optimisé (HTML + PDF + DOCX)
- Rapport modifications (delta visible)
- Mots-clés ajoutés/changés (highlight)
- Score "ATS-friendliness" (0-100%)

**Garanties** :
- Aucune information inventée
- Aucune qualification fictive
- Dates/faits intacts
- Structure lisible humain (pas de keyword-stuffing)

---

### 5.5 Génération de lettres et emails
**Inputs** :
- Profil utilisateur
- Offre cible
- Ton souhaité (formel, moderne, technique)

**Génération** :
1. Contextualization (extrait offre + entreprise)
2. Personnalisation (profil + offre)
3. Structure (intro, body, call-to-action)
4. Formatting (Markdown → PDF/DOCX)

**Sorties** :
- Lettre de motivation (1-2 pages)
- Email d'accompagnement (150-200 mots)
- 2-3 variantes de ton (user choisit)
- Suggestions de personnalisations (sections à enrichir)

**Restrictions** :
- Jamais mentir sur expériences
- Références réelles seulement
- Ton respectueux de culture entreprise

---

### 5.6 Gestion des candidatures
**Statut machine** :
```
Workflow:
  DRAFT → READY → SENT → [VIEWED | REJECTED | INTERVIEWED | ACCEPTED]
  
Substatus options:
  - DRAFT: Création en cours
  - READY: Prête à envoyer
  - SENT: Envoyée
  - VIEWED: Email ouvert (tracking)
  - REJECTED: Refus explicite
  - PHONE_INTERVIEW: Entretien RH
  - TECHNICAL_INTERVIEW: Entretien tech
  - TEST: Test technique/case study
  - OFFER: Offre reçue
  - NEGOTIATION: En négociation
  - ACCEPTED: Acceptée
  - ARCHIVED: Archivée (old ou refusée finalement)
```

**Métadonnées** :
- ID unique (uuid)
- Profil (user_id)
- Offre (job_id)
- Source (LinkedIn, Indeed, etc.)
- Dates (created, sent, last_update, deadline)
- Documents (CV_version, letter_version, email_text)
- Contacts (recruiter name, email, phone)
- Notes (free text, tags)
- Résultat (status + reasoning)
- Feedback (entretien: points forts/faibles)

**Historique** :
- Status change timeline
- Document versions
- Interactions enregistrées

---

### 5.7 Relances intelligentes
**Règles** :
- Relance auto 7j après envoi (si 0 réaction)
- Jours ouvrables uniquement (lun-ven)
- Max 2 relances (puis "dormante")
- Annuler si réponse reçue
- Délai modifiable par user

**Personnalisation** :
- Référence offre + entreprise
- Tone: professional, friendly
- Peut inclure links (GitHub, portfolio)
- Peut inclure mutual connection si applicable

**Contrôle utilisateur** :
- Validation requise avant envoi (option : auto-send après validation 1x)
- Modification possible
- Peuvent reprogrammer relance

---

### 5.8 Coaching d'entretien
**Module IA conversationnel** :

1. **Préparation** :
   - Info entreprise (auto-fetch Crunchbase, LinkedIn, Glassdoor)
   - Résumé offre + compétences clés
   - Culture d'entreprise (sentiment analysis)
   - Info recruteur si LinkedIn visible

2. **Questions RH** (générées) :
   - "Parlez-moi de vous"
   - "Pourquoi cette entreprise ?"
   - "Vos forces/faiblesses ?"
   - "Situation challenge, comment avez-vous réagi ?"
   - Questions situationnelles selon offre

3. **Questions techniques** (générées depuis skills match) :
   - Concepts clés de la stack (Python, FastAPI, DB, etc.)
   - Architecture questions
   - Code review scenarios
   - Design problems

4. **Simulation** :
   - Questions posées 1 par 1
   - User répond (text ou future: voice)
   - IA analyse réponse :
     - Pertinence vs. question
     - Clarté expression
     - Keywords utilisés
     - Confiance détectée
   - Feedback immédiat
   - Suggestions d'amélioration

5. **Résumé** :
   - Points forts identifiés
   - Axes d'amélioration
   - Confiance score (0-100%)
   - Recommandations d'entraînement

---

### 5.9 Tableau de bord
**Vue synthétique** :
- Candidatures : Total | Envoyées | Entretiens | Offres
- Taux de réponse (%)
- Taux de conversion (offres / envoyées)
- Graphiques :
  - Timeline candidatures (courbe cumulative)
  - Répartition par status (pie chart)
  - Entretiens par semaine (bar chart)
  - Entreprises réactives (top 5)
- Calendar : entretiens/relances prochains
- Insights : "3 nouvelles offres match 80%+"

**Filtres** :
- Période (derniers 7j, mois, tout)
- Secteur
- Localisation
- Entreprise

**Export** :
- CSV candidatures
- PDF rapport mensuel

---

## 6. Exigences non-fonctionnelles

### Performance
- API response < 200ms (p95)
- Dashboard load < 1s
- Search job listing < 2s
- PDF generation < 5s

### Scalabilité
- 100K+ users
- 10M+ candidatures tracked
- Horizontal scaling (Kubernetes)
- Database sharding si nécessaire

### Disponibilité
- 99.5% uptime (4 heures downtime/mois)
- Multi-region failover
- Database replication
- CDN pour assets

### Sécurité
- Chiffrement données sensibles (AES-256)
- HTTPS partout
- HTTPS SSL/TLS
- JWT tokens (refresh + access)
- Rate limiting
- Input validation/sanitization
- SQL injection prevention (ORM + parameterized queries)
- CSRF protection
- Audit logging (qui a modifié quoi, quand)
- RGPD compliant (droit oubli, export données)
- Pas de données sensibles en logs

### Maintenabilité
- Code testé (unit + integration, 70%+ coverage)
- Documentation developer
- Architecture documentée
- Patterns clairs (MVC-like)
- No hardcoded secrets (env vars)
- Versioning API (v1/, v2/)

---

## 7. MVP vs. Post-MVP

### MVP (Phase 1) - 2 months
- [x] Profil utilisateur (CRUD)
- [x] Import CV + parsing basic
- [x] Search job listings (API LinkedIn via RapidAPI ou similaire)
- [x] Candidature CRUD (create, read, update)
- [x] CV generation + basic ATS optimization
- [x] Letter generation template
- [x] Dashboard basique (stats)
- [x] Email login/auth
- [ ] Interview coaching (phase 2)
- [ ] Advanced analytics (phase 2)
- [ ] Mobile app (phase 3)

### Phase 2 (Months 3-4)
- [ ] Interview coaching (full)
- [ ] Advanced ATS analysis
- [ ] Relances intelligentes (full automation)
- [ ] Integration Indeed API
- [ ] Integration Indeed API
- [ ] Glassdoor scraping
- [ ] Advanced dashboard
- [ ] Mobile iOS/Android

### Phase 3+ (Months 5+)
- [ ] Chrome extension (quick apply)
- [ ] Slack integration
- [ ] Advanced ML (offer fit prediction)
- [ ] Market salary data
- [ ] Team collaboration (share templates)
- [ ] White-label / B2B
- [ ] API public (partners)

---

## 8. Constraints et compromis

### Constraint 1 : Coût LLM
**Problème** : API OpenAI/Claude coûtent $$$ à scale
**Solution** :
- Caching aggressif (Redis)
- Ollama local pour certaines tâches (résumés)
- Batch processing (relances = 1x/jour, pas real-time)
- User tier (starter gratuit = features limitées)
- Rate limits stricts

### Constraint 2 : Scraping job boards
**Problème** : Légal + technique complexe (bot detection)
**Solution** :
- APIs officielles d'abord (LinkedIn, Indeed)
- RSS feeds quand possible
- Respecter robots.txt
- User-agent réaliste
- Throttling (1 request/sec)
- Partner agreements si scale

### Constraint 3 : GDPR + régulations
**Problème** : Données sensibles, récurrence réglementaire
**Solution** :
- Pas de stockage SSN/documents identité
- Droit de suppression (cascade delete)
- Export données simple (JSON)
- Privacy policy claire
- Data processing agreement si EU
- Audit log complet

---

## 9. Métriques de succès

### User Metrics
- Sign-ups/mois
- MAU (Monthly Active Users)
- Candidatures/user/mois
- Taux de rétention (30j, 90j)
- NPS (Net Promoter Score)

### Business Metrics
- CAC (Customer Acquisition Cost)
- LTV (Lifetime Value)
- Churn rate
- Conversion rates (trial → paid)
- ARR (Annual Recurring Revenue)

### Product Metrics
- Jobs matched/user/mois
- Avg time to offer (days)
- Interview rate (interviews / candidatures)
- Offer rate (offers / candidatures)
- Feature usage (% users utilisant coaching, relances, etc.)

---

## 10. Pricing (futur)

**Tiers** :
- **Free** : 5 candidatures/mois, no automation
- **Pro** : $9.99/mois → 50 candidatures/mois, relances, letter gen
- **Premium** : $29.99/mois → unlimited, interview coaching, analytics
- **Team** : $99/mois → 5 users, templates partagés

---

## Conclusion

CareerOS AI est une plateforme sérieuse, réaliste et commercialisable. Les fonctionnalités proposées
répondent à des besoins réels. L'architecture est modulaire et peut évolver.

**Prochaine étape** : Validation de cette spec + définition des personas en détail + architecture technique.

---

**Signez-off** :
- [ ] Product Manager validates specs
- [ ] Tech Lead validates feasibility
- [ ] Design Lead validates UX approach
- [ ] Go ahead for Phase 1 architecture doc
