import requests
import json
import gzip
from io import BytesIO
import os
import re

def parse_m3u(filepath):
    if not os.path.exists(filepath):
        return {}

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    entries = re.split(r'#EXTINF:-1', content)[1:]
    kanal_dict = {}

    for entry in entries:
        lines = entry.strip().splitlines()
        if len(lines) >= 2:
            info = lines[0]
            url = lines[1]
            name_match = re.search(r',(.+)', info)
            name = name_match.group(1).strip() if name_match else "Unknown"
            kanal_dict[name] = (info, url)

    return kanal_dict

def get_canli_tv_m3u():
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Kısaltıldı
    }

    m3u_path = "1.m3u"

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
        channels = data.get('Data', {}).get('AllChannels', [])
        if not channels:
            print("❌ API'den kanal verisi alınamadı.")
            return False

        # Mevcut M3U içeriğini oku
        existing_channels = parse_m3u(m3u_path)

        # Güncellenecek kanallar
        updated_channels = {}

        kanal_index = 1000
        for channel in channels:
            name = channel.get('Name')
            stream_data = channel.get('StreamData', {})
            hls_url = stream_data.get('HlsStreamUrl')
            logo = channel.get('PrimaryLogoImageUrl', '')
            categories = channel.get('Categories', [])
            group = categories[0].get('Name', 'Genel') if categories else 'Genel'

            if not name or not hls_url or group == "Bilgilendirme":
                continue

            tvg_id = str(kanal_index)
            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}'
            updated_channels[name] = (extinf, hls_url)
            kanal_index += 1

        # Güncellemeleri uygula
        final_channels = existing_channels.copy()
        final_channels.update(updated_channels)  # Aynı isim varsa günceller

        # M3U dosyasını yaz
        with open(m3u_path, "w", encoding="utf-8-sig") as f:
            f.write("#EXTM3U\n")
            for name, (info, url) in final_channels.items():
                f.write(f"{info}\n{url}\n")

        print(f"✅ Güncellendi: {len(updated_channels)} kanal güncellendi, toplam {len(final_channels)} kanal.")
        return True

    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False

if __name__ == "__main__":
    get_canli_tv_m3u()
