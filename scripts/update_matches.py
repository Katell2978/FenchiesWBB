import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {
    "x-apisports-key": API_KEY
}

def get_team_id(team_name):
    if not team_name:
        return None
    url = f"{BASE_URL}/teams"
    params = {"search": team_name}
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = response.json()
        if data.get("response"):
            return data["response"][0]["id"]
    except Exception as e:
        print(f"Erreur pour l'équipe {team_name} : {e}")
    return None

def get_upcoming_games(team_id):
    if not team_id:
        return []
    url = f"{BASE_URL}/games"
    params = {"team": team_id, "season": "2026"}
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

    clubs_set = set()
    for player in roster.get("players", []):
        for val in player.get("clubs", {}).values():
            if val and isinstance(val, str):
                clubs_set.add(val)

    schedule_results = []
    for club in clubs_set:
        team_id = get_team_id(club)
        if team_id:
            games = get_upcoming_games(team_id)
            schedule_results.append({
                "club": club,
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

    print("Données enregistrées dans data/matches.json.")

if __name__ == "__main__":
    main()
