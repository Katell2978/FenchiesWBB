import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_usk_prague_games():
    matches = []
    # URL officielle FIBA EuroLeague Women 2026-2027
    url = "https://www.fiba.basketball/en/events/euroleague-women-26-27/schedules"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"[DEBUG] Connexion à {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        print(f"[DEBUG] Code statut HTTP : {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            script_tag = soup.find('script', id='__NEXT_DATA__')
            
            if script_tag:
                print("[DEBUG] Balise __NEXT_DATA__ trouvée !")
                data = json.loads(script_tag.string)
                
                # On inspecte les clés principales du JSON de la FIBA
                page_props = data.get("props", {}).get("pageProps", {})
                print(f"[DEBUG] Clés disponibles dans pageProps : {list(page_props.keys())}")
                
                # On affiche un extrait du JSON pour repérer où sont stockés les matchs
                extrait = json.dumps(page_props)[:1500]
                print(f"[DEBUG] Extrait des données : {extrait}")
            else:
                print("[DEBUG] Balise __NEXT_DATA__ introuvable sur cette page.")
                # Vérifions le titre de la page pour voir si on n'est pas bloqué par un anti-bot
                title = soup.title.string if soup.title else "Pas de titre"
                print(f"[DEBUG] Titre de la page reçue : {title}")
                
    except Exception as e:
        print(f"[ERREUR] Échec du scraping : {e}")
        
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

    print(f"Mise à jour terminée. {len(all_matches)} match(es) enregistrés.")

if __name__ == "__main__":
    main()
