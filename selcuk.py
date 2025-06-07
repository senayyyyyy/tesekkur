import requests
import re

def find_working_selcuksportshd(start=1825, end=1830):
    print("🧭 Sporcafe domainleri taranıyor...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

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
    # baseStreamUrl veya adsBaseUrl değerini çek
    match = re.search(r"this\.(?:baseStreamUrl|adsBaseUrl)\s*=\s*'([^']+)'", page_html)
    if match:
        return match.group(1)
    return None

def fetch_m3u8_links(base_url, channel_ids):
    # base_url sonu '/' ile biter zaten, onu kullanarak link oluşturacağız
    m3u8_links = []

    for cid in channel_ids:
        # Örnek: https://alpha.cf-worker-xxxx.workers.dev/live/ + selcukbeinsports1 + /playlist.m3u8
        full_url = f"{base_url}{cid}/playlist.m3u8"
        print(f"🎥 Yayın kontrol ediliyor: {full_url}")
        try:
            response = requests.head(full_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ M3U8 erişilebilir: {full_url}")
                m3u8_links.append((cid, full_url))
            else:
                print(f"❌ M3U8 erişilemiyor: {full_url} (Status: {response.status_code})")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {full_url} ({e})")

    return m3u8_links

def update_m3u_file_with_referer_and_links(m3u8_links, filename="5.m3u", referer=""):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = ["#EXTM3U\n"]

    updated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:-1"):
            updated_lines.append(line)  # #EXTINF:-1, kanal ismi
            i += 1
            # Önceki URL ve Referer satırlarını atla
            while i < len(lines) and (lines[i].startswith("http") or lines[i].startswith("# Referer:")):
                i += 1

            kanal_adi = line.strip().split(',', 1)[1].strip()
            url_to_write = None
            for cid, url in m3u8_links:
                if cid.lower() in kanal_adi.lower():
                    url_to_write = url
                    break

            if url_to_write:
                updated_lines.append(f"# Referer: {referer}\n")
                updated_lines.append(f"{url_to_write}\n")
            else:
                # Eğer link yoksa boş satır bırak
                updated_lines.append("\n")
        else:
            updated_lines.append(line)
            i += 1

    # Yeni kanalları ekle
    existing_channels = [l for l in updated_lines if l.startswith("#EXTINF:-1")]
    for cid, url in m3u8_links:
        if not any(cid.lower() in l.lower() for l in existing_channels):
            updated_lines.append(f"#EXTINF:-1,{cid}\n")
            updated_lines.append(f"# Referer: {referer}\n")
            updated_lines.append(f"{url}\n")

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"\n💾 M3U dosyası güncellendi: {filename}")

if __name__ == "__main__":
    # Kanal ID'leri
    channel_ids = [
        "selcukbeinsports1",
        "selcukbeinsports2",
        "selcukbeinsports3",
        "selcukbeinsports4",
        "selcukbeinsports5"
    ]

    # 1- Aktif sporcafe domaini bul
    html, referer_url = find_working_selcuksportshd()
    if html:
        # 2- Yayın base URL'sini bul
        base_url = find_dynamic_player_domain(html)
        if base_url:
            print(f"\n🔗 Yayın base URL bulundu: {base_url}")

            # 3- M3U8 linklerini oluştur ve kontrol et
            m3u8_list = fetch_m3u8_links(base_url, channel_ids)

            if m3u8_list:
                # 4- M3U dosyasını referer ile güncelle
                update_m3u_file_with_referer_and_links(m3u8_list, filename="5.m3u", referer=referer_url)
            else:
                print("❌ Hiçbir M3U8 yayını bulunamadı.")
        else:
            print("❌ Yayın base URL bulunamadı.")
    else:
        print("⛔ Aktif sporcafe sitesi bulunamadı.")
