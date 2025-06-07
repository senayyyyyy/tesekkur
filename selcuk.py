import requests
import re

def find_working_sporcafe(start=1825, end=1850):
    print("🧭 Sporcafe domainleri taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}
    for i in range(start, end + 1):
        url = f"https://www.selcuksportshd{i}.xyz/"
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
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    if match:
        return f"https://{match.group(1)}"
    return None

def extract_stream_url(html):
    # baseStreamUrl veya adsBaseUrl yakala
    match = re.search(r'this\.(baseStreamUrl|adsBaseUrl)\s*=\s*"([^"]+)"', html)
    if match:
        return match.group(2)
    return None

def fetch_m3u8_links(base_url, channel_ids, referer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }
    m3u8_links = []
    for cid in channel_ids:
        url = f"{base_url}/index.php?id={cid}"
        print(f"🎥 Yayın sayfası inceleniyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            html = response.text
            stream_url = extract_stream_url(html)
            if stream_url:
                full_m3u8 = f"{stream_url}/live/{cid}/playlist.m3u8"
                print(f"✅ M3U8 linki oluşturuldu: {full_m3u8}")
                m3u8_links.append((cid, full_m3u8))
            else:
                print(f"❌ Yayın stream adresi bulunamadı: {cid}")
        except Exception as e:
            print(f"⚠️ Hata oluştu ({cid}): {e}")
    return m3u8_links

def write_m3u_file(m3u8_links, filename="selcuk.m3u"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for name, url in m3u8_links:
            f.write(f"#EXTINF:-1,{name}\n{url}\n")
    print(f"\n💾 M3U dosyası oluşturuldu: {filename}")

# 🔧 Ayarlar
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

# ▶️ Ana işlem
html, referer_url = find_working_sporcafe()
if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın domaini bulundu: {stream_domain}")
        m3u8_list = fetch_m3u8_links(stream_domain, channel_ids, referer_url)
        if m3u8_list:
            write_m3u_file(m3u8_list)
        else:
            print("❌ Hiçbir yayın bağlantısı bulunamadı.")
    else:
        print("❌ Yayın domaini çözümlenemedi.")
else:
    print("⛔ Uygun yayın sayfası bulunamadı.")
