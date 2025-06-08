import requests
from cloudscraper import CloudScraper
import re
import os

class RecTVUrlFetcher:
    def __init__(self):
        self.session = CloudScraper()

    def get_rectv_domain(self):
        try:
            response = self.session.post(
                url="https://firebaseremoteconfig.googleapis.com/v1/projects/791583031279/namespaces/firebase:fetch",
                headers={
                    "X-Goog-Api-Key": "AIzaSyBbhpzG8Ecohu9yArfCO5tF13BQLhjLahc",
                    "X-Android-Package": "com.rectv.shot",
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12)",
                },
                json={
                    "appBuild": "81",
                    "appInstanceId": "evON8ZdeSr-0wUYxf0qs68",
                    "appId": "1:791583031279:android:1",
                }
            )
            main_url = response.json().get("entries", {}).get("api_url", "")
            base_domain = main_url.replace("/api/", "")
            print(f"🟢 Güncel RecTV domain alındı: {base_domain}")
            return base_domain
        except Exception as e:
            print("🔴 RecTV domain alınamadı!")
            print(f"Hata: {type(e).__name__} - {e}")
            return None

def get_all_channels(base_domain):
    all_channels = []
    page = 0

    while True:
        url = f"{base_domain}/api/channel/by/filtres/0/0/{page}/4F5A9C3D9A86FA54EACEDDD635185/c3c5bd17-e37b-4b94-a944-8a3688a30452"
        print(f"🔍 İstek atılıyor: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ HTTP {response.status_code}")
            break

        data = response.json()
        if not data:
            print(f"✅ Veri bitti, {page} sayfa tarandı.")
            break

        all_channels.extend(data)
        page += 1

    return all_channels

def extract_m3u8_links(channels):
    playlist_lines = ['#EXTM3U']
    priority_order = ["Spor", "Haber", "Ulusal", "Sinema","Belgesel","Diğer", "Müzik"]
    grouped_channels = {}

    for channel in channels:
        title = channel.get("title", "Bilinmeyen")
        logo = channel.get("image", "")
        channel_id = str(channel.get("id", ""))
        categories = channel.get("categories", [])
        group_title = categories[0]["title"] if categories else "Diğer"
        sources = channel.get("sources", [])

        for source in sources:
            url = source.get("url")
            if url and url.endswith(".m3u8"):
                quality = source.get("quality")
                quality_str = f" [{quality}]" if quality and quality.lower() != "none" else ""
                entry = (
                    f'#EXTINF:-1 tvg-id="{channel_id}" tvg-logo="{logo}" tvg-name="{title}" group-title="{group_title}",{title}{quality_str}',
                    '#EXTVLCOPT:http-user-agent=okhttp/4.12.0',
                    '#EXTVLCOPT:http-referrer=https://twitter.com',
                    url
                )
                grouped_channels.setdefault(group_title, []).append(entry)

    for group in priority_order + sorted(set(grouped_channels.keys()) - set(priority_order)):
        entries = grouped_channels.get(group)
        if entries:
            sorted_entries = sorted(entries, key=lambda e: e[0].split(",")[-1].lower())
            for entry in sorted_entries:
                playlist_lines.extend(entry)

    return playlist_lines

def save_to_file(new_lines, filename="Kanallar/kerim.m3u"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            old_content = f.read().splitlines()
        old_channels = extract_entries(old_content)
        new_channels = extract_entries(new_lines)

        merged_channels = merge_channels(old_channels, new_channels)
        content = "#EXTM3U\n" + '\n'.join([item for entry in merged_channels for item in entry])
    else:
        content = '\n'.join(new_lines)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"💾 M3U dosyası güncellendi: {filename}")

# ------------------------ 🔽 Eklenen Yardımcı Fonksiyonlar 🔽 ------------------------

def extract_entries(lines):
    entries = []
    temp = []
    for line in lines:
        if line.startswith("#EXTINF:"):
            if temp:
                entries.append(tuple(temp))
                temp = []
            temp = [line]
        elif temp:
            temp.append(line)
    if temp:
        entries.append(tuple(temp))
    return entries

def get_id_from_info(info_line):
    m = re.search(r'tvg-id="([^"]+)"', info_line)
    return m.group(1) if m else None

def is_rectv_id(tvg_id):
    return tvg_id and re.fullmatch(r"\d+", tvg_id)

def merge_channels(old_channels, new_channels):
    old_dict = {}
    final_channels = []

    for ch in old_channels:
        ch_id = get_id_from_info(ch[0])
        if is_rectv_id(ch_id):
            old_dict[ch_id] = ch  # eski rectv yayınları
        else:
            final_channels.append(ch)  # diğer yayınları koru

    # RecTV yayınıysa güncelle
    for ch in new_channels:
        ch_id = get_id_from_info(ch[0])
        if is_rectv_id(ch_id):
            final_channels.append(ch)

    return final_channels

# ------------------------ 🔚 ------------------------

if __name__ == "__main__":
    fetcher = RecTVUrlFetcher()
    domain = fetcher.get_rectv_domain()

    if domain:
        kanallar = get_all_channels(domain)
        print(f"📺 Toplam {len(kanallar)} kanal bulundu.")
        m3u_lines = extract_m3u8_links(kanallar)
        save_to_file(m3u_lines)
    else:
        print("🚫 Geçerli domain alınamadı.")
