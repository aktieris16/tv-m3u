import requests

LOCAL_FILENAME = "mans_kanalu_saraksts.m3u"

PLAYLIST_SOURCES = [
    "http://www.skynet.net.ua/iptv.m3u8",
    "https://iptv.org.ua/iptv/avtomini.m3u",
    "https://iptv-org.github.io/iptv/countries/ru.m3u",
    "https://ngrch.github.io/iptv/ru.m3u",
    "https://ngrch.github.io/iptv/cartoons.m3u"
]

def check_url(url):
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

def parse_m3u_content(text_content):
    channels = []
    lines = text_content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if url_line and not url_line.startswith("#"):
                    channels.append((line, url_line))
                    i += 2
                    continue
        i += 1
    return channels

def aggregate_and_clean_all():
    all_channels = []
    epg_header = '#EXTM3U url-tvg="https://iptvx.one/epg/epg.xml.gz"'

    print(f"Nolasu vietējo failu: {LOCAL_FILENAME}...")
    try:
        with open(LOCAL_FILENAME, "r", encoding="utf-8") as f:
            local_text = f.read()
            for line in local_text.splitlines():
                if line.startswith("#EXTM3U"):
                    epg_header = line.strip()
                    break
            local_channels = parse_m3u_content(local_text)
            all_channels.extend(local_channels)
            print(f"Iegūti {len(local_channels)} kanāli no tava lokālā faila.")
    except FileNotFoundError:
        print(f"⚠️ Lokālais fails {LOCAL_FILENAME} nav atrasts, veidosim jaunu.")

    for source_url in PLAYLIST_SOURCES:
        if not source_url.strip():
            continue
        print(f"Ielādē jaunu avotu: {source_url}")
        try:
            res = requests.get(source_url, timeout=10)
            if res.status_code == 200:
                external_channels = parse_m3u_content(res.text)
                all_channels.extend(external_channels)
                print(f"Iegūti {len(external_channels)} kanāli no avota.")
            else:
                print(f"❌ Neizdevās ielādēt (kods {res.status_code})")
        except Exception as e:
            print(f"❌ Kļūda ielādējot avotu: {e}")

    print(f"\nKopā savākti {len(all_channels)} kanāli. Sākam filtrēšanu un saišu pārbaudi...")

    valid_channels = []
    seen_urls = set()
    saved_count = 0
    dead_count = 0
    filtered_count = 0

    # Aともrache/paid/mpd saiti block karnyasathi keywords
    blocked_keywords = [".mpd", "redtraffic", "paperstreetcash", "cheerleaderfacials"]

    for inf, url in all_channels:
        url_lower = url.lower()
        
        # Jar link madhe paid/mpd asel tar te galitun nighun jail
        if any(keyword in url_lower for keyword in blocked_keywords):
            filtered_count += 1
            continue

        if url in seen_urls:
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

    with open(LOCAL_FILENAME, "w", encoding="utf-8") as f:
        f.write(f"{epg_header}\n")
        for inf, url in valid_channels:
            f.write(f"{inf.strip()}\n{url.strip()}\n")
            
    print(f"\n🎉 Process pabeigts!")
    print(f"✅ Saglabāti strādājoši un unikāli kanāli: {saved_count}")
    print(f"🚫 Atmestas nevēlamās (.mpd / paid) saites: {filtered_count}")
    print(f"❌ Izmesti mirušie un dublikāti: {dead_count}")

if __name__ == "__main__":
    aggregate_and_clean_all()
