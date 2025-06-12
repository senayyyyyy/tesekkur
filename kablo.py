import requests
import json
import gzip
from io import BytesIO
import os
import re

KANAL_DOSYASI = "Kanallar/kerim.m3u"

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

def get_id_from_info(info_line):
    m = re.search(r'tvg-id="([^"]+)"', info_line)
    return m.group(1) if m else None

def get_source_from_id(tvg_id):
    if tvg_id:
        if tvg_id.startswith("rec_"):
            return "rec"
        elif tvg_id.startswith("canli_"):
            return "canli"
    return "other"

def merge_channels_by_source(old_entries, new_entries, source_prefix):
    new_dict = {
        get_id_from_info(entry[0]): entry
        for entry in new_entries
    }

    result = []
    for old in old_entries:
        tvg_id = get_id_from_info(old[0])
        src = get_source_from_id(tvg_id)
        if src == source_prefix and tvg_id in new_dict:
            result.append(new_dict[tvg_id])  # Güncellenmiş kanal
        elif src != source_prefix:
            result.append(old)  # Diğer kanal dokunulmaz
    return result

def update_m3u_file(source_name, new_entries):
    if os.path.exists(KANAL_DOSYASI):
        with open(KANAL_DOSYASI, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    else:
        lines = ["#EXTM3U"]

    old_entries = extract_entries(lines)
    updated_entries = merge_channels_by_source(old_entries, new_entries, source_name)

    with open(KANAL_DOSYASI, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for entry in updated_entries:
            f.write("\n".join(entry) + "\n")

def update_sadederecel_channels():
    try:
        print("🔁 SadedeReçel kanalları alınıyor...")
        url = "https://recel.id.tr/kanallar.json"
        response = requests.get(url, timeout=15)
        data = response.json()

        new_entries = []
        for i, kanal in enumerate(data, 1):
            if not kanal.get("url"):
                continue
            tvg_id = f"rec_{i}"
            logo = kanal.get("logo", "")
            group = kanal.get("kategori", "Genel")
            name = kanal.get("isim", "Bilinmeyen")
            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}'
            new_entries.append((extinf, kanal["url"]))

        update_m3u_file("rec", new_entries)
        print(f"✅ SadedeReçel kanalları güncellendi! ({len(new_entries)} kanal)")
    except Exception as e:
        print(f"❌ SadedeReçel güncelleme hatası: {e}")

def update_canlitv_channels():
    try:
        print("🔁 CanliTV kanalları alınıyor...")
        url = "https://core-api.kablowebtv.com/api/channels"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://tvheryerde.com",
            "Origin": "https://tvheryerde.com",
            "Accept-Encoding": "gzip",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey..."
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        try:
            with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
                content = gz.read().decode('utf-8')
        except:
            content = response.content.decode('utf-8')

        data = json.loads(content)
        channels = data['Data']['AllChannels']

        new_entries = []
        for i, ch in enumerate(channels, 1):
            stream = ch.get("StreamData", {})
            hls = stream.get("HlsStreamUrl")
            if not hls:
                continue
            name = ch.get("Name", "Bilinmeyen")
            logo = ch.get("PrimaryLogoImageUrl", "")
            group = ch.get("Categories", [{}])[0].get("Name", "Genel")
            if group == "Bilgilendirme":
                continue
            tvg_id = f"canli_{i}"
            extinf = f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}'
            new_entries.append((extinf, hls))

        update_m3u_file("canli", new_entries)
        print(f"✅ CanliTV kanalları güncellendi! ({len(new_entries)} kanal)")
    except Exception as e:
        print(f"❌ CanliTV güncelleme hatası: {e}")

if __name__ == "__main__":
    update_sadederecel_channels()
    update_canlitv_channels()
