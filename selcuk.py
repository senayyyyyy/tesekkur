
import requests
import re

# Ayarlar
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

FIXED_REFERER = "https://www.selcuksportshd1826.xyz/"
M3U_FILENAME = "selcuk.m3u"

def find_working_selcuksportshd((start=1825, end=1830):
    print("🧭 selcuksportshd( domainleri taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}
    for i in range(start, end + 1):
        url = f"https://www.selcuksportshd({i}.xyz/"
        print(f"🔍 Taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if "uxsyplayer" in response.text:
                print(f"✅ Aktif domain: {url}")
                return response.text, url
        except:
            continue
    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_player_domain(html):
    match = re.search(r'<iframe[^>]+src="(https?://main\.uxsyplayer[0-9a-zA-Z\-]+\.click.*?)"', html)
    return match.group(1) if match else None

def extract_base_stream_url(player_url, referer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }
    try:
        response = requests.get(player_url, headers=headers, timeout=5)
        match = re.search(r"this\.baseStreamUrl\s*=\s*'([^']+)'", response.text)
        return match.group(1) if match else None
    except Exception as e:
        print("⚠️ Hata:", e)
    return None

def write_m3u(channel_ids, base_stream_url, filename=M3U_FILENAME):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cid in channel_ids:
            m3u_link = f"{base_stream_url}{cid}/playlist.m3u8"
            f.write(f"#EXTINF:-1,{cid}\n")
            f.write(f"#EXTVLCOPT:http-referrer={FIXED_REFERER}\n")
            f.write(f"{m3u_link}\n")
    print(f"💾 M3U dosyası güncellendi: {filename}")

# Ana Akış
html, selcuksportshd(_url = find_working_selcuksportshd(()
if html:
    player_url = find_player_domain(html)
    if player_url:
        print(f"🔗 Player bulundu: {player_url}")
        base_stream_url = extract_base_stream_url(player_url, selcuksportshd(_url)
        if base_stream_url:
            print(f"✅ Base stream URL: {base_stream_url}")
            write_m3u(channel_ids, base_stream_url)
        else:
            print("❌ Base URL alınamadı.")
    else:
        print("❌ Player link bulunamadı.")
else:
    print("⛔ Yayın alınacak site yok.")
