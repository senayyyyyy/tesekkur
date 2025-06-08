import requests
import re

def find_working_selcuksportshd(start=1825, end=1830):
    print("🧭 Sporcafe domainleri taranıyor...")
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for i in range(start, end + 1):
        url = f"https://www.selcuksportshd{i}.xyz/"
        print(f"🔍 Site taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200 and "uxsyplayer" in response.text:
                print(f"✅ Aktif domain bulundu: {url}")
                return response.text, url
        except requests.RequestException:
            print(f"⚠️ Erişim hatası, geçiliyor: {url}")

    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    # main.uxsyplayer...click domainini yakala
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    if match:
        return f"https://{match.group(1)}"
    return None

def fetch_m3u8_links(base_url, channel_ids, referer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }
    m3u8_links = []

    for cid in channel_ids:
        url = f"{base_url}/index.php?id={cid}"
        print(f"🎥 Yayın kontrol ediliyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            # baseStreamUrl veya adsBaseUrl yakala
            base_stream_match = re.search(r"this\.baseStreamUrl\s*=\s*'([^']+)'", response.text)
            ads_base_match = re.search(r"this\.adsBaseUrl\s*=\s*'([^']+)'", response.text)
            base_stream_url = base_stream_match.group(1) if base_stream_match else None
            ads_base_url = ads_base_match.group(1) if ads_base_match else None

            base_url_to_use = base_stream_url or ads_base_url

            if base_url_to_use:
                # id (channel id) + "playlist.m3u8" ekle
                m3u8_link = f"{base_url_to_use}{cid}/playlist.m3u8"
                print(f"✅ M3U8 linki oluşturuldu: {m3u8_link}")
                m3u8_links.append((cid, m3u8_link))
            else:
                print(f"❌ baseStreamUrl veya adsBaseUrl bulunamadı: {url}")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {url} - {e}")
    
    return m3u8_links

def update_m3u_file_with_referer_and_links(m3u8_list, filename="5.m3u", referer=""):
    # Eğer dosya yoksa oluştur, varsa varolan #EXTINF satırlarını koru, link kısmını güncelle
    try:
        lines = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            # Dosya yoksa yeni oluşturacağız
            lines = ["#EXTM3U\n"]

        # Dosyadaki #EXTINF satırları ve takip eden link satırlarını eşle
        # Kanal id listesi ve linkleri dict olarak
        m3u_dict = {cid: link for cid, link in m3u8_list}

        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("#EXTINF"):
                # #EXTINF satırı, onu koru
                extinf_line = line.rstrip("\n")
                # Sonraki satır link olabilir, onu güncelle
                if i + 1 < len(lines):
                    old_link_line = lines[i + 1].rstrip("\n")
                    # Burada hangi id olduğunu bulmaya çalış
                    found_id = None
                    # extinf_line içindeki isimle eşleştirmek yerine linki kullanıyoruz
                    for cid, link in m3u_dict.items():
                        if old_link_line.endswith(cid) or cid in old_link_line:
                            found_id = cid
                            break
                    if found_id:
                        new_lines.append(extinf_line + "\n")
                        new_lines.append(m3u_dict[found_id] + "\n")
                        # Eşleşen link yazıldı, dict'ten kaldır (yeni eklemeyi engellemek için)
                        del m3u_dict[found_id]
                        i += 2
                        continue
                # Eşleşme yoksa orijinal haliyle yaz
                new_lines.append(line)
                i += 1
            else:
                new_lines.append(line)
                i += 1

        # Geri kalan yeni linkleri ekle (yeni kanallar)
        for cid, link in m3u_dict.items():
            new_lines.append(f"#EXTINF:-1,{cid}\n")
            new_lines.append(link + "\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"\n💾 M3U dosyası güncellendi: {filename}")
    except Exception as e:
        print(f"⚠️ M3U dosyası güncellenirken hata oluştu: {e}")

# Ayarlar ve ana program akışı
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

html, referer_url = find_working_selcuksportshd()
if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın domaini: {stream_domain}")
        m3u8_list = fetch_m3u8_links(stream_domain, channel_ids, referer_url)
        if m3u8_list:
            update_m3u_file_with_referer_and_links(m3u8_list, filename="selcuk1.m3u", referer=referer_url)
        else:
            print("❌ M3U8 linki bulunamadı.")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Aktif site bulunamadı.")
import requests
import re

def find_working_selcuksportshd(start=1825, end=1830):
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

def fetch_m3u8_links(base_url, channel_ids, referer):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": referer
    }
    m3u8_links = []

    for cid in channel_ids:
        url = f"{base_url}/index.php?id={cid}"
        print(f"🎥 Yayın kontrol ediliyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            # baseStreamUrl veya adsBaseUrl yakala
            base_stream_match = re.search(r"this\.baseStreamUrl\s*=\s*'([^']+)'", response.text)
            ads_base_match = re.search(r"this\.adsBaseUrl\s*=\s*'([^']+)'", response.text)
            base_stream_url = base_stream_match.group(1) if base_stream_match else None
            ads_base_url = ads_base_match.group(1) if ads_base_match else None
            base_url_to_use = base_stream_url or ads_base_url

            if base_url_to_use:
                # URL oluştur: base_url + id + /playlist.m3u8
                final_url = f"{base_url_to_use}{cid}/playlist.m3u8"
                print(f"✅ M3U8 linki bulundu: {final_url}")
                m3u8_links.append((cid, final_url))
            else:
                print(f"❌ baseStreamUrl veya adsBaseUrl bulunamadı: {url}")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {url} - {e}")

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
            updated_lines.append(line)
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
                updated_lines.append("\n")
        else:
            updated_lines.append(line)
            i += 1

    # Yeni kanalları ekle (eğer yoksa)
    existing_channels = [l for l in updated_lines if l.startswith("#EXTINF:-1")]
    for cid, url in m3u8_links:
        if not any(cid.lower() in l.lower() for l in existing_channels):
            updated_lines.append(f"#EXTINF:-1,{cid}\n")
            updated_lines.append(f"# Referer: {referer}\n")
            updated_lines.append(f"{url}\n")

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"\n💾 M3U dosyası güncellendi: {filename}")

# --- Ana Akış ---

channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

html, referer_url = find_working_selcuksportshd()
if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın adresi bulundu: {stream_domain}")
        m3u8_list = fetch_m3u8_links(stream_domain, channel_ids, referer_url)
        if m3u8_list:
            update_m3u_file_with_referer_and_links(m3u8_list, filename="selcuksports.m3u", referer=referer_url)
        else:
            print("❌ Hiçbir M3U8 yayını bulunamadı.")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Yayın alınacak site bulunamadı.")
import requests
import re

def find_working_selcuksportshd(start=1825, end=1850):
    print("🧭 Selcuksportshd domainleri taranıyor...")
    headers = {"User-Agent": "Mozilla/5.0"}

    for i in range(start, end + 1):
        url = f"https://www.selcuksportshd{i}.xyz/"
        print(f"🔍 Taranıyor: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200 and "uxsyplayer" in response.text:
                print(f"✅ Aktif domain bulundu: {url}")
                return response.text, url
        except:
            print(f"⚠️ Hata: {url}")
            continue

    print("❌ Aktif domain bulunamadı.")
    return None, None

def find_dynamic_player_domain(page_html):
    match = re.search(r'https?://(main\.uxsyplayer[0-9a-zA-Z\-]+\.click)', page_html)
    if match:
        return f"https://{match.group(1)}"
    return None

def extract_base_stream_url(html):
    match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"]([^\'"]+)', html)
    if match:
        return match.group(1)
    return None

def build_m3u8_links(base_stream_url, channel_ids):
    m3u8_links = []
    for cid in channel_ids:
        full_url = f"{base_stream_url}{cid}/playlist.m3u8"
        print(f"✅ M3U8 link oluşturuldu: {full_url}")
        m3u8_links.append((cid, full_url))
    return m3u8_links

def update_m3u_file_with_referer_and_links(m3u8_list, filename="5.m3u", referer=referer_url)

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = ["#EXTM3U\n"]

    updated_lines = []
    i = 0
    total_channels = len(m3u8_links)

    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTINF:-1"):
            updated_lines.append(line)
            i += 1
            # Eski URL ve Referer satırlarını atla
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


# Kanal ID'leri
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5"
]

# Ana işlem
html, referer_url = find_working_selcuksportshd()

if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        print(f"\n🔗 Yayın domaini bulundu: {stream_domain}")
        try:
            player_page = requests.get(f"{stream_domain}/index.php?id={channel_ids[0]}",
                                       headers={"User-Agent": "Mozilla/5.0", "Referer": referer_url})
            base_stream_url = extract_base_stream_url(player_page.text)
            if base_stream_url:
                print(f"📡 Base stream URL bulundu: {base_stream_url}")
                m3u8_list = build_m3u8_links(base_stream_url, channel_ids)
                write_m3u_file(m3u8_list, referer=referer_url)
            else:
                print("❌ baseStreamUrl bulunamadı.")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Aktif yayın alınamadı.")
