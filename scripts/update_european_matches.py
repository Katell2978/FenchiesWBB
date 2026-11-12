import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY} if API_KEY else {}

def get_club_games_for_competition(team_id, league_id, club_name, comp_name):
    if not API_KEY or not team_id:
        print(f"[DEBUG] Clé API ou Team ID manquant pour {club_name}")
        return []
    
    seasons = ["2026-2027", "2026", "2025-2026"]
    for season in seasons:
        url = f"{BASE_URL}/games"
        params = {"team": team_id, "season": season}
        if league_id:
            params["league"] = league_id
            
        try:
            print(f"[DEBUG] Appel API -> Club: {club_name} | Compétition: {comp_name} | URL: {url} | Params: {params}")
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            data = response.json()
            
            print(f"[DEBUG] Réponse API (status {response.status_code}) : {data}")
            
            games = []
            now = datetime.utcnow()
            
            for game in data.get("response", []):
                game_date_str = game["date"]
                try:
                    game_date = datetime.fromisoformat(game_date_str.replace("Z", ""))
                except ValueError:
                    continue
                
                if game_date >= now and game.get("status", {}).get("short") == "NS":
                    games.append({
                        "entity": club_name,
                        "competition": game.get("league", {}).get("name", comp_name),
                        "home": game["teams"]["home"]["name"],
                        "away": game["teams"]["away"]["name"],
                        "date": game_date_str
                    })
            if games:
                print(f"[SUCCÈS] {len(games)} match(es) trouvé(s) pour {club_name} ({comp_name}) en saison {season}")
                return games
        except Exception as e:
            print(f"Erreur API pour {club_name} ({comp_name}) : {e}")
            
    print(f"[AVERTISSEMENT] Aucun match trouvé pour {club_name} sur les saisons testées.")
    return []

def main():
    if not API_KEY:
        print("Erreur critique : API_SPORTS_KEY est vide.")
        return

    json_path = "data/matches.json"
    existing_matches = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                existing_matches = content.get("matches", [])
        except Exception:
            pass

    roster_path = "data/joueuses.json"
    if not os.path.exists(roster_path):
        print("Erreur : data/joueuses.json introuvable.")
        return

    with open(roster_path, 'r', encoding='utf-8') as f:
        roster = json.load(f)

    active_clubs = set()
    for player in roster.get("players", []):
        club = player.get("clubs", {}).get("european_club")
        if isinstance(club, dict) and club.get("name"):
            active_clubs.add(club["name"])

    preserved_matches = [m for m in existing_matches if m.get("entity") not in active_clubs]
    new_club_matches = []
    checked_keys = set()

    for player in roster.get("players", []):
        club = player.get("clubs", {}).get("european_club")
        if isinstance(club, dict) and club.get("team_id"):
            t_id = club["team_id"]
            c_name = club["name"]
            competitions = club.get("competitions", [])
            
            if competitions:
                for comp in competitions:
                    l_id = comp.get("league_id")
                    c_name_comp = comp.get("name", "Compétition")
                    key = (t_id, l_id)
                    if key not in checked_keys:
                        checked_keys.add(key)
                        games = get_club_games_for_competition(t_id, l_id, c_name, c_name_comp)
                        if games:
                            new_club_matches.extend(games)
            else:
                l_id = club.get("league_id")
                key = (t_id, l_id)
                if key not in checked_keys:
                    checked_keys.add(key)
                    games = get_club_games_for_competition(t_id, l_id, c_name, "Championnat / Coupe")
                    if games:
                        new_club_matches.extend(games)

    all_matches = preserved_matches + new_club_matches
    all_matches.sort(key=lambda x: x["date"])

    output_data = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "matches": all_matches
    }

    os.makedirs("data", exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Mise à jour terminée. {len(all_matches)} match(es) au total dans data/matches.json.")

if __name__ == "__main__":
    main()
