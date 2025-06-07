import requests
import re

BASE_DOMAIN = "https://www.sporcafe{}.xyz/"
MAX_INDEX = 20  # Kaç sporcafe sayfası taransın
M3U_FILENAME = "selcuk.m3u"

def get_all_dynamic_links():
    found_links = set()
    for i in range(1, MAX_INDEX + 1):
        url = BASE_DOMAIN.format(i)
        print(f"Site taranıyor: {url}")
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                matches = re.findall(r"https://main\.uxsyplayer[0-9a-f]+\.click", r.text)
                for m in matches:
                    found_links.add(m)
            else:
                print(f"Siteye erişilemedi: {url} (Status: {r.status_code})")
        except Exception as e:
            print(f"Hata {url} için: {e}")
    return list(found_links)

def extract_m3u8_links(base_url):
    m3u8_links = []
    for i in range(1, 100):  # id=1..99 dene
        full_url = f"{base_url}/index.php?id={i}"
        try:
            r = requests.get(full_url, timeout=5)
            if r.status_code == 200:
                # m3u8 linklerini ara (iframe, source, script, text içinde olabilir)
                matches = re.findall(r'(https?://[^\s"\']+\.m3u8)', r.text)
                if matches:
                    for link in matches:
                        m3u8_links.append((f"Channel {i}", link))
                        print(f"✅ Bulundu: {link}")
        except Exception as e:
            continue
    return m3u8_links

def generate_m3u(playlist, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            for name, link in playlist:
                file.write(f"#EXTINF:-1,{name}\n")
                file.write(f"{link}\n")
        print(f"\n{filename} dosyası başarıyla oluşturuldu. Toplam {len(playlist)} yayın eklendi.")
    except Exception as e:
        print(f"M3U yazma hatası: {e}")

def main():
    print("🔍 Dinamik linkler aranıyor...")
    links = get_all_dynamic_links()
    all_streams = []

    if links:
        print(f"\nToplam {len(links)} yayın sunucusu bulundu.\n")
        for base_link in links:
            print(f"\n🎯 Yayın sunucusu: {base_link}")
            streams = extract_m3u8_links(base_link)
            all_streams.extend(streams)
    else:
        print("⚠️ Hiç yayın sunucusu bulunamadı.")
        return

    if all_streams:
        generate_m3u(all_streams, M3U_FILENAME)
    else:
        print("⚠️ Hiç yayın linki bulunamadı.")

if __name__ == "__main__":
    main()
