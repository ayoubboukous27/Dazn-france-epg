import datetime

def generate_epg():
    now = datetime.datetime.now(datetime.UTC)

    epg = '''<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="ChatGPT EPG Generator">
'''

    channels = [
        ("DAZN.fr1@Europe", "DAZN France 1", "https://i.postimg.cc/k4kLn7KJ/dazn-1-fr-be.png"),
        ("DAZN.fr2@Europe", "DAZN France 2", "https://i.postimg.cc/CLp9XLFT/dazn-2-fr-be.png"),
        ("DAZN.fr3@Europe", "DAZN France 3", "https://i.postimg.cc/CxmtRGk4/dazn-3-fr-be.png"),
    ]

    # --- القنوات ---
    for ch_id, name, logo in channels:
        epg += f'''
  <channel id="{ch_id}">
    <display-name>{name}</display-name>
    <icon src="{logo}" />
    <url>https://www.dazn.com/fr-FR</url>
  </channel>
'''

    # --- البرامج لكل 8 ساعات ولمدة 3 أيام ---
    hours_per_block = 8
    total_days = 3
    total_blocks = 24 // hours_per_block

    for day_offset in range(total_days):
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=day_offset)

        for block in range(total_blocks):
            start = day_start + datetime.timedelta(hours=block * hours_per_block)
            stop = start + datetime.timedelta(hours=hours_per_block)

            start_str = start.strftime("%Y%m%d%H%M%S +0000")
            stop_str = stop.strftime("%Y%m%d%H%M%S +0000")

            for ch_id, name, _ in channels:
                epg += f'''
  <programme start="{start_str}" stop="{stop_str}" channel="{ch_id}">
    <title lang="fr">Serie A sur {name}</title>
    <desc lang="fr">Diffusion en direct des matchs du championnat italien Serie A sur {name}.</desc>
  </programme>
'''

    epg += "\n</tv>"

    with open("epg.xml", "w", encoding="utf-8") as f:
        f.write(epg)

    print(f"✅ epg.xml generated for 3 days (8-hour blocks) at {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")

generate_epg()
