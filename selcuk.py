import requests
import re
import os

def find_working_selcuksportshd(start=1825, end=1850):
    print("🧭 Selcuksportshd domainleri taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}
    for i in range(start, end + 1):
        url = f"https://www.selcuksportshd{i}.xyz/"
        print(f"🔍 Taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200 and "uxsyplayer" in response.text:
                print(f"✅ Aktif domain bulundu: {url}")
                return response.text, url
        except:
            print(f"⚠️ Hata: {url}")
    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    return f"https://{match.group(1)}" if match else None

def extract_base_stream_url(html):
    match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', html)
    return match.group(1) if match else None

def build_m3u8_links(base_stream_url, channel_ids):
    return [(cid, f"{base_stream_url}{cid}/playlist.m3u8") for cid in channel_ids]

def write_m3u_file(m3u8_links, filename="5.m3u", referer=""):
    existing_extinf = {}

    # Mevcut dosyadaki EXTINF satırlarını koru
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF:-1"):
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith("#EXTVLCOPT") or next_line.startswith("http"):
                        channel_url = next_line if next_line.startswith("http") else lines[i + 2].strip()
                        channel_id = channel_url.split("/")[-2] if "/playlist.m3u8" in channel_url else None
                        if channel_id:
                            existing_extinf[channel_id] = lines[i]

    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cid, url in m3u8_links:
            extinf_line = existing_extinf.get(cid, f"#EXTINF:-1,{cid}\n")
            f.write(extinf_line)
            f.write("#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5)\n")
            f.write(f"#EXTVLCOPT:http-referrer={referer}\n")
            f.write(f"{url}\n")
    print(f"💾 M3U dosyası güncellendi: {filename}")

# Kanal ID listesi
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

# Ana işlem
html, referer_url = find_working_selcuksportshd()
if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        try:
            player_page = requests.get(f"{stream_domain}/index.php?id={channel_ids[0]}", headers={
                "User-Agent": "Mozilla/5.0", "Referer": referer_url
            })
            base_stream_url = extract_base_stream_url(player_page.text)
            if base_stream_url:
                print(f"📡 baseStreamUrl bulundu: {base_stream_url}")
                m3u8_list = build_m3u8_links(base_stream_url, channel_ids)
                write_m3u_file(m3u8_list, referer=referer_url)
            else:
                print("❌ baseStreamUrl bulunamadı.")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Aktif yayın alınamadı.")
