import requests
import re

CHECK_URL = "https://main.uxsyplayer425b9907af.click/"
M3U_FILENAME = "selcuk.m3u"

def get_latest_dynamic_url():
    try:
        response = requests.get(CHECK_URL, timeout=10)
        if response.status_code == 200:
            # Sayfa metni içinde main.uxsyplayerXXXXX.click şeklinde geçen kısmı bul
            matches = re.findall(r"https://main\.(uxsyplayer[0-9a-f]+)\.click", response.text)
            if matches:
                dynamic_part = matches[0]
                return f"https://main.{dynamic_part}.click"
        print("Dinamik link bulunamadı.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

def extract_stream_ids(base_url):
    stream_ids = []
    for i in range(1, 100):
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
        print(f"{filename} güncellendi. {len(stream_ids)} kanal eklendi.")
    except Exception as e:
        print(f"M3U dosyası yazma hatası: {e}")

def main():
    print("Dinamik link aranıyor...")
    dynamic_base = get_latest_dynamic_url()
    if dynamic_base:
        print(f"Güncel yayın adresi bulundu: {dynamic_base}")
        stream_ids = extract_stream_ids(dynamic_base)
        if stream_ids:
            print(f"{len(stream_ids)} adet aktif yayın bulundu.")
            generate_m3u(stream_ids, dynamic_base, M3U_FILENAME)
        else:
            print("Yayın bulunamadı.")
    else:
        print("Güncel yayın adresi alınamadı.")

if __name__ == "__main__":
    main()
