# CoverRIP ✝️

**CoverRIP ✝️** is a Python desktop app that downloads the best available audio from a YouTube video, converts it to MP3, embeds the video thumbnail as cover art, and lets you edit the final file name and metadata before saving. 

It also adds **ReplayGain track tags** to help compatible music players keep songs at a more consistent playback level without applying destructive dynamic compression to the track itself. ReplayGain in MP3 is usually stored as metadata, and actual playback behavior depends on whether the player supports those tags.

**Author:** Dr.Sopes 

## Features

- Automatic YouTube URL analysis after pasting a link, with detected title, channel, and duration shown in the interface. 
- Editable output file name before download. 
- Editable MP3 metadata, including title, artist, album, year, and comment. 
- Thumbnail embedding as cover art in the final MP3. 
- Saved preferences for the last destination folder and other recent settings. 
- Integrated ReplayGain track tag writing with a configurable target volume. 
- No separate manual FFmpeg installation required, because the app uses `imageio-ffmpeg` from Python.

## Requirements

- Python 3.10 or newer.
- Windows, macOS, or Linux. 
- Internet connection. 

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

Install dependencies:

```bash
pip install -r requirements.txt
```

The current dependency file contains `yt-dlp`, `imageio-ffmpeg`, and `mutagen`.

## Run

```bash
python CoverRIP.py
```

The main application file is the Python script you currently have in the repository. 

## Workflow

1. Paste a YouTube URL into the app. 
2. Wait for automatic analysis to load the detected metadata. 
3. Choose the destination folder. 
4. Edit the final output file name if needed. 
5. Review or modify metadata fields before saving. 
6. Optionally keep ReplayGain enabled and adjust the target level. 
7. Download the MP3.

## ReplayGain

CoverRIP writes **ReplayGain track tags** to the MP3 file so compatible players can reduce differences in perceived loudness between songs. ReplayGain is designed for more consistent playback level across tracks rather than changing the internal dynamic shape of each song.

This is not the same as permanently rewriting the audio like MP3Gain frame-level changes. In MP3 workflows, ReplayGain metadata is commonly stored in tags, and whether it has audible effect depends on the player reading and applying those tags during playback.

Because of that, two different music players may not behave the same way with the same output file. Some players support ReplayGain well, while others ignore it completely.

## Notes

The app uses `yt-dlp` to extract and download media, `imageio-ffmpeg` to provide FFmpeg access from Python, and `mutagen` to write MP3 metadata.

The README is intentionally kept focused on installation, usage, and playback behavior, which are the most important sections for a GitHub project like this.

## Project Files

```text
.
├── CoverRIP.py
├── requirements.txt
├── README.md
└── LICENSE
```

The current repository files you shared include `CoverRIP.py` and `requirements.txt`.

## License

This project is licensed under the MIT License. If your repository already includes a `LICENSE` file, GitHub will surface it alongside the README as part of the repository metadata.