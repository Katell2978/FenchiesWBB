import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY} if API_KEY else {}

def get_european_club_games(team_id, club_name):
    """Interroge l'API-Sports pour trouver les matchs à venir d'un club européen."""
    if not API_KEY or not team_id:
        return []
    
    # Saisons en cours pour le calendrier européen 2026-2027
    seasons = ["2026-2027", "2026", "2025-2026"]
    
    for season in seasons:
        url = f"{BASE_URL}/games"
        params = {"team": team_id, "season": season}
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            data = response.json()
            games = []
            now = datetime.utcnow()
            
            for game in data.get("response", []):
                game_date_str = game["date"]
                try:
                    game_date = datetime.fromisoformat(game_date_str.replace("Z", ""))
                except ValueError:
                    continue
                
                # Filtrer uniquement les matchs futurs et non joués (NS = Not Started)
                if game_date >= now and game.get("status", {}).get("short") == "NS":
                    games.append({
                        "entity": club_name,
                        "competition": game.get("league", {}).get("name", "Championnat / Coupe d'Europe"),
                        "home": game["teams"]["home"]["name"],
                        "away": game["teams"]["away"]["name"],
                        "date": game_date_str
                    })
            if games:
                return games
        except Exception as e:
            print(f"Erreur API pour {club_name} (ID {team_id}) : {e}")
            
    return []

def main():
    if not API_KEY:
        print("Attention : API_SPORTS_KEY absente. Aucun match ne sera récupéré via l'API.")
    
    # 1. Charger les joueuses pour extraire les clubs européens
    roster_path = "data/joueuses.json"
    if not os.path.exists(roster_path):
        print("Erreur : data/joueuses.json introuvable.")
        return

    with open(roster_path, 'r', encoding='utf-8') as f:
        roster = json.load(f)

    all_matches = []
    checked_teams = set()

    for player in roster.get("players", []):
        # On cible spécifiquement european_club (et éventuellement d'autres ligues de club)
        clubs = player.get("clubs", {})
        european_club = clubs.get("european_club")
        
        if isinstance(european_club, dict) and european_club.get("team_id"):
            t_id = european_club["team_id"]
            c_name = european_club["name"]
            
            if t_id not in checked_teams:
                checked_teams.add(t_id)
                print(f"Récupération des matchs pour le club européen : {c_name} (ID: {t_id})")
                club_games = get_european_club_games(t_id, c_name)
                all_matches.extend(club_games)

    # Trier tous les matchs par date croissante
    all_matches.sort(key=lambda x: x["date"])

    output_data = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "matches": all_matches
    }

    os.makedirs("data", exist_ok=True)
    with open("data/matches.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Succès ! {len(all_matches)} match(es) européen(s) enregistrés dans data/matches.json.")

if __name__ == "__main__":
    main()
