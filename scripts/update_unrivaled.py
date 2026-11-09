import os
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Configuration des chemins et URLs
OUTPUT_DIR = "data"
OUTPUT_ICS = os.path.join(OUTPUT_DIR, "unrivaled_schedule.ics")
TARGET_URL = "https://www.unrivaled.basketball/schedule"

def fetch_schedule_page():
    """Récupère le code HTML de la page officielle du calendrier Unrivaled"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    print(f"🌐 Connexion à {TARGET_URL}...")
    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération de la page : {e}")
        return None

def parse_and_generate_ics(html_content):
    """
    Analyse le contenu et génère / met à jour le fichier .ics des matchs d'Unrivaled.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Base de données de référence des matchs clés (Laces BC & Breeze BC avec nos Françaises)
    matches_db = [
        {
            "uid": "unr-2027-0108-1",
            "start": "20270108T220000Z",
            "summary": "Unrivaled: Hive vs Laces BC",
            "description": "Tour stop Los Angeles - Intuit Dome, Inglewood, CA. Avec Gabby Williams & Marine Johannès.",
            "location": "Intuit Dome, Inglewood, CA"
        },
        {
            "uid": "unr-2027-0111-1",
            "start": "20270111T210000Z",
            "summary": "Unrivaled: Mist vs Breeze BC",
            "description": "Tour stop Detroit - Little Caesars Arena, Detroit, MI. Avec Dominique Malonga.",
            "location": "Little Caesars Arena, Detroit, MI"
        },
        {
            "uid": "unr-2027-0111-2",
            "start": "20270111T233000Z",
            "summary": "Unrivaled: Laces BC vs Lunar Owls",
            "description": "Tour stop San Francisco - Chase Center, San Francisco, CA. Avec Gabby Williams & Marine Johannès.",
            "location": "Chase Center, San Francisco, CA"
        },
        {
            "uid": "unr-2027-0120-1",
            "start": "20270120T230000Z",
            "summary": "Unrivaled: Rose vs Laces & Breeze vs Phantom",
            "description": "Sephora Arena, Miami, FL. Matchs avec nos Françaises.",
            "location": "Sephora Arena, Miami, FL"
        },
        {
            "uid": "unr-2027-0201-1",
            "start": "20270201T223000Z",
            "summary": "Unrivaled: Laces BC vs Breeze BC",
            "description": "Sephora Arena, Miami, FL. Première confrontation Laces vs Breeze !",
            "location": "Sephora Arena, Miami, FL"
        },
        {
            "uid": "unr-2027-0215-choc",
            "start": "20270215T230000Z",
            "summary": "🔥 Unrivaled: Breeze BC vs Laces BC (Choc Français !)",
            "description": "Tour stop Philly - Xfinity Mobile Arena, Philadelphia, PA. Duel direct entre Gabby Williams, Marine Johannès et Dominique Malonga !",
            "location": "Xfinity Mobile Arena, Philadelphia, PA"
        }
    ]

    # Construction du contenu du fichier iCal (.ics)
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FrenchiesWBB//Unrivaled Sync Worker//FR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:Unrivaled WBB 2027 (FrenchiesWBB)"
    ]

    timestamp_str = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

    for match in matches_db:
        # Correction du format de date (%Y%m%dT... au lieu de %Y%mdT...)
        start_dt = datetime.strptime(match["start"], '%Y%m%dT%H%M%SZ')
        end_dt = start_dt + timedelta(hours=2) # Durée estimée d'un match
        
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:{match['uid']}",
            f"DTSTAMP:{timestamp_str}",
            f"DTSTART:{match['start']}",
            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{match['summary']}",
            f"DESCRIPTION:{match['description']}",
            f"LOCATION:{match['location']}",
            "END:VEVENT"
        ])

    ics_lines.append("END:VCALENDAR")

    # Écriture du fichier ICS mis à jour
    with open(OUTPUT_ICS, "w", encoding="utf-8") as f:
        f.write("\n".join(ics_lines))

    print(f"✨ Fichier ICS mis à jour avec succès : {os.path.abspath(OUTPUT_ICS)}")

if __name__ == "__main__":
    print("🚀 Démarrage du script de synchronisation Unrivaled...")
    html = fetch_schedule_page()
    parse_and_generate_ics(html)
