import os
import json
import re
import requests
from datetime import datetime

API_KEY = os.getenv("API_SPORTS_KEY")
BASE_URL = "https://v1.basketball.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY} if API_KEY else {}

def parse_ics_calendar(file_path):
    """Parse le fichier ICS de l'Équipe de France sans dépendance externe."""
    if not os.path.exists(file_path):
        print(f"Fichier ICS non trouvé : {file_path}")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    events = []
    vevents = content.split('BEGIN:VEVENT')
    for vevent in vevents[1:]:
        summary_match = re.search(r'SUMMARY:(.*?)(?:\r?\n|$)', vevent)
        dtstart_match = re.search(r'DTSTART:(.*?)(?:\r?\n|$)', vevent)
        
        if summary_match and dtstart_match:
            summary = summary_match.group(1).strip()
            dtstart_str = dtstart_match.group(1).strip()
            
            # Conversion format ICS (20261111T163000Z) vers ISO
            try:
                dt = datetime.strptime(dtstart_str, '%Y%m%dT%H%M%SZ')
                iso_date = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                iso_date = dtstart_str
            
            # Nettoyage du résumé (ex: "France 🆚 Grande-Bretagne")
            teams = re.split(r'\s*[🆚vV][sS]?\s*', summary)
            home = teams[0].strip() if len(teams) > 0 else "France"
            away = teams[1].strip() if len(teams) > 1 else ""
            
            events.append({
                "entity": "Équipe de France",
                "competition": "EuroBasket 2027 Qualifiers",
                "home": home,
                "away": away,
                "date": iso_date
            })
    return events

def fetch_club_games(team_id, club_name):
    """Récupère les matchs d'un club via API-Sports."""
    if not API_KEY:
        return []
    
    for season in ["2026-2027", "2026", "2025-2026"]:
        url = f"{BASE_URL}/games"
        params = {"team": team_id, "season": season}
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
                        "entity": club_name,
                        "competition": game.get("league", {}).get("name", "Club Match"),
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
    os.makedirs("data", exist_ok=True)
    
    # 1. Charger les matchs de l'Équipe de France depuis l'ICS
    ics_path = "data/agenda_edf.ics"
    all_matches = parse_ics_calendar(ics_path)
    print(f"{len(matches_edf := all_matches)} match(es) de l'Équipe de France chargés.")

    # 2. Charger les joueuses pour identifier les clubs et leurs team_id
    roster_path = "data/joueuses.json"
    if os.path.exists(roster_path):
        with open(roster_path, 'r', encoding='utf-8') as f:
            roster = json.load(f)
        
        checked_teams = set()
        for player in roster.get("players", []):
            for club_info in player.get("clubs", {}).values():
                if isinstance(club_info, dict) and club_info.get("team_id"):
                    t_id = club_info["team_id"]
                    c_name = club_info["name"]
                    if t_id not in checked_teams:
                        checked_teams.add(t_id)
                        print(f"Récupération des matchs pour : {c_name} (ID: {t_id})...")
                        club_games = fetch_club_games(t_id, c_name)
                        all_matches.extend(club_games)

    # Trier tous les matchs par date croissante
    all_matches.sort(key=lambda x: x["date"])

    output_data = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "matches": all_matches
    }

    with open("data/matches.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print("Fichier data/matches.json généré avec succès !")

if __name__ == "__main__":
    main()
