import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY
}

def get_upcoming_games(team_id, league_id):
    for season in ["2026-2027", "2026"]:
        url = f"{BASE_URL}/games"
        params = {"team": team_id, "season": season}
        if league_id:
            params["league"] = league_id
            
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            data = response.json()
            games = []
            now = datetime.utcnow()
            for game in data.get("response", []):
                game_date_str = game["date"]
                game_date = datetime.fromisoformat(game_date_str.replace("Z", ""))
                if game_date >= now and game.get("status", {}).get("short") == "NS":
                    games.append({
                        "date": game_date_str,
                        "home": game["teams"]["home"]["name"],
                        "away": game["teams"]["away"]["name"]
                    })
            if games:
                return games
        except Exception as e:
            print(f"Erreur pour l'équipe ID {team_id} : {e}")
    return []

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
                teams_to_check[club_info["team_id"]] = {
                    "name": club_info["name"],
                    "league_id": club_info.get("league_id")
                }

    schedule_results = []
    for team_id, info in teams_to_check.items():
        print(f"Récupération pour {info['name']} (ID : {team_id}, Ligue : {info['league_id']})")
        games = get_upcoming_games(team_id, info['league_id'])
        schedule_results.append({
            "club": info['name'],
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
