import requests
import json
import gzip
from io import BytesIO
import re
import os

def get_canli_tv_m3u():
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGQ3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E"
    }

    try:
        print("📡 CanliTV API'den veri alınıyor...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                content = gz.read().decode('utf-8')
        except:
            content = response.content.decode('utf-8')

        data = json.loads(content)
        if not data.get('IsSucceeded') or not data.get('Data', {}).get('AllChannels'):
            print("❌ Geçerli veri alınamadı!")
            return False

        channels = data['Data']['AllChannels']
        print(f"✅ {len(channels)} canlı kanal bulundu")

        # Yeni verileri dict olarak topla (isim yerine sabit id atanıyor)
        updated_channels = {}
        kanal_index = 1000
        for channel in channels:
            name = channel.get('Name')
            stream_data = channel.get('StreamData', {})
            hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
            logo = channel.get('PrimaryLogoImageUrl', '')
            categories = channel.get('Categories', [])
            group = categories[0].get('Name', 'Genel') if categories else 'Genel'

            if not name or not hls_url or group == "Bilgilendirme":
                continue

            updated_channels[str(kanal_index)] = {
                "name": name,
                "logo": logo,
                "group": group,
                "url": hls_url
            }
            kanal_index += 1

        # Eski dosya varsa oku
        m3u_path = "1.m3u"
        if os.path.exists(m3u_path):
            with open(m3u_path, "r", encoding="utf-8") as f:
                lines = f.read().strip().splitlines()
        else:
            lines = ["#EXTM3U"]

        # Güncelleme işlemi
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            match = re.match(r'#EXTINF:-1 tvg-id="(\d+)"', line)
            if match:
                tvg_id = match.group(1)
                if tvg_id in updated_channels:
                    ch = updated_channels[tvg_id]
                    new_lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}')
                    new_lines.append(ch["url"])
                    i += 2
                    continue
            new_lines.append(line)
            i += 1

        # Yeni kanallar eklensin
        mevcut_idler = set(re.findall(r'tvg-id="(\d+)"', "\n".join(new_lines)))
        for tvg_id, ch in updated_channels.items():
            if tvg_id not in mevcut_idler:
                new_lines.append(f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{ch["logo"]}" group-title="{ch["group"]}",{ch["name"]}')
                new_lines.append(ch["url"])

        with open(m3u_path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")

        print(f"📺 Güncellenmiş dosya kaydedildi! ({len(updated_channels)} kanal işlendi)")
        return True

    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


if __name__ == "__main__":
    get_canli_tv_m3u()
