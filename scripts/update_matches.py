import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY
}

def get_team_games(team_id):
    if not team_id:
        return []
    
    # 1. Récupérer dynamiquement les ligues et saisons de l'équipe
    leagues_url = f"{BASE_URL}/leagues"
    try:
        res = requests.get(leagues_url, headers=HEADERS, params={"team": team_id}, timeout=10)
        leagues_data = res.json().get("response", [])
    except Exception as e:
        print(f"Erreur lors de la récupération des ligues pour l'équipe {team_id} : {e}")
        return []

    games = []
    now = datetime.utcnow()

    # 2. Interroger les matchs pour chaque ligue et saison active trouvée
    for league_info in leagues_data:
        league_id = league_info["league"]["id"]
        seasons = [s["season"] for s in league_info.get("seasons", [])]
        
        # Cibler en priorité la saison en cours (2026 ou 2026-2027)
        target_seasons = [s for s in seasons if str(s).startswith("2026") or str(s).startswith("2025")]
        if not target_seasons and seasons:
            target_seasons = [seasons[-1]]

        for season in target_seasons:
            games_url = f"{BASE_URL}/games"
            params = {"team": team_id, "league": league_id, "season": season}
            try:
                g_res = requests.get(games_url, headers=HEADERS, params=params, timeout=10)
                g_data = g_res.json()
                for game in g_data.get("response", []):
                    game_date_str = game["date"]
                    game_date = datetime.fromisoformat(game_date_str.replace("Z", ""))
                    if game_date >= now and game.get("status", {}).get("short") == "NS":
                        if not any(g["date"] == game_date_str and g["home"] == game["teams"]["home"]["name"] for g in games):
                            games.append({
                                "date": game_date_str,
                                "home": game["teams"]["home"]["name"],
                                "away": game["teams"]["away"]["name"]
                            })
            except Exception as e:
                print(f"Erreur pour l'équipe {team_id}, ligue {league_id}, saison {season} : {e}")
                
    games.sort(key=lambda x: x["date"])
    return games

def main():
    if not API_KEY:
        print("Erreur : API_SPORTS_KEY absente.")
        return

    with open("data/joueuses.json", "r", encoding="utf-8") as f:
        roster = json.load(f)

    teams_to_check = {}
    for player in roster.get("players", []):
        for club_info in player.get("clubs", {}).values():
            if isinstance(club_info, dict) and club_info.get("team_id"):
                teams_to_check[club_info["team_id"]] = club_info["name"]

    schedule_results = []
    for team_id, club_name in teams_to_check.items():
        print(f"Récupération pour {club_name} (ID : {team_id})...")
        games = get_team_games(team_id)
        schedule_results.append({
            "club": club_name,
            "team_id": team_id,
            "upcoming_games": games
        })

    output_data = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "matches": schedule_results
    }

    os.makedirs("data", exist_ok=True)
    with open("data/matches.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("Fichier data/matches.json généré avec succès.")

if __name__ == "__main__":
    main()
