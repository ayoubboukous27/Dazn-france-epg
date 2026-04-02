import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# -------------------------
# الإعدادات
# -------------------------
API_KEY = "509ceffac75b4189b4c0e129e35941bb"
COMPETITION = "SA"  # Serie A
NUM_DAYS = 20

CHANNELS = [
    {"id": "daznfr", "name": "DAZN France", "logo": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/dazn.png"}
]

DEFAULT_PROGRAM_TITLE = "Couverture complète de la Serie A: Résumés, Analyse et Commentaire d'Experts"
POSTER_URL = "https://github.com/ayoubboukous27/Dazn-france-epg/raw/refs/heads/main/Logo/serie-a-om-dazn_dm0f6994d6wq1m5dxtayqkxk0.jpg"
HEADERS = {"X-Auth-Token": API_KEY}

# -------------------------
# سحب جميع المباريات القادمة
# -------------------------
url = f"https://api.football-data.org/v4/competitions/{COMPETITION}/matches?status=SCHEDULED"
response = requests.get(url, headers=HEADERS)
data = response.json()
matches = data.get("matches", [])

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
for day_offset in range(NUM_DAYS):
    current_date = today + timedelta(days=day_offset)
    date_str = current_date.strftime("%Y-%m-%d")

    # فلترة المباريات لهذا اليوم
    day_matches = [m for m in matches if m["utcDate"].startswith(date_str)]
    day_matches.sort(key=lambda m: m["utcDate"])

    # قائمة ساعات المباريات الفعلية
    busy_hours = []
    for match in day_matches:
        match_start = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        for hour in range(match_start.hour, match_start.hour + 2):  # نفترض كل مباراة ساعتين
            busy_hours.append(hour)

    for ch in CHANNELS:
        # المباريات الحقيقية
        for match in day_matches:
            start_dt = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
            stop_dt = start_dt + timedelta(hours=2)
            title = f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} - Serie A en direct"
            desc = f"Diffusion en direct de {match['homeTeam']['name']} contre {match['awayTeam']['name']} dans la Serie A."

            prog = ET.SubElement(tv, "programme", {
                "channel": ch["id"],
                "start": start_dt.strftime("%Y%m%d%H%M%S +0000"),
                "stop": stop_dt.strftime("%Y%m%d%H%M%S +0000")
            })
            ET.SubElement(prog, "title").text = title
            ET.SubElement(prog, "desc").text = desc
            ET.SubElement(prog, "icon", src=ch["logo"])
            ET.SubElement(prog, "poster", src=POSTER_URL)   # ← Poster مضاف
            ET.SubElement(prog, "banner", src=POSTER_URL)   # ← Banner مضاف

        # البرنامج الوهمي كل ساعة ما عدا وقت المباريات
        for hour in range(0, 24):
            if hour not in busy_hours:
                start_dt = datetime.combine(current_date.date(), datetime.min.time()) + timedelta(hours=hour)
                stop_dt = start_dt + timedelta(hours=1)
                prog = ET.SubElement(tv, "programme", {
                    "channel": ch["id"],
                    "start": start_dt.strftime("%Y%m%d%H%M%S +0000"),
                    "stop": stop_dt.strftime("%Y%m%d%H%M%S +0000")
                })
                ET.SubElement(prog, "title").text = DEFAULT_PROGRAM_TITLE
                ET.SubElement(prog, "desc").text = f"Couverture complète de la Serie A pour {ch['name']}. Résumés, Analyse et Commentaire d'Experts."
                ET.SubElement(prog, "icon", src=ch["logo"])
                ET.SubElement(prog, "poster", src=POSTER_URL)  # ← Poster مضاف
                ET.SubElement(prog, "banner", src=POSTER_URL)  # ← Banner مضاف

# -------------------------
# حفظ XML
# -------------------------
tree = ET.ElementTree(tv)
tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

print(f"تم إنشاء epg.xml لمدة {NUM_DAYS} يوم لقناة {CHANNELS[0]['name']} مع بوستر لجميع البرامج")
