import requests

# Šeit tu vari sarakstīt vairākas dažādas M3U saišu adreses no dažādiem avotiem
PLAYLIST_SOURCES = [
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/lv.m3u", # Piemērs: varēsi nomainīt uz savām saitēm
    "ŠEIT_IEVIETO_CITU_SAITI_1.m3u",
    "ŠEIT_IEVIETO_CITU_SAITI_2.m3u"
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
        if "ŠEIT_IEVIETO" in source_url:
            continue
        print(g := f"Ielādē avotu: {source_url}")
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
            print(f"Kļūda ielādējot avotu: {e}")

    print(f"Kopā atrasti {len(all_channels)} kanāli no visiem avotiem. Sākam pārbaudi...")

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
        for inf, url in valid_channels:
            f.write(f"{inf}\n{url}\n")
            
    print(f"Gatavs! Saglabāti {len(valid_channels)} strādājoši kanāli failā {OUTPUT_FILENAME}")

if __name__ == "__main__":
    aggregate_and_clean()
