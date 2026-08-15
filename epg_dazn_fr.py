import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# -------------------------
# الإعدادات
# -------------------------
API_KEY = "509ceffac75b4189b4c0e129e35941bb"
NUM_DAYS = 20
HEADERS = {"X-Auth-Token": API_KEY}

# كل قناة مرتبطة بمسابقة (competition code في football-data.org)
# SA = Serie A | PD = LaLiga (Primera División)
CHANNELS = [
    {
        "id": "daznseriea",
        "name": "DAZN Serie A",
        "competition": "SA",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/dazn.png",
        "poster": "https://github.com/ayoubboukous27/Dazn-france-epg/raw/refs/heads/main/Logo/serie-a-om-dazn_dm0f6994d6wq1m5dxtayqkxk0.jpg",
        "league_label": "Serie A",
        "default_title": "Couverture complète de la Serie A: Résumés, Analyse et Commentaire d'Experts",
    },
    {
        "id": "daznlaliga",
        "name": "DAZN LaLiga",
        "competition": "PD",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/dazn.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/dazn_poster.png",
        "league_label": "LaLiga",
        "default_title": "Couverture complète de LaLiga: Résumés, Analyse et Commentaire d'Experts",
    },
    {
        "id": "disneypluslaliga",
        "name": "Disney+ LaLiga",
        "competition": "PD",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/disney_plus.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/disney_poster.png",
        "league_label": "LaLiga",
        "default_title": "Couverture complète de LaLiga: Résumés, Analyse et Commentaire d'Experts",
    },
]

# -------------------------
# سحب المباريات لكل مسابقة (مرة وحدة لكل competition code، حتى لو استعملتها بزوج قنوات)
# -------------------------
matches_by_competition = {}
for competition in {ch["competition"] for ch in CHANNELS}:
    url = f"https://api.football-data.org/v4/competitions/{competition}/matches?status=SCHEDULED"
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        matches_by_competition[competition] = data.get("matches", [])
    except requests.exceptions.RequestException as e:
        print(f"خطأ أثناء الاتصال بـ API لمسابقة {competition}: {e}")
        matches_by_competition[competition] = []

# -------------------------
# إنشاء XMLTV
# -------------------------
tv = ET.Element("tv")

# تعريف القنوات
for ch in CHANNELS:
    channel = ET.SubElement(tv, "channel", id=ch["id"])
    ET.SubElement(channel, "display-name").text = ch["name"]
    ET.SubElement(channel, "icon", src=ch["logo"])

today = datetime.utcnow()

# -------------------------
# بناء البرامج اليومية لكل قناة
# -------------------------
for ch in CHANNELS:
    matches = matches_by_competition[ch["competition"]]

    for day_offset in range(NUM_DAYS):
        current_date = today + timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")

        # فلترة مباريات هذا اليوم لهاذ المسابقة
        day_matches = [m for m in matches if m["utcDate"].startswith(date_str)]
        day_matches.sort(key=lambda m: m["utcDate"])

        # ساعات المباريات الفعلية (باش نتفاداو التعارض مع البرنامج الافتراضي)
        busy_hours = []
        for match in day_matches:
            match_start = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            for hour in range(match_start.hour, match_start.hour + 2):
                busy_hours.append(hour % 24)

        # المباريات الحقيقية
        for match in day_matches:
            start_dt = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            stop_dt = start_dt + timedelta(hours=2)
            title = f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} - {ch['league_label']} en direct"
            desc = f"Diffusion en direct de {match['homeTeam']['name']} contre {match['awayTeam']['name']} dans {ch['league_label']}, sur {ch['name']}."

            prog = ET.SubElement(tv, "programme", {
                "channel": ch["id"],
                "start": start_dt.strftime("%Y%m%d%H%M%S +0000"),
                "stop": stop_dt.strftime("%Y%m%d%H%M%S +0000")
            })
            ET.SubElement(prog, "title").text = title
            ET.SubElement(prog, "desc").text = desc
            ET.SubElement(prog, "icon", src=ch["logo"])
            ET.SubElement(prog, "poster", src=ch["poster"])
            ET.SubElement(prog, "banner", src=ch["poster"])

        # البرنامج الافتراضي كل ساعة خارج أوقات المباريات
        for hour in range(0, 24):
            if hour not in busy_hours:
                start_dt = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=hour)
                stop_dt = start_dt + timedelta(hours=1)
                prog = ET.SubElement(tv, "programme", {
                    "channel": ch["id"],
                    "start": start_dt.strftime("%Y%m%d%H%M%S +0000"),
                    "stop": stop_dt.strftime("%Y%m%d%H%M%S +0000")
                })
                ET.SubElement(prog, "title").text = ch["default_title"]
                ET.SubElement(prog, "desc").text = f"Couverture complète de {ch['league_label']} sur {ch['name']}. Résumés, Analyse et Commentaire d'Experts."
                ET.SubElement(prog, "icon", src=ch["logo"])
                ET.SubElement(prog, "poster", src=ch["poster"])
                ET.SubElement(prog, "banner", src=ch["poster"])

# -------------------------
# حفظ XML
# -------------------------
tree = ET.ElementTree(tv)
try:
    ET.indent(tree, space="  ")  # تنسيق أنيق (Python 3.9+)
except AttributeError:
    pass
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

channel_names = " و ".join(ch["name"] for ch in CHANNELS)
print(f"تم إنشاء epg.xml لمدة {NUM_DAYS} يوم لقنوات {channel_names}")
            
