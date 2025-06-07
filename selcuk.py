import re
from httpx import Client
from Kekik.cli import konsol as log 

# Ana domain (subdomain kısmı dinamik)
BASE_DOMAIN = "https://main."
DOMAIN_SUFFIX = ".click"

# Ana sayfayı kontrol edeceğin URL
CHECK_URL = "https://main.uxsyplayer425b9907af.click/"  # Eski bir örnek

# M3U dosyasına yazılacak dosya adı
M3U_FILENAME = "selcuk.m3u"

def get_latest_dynamic_url():
    try:
        response = requests.get(CHECK_URL, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup.find_all('script'):
                if script.string:
                    matches = re.findall(r"https://main\.(uxsyplayer[0-9a-f]+)\.click", script.string)
                    if matches:
                        dynamic_part = matches[0]
                        return f"https://main.{dynamic_part}.click"
        print("Dinamik link bulunamadı.")
    except Exception as e:
        print(f"Hata oluştu: {e}")
    return None

def extract_stream_ids(base_url):
    try:
        stream_ids = []
        for i in range(1, 100):  # Örneğin 1'den 100'e kadar id'leri dene
            url = f"{base_url}/index.php?id={i}"
            r = requests.head(url, allow_redirects=True, timeout=5)
            if r.status_code == 200:
                stream_ids.append(i)
        return stream_ids
    except Exception as e:
        print(f"Stream ID alma hatası: {e}")
        return []

def generate_m3u(stream_ids, base_url, filename):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        for i in stream_ids:
            file.write(f"#EXTINF:-1,Channel {i}\n")
            file.write(f"{base_url}/index.php?id={i}\n")
    print(f"{filename} dosyası başarıyla oluşturuldu.")

# Ana akış
dynamic_base = get_latest_dynamic_url()
if dynamic_base:
    print(f"Güncel URL bulundu: {dynamic_base}")
    ids = extract_stream_ids(dynamic_base)
    print(f"{len(ids)} adet yayın bulundu.")
    generate_m3u(ids, dynamic_base, M3U_FILENAME)
else:
    print("Güncel link alınamadı.")
