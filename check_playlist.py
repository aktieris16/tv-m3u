import requests

# Fails, kuru skripts nolasīs, iztīrīs un saglabās atpakaļ
FILENAME = "mans_kanalu_saraksts.m3u"

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

def clean_local_playlist():
    print(f"Nolasu vietējo failu: {FILENAME}...")
    try:
        with open(FILENAME, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ Fails {FILENAME} netika atrasts!")
        return

    header_line = ""
    all_channels = []
    
    # 1. solis: Nolasām galveni un atrodam kanālus ar saitēm
    i = 0
    if lines and lines[0].startswith("#EXTM3U"):
        header_line = lines[0].strip()
        i = 1

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

    print(f"Kopā sarakstā atrasti {len(all_channels)} kanāli. Sākam saišu pārbaudi...")

    # 2. solis: Pārbaudām saites un novēršam dublikātus
    valid_channels = []
    seen_urls = set()
    saved_count = 0
    dead_count = 0

    for inf, url in all_channels:
        if url in seen_urls:
            # Dublikāts - izlaižam
            continue
            
        print(f"Pārbauda: {url}")
        if check_url(url):
            print("✅ Strādā")
            valid_channels.append((inf, url))
            seen_urls.add(url)
            saved_count += 1
        else:
            print("❌ Nedarbojas — izmetam")
            dead_count += 1

    # 3. solis: Saglabājam rezultātu atpakaļ tajā pašā failā
    with open(FILENAME, "w", encoding="utf-8") as f:
        # Saglabājam galveni (piemēram, ar visu url-tvg)
        if header_line:
            f.write(f"{header_line}\n")
        else:
            f.write("#EXTM3U\n")
            
        for inf, url in valid_channels:
            f.write(f"{inf.strip()}\n{url.strip()}\n")
            
    print(f"\n🎉 Gatavs! Fails iztīrīts.")
    print(f"✅ Saglabāti strādājoši kanāli: {saved_count}")
    print(f"❌ Izmesti mirušie un dublikāti: {dead_count}")

if __name__ == "__main__":
    clean_local_playlist()
