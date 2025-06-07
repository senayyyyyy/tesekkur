import requests
import re

BASE_DOMAIN = "https://www.sporcafe{}.xyz/"
MAX_INDEX = 10  # 1-1000 arası denenecek
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

def extract_stream_ids(base_url):
    stream_ids = []
    for i in range(1, 100):  # 1-100 arası dene
        url = f"{base_url}/index.php?id={i}"
        try:
            r = requests.head(url, allow_redirects=True, timeout=3)
            if r.status_code == 200:
                stream_ids.append(i)
        except:
            continue
    return stream_ids

def generate_m3u(stream_ids, base_url, filename):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write("#EXTM3U\n")
            for i in stream_ids:
                file.write(f"#EXTINF:-1,Channel {i}\n")
                file.write(f"{base_url}/index.php?id={i}\n")
        print(f"{filename} dosyası güncellendi. {len(stream_ids)} kanal eklendi.")
    except Exception as e:
        print(f"M3U dosyası yazma hatası: {e}")

def main():
    print("Dinamik linkler aranıyor...")
    links = get_all_dynamic_links()
    if links:
        print(f"Toplam {len(links)} farklı base link bulundu.")
        for base_link in links:
            print(f"\nBase link: {base_link}")
            stream_ids = extract_stream_ids(base_link)
            if stream_ids:
                print(f"{len(stream_ids)} adet aktif yayın bulundu.")
                # Her base_link için ayrı dosya oluşturabilirsin
                filename = f"iptv_list_{base_link.split('.')[1]}.m3u"
                generate_m3u(stream_ids, base_link, filename)
            else:
                print("Yayın bulunamadı.")
    else:
        print("Hiç link bulunamadı.")

if __name__ == "__main__":
    main()
