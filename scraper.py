import requests
import json
import re
from datetime import date
from bs4 import BeautifulSoup

today = str(date.today())

# ─── Tarifs de base (fallback manuel si scraping échoue) ───
tarifs = {
    "updated": today,
    "source": "auto-scrape + fallback manuel",
    "offres": [
        {
            "id": "edf-trv",
            "nom": "Tarif Réglementé (TRV)",
            "fournisseur": "EDF",
            "abonnement": {"3": 127, "6": 156, "9": 202, "12": 240},
            "prix_base": 25.16,
            "prix_hp": 27.36,
            "prix_hc": 20.08,
            "type_prix": "Réglementé",
            "engagement": "Sans engagement",
            "lien": "https://www.edf.fr",
            "note": "Référence officielle"
        },
        {
            "id": "engie-vert",
            "nom": "Vert Électrique Base",
            "fournisseur": "Engie",
            "abonnement": {"3": 120, "6": 148, "9": 193, "12": 228},
            "prix_base": 23.89,
            "prix_hp": 26.10,
            "prix_hc": 18.70,
            "type_prix": "Fixe 1 an",
            "engagement": "12 mois",
            "lien": "https://www.engie.fr",
            "note": "Populaire déménagement"
        },
        {
            "id": "total-fixe",
            "nom": "Prix Fixe 2 ans",
            "fournisseur": "TotalEnergies",
            "abonnement": {"3": 115, "6": 142, "9": 185, "12": 219},
            "prix_base": 23.10,
            "prix_hp": 25.50,
            "prix_hc": 18.20,
            "type_prix": "Fixe 2 ans",
            "engagement": "24 mois",
            "lien": "https://totalenergies.fr",
            "note": "Stabilité long terme"
        },
        {
            "id": "ekwateur-vert",
            "nom": "Offre Verte",
            "fournisseur": "Ekwateur",
            "abonnement": {"3": 118, "6": 145, "9": 189, "12": 224},
            "prix_base": 22.95,
            "prix_hp": 25.20,
            "prix_hc": 18.00,
            "type_prix": "Indexé",
            "engagement": "Sans engagement",
            "lien": "https://ekwateur.fr",
            "note": "100% renouvelable"
        },
        {
            "id": "ilek-vert",
            "nom": "Électricité verte",
            "fournisseur": "Ilek",
            "abonnement": {"3": 116, "6": 143, "9": 187, "12": 221},
            "prix_base": 23.20,
            "prix_hp": 25.40,
            "prix_hc": 18.10,
            "type_prix": "Indexé",
            "engagement": "Sans engagement",
            "lien": "https://ilek.fr",
            "note": "Coopérative locale"
        }
    ]
}

# ─── Tentative de scraping EDF TRV (prix réglementé officiel) ───
try:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; tarif-bot/1.0)"}
    r = requests.get("https://www.prix-elec.com/tarif-reglemente.php", headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # Chercher prix base 6kVA
    text = soup.get_text()
    match_base = re.search(r'Base[^\d]*([\d,]+)\s*c€', text)
    match_hp   = re.search(r'Heures? [Pp]leines?[^\d]*([\d,]+)\s*c€', text)
    match_hc   = re.search(r'Heures? [Cc]reuses?[^\d]*([\d,]+)\s*c€', text)

    if match_base:
        tarifs["offres"][0]["prix_base"] = float(match_base.group(1).replace(',', '.'))
        tarifs["source"] = "scrape prix-elec.com + fallback"
        print(f"✅ TRV Base scraped: {tarifs['offres'][0]['prix_base']} c€/kWh")
    if match_hp:
        tarifs["offres"][0]["prix_hp"] = float(match_hp.group(1).replace(',', '.'))
        print(f"✅ TRV HP scraped: {tarifs['offres'][0]['prix_hp']} c€/kWh")
    if match_hc:
        tarifs["offres"][0]["prix_hc"] = float(match_hc.group(1).replace(',', '.'))
        print(f"✅ TRV HC scraped: {tarifs['offres'][0]['prix_hc']} c€/kWh")

except Exception as e:
    print(f"⚠️ Scraping failed, using fallback values: {e}")

# ─── Sauvegarde ───
with open("tarifs.json", "w", encoding="utf-8") as f:
    json.dump(tarifs, f, ensure_ascii=False, indent=2)

print(f"✅ tarifs.json saved — {today}")
