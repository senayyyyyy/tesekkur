import requests
import re

def find_working_selcuksportshd(start=1825, end=1830):
    print("🧭 selcuksportshd domainleri taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}

    for i in range(start, end + 1):
        url = f"https://www.selcuksportshd{i}.xyz/"
        print(f"🔍 selcuksportshd taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if "uxsyplayer" in response.text:
                print(f"✅ Aktif domain bulundu: {url}")
                return response.text, url
        except:
            continue
    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_player_domain(html):
    match = re.search(r'<iframe[^>]+src="(https?://main\.uxsyplayer[0-9a-zA-Z\-]+\.click.*?)"', html)
    if match:
        return match.group(1)
    return None

def extract_base_stream_url(player_url, referer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }
    try:
        response = requests.get(player_url, headers=headers, timeout=5)
        match = re.search(r"this\.baseStreamUrl\s*=\s*'([^']+)'", response.text)
        if match:
            return match.group(1)
    except Exception as e:
        print("⚠️ Hata:", e)
    return None

def write_m3u(channel_ids, base_stream_url, filename="selcuk.m3u"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cid in channel_ids:
            full_url = f"{base_stream_url}{cid}/playlist.m3u8"
            f.write(f"#EXTINF:-1,{cid}\n{full_url}\n")
    print(f"💾 M3U dosyası yazıldı: {filename}")

# 🔧 Ayarlar
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

# ▶️ Ana işlem
html, referer = find_working_selcuksportshd()
if html:
    player_url = find_player_domain(html)
    if player_url:
        print(f"🔗 Player URL bulundu: {player_url}")
        base_stream = extract_base_stream_url(player_url, referer)
        if base_stream:
            print(f"✅ Yayın Base URL: {base_stream}")
            write_m3u(channel_ids, base_stream)
        else:
            print("❌ Base stream URL bulunamadı.")
    else:
        print("❌ Player domaini bulunamadı.")
else:
    print("⛔ selcuksportshd aktif değil.")
