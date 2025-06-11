import requests

# Birleştirmek istediğin M3U dosyalarının URL'leri
m3u_urls = [
    "https://raw.githubusercontent.com/kadirsener1/CanliTvListe/refs/heads/main/yeni.m3u",
    "https://raw.githubusercontent.com/kadirsener1/CanliTvListe/refs/heads/main/rectv.m3u",
    "https://raw.githubusercontent.com/kadirsener1/CanliTvListe/refs/heads/main/trgoals.m3u",
    "https://raw.githubusercontent.com/kadirsener1/CanliTvListe/refs/heads/main/daddylive.m3u"
]

# Çıktı dosyası adı
output_file = "sentv.m3u"

# M3U başlığı
merged_content = "#EXTM3U\n"

for url in m3u_urls:
    try:
        print(f"İndiriliyor: {url}")
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        # Başlık satırını (eğer varsa) çıkarıyoruz
        if content.startswith("#EXTM3U"):
            content = content.split("\n", 1)[1]

        merged_content += content.strip() + "\n"

    except Exception as e:
        print(f"Hata oluştu: {url}\n{e}")

# Birleştirilmiş içeriği dosyaya yaz
with open(output_file, "w", encoding="utf-8") as f:
    f.write(merged_content)

print(f"\nBirleştirme tamamlandı: {output_file}")
