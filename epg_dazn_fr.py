import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# -------------------------
# الإعدادات
# -------------------------
API_KEY = "509ceffac75b4189b4c0e129e35941bb"
NUM_DAYS = 20
HEADERS = {"X-Auth-Token": API_KEY}

# كل قناة مرتبطة بمسابقة (competition code في football-data.org) ولغة (fr / en)
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
        "lang": "fr",
    },
    {
        "id": "daznlaliga",
        "name": "DAZN LaLiga",
        "competition": "PD",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/dazn.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/dazn_poster.png",
        "league_label": "LaLiga",
        "default_title": "Couverture complète de LaLiga: Résumés, Analyse et Commentaire d'Experts",
        "lang": "fr",
    },
    {
        "id": "disneypluslaliga",
        "name": "Disney+ LaLiga",
        "competition": "PD",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/disney_plus.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Dazn-france-epg/refs/heads/main/Logo/disney_poster.png",
        "league_label": "LaLiga",
        "default_title": "Couverture complète de LaLiga: Résumés, Analyse et Commentaire d'Experts",
        "lang": "fr",
    },
    # قنوات StarzPlay بالإنجليزي - Serie A
    {
        "id": "starzplay1",
        "name": "Starzplay 1",
        "competition": "SA",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Starzplay-sports-epg-xml/refs/heads/main/Logos/starz1.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Starzplay-sports-epg-xml/refs/heads/main/Logos/seriea.jpg",
        "league_label": "Serie A",
        "default_title": "Serie A Highlights, Analysis, and Expert Commentary",
        "lang": "en",
    },
    {
        "id": "starzplay2",
        "name": "Starzplay 2",
        "competition": "SA",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Starzplay-sports-epg-xml/refs/heads/main/Logos/starz2.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Starzplay-sports-epg-xml/refs/heads/main/Logos/seriea.jpg",
        "league_label": "Serie A",
        "default_title": "Serie A Highlights, Analysis, and Expert Commentary",
        "lang": "en",
    },
    {
        "id": "starzplay3",
        "name": "Starzplay 3",
        "competition": "SA",
        "logo": "https://raw.githubusercontent.com/ayoubboukous27/Starzplay-sports-epg-xml/refs/heads/main/Logos/starz3.png",
        "poster": "https://raw.githubusercontent.com/ayoubboukous27/Starzplay-sports-epg-xml/refs/heads/main/Logos/seriea.jpg",
        "league_label": "Serie A",
        "default_title": "Serie A Highlights, Analysis, and Expert Commentary",
        "lang": "en",
    },
]

# -------------------------
# سحب المباريات لكل مسابقة (مرة وحدة لكل competition code)
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

for ch in CHANNELS:
    channel = ET.SubElement(tv, "channel", id=ch["id"])
    ET.SubElement(channel, "display-name").text = ch["name"]
    ET.SubElement(channel, "icon", src=ch["logo"])


def add_programme(channel_id, start_dt, stop_dt, title, desc, logo, poster):
    prog = ET.SubElement(tv, "programme", {
        "channel": channel_id,
        "start": start_dt.strftime("%Y%m%d%H%M%S +0000"),
        "stop": stop_dt.strftime("%Y%m%d%H%M%S +0000"),
    })
    ET.SubElement(prog, "title").text = title
    ET.SubElement(prog, "desc").text = desc
    ET.SubElement(prog, "icon", src=logo)
    ET.SubElement(prog, "poster", src=poster)
    ET.SubElement(prog, "banner", src=poster)


def add_filler(channel_id, cursor, end_dt, ch):
    """يعمر الفراغ بين cursor و end_dt ببلوكات ساعة وحدة (أو أقل فالبلوك الأخير)، بلا أي تداخل ولا فراغ."""
    if ch.get("lang") == "en":
        desc = f"Full coverage of {ch['league_label']} on {ch['name']}. Highlights, Analysis and Expert Commentary."
    else:
        desc = f"Couverture complète de {ch['league_label']} sur {ch['name']}. Résumés, Analyse et Commentaire d'Experts."
    while cursor < end_dt:
        block_stop = min(cursor + timedelta(hours=1), end_dt)
        add_programme(channel_id, cursor, block_stop, ch["default_title"], desc, ch["logo"], ch["poster"])
        cursor = block_stop
    return cursor


