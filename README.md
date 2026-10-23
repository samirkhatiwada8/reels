# Reels and Video Downloader TAU

A Flask web app with separate HTML, CSS, JavaScript, and Python backend files.

## Project structure

```text
app.py
requirements.txt
Procfile
render.yaml
README.md
templates/index.html
static/style.css
static/script.js
```

## Run locally (Windows)

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   ```powershell
   py -m pip install -r requirements.txt
   ```
4. Start the server:
   ```powershell
   py app.py
   ```
5. Visit `http://127.0.0.1:5000` in your browser.

## Deploy on Render

1. Upload the contents of this folder to a GitHub repository (upload the files and folders, not the ZIP itself).
2. In Render, create a new Web Service and connect the repository.
3. Use build command `pip install -r requirements.txt`.
4. Use start command `gunicorn app:app --workers 1 --threads 4 --timeout 300`.
5. Choose a plan and deploy. Free hosting may sleep while idle and can have resource limits.

## Important limitations

- Downloads are not guaranteed to work for every link or platform. Platform changes and hosting limits can cause failures.
- Private, login-required, and DRM-protected content is not supported.
- Only download videos you own, have permission to save, or are otherwise legally allowed to download. Follow applicable platform terms and local law.
- This is a starter project, not a production-hardened public service. Before wide public use, add stronger abuse protection, job handling, storage cleanup, monitoring, and privacy/legal review.
