import os
import socket
import qrcode
from flask import Flask, request, render_template_string

app = Flask(__name__)

UPLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "PhoneUploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Senden</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; max-width: 420px; margin: 60px auto; padding: 20px; background: #f2f2f7; }
        .card { background: white; border-radius: 16px; padding: 30px; text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }
        h1 { font-size: 1.4em; }
        .drop { display: block; border: 2px dashed #007aff; border-radius: 12px; padding: 30px; cursor: pointer; color: #007aff; }
        input[type=file] { display: none; }
        button { margin-top: 16px; background: #007aff; color: white; border: none; padding: 14px; border-radius: 12px; font-size: 1em; width: 100%; cursor: pointer; }
        .ok { color: #34c759; font-weight: 600; margin-top: 16px; }
        .names { font-size: 0.85em; color: #555; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="card">
        <h1>📤 Datei senden</h1>
        <form method="POST" enctype="multipart/form-data">
            <label class="drop">
                Tippe hier zum Auswählen
                <input type="file" name="files" multiple id="f" onchange="document.getElementById('n').textContent=Array.from(this.files).map(x=>x.name).join(', ')">
            </label>
            <div class="names" id="n"></div>
            <button type="submit">⬆ Hochladen</button>
        </form>
        {% if saved %}
        <div class="ok">✅ {{ saved | join(", ") }}</div>
        {% endif %}
    </div>
</body>
</html>"""

@app.route("/", methods=["GET", "POST"])
def upload():
    saved = []
    if request.method == "POST":
        for f in request.files.getlist("files"):
            if f.filename:
                dest = os.path.join(UPLOAD_DIR, f.filename)
                f.save(dest)
                saved.append(f.filename)
                print(f"✅  Gespeichert: {dest}")
    return render_template_string(HTML, saved=saved)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

if __name__ == "__main__":
    PORT = 8080
    ip = get_local_ip()
    url = f"http://{ip}:{PORT}"
    qr = qrcode.QRCode(border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr.print_ascii(invert=True)
    print(f"\n  Öffne auf dem iPhone: {url}")
    print(f"  Dateien landen in:    {UPLOAD_DIR}\n")
    app.run(host="0.0.0.0", port=PORT, debug=False)
