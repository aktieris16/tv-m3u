import requests

# Šeit ir saraksts ar avotiem (publiskām saitēm), no kuriem skripts ievāks krievu kanālus
PLAYLIST_SOURCES = [
    # 1. Lielākais un populārākais atvērtā koda IPTV repozitorijs (Krievijas kanāli)
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/ru.m3u",
    
    # 2. Alternatīvs "Free-TV" repozitorijs (arī Krievijas sadaļa)
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlists/playlist_russia.m3u",
    
    # 3. iptv-org repozitorijs, kur kanāli atlasīti tieši pēc krievu valodas (var trāpīties arī citas valstis, kas raida krieviski)
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/rus.m3u"
]

OUTPUT_FILENAME = "mans_kanalu_saraksts.m3u"

def check_url(url):
    """Pārbauda, vai straumes saite strādā"""
    try:
        response = requests.head(url, timeout=4, allow_redirects=True)
        if response.status_code < 400:
            return True
    except:
        pass
    
    try:
        response = requests.get(url, timeout=4, stream=True)
        if response.status_code < 400:
            return True
    except:
        pass
        
    return False

def aggregate_and_clean():
    all_channels = []
    
    # 1. solis: Nolasām kanālus no visiem norādītajiem avotiem
    for source_url in PLAYLIST_SOURCES:
        print(f"Ielādē avotu: {source_url}")
        try:
            res = requests.get(source_url, timeout=10)
            if res.status_code == 200:
                lines = res.text.splitlines()
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith("#EXTINF:"):
                        if i + 1 < len(lines):
                            url_line = lines[i + 1].strip()
                            if url_line and not url_line.startswith("#"):
                                all_channels.append((lines[i], url_line))
                                i += 2
                                continue
                    i += 1
        except Exception as e:
            print(f"❌ Kļūda ielādējot avotu {source_url}: {e}")

    print(f"Kopā atrasti {len(all_channels)} kanāli no visiem avotiem. Sākam pārbaudi (tas var aizņemt kādu laiku)...")

    # 2. solis: Pārbaudām un atlasām tikai strādājošos kanālus
    valid_channels = []
    for inf, url in all_channels:
        print(f"Pārbauda: {url}")
        if check_url(url):
            print("✅ Strādā")
            valid_channels.append((inf, url))
        else:
            print("❌ Nedarbojas — izmetam")

    # 3. solis: Saglabājam rezultātu galvenajā M3U failā
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        # Lai izvairītos no pilnīgi vienādiem kanāliem (dublikātiem no dažādiem avotiem), izmantojam set() unikālajām saitēm
        seen_urls = set()
        saved_count = 0
        for inf, url in valid_channels:
            if url not in seen_urls:
                f.write(f"{inf}\n{url}\n")
                seen_urls.add(url)
                saved_count += 1
            
    print(f"🎉 Gatavs! Saglabāti {saved_count} unikāli un strādājoši kanāli failā {OUTPUT_FILENAME}")

if __name__ == "__main__":
    aggregate_and_clean()
