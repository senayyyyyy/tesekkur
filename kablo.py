import requests
import json
import gzip
from io import BytesIO
import os

def merge_channels(old_channels, new_channels):
    new_dict = {ch[0]: ch for ch in new_channels}
    merged = []

    existing_names = set()

    # Önce eski kanallar üzerinden geçiyoruz
    for old_ch in old_channels:
        name = old_ch[0]
        if name in new_dict:
            merged.append(new_dict[name])  # Güncellenmiş kanal
            existing_names.add(name)
        else:
            merged.append(old_ch)  # Eski haliyle kalıyor

    # Sonra yeni listede olup eskide olmayanları ekliyoruz
    for name, ch in new_dict.items():
        if name not in existing_names:
            merged.append(ch)

    return merged

def get_canli_tv_m3u():
    url = "https://core-api.kablowebtv.com/api/channels"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://tvheryerde.com",
        "Origin": "https://tvheryerde.com",
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJMSVZFIiwiaXBiIjoiMCIsImNnZCI6IjA5M2Q3MjBhLTUwMmMtNDFlZC1hODBmLTJiODE2OTg0ZmI5NSIsImNzaCI6IlRSS1NUIiwiZGN0IjoiM0VGNzUiLCJkaSI6ImE2OTliODNmLTgyNmItNGQ5OS05MzYxLWM4YTMxMzIxOGQ0NiIsInNnZCI6Ijg5NzQxZmVjLTFkMzMtNGMwMC1hZmNkLTNmZGFmZTBiNmEyZCIsInNwZ2QiOiIxNTJiZDUzOS02MjIwLTQ0MjctYTkxNS1iZjRiZDA2OGQ3ZTgiLCJpY2giOiIwIiwiaWRtIjoiMCIsImlhIjoiOjpmZmZmOjEwLjAuMC4yMDYiLCJhcHYiOiIxLjAuMCIsImFibiI6IjEwMDAiLCJuYmYiOjE3NDUxNTI4MjUsImV4cCI6MTc0NTE1Mjg4NSwiaWF0IjoxNzQ1MTUyODI1fQ.OSlafRMxef4EjHG5t6TqfAQC7y05IiQjwwgf6yMUS9E"  # Token'ı kendi sistemine göre doldur
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

        new_channels = []
        kanal_index = 1
        for channel in channels:
            name = channel.get('Name')
            stream_data = channel.get('StreamData', {})
            hls_url = stream_data.get('HlsStreamUrl') if stream_data else None
            logo = channel.get('PrimaryLogoImageUrl', '')
            categories = channel.get('Categories', [])
            group = categories[0].get('Name', 'Genel') if categories else 'Genel'

            if not name or not hls_url or group == "Bilgilendirme":
                continue

            new_channels.append([name, hls_url, logo, group])
            kanal_index += 1

        old_channels = []
        if os.path.exists("1.m3u"):
            with open("1.m3u", "r", encoding="utf-8") as f:
                lines = f.readlines()
                for i in range(0, len(lines), 2):
                    if lines[i].startswith("#EXTINF"):
                        name_line = lines[i].strip()
                        name = name_line.split(",")[-1]
                        url = lines[i+1].strip()
                        logo = ""
                        group = "Genel"
                        try:
                            logo = name_line.split('tvg-logo="')[1].split('"')[0]
                        except: pass
                        try:
                            group = name_line.split('group-title="')[1].split('"')[0]
                        except: pass
                        old_channels.append([name, url, logo, group])

        # 🔁 Sadece burada birleştirme yapılıyor
        final_channels = merge_channels(old_channels, new_channels)

        with open("1.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            for idx, ch in enumerate(final_channels, 1):
                name, url, logo, group = ch
                f.write(f'#EXTINF:-1 tvg-id="{idx}" tvg-logo="{logo}" group-title="{group}",{name}\n')
                f.write(f'{url}\n')

        print(f"📺 1.m3u dosyası oluşturuldu! ({len(final_channels)} kanal)")
        return True

    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

if __name__ == "__main__":
    get_canli_tv_m3u()
