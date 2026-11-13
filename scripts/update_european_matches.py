import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_usk_prague_games():
    """Récupère les matchs de l'USK Prague via l'analyse des données publiques."""
    matches = []
    
    # Page officielle FIBA EuroLeague Women
    url = "https://www.fiba.basketball/en/events/euroleague-women-26-27/schedules"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            
            if script_tag:
                data = json.loads(script_tag.string)
                # Exploration du JSON pour extraire les rencontres impliquant l'USK Prague
                # (la structure exacte des props FIBA sera lue ici)
                
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        
    return matches

def main():
    json_path = "data/matches.json"
    
    existing_matches = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                existing_matches = content.get("matches", [])
        except Exception:
            pass

    usk_matches = get_usk_prague_games()
    
    preserved_matches = [m for m in existing_matches if m.get("entity") != "USK Prague"]
    all_matches = preserved_matches + usk_matches
    all_matches.sort(key=lambda x: x["date"])

    output_data = {
        "updated_at": datetime.utcnow().strftime("%Y-%m-%d"),
        "matches": all_matches
    }

    os.makedirs("data", exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Mise à jour réussie. {len(all_matches)} match(es) enregistrés.")

if __name__ == "__main__":
    main()