def build_match_clusters(parsed_matches):
    """
    يجمع المباريات المتداخلة/المتزامنة زمنيا فـ cluster واحد.
    كل cluster = (cluster_start, cluster_end, [قائمة المباريات]).
    """
    clusters = []
    for start_dt, stop_dt, match in parsed_matches:
        if clusters and start_dt < clusters[-1]["end"]:
            # فيه تداخل زمني مع آخر cluster -> ندمجها
            clusters[-1]["end"] = max(clusters[-1]["end"], stop_dt)
            clusters[-1]["matches"].append((start_dt, stop_dt, match))
        else:
            clusters.append({
                "start": start_dt,
                "end": stop_dt,
                "matches": [(start_dt, stop_dt, match)],
            })
    return clusters


def format_cluster_programme(cluster, ch):
    matches = cluster["matches"]
    is_en = ch.get("lang") == "en"

    if len(matches) == 1:
        start_dt, stop_dt, match = matches[0]
        if is_en:
            title = f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} - {ch['league_label']} Live"
            desc = f"Live coverage of {match['homeTeam']['name']} vs {match['awayTeam']['name']} in {ch['league_label']}, on {ch['name']}."
        else:
            title = f"{match['homeTeam']['name']} vs {match['awayTeam']['name']} - {ch['league_label']} en direct"
            desc = f"Diffusion en direct de {match['homeTeam']['name']} contre {match['awayTeam']['name']} dans {ch['league_label']}, sur {ch['name']}."
        return title, desc

    # عدة مباريات فنفس الوقت -> برنامج واحد "Multiplex"، سطر واحد بلا قطع
    # الفصل بين المباريات: "et" بالفرنسية / "and" بالإنجليزي
    n = len(matches)
    sorted_matches = sorted(matches, key=lambda x: x[0])
    separator = " and " if is_en else " et "
    matchups = separator.join(
        f"{match['homeTeam']['name']} vs {match['awayTeam']['name']}"
        for _, _, match in sorted_matches
    )

    if is_en:
        title = f"Multiplex {ch['league_label']}: {matchups}"
        desc = f"Multiplex {ch['league_label']} on {ch['name']} - {n} matches live simultaneously: {matchups}."
    else:
        title = f"Multiplex {ch['league_label']} : {matchups}"
        desc = f"Multiplex {ch['league_label']} sur {ch['name']} - {n} rencontres en direct simultané : {matchups}."
    return title, desc


today = datetime.utcnow()
timeline_start = datetime(today.year, today.month, today.day)  # منتصف الليل اليوم (00:00 UTC)
timeline_end = timeline_start + timedelta(days=NUM_DAYS)

# -------------------------
# بناء خط زمني متواصل لكل قناة (بلا تداخل وبلا فراغ)، مع دمج المباريات المتزامنة
# -------------------------
for ch in CHANNELS:
    matches = matches_by_competition[ch["competition"]]

    parsed_matches = []
    for match in matches:
        start_dt = datetime.strptime(match["utcDate"], "%Y-%m-%dT%H:%M:%SZ")
        if timeline_start <= start_dt < timeline_end:
            stop_dt = start_dt + timedelta(hours=2)
            parsed_matches.append((start_dt, stop_dt, match))
    parsed_matches.sort(key=lambda x: x[0])

    clusters = build_match_clusters(parsed_matches)

    cursor = timeline_start
    for cluster in clusters:
        if cluster["start"] > cursor:
            cursor = add_filler(ch["id"], cursor, cluster["start"], ch)

        title, desc = format_cluster_programme(cluster, ch)
        add_programme(ch["id"], cluster["start"], cluster["end"], title, desc, ch["logo"], ch["poster"])
        cursor = cluster["end"]

    if cursor < timeline_end:
        add_filler(ch["id"], cursor, timeline_end, ch)

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
print(f"تم إنشاء epg.xml لمدة {NUM_DAYS} يوم لقنوات {channel_names} - مباريات متزامنة مدموجة، بلا فراغات")
