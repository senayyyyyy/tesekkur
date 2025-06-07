import re
from httpx import Client
from Kekik.cli import konsol  # Yoksa print() ile değiştirilebilir

class UXSYPlayer:
    def __init__(self, m3u_dosyasi):
        self.m3u_dosyasi = m3u_dosyasi
        self.httpx = Client(timeout=10)

    def referer_domainini_al(self):
        desen = r'#EXTVLCOPT:http-referrer=(https?://[^/]*uxsyplayer[^/]*\.[^\s/]+)'
        with open(self.m3u_dosyasi, "r") as f:
            icerik = f.read()

        if eslesme := re.search(desen, icerik):
            return eslesme[1]
        raise ValueError("Referer içinde 'sporcafe' geçen bir domain bulunamadı!")

    def yayin_urlini_al(self):
        api_url = (
            "https://vavoo.vercel.app/api/stream.js?"
            "url=https://main.uxsyplayer425b9907af.click/index.php"
            "&referer=https://www.sporcafe6.xyz/"
            "&useragent=okhttp/4.12.0"
        )
        konsol.log(f"[cyan][~] API çağrısı yapılıyor: {api_url}")
        try:
            response = self.httpx.get(api_url)
            response.raise_for_status()
            json_data = response.json()
            baseurl = json_data["baseurl"].replace("\\/", "/").rstrip("/")
            return baseurl
        except Exception as e:
            raise ValueError(f"Base URL alınamadı: {e}")

    def m3u_guncelle(self):
        with open(self.m3u_dosyasi, "r", encoding="utf-8") as f:
            icerik = f.read()

        eski_referer = self.referer_domainini_al()
        konsol.log(f"[yellow][~] Eski Referer: {eski_referer}")

        yeni_baseurl = self.yayin_urlini_al()
        konsol.log(f"[green][+] Yeni BaseURL: {yeni_baseurl}")

        yayin_deseni = r'https?:\/\/[^\/]+\.(workers\.dev|shop|click|lat)\/?'
        if not (eski_yayin := re.search(yayin_deseni, icerik)):
            raise ValueError("M3U içinde eski yayın URL’si bulunamadı!")

        eski_yayin_url = eski_yayin[0]
        konsol.log(f"[yellow][~] Eski Yayın URL: {eski_yayin_url}")

        yeni_icerik = icerik.replace(eski_yayin_url, yeni_baseurl)
        yeni_icerik = yeni_icerik.replace(eski_referer, "https://main.uxsyplayer425b9907af.click")

        with open(self.m3u_dosyasi, "w", encoding="utf-8") as f:
            f.write(yeni_icerik)

        konsol.log(f"[green][✓] M3U dosyası başarıyla güncellendi.")

if __name__ == "__main__":
    guncelleyici = CAFE("selcuk.m3u")
    guncelleyici.m3u_guncelle()
