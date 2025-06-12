import requests
import json
import gzip
import os
import re
from io import BytesIO

def get_canli_tv_m3u():
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer <TOKEN>"  # GÜNCEL token ile değiştir
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
        print(f"✅ {len(channels)} CanliTV kanalı bulundu")

        new_channels = {}
        kanal_index = 1
        for channel in channels:
            name = channel.get('Name')
            stream_data = channel.get('StreamData', {})
            hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
            logo = channel.get('PrimaryLogoImageUrl', '')
            categories = channel.get('Categories', [])
            if not name or not hls_url:
                continue
            group = categories[0].get('Name', 'Genel') if categories else 'Genel'
            if group == "Bilgilendirme":
                continue
            tvg_id = str(kanal_index)
            new_channels[name.strip().lower()] = (
                f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}',
                hls_url
            )
            kanal_index += 1

        # Var olan dosya
        filename = "Kanallar/kerim.m3u"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        else:
            lines = ["#EXTM3U"]

        old_entries = extract_entries(lines)
        updated = merge_by_name(old_entries, new_channels)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for entry in updated:
                f.write("\n".join(entry) + "\n")

        print(f"📺 Dosya güncellendi: {filename} ({len(new_channels)} kanal güncellendi)")
        return True

    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def extract_entries(lines):
    entries = []
    temp = []
    for line in lines:
        if line.startswith("#EXTINF:"):
            if temp:
                entries.append(tuple(temp))
            temp = [line]
        elif line.strip() and temp:
            temp.append(line)
    if temp:
        entries.append(tuple(temp))
    return entries

def get_channel_name(info_line):
    m = re.search(r',(.+)$', info_line)
    return m.group(1).strip() if m else None

def merge_by_name(old_entries, new_dict):
    result = []
    for entry in old_entries:
        name = get_channel_name(entry[0]).lower()
        if name in new_dict:
            result.append(new_dict[name])
        else:
            result.append(entry)
    return result

if __name__ == "__main__":
    get_canli_tv_m3u()
