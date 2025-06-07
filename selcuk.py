import requests
import re

def find_working_sporcafe(start=5, end=8):
    print("🧭 Sporcafe domainleri taranıyor...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for i in range(start, end + 1):
        url = f"https://www.sporcafe{i}.xyz/"
        print(f"🔍 Sporcafe taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200 and "uxsyplayer" in response.text:
                print(f"✅ Aktif domain bulundu: {url}")
                return response.text, url
        except requests.RequestException:
            print(f"⚠️ Erişim hatası, geçiliyor: {url}")

    print("❌ Aktif Sporcafe domaini bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    # iframe veya direkt bağlantıdan yayın domainini çek
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    if match:
        return f"https://{match.group(1)}"
    return None

def fetch_m3u8_links(base_url, channel_ids, referer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }
    m3u8_links = []

    for cid in channel_ids:
        url = f"{base_url}/index.php?id={cid}"
        print(f"🎥 Yayın kontrol ediliyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            match = re.search(r'(https?://[^"\']+\.m3u8)', response.text)
            if match:
                print(f"✅ M3U8 bulundu: {match.group(1)}")
                m3u8_links.append((cid, match.group(1)))
            else:
                print(f"❌ M3U8 bulunamadı: {url}")
        except:
            print(f"⚠️ Hata oluştu: {url}")
    
    return m3u8_links

def write_m3u_file(m3u8_links, filename="selcuk1.m3u"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in m3u8_links:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"\n💾 M3U dosyası oluşturuldu: {filename}")

# 🔧 Ayarlar
channel_ids = [
    "sbeinsports-1",
    "sbeinsports-2",
    "sbeinsports-3",
    "sbeinsports-4",
    "sbeinsports-5"
]

# ▶️ Ana işlem akışı
html, referer_url = find_working_sporcafe()
if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın adresi bulundu: {stream_domain}")
        m3u8_list = fetch_m3u8_links(stream_domain, channel_ids, referer_url)
        if m3u8_list:
            write_m3u_file(m3u8_list)
        else:
            print("❌ Hiçbir M3U8 yayını bulunamadı.")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Yayın alınacak site bulunamadı.")
