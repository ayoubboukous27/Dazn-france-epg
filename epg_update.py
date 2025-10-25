import datetime
import time

def generate_epg():
    now = datetime.datetime.utcnow()
    start = now.replace(minute=0, second=0, microsecond=0)
    stop = start + datetime.timedelta(hours=1)

    start_str = start.strftime("%Y%m%d%H%M%S +0000")
    stop_str = stop.strftime("%Y%m%d%H%M%S +0000")

    epg = f'''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="ChatGPT EPG Generator">

  <channel id="DAZN.fr1@Europe">
    <display-name>DAZN France 1</display-name>
    <icon src="https://i.postimg.cc/k4kLn7KJ/dazn-1-fr-be.png" />
    <url>https://www.dazn.com/fr-FR</url>
  </channel>

  <channel id="DAZN.fr2@Europe">
    <display-name>DAZN France 2</display-name>
    <icon src="https://i.postimg.cc/CLp9XLFT/dazn-2-fr-be.png" />
    <url>https://www.dazn.com/fr-FR</url>
  </channel>

  <channel id="DAZN.fr3@Europe">
    <display-name>DAZN France 3</display-name>
    <icon src="https://i.postimg.cc/CxmtRGk4/dazn-3-fr-be.png" />
    <url>https://www.dazn.com/fr-FR</url>
  </channel>

  <programme start="{start_str}" stop="{stop_str}" channel="DAZN.fr1@Europe">
    <title lang="fr">Serie A sur DAZN France 1</title>
    <desc lang="fr">Diffusion en direct des matchs du championnat italien Serie A sur DAZN France 1.</desc>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="DAZN.fr2@Europe">
    <title lang="fr">Serie A sur DAZN France 2</title>
    <desc lang="fr">Diffusion en direct des matchs du championnat italien Serie A sur DAZN France 2.</desc>
  </programme>

  <programme start="{start_str}" stop="{stop_str}" channel="DAZN.fr3@Europe">
    <title lang="fr">Serie A sur DAZN France 3</title>
    <desc lang="fr">Diffusion en direct des matchs du championnat italien Serie A sur DAZN France 3.</desc>
  </programme>

</tv>'''

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(epg)

    print(f"✅ epg.xml updated successfully at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")

# حلقة التكرار كل ساعة
while True:
    generate_epg()
    time.sleep(3600)  # انتظر ساعة (3600 ثانية)
