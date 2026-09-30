import requests

FILENAME = "tv.m3u"

def check_url(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code < 400:
            return True
    except:
        pass
    try:
        response = requests.get(url, timeout=5, stream=True)
        if response.status_code < 400:
            return True
    except:
        pass
    return False

def clean_playlist():
    with open(FILENAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if url_line and not url_line.startswith("#"):
                    print(f"Checking: {url_line}")
                    if check_url(url_line):
                        print("✅ Working")
                        new_lines.append(lines[i])
                        new_lines.append(lines[i + 1])
                    else:
                        print("❌ Dead - removing")
                    i += 2
                    continue
        new_lines.append(lines[i])
        i += 1

    with open(FILENAME, "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Playlist cleaned successfully!")

if __name__ == "__main__":
    clean_playlist()