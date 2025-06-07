import requests
import re

# Tarayacağımız ana domainlerin formatı
SPORCAFE_BASE = "https://www.sporcafe{}.xyz/"
MAX_SPORCAFE = 10  # Kaç tane sporcafe adresi denensin

# Yayın ID'leri
CHANNEL_IDS = [
    "sbeinsports-1",
    "sbeinsports-2",
    "sbeinsports-3",
    "sbeinsports-4",
    "sbeinsports-5"
]

OUTPUT_FILE = "selcuk.m3u"

def find_working_sporcafe():
    for i in range(1, MAX_SPORCAFE + 1):
        url = SPORCAFE_BASE.format(i)
        try:
            print(f"🔍 Sporcafe taranıyor: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except:
            continue
    return None

def find_dynamic_player_domain(page_html):
    matches = re.findall(r'https://main\.uxsyplayer[0-9a-f]+\.click', page_html)
    if matches:
        return matches[0]
    return None

def get_m3u8_from_page(full_url):
    try:
        r = requests.get(full_url, timeout=5)
        if r.status_code == 200:
            matches = re.findall(r'(https?://[^\s"\']+\.m3u8)', r.text)
            if matches:
                return matches[0]
    except:
        pass
    return None

def create_m3u_file(base_stream_url, channel_ids, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for cid in channel_ids:
            full_url = f"{base_stream_url}/index.php?id={cid}"
            print(f"🎯 Yayın kontrol ediliyor: {cid}")
            m3u8_link = get_m3u8_from_page(full_url)
            if m3u8_link:
                f.write(f"#EXTINF:-1,{cid}\n{m3u8_link}\n")
                print(f"✅ Yayın eklendi: {m3u8_link}")
            else:
                print(f"❌ Yayın bulunamadı: {cid}")
    print(f"\n📁 M3U dosyası hazır: {output_file}")

def main():
    print("🧭 Sporcafe domainleri taranıyor...")
    html = find_working_sporcafe()

    if not html:
        print("❌ Hiçbir sporcafe adresi erişilebilir değil.")
        return

    print("🔍 Yayın domaini aranıyor...")
    base_stream_url = find_dynamic_player_domain(html)

    if not base_stream_url:
        print("❌ Yayın domaini bulunamadı.")
        return

    print(f"📡 Yayın domaini bulundu: {base_stream_url}")
    create_m3u_file(base_stream_url, CHANNEL_IDS, OUTPUT_FILE)

if __name__ == "__main__":
    main()
