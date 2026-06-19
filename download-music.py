import os
import subprocess
import sys

def main():
    print("--- YouTube Audio Downloader ---")
    print("Füge die URLs hier ein (eine pro Zeile).")
    print("Wenn du fertig bist, drücke ENTER in einer leeren Zeile, um den Download zu starten:")

    urls = []
    while True:
        try:
            line = input().strip()
            if not line:  # Beendet die Eingabe bei einer leeren Zeile
                break
            urls.append(line)
        except EOFError:
            break

    if not urls:
        print("Keine URLs gefunden. Programm beendet.")
        return

    # Zielordner definieren und erstellen, falls er noch nicht existiert
    output_dir = "music"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nStarte Download von {len(urls)} Liedern in den Ordner '.\\{output_dir}'...\n")

    for index, url in enumerate(urls, start=1):
        print(f"[{index}/{len(urls)}] Verarbeite: {url}")
        
        # Der yt-dlp Befehl mit dem -P (Path) Parameter
        command = [
            "yt-dlp",
            "-P", output_dir,        # Speichert die Dateien im Unterordner "music"
            "-f", "ba",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            url
        ]

        try:
            # Führt den Befehl aus und wartet, bis er fertig ist
            subprocess.run(command, check=True)
            print(f"Erfolgreich heruntergeladen.\n")
        except subprocess.CalledProcessError as e:
            print(f"Fehler beim Download von {url}: {e}\n")
        except FileNotFoundError:
            print("Fehler: 'yt-dlp' wurde nicht gefunden. Ist es installiert und im PATH?")
            break

    print("Alle Aufgaben abgeschlossen!")

if __name__ == "__main__":
    main()