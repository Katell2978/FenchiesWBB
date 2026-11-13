# FrenchiesWBB — Suivi automatisé des matchs

Automatisation quotidienne de la récupération des calendriers de matchs des joueuses françaises évoluant à l'international et en Europe.

## Architecture du projet

* **`data/joueuses.json`** : Référentiel des joueuses suivies, de leurs sélections nationales et de leurs clubs respectifs (ligues nationales et coupes d'Europe).
* **`data/matches.json`** : Fichier de sortie généré automatiquement contenant la liste chronologique des rencontres à venir.
* **`scripts/update_european_matches.py`** : Script Python chargé d'extraire les calendriers depuis les flux publics des compétitions (FIBA, ligues nationales) via scraping (`requests` et `beautifulsoup4`).
* **`.github/workflows/update_matches.yml`** : Workflow GitHub Actions exécutant le script chaque jour à 4h00 UTC et enregistrant les mises à jour dans le dépôt.

## Choix techniques

* **Pivot vers le scraping** : L'offre gratuite d'API-Sports limitant l'accès aux saisons passées (2022–2024), le projet interroge directement les sources publiques (données JSON embarquées des pages officielles FIBA et ligues) pour récupérer les calendriers en cours sans dépendance à une API payante.

## Utilisation

Le script se déclenche automatiquement via GitHub Actions, mais peut également être lancé manuellement depuis l'onglet **Actions** du dépôt (*Run workflow*).
