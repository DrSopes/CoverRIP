# YouTube to MP3 GUI Downloader

A simple Python desktop app with a graphical interface to download the best available audio from a YouTube video, convert it to MP3, and embed the video thumbnail as album art.

This version is designed to work **without a system-wide FFmpeg installation**. It uses `imageio-ffmpeg` to provide an FFmpeg binary directly from Python and passes that executable to `yt-dlp` automatically.

## Features

- Paste a YouTube URL into a desktop GUI
- Choose the destination folder before downloading
- Download the best available audio stream
- Convert audio to MP3
- Embed the YouTube thumbnail as cover art
- No manual FFmpeg installation required

## Tech Stack

- **Python**
- **Tkinter** for the GUI
- **yt-dlp** for extracting and downloading media
- **imageio-ffmpeg** for bundled FFmpeg access

## Requirements

- Python 3
- Internet connection
- Windows, macOS, or Linux

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

Create and activate a virtual environment (recommended):

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
python youtube_mp3_gui.py
```

## How It Works

1. Paste a YouTube video URL.
2. Choose the folder where the MP3 file should be saved.
3. Click **Download MP3**.
4. The app downloads the best available audio.
5. The audio is converted to MP3.
6. The video thumbnail is embedded as album art.

## Project Structure

```text
.
├── youtube_mp3_gui.py
├── requirements.txt
└── README.md
```

## Dependency Notes

`tkinter` is part of the Python standard library in most Python installations, so it is usually not included in `requirements.txt`.

`imageio-ffmpeg` is used so the application can work without asking users to manually install FFmpeg and configure environment variables.

## Troubleshooting

### The app does not open

Make sure Python is installed correctly and that `tkinter` is available in your Python build.

### Download fails on some videos

Some videos may be unavailable due to regional restrictions, age restrictions, removed content, or platform-side changes.

### Thumbnail is not embedded

The thumbnail embedding step depends on successful post-processing. Updating `yt-dlp` and reinstalling dependencies often fixes this.

## Legal Notice

Use this project only for content you have the right to download. Users are responsible for complying with YouTube's terms and applicable copyright laws.

## License

Add your preferred license here, for example MIT.
