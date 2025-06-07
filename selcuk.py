import re
import requests
from parsel import Selector

class SporCafe6Updater:
    def __init__(self, m3u_dosyasi, site_url="https://www.sporcafe6.xyz"):
        self.m3u_dosyasi = m3u_dosyasi
        self.site_url = site_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

    def sayfa_icerigini_getir(self, path="/"):
        url = f"{self.site_url}{path}"
        print(f"[i] GET {url}")
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text

    def yayin_linklerini_al(self, html):
        sel = Selector(html)
        links = set()

        for iframe in sel.xpath("//iframe"):
            src = iframe.attrib.get("src")
            if src and src.startswith("http"):
                links.add(src)

        for source in sel.xpath("//video/source"):
            src = source.attrib.get("src")
            if src:
                links.add(src)

        for a in sel.xpath("//a"):
            href = a.attrib.get("href")
            if href and (".m3u" in href or ".m3u8" in href):
                full = href if href.startswith("http") else self.site_url + href
                links.add(full)

        return links

    def m3u_guncelle(self, paths=None):
        if paths is None:
            paths = ["/"]

        # Mevcut içerik
        with open(self.m3u_dosyasi, "r", encoding="utf-8") as f:
            m3u_icerik = f.read()

        # Tüm yeni yayın linkleri
        yeni_linkler = set()
        for p in paths:
            html = self.sayfa_icerigini_getir(p)
            alinan = self.yayin_linklerini_al(html)
            print(f"[+] {p} → {len(alinan)} yayın bulundu.")
            yeni_linkler |= alinan

        if not yeni_linkler:
            print("[!] Hiç yayın linki bulunamadı, çıkılıyor.")
            return

        # Her link ile m3u içinde var mı kontrol: yoksa referer satırıyla ekle
        mevcut = set(re.findall(r'#EXTVLCOPT:http-referrer=(https?://[^\s]+)\s*\n([^\n\r]+)', m3u_icerik))
        for ref, old_link in mevcut:
            yeni_linkler.discard(old_link)

        ekleme_satiri = ""
        for link in yeni_linkler:
            ekleme_satiri += f"#EXTVLCOPT:http-referrer={self.site_url}\n{link}\n"
            print(f"[+] Eklenecek: {link}")

        if ekleme_satiri:
            with open(self.m3u_dosyasi, "a", encoding="utf-8") as f:
                f.write("\n" + ekleme_satiri)
            print(f"[✓] {len(yeni_linkler)} yeni yayın eklendi.")
        else:
            print("[✓] Yeni eklenmesi gereken link yok, dosya güncellenmedi.")

        # TODO: eski linkleri güncellemek için yeni referer veya base url belirlenip replace yapılabilir.

if __name__ == "__main__":
    updater = SporCafe6Updater("selcuk.m3u", site_url="https://www.sporcafe6.xyz")
    updater.m3u_guncelle(paths=["/"])
