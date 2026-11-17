# Karaoke Maker

Upload a song, get an instrumental (karaoke) MP3 back.

## Structure
```
karaoke-maker/
├── app.py            # Flask server + routes
├── processor.py      # Audio logic (Demucs AI + FFmpeg fallback)
├── templates/index.html
├── static/style.css, script.js   # Drag-and-drop UI
├── uploads/          # temp uploads (auto-deleted)
└── outputs/          # generated karaoke tracks
```

## Setup
1. Install Python 3.9+ and FFmpeg (ffmpeg.org, make sure `ffmpeg` works in terminal).
2. `python -m venv venv` then activate it (`venv\Scripts\activate` on Windows).
3. `pip install -r requirements.txt`  (Demucs/torch is large; skip it to use basic mode only: `pip install flask`)
4. `python app.py` and open http://127.0.0.1:5000

## How it works
- **AI mode:** Demucs (Meta's neural network) splits the song into vocals and the rest; we keep the rest.
- **Basic mode:** vocals are usually mixed in the centre of a stereo track, so subtracting left from right cancels them. Fast, but also dulls bass/drums.

## Ideas for extra marks
Lyrics display synced with Whisper, key/pitch shifting, YouTube link input, progress bar, user accounts/history.

## Deploying (free, basic mode)
Free hosts are too small for Demucs/PyTorch, so the deployed version uses basic mode.
1. Push this folder to a GitHub repo.
2. On render.com: New > Web Service > connect the repo > Runtime: Docker > Free plan > Deploy.
3. Copy the `https://....onrender.com` URL into the landing page's "Try it now" button.
Note: free services sleep after inactivity, so the first load can take ~1 minute.
