# FenchiesWBB
FenchiesWBB project repository

External email | Be CAUTIOUS, especially with links and attachments. 


# 🏀 FrenchiesWBB

> La plateforme de référence pour suivre les joueuses françaises de basket-ball professionnel à travers le monde (WNBA, EuroLigue, Unrivaled, LFB et compétitions internationales et projetX).
>> ajout de l'unrivaled en français pour me prep pour miami
---

## 🎯 Objectif du Projet

**FrenchiesWBB** a pour mission de centraliser en un seul endroit :
* Le suivi des performances individuelles et collectives des basketteuses françaises.
* Les calendriers des matchs en direct avec les horaires adaptés.
* Les informations de diffusion TV et streaming (chaînes, plateformes).
* Un système d'alertes et de notifications personnalisées.
* une selections de joueuses que l'on veut suivre

---

## 🛠️ Stack Technique (Prévue)

* **Mobile Frontend** : Flutter *(ou React Native)*
* **Backend / API Workers** : Python (FastAPI) ou Node.js (NestJS)
* **Base de Données & Cache** : PostgreSQL + Redis
* **Notifications** : Firebase Cloud Messaging (FCM)

---

## 📡 APIs & Sources de Données à Considérer

Pour alimenter l'application, plusieurs sources combinées sont nécessaires :

| Compétition / Domaine | Source / API Recommandée | Type d'accès |
| :--- | :--- | :--- |
| **Ligue Féminine (LFB / FFBB)** | SDK & Open Data FFBB (`ffbb-data-client`) | Officiel / Gratuit |
| **WNBA** | Big Balls Sports Data API / ESPN Hidden API | Non officiel / REST |
| **EuroLigue & FIBA** | FIBA API / Scraping structuré (`Playwright` / `BeautifulSoup`) | Semi-ouvert / Scraping |
| **Unrivaled League** | Flux officiels / Scraping du site officiel | Web Scraping |
| **Grille TV / Diffusion** | Base de données interne (CMS Admin / Saisie manuelle) | Interne |

---

## 🚀 Plan d'Actions (Roadmap)

### Phase 1 : Fondations & Base de Données
- [ ] Initialiser le dépôt GitHub et structurer le monorepo (Backend / Frontend).
- [ ] Concevoir le schéma relationnel PostgreSQL (Tables : `players`, `teams`, `competitions`, `matches`, `stats`, `broadcasts`).
- [ ] Créer la liste initiale des joueuses françaises cibles (WNBA, EuroLigue, Unrivaled, LFB).

### Phase 2 : Collecte des Données (Backend Workers)
- [ ] Développer les scripts d'agrégation (Cron jobs) pour récupérer les calendriers des matchs.
- [ ] Intégrer l'API/SDK de la LFB pour les championnats français.
- [ ] Mettre en place les connecteurs pour la WNBA et l'EuroLigue.

### Phase 3 : Application Mobile & Expérience Utilisateur
- [ ] Développer l'écran d'accueil : **Feed "Les Bleues du jour"**.
- [ ] Intégrer la vue détaillée par joueuse (Moyennes comparées par ligue).
- [ ] Ajouter l'indicateur clair des **chaînes de diffusion** (Ex: *Skweek, L'Équipe, WNBA Pass*).

### Phase 4 : Notifications & Automatisation
- [ ] Configurer Firebase Cloud Messaging (FCM) pour les pushs mobiles.
- [ ] Implémenter les alertes contextuelles (Rappel de match à J-30 min, récapitulatif des stats post-match).

---

## 💻 Installation & Développement (Bientôt disponible)

Instructions pour lancer le projet en local une fois le code initialisé.

```bash
# Cloner le projet
git clone [https://github.com/votre-pseudo/FrenchiesWBB.git](https://github.com/votre-pseudo/FrenchiesWBB.git)

# Installer les dépendances du backend
cd backend && npm install # ou pip install -r requirements.txt

# Lancer l'application mobile
cd ../mobile && flutter run
