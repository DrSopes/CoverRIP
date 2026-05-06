# CoverRIP ✝️

**CoverRIP ✝️** is a Python desktop app with a graphical interface that downloads the best available audio from a YouTube video, converts it to MP3, embeds the thumbnail as cover art, and lets you review or edit the final file name and metadata before saving.

Author: **Dr.Sopes**

## Features

- Paste a YouTube URL and trigger automatic analysis
- Choose the destination folder before downloading
- Edit the final output file name manually
- Review and edit metadata before saving
- Convert the best available audio stream to MP3
- Embed the YouTube thumbnail as album art
- Remember the last destination folder and comment field
- Work without a system-wide FFmpeg installation

## Requirements

- Python 3.10+
- Windows, macOS, or Linux
- Internet connection

## Installation

Clone the repository:

```bash
git clone https://github.com/DrSopes/CoverRIP.git
cd CoverRIP
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

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Dependencies

- `yt-dlp`
- `imageio-ffmpeg`
- `mutagen`

## Run

```bash
python CoverRIP.py
```

## Workflow

1. Paste a YouTube URL.
2. Wait for the app to analyze the URL automatically.
3. Review the detected title, channel, and duration.
4. Edit the output file name if needed.
5. Edit metadata such as title, artist, album, year, or comment.
6. Choose the destination folder.
7. Download the final MP3.

## Notes

The app uses `imageio-ffmpeg` so users do not need to install FFmpeg manually at the system level.

The metadata fields are written again after the MP3 is created so your manual edits override the default values detected from YouTube.

## Files

```text
.
├── CoverRIP.py
├── requirements.txt
├── README.md
└── LICENSE
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
