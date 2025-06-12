import requests
import json
import gzip
import os
import re
from io import BytesIO

def get_canli_tv_m3u():
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer <TOKEN>"  # Token'ı kendi değerinizle değiştirin
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
            print("❌ CanliTV API'den geçerli veri alınamadı!")
            return False

        channels = data['Data']['AllChannels']
        print(f"✅ {len(channels)} kanal bulundu")

        # Yeni CanliTV kanallarını oluştur
        new_channels = []
        kanal_index = 1000
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
            entry = (
                f'#EXTINF:-1 tvg-id="{tvg_id}" tvg-logo="{logo}" group-title="{group}",{name}',
                hls_url
            )
            new_channels.append(entry)
            kanal_index += 1

        # Var olan m3u dosyasını oku
        filename = "Kanallar/kerim.m3u"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        else:
            lines = ["#EXTM3U"]

        old_entries = extract_entries(lines)
        updated = merge_channels_keep_order(old_entries, new_channels)
        with open(filename, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for entry in updated:
                f.write("\n".join(entry) + "\n")

        print(f"📺 Kanallar/kerim.m3u dosyası güncellendi! ({len(new_channels)} CanliTV kanalı)")
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

def get_id_from_info(info_line):
    m = re.search(r'tvg-id="([^"]+)"', info_line)
    return m.group(1) if m else None

def is_canlitv_id(tvg_id):
    return tvg_id and tvg_id.isdigit()

def merge_channels_keep_order(old_channels, new_channels):
    new_dict = {
        get_id_from_info(ch[0]): ch for ch in new_channels
        if is_canlitv_id(get_id_from_info(ch[0]))
    }

    final_channels = []
    for old in old_channels:
        ch_id = get_id_from_info(old[0])
        if is_canlitv_id(ch_id) and ch_id in new_dict:
            final_channels.append(new_dict[ch_id])  # Güncellenmiş CanliTV kanalı
        else:
            final_channels.append(old)  # Diğer kanal

    return final_channels

if __name__ == "__main__":
    get_canli_tv_m3u()
