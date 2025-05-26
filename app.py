from flask import Flask, request, jsonify, send_file, make_response
import yt_dlp
import uuid
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "/tmp"

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    urls = data.get("urls", [])
    output_files = []

    for url in urls:
        filename = f"{uuid.uuid4()}.mp4"
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        ydl_opts = {
            "outtmpl": filepath,
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.amazon.es/"
            }
        }

        try:
            print(f"Descargando: {url}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"Archivo generado: {filename}")
            output_files.append(filename)
        except Exception as e:
            print(f"Error con {url}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    return jsonify({"files": output_files})

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        response = make_response(send_file(filepath, mimetype="video/mp4"))
        response.headers["Content-Disposition"] = "inline"
        return response
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)