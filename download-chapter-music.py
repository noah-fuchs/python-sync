import yt_dlp

def main():
    print("=== YouTube Kapitel-Extractor ===")
    
    # Fragt dich interaktiv nach dem Link
    youtube_url = input("\nBitte füge hier den YouTube-Link ein und drücke Enter:\n> ").strip()
    
    # Kurzer Check, ob das Feld leer gelassen wurde
    if not youtube_url:
        print("Fehler: Du hast keinen Link eingegeben. Skript wird abgebrochen.")
        return

    # Die Einstellungen für yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegSplitChapters',
            }
        ],
        'outtmpl': {
            # HIER GEÄNDERT: "music/" sorgt dafür, dass die Songs im Unterordner landen
            'chapter': 'music/%(section_number)s - %(section_title)s.%(ext)s',
        },
        'quiet': False,
    }

    print("\n[INFO] Starte Download und Extraktion der Kapitel...")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        print("\n=== FERTIG! Die Songs wurden erfolgreich im Ordner 'music' extrahiert. ===")
    except Exception as e:
        print(f"\n[FEHLER] Es gab ein Problem beim Download: {e}")

if __name__ == "__main__":
    main()