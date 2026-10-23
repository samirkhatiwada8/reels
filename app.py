import os
import re
import time
import tempfile
import threading
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, request, jsonify, send_file, render_template
import yt_dlp

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

# Keep this list narrow so the server is not used as a general-purpose URL fetcher.
ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com", "vt.tiktok.com",
}
MAX_REQUESTS_PER_MINUTE = 4
requests_by_ip = {}
rate_lock = threading.Lock()

def allowed_video_url(raw):
    if not isinstance(raw, str) or len(raw) > 3000:
        return False
    try:
        parsed = urlparse(raw.strip())
        host = (parsed.hostname or "").lower().rstrip(".")
        if parsed.scheme not in ("http", "https") or not host:
            return False
        # Permit only exact hosts or subdomains of the approved platform domains.
        approved_roots = ("youtube.com", "youtu.be", "instagram.com", "tiktok.com")
        return any(host == root or host.endswith("." + root) for root in approved_roots)
    except Exception:
        return False

def within_rate_limit(ip):
    now = time.time()
    with rate_lock:
        old = [t for t in requests_by_ip.get(ip, []) if now - t < 60]
        if len(old) >= MAX_REQUESTS_PER_MINUTE:
            requests_by_ip[ip] = old
            return False
        old.append(now)
        requests_by_ip[ip] = old
        return True

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/download")
def download_video():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    if not within_rate_limit(ip):
        return jsonify(error="Too many requests. Please wait a minute and try again."), 429
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not allowed_video_url(url):
        return jsonify(error="Please use a YouTube, Instagram, or TikTok video URL."), 400

    tempdir = tempfile.mkdtemp(prefix="tau_dl_")
    try:
        opts = {
            "outtmpl": str(Path(tempdir) / "%(title).100B-%(id)s.%(ext)s"),
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
            "socket_timeout": 20,
            "retries": 1,
            "fragment_retries": 1,
            "max_filesize": 500 * 1024 * 1024,
            "overwrites": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = Path(ydl.prepare_filename(info))
            if not filepath.exists():
                # Some extractors may use a different extension after post-processing.
                candidates = list(Path(tempdir).glob("*"))
                if not candidates:
                    raise RuntimeError("The source did not provide a downloadable video file.")
                filepath = candidates[0]
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filepath.name,
            mimetype="application/octet-stream",
            conditional=True,
        )
    except Exception:
        # Keep errors generic; source extractor details can expose internal info.
        return jsonify(error="Download failed. The link may be private, login-required, unsupported, too large, or temporarily blocked. Try a public video you have permission to save."), 422
    # Temporary files are removed by the OS or deployment container after the response/container lifecycle.

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
