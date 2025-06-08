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

def build_m3u8_dict(base_stream_url, channel_ids):
    links = {}
    for cid in channel_ids:
        url = f"{base_stream_url}{cid}/playlist.m3u8"
        print(f"✅ M3U8 link oluşturuldu: {url}")
        links[cid] = url
    return links

def update_existing_m3u_file(input_file, output_file, m3u8_links, referer):
    updated_lines = []
    current_channel = None
    skip_next = False

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.startswith("#EXTINF:-1"):
            updated_lines.append(line)
            current_channel = None
            skip_next = False

        elif "selcukbeinsports" in line and ".m3u8" in line:
            for cid in m3u8_links:
                if cid in line:
                    current_channel = cid
                    break
            if current_channel:
                # önceki satır EXTVLCOPT ise güncelle
                if i > 0 and lines[i - 1].startswith("#EXTVLCOPT:http-referrer="):
                    updated_lines[-1] = f"#EXTVLCOPT:http-referrer={referer}\n"
                updated_lines.append(f"{m3u8_links[current_channel]}\n")
            else:
                updated_lines.append(line)

        elif line.startswith("#EXTVLCOPT:http-referrer="):
            # EXTVLCOPT varsa ama bir sonraki satırda m3u8 yoksa, güncelleme
            if i + 1 < len(lines) and ".m3u8" in lines[i + 1]:
                updated_lines.append(f"#EXTVLCOPT:http-referrer={referer}\n")
            else:
                updated_lines.append(line)

        else:
            updated_lines.append(line)
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print(f"\n💾 Güncellenmiş M3U dosyası yazıldı: {output_file}")

# Kanal ID'leri
channel_ids = [
    "selcukbeinsports1",
    "selcukbeinsports2",
    "selcukbeinsports3",
    "selcukbeinsports4",
    "selcukbeinsports5",
    "selcukbeinsportsmax1",
    "selcukbeinsportsmax2",
    "selcukssport",
    "selcukssport2",
    "selcuksmartspor",
    "selcuksmartspor2",
    "selcuktivibuspor1",
    "selcuktivibuspor2",
    "selcuktivibuspor3",
    "selcuktivibuspor4",
    "selcukbeinsportshaber",
    "selcukaspor",
    "selcukeurosport1",
    "selcukeurosport2",
    "selcuksf1",
    "selcuktabiispor",
    "ssportplus1"
    
    
]

# Ana işlem
html, referer_url = find_working_selcuksportshd()
if html:
    stream_domain = find_dynamic_player_domain(html)
    if stream_domain:
        try:
            player_page = requests.get(f"{stream_domain}/index.php?id={channel_ids[0]}", headers={
                "User-Agent": "Mozilla/5.0", "Referer": referer_url
            })
            base_stream_url = extract_base_stream_url(player_page.text)
            if base_stream_url:
                m3u8_links = build_m3u8_dict(base_stream_url, channel_ids)
                update_existing_m3u_file(
                    input_file="kanallar/kerim.m3u",     # El ile düzenlediğin orijinal dosya
                    output_file="kanallar/kerim.m3u",  # Yeni çıktı dosyası
                    m3u8_links=m3u8_links,
                    referer=referer_url
                )
            else:
                print("❌ baseStreamUrl bulunamadı.")
        except Exception as e:
            print(f"⚠️ Hata oluştu: {e}")
    else:
        print("❌ Yayın domaini bulunamadı.")
else:
    print("⛔ Aktif yayın alınamadı.")
