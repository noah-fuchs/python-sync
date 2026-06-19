from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import socket
import os
import io
import zipfile
import urllib.parse

# Sucht den Ordner "upload-to-phone" im gleichen Verzeichnis
BASE_DIR = Path(__file__).parent.resolve()
SHARE_DIR = BASE_DIR / "upload-to-phone"
PORT = 8080

class ModernHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SHARE_DIR), **kwargs)

    def end_headers(self):
        # Verhindert aggressives Caching auf dem Handy
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        super().end_headers()

    def list_directory(self, path):
        """Erzeugt die moderne HTML-Ansicht mit Einzel- und ZIP-Download."""
        try:
            files = os.listdir(path)
        except OSError:
            self.send_error(404, "Keine Berechtigung")
            return None
        
        files.sort(key=lambda a: a.lower())
        
        html = """<!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dateien Herunterladen</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f3f4f6; margin: 0; padding: 20px; color: #1f2937; }
                .container { max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); padding: 24px; }
                h2 { margin-top: 0; color: #111827; text-align: center; margin-bottom: 24px; font-size: 22px; }
                .file-list { list-style: none; padding: 0; margin: 0; }
                .file-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #e5e7eb; gap: 10px; }
                .file-item:last-child { border-bottom: none; }
                .file-label { display: flex; align-items: center; cursor: pointer; flex-grow: 1; overflow: hidden; }
                .file-label input { margin-right: 12px; width: 22px; height: 22px; cursor: pointer; flex-shrink: 0; }
                .file-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 16px; }
                .dl-single { background: #f3f4f6; color: #4b5563; text-decoration: none; padding: 8px 14px; border-radius: 6px; font-size: 14px; font-weight: 500; transition: background 0.2s; white-space: nowrap; }
                .dl-single:hover { background: #e5e7eb; color: #1f2937; }
                
                .btn-group { display: flex; flex-direction: column; gap: 12px; margin-top: 24px; }
                .btn { display: block; width: 100%; border: none; padding: 14px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; transition: background 0.2s; text-align: center; }
                .btn-primary { background: #3b82f6; color: white; }
                .btn-primary:hover { background: #2563eb; }
                .btn-secondary { background: #e5e7eb; color: #374151; }
                .btn-secondary:hover { background: #d1d5db; }
                .empty { text-align: center; color: #6b7280; font-style: italic; padding: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📥 Laptop -> Handy</h2>
                <form id="dl-form" method="POST" action="/download_zip">
                    <ul class="file-list">
        """
        
        has_files = False
        for name in files:
            fullname = os.path.join(path, name)
            if not os.path.isdir(fullname):
                has_files = True
                linkname = urllib.parse.quote(name)
                # data-url speichert den korrekten Link für das JavaScript
                html += f'''
                    <li class="file-item">
                        <label class="file-label">
                            <input type="checkbox" name="files" value="{name}" data-url="{linkname}">
                            <span class="file-name" title="{name}">{name}</span>
                        </label>
                        <a href="{linkname}" class="dl-single" download="{name}">Laden</a>
                    </li>
                '''
        
        if not has_files:
            html += '<li class="empty">Der Ordner ist aktuell leer.</li>'

        html += "</ul>"
        
        if has_files:
            html += '''
                    <div class="btn-group">
                        <button type="button" class="btn btn-primary" onclick="downloadIndividually()">Ausgewählte einzeln laden</button>
                        <button type="submit" class="btn btn-secondary">Ausgewählte als ZIP laden</button>
                    </div>
            '''
            
        html += """
                </form>
            </div>
            
            <script>
            // JavaScript, um die Dateien nacheinander herunterzuladen
            function downloadIndividually() {
                const checkboxes = document.querySelectorAll('input[name="files"]:checked');
                if (checkboxes.length === 0) {
                    alert("Bitte wähle zuerst Dateien aus.");
                    return;
                }
                
                checkboxes.forEach((cb, index) => {
                    // Verzögerung einbauen (500ms pro Datei), damit der Browser die Popups nicht blockiert
                    setTimeout(() => {
                        const link = document.createElement('a');
                        link.href = cb.getAttribute('data-url');
                        link.download = cb.value;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }, index * 500);
                });
            }
            </script>
        </body>
        </html>
        """
        
        encoded = html.encode('utf-8', 'replace')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    def do_POST(self):
        """Behält die ZIP-Funktion für den zweiten Button bei."""
        if self.path == '/download_zip':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            parsed_data = urllib.parse.parse_qs(post_data)
            files_to_download = parsed_data.get('files', [])
            
            if not files_to_download:
                self.send_response(303)
                self.send_header('Location', '/')
                self.end_headers()
                return
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for filename in files_to_download:
                    file_path = SHARE_DIR / filename
                    try:
                        if file_path.is_file() and SHARE_DIR.resolve() in file_path.resolve().parents:
                            zip_file.write(file_path, arcname=filename)
                    except Exception:
                        pass
            
            zip_data = zip_buffer.getvalue()
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', 'attachment; filename="Handy_Download.zip"')
            self.send_header('Content-Length', str(len(zip_data)))
            self.end_headers()
            self.wfile.write(zip_data)
        else:
            self.send_error(404, "Not Found")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

if __name__ == "__main__":
    SHARE_DIR.mkdir(parents=True, exist_ok=True)
    ip = get_local_ip()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ModernHandler)

    print("\n" + "=" * 50)
    print(f"📁 Ordner bereit: {SHARE_DIR}")
    print("=" * 50)
    print(f"📱 Am Handy öffnen: http://{ip}:{PORT}")
    print("=" * 50)
    print("Beenden mit Ctrl+C\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer gestoppt.")