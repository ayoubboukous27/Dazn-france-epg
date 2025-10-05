import datetime

now = datetime.datetime.utcnow()
start = now.replace(hour=0, minute=0, second=0, microsecond=0)
stop = start + datetime.timedelta(hours=23, minutes=59, seconds=59)

start_str = start.strftime("%Y%m%d%H%M%S +0000")
stop_str = stop.strftime("%Y%m%d%H%M%S +0000")

epg = f'''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="ChatGPT EPG Generator">
  <channel id="DAZN.fr@Europe">
    <display-name>DAZN France</display-name>
    <icon src="https://i.postimg.cc/J0G130V3/Picsart-25-10-04-13-20-21-280.png" />
    <url>https://www.dazn.com/fr-FR</url>
  </channel>

  <programme start="{start_str}" stop="{stop_str}" channel="DAZN.fr@Europe">
    <title lang="fr">Serie A sur DAZN France</title>
    <desc lang="fr">Diffusion en direct des matchs du championnat italien Serie A sur DAZN France.</desc>
  </programme>
</tv>'''

with open("epg.xml", "w", encoding="utf-8") as f:
    f.write(epg)

print("✅ epg.xml updated successfully.")
