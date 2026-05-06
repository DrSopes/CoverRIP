CoverRIP

CoverRIP is a Python desktop app with a graphical interface that downloads the best available audio from a YouTube video, converts it to MP3, and embeds the video thumbnail as album art.

Author

Dr.Sopes
Features

    Paste a YouTube URL into a desktop GUI

    Choose the destination folder before downloading

    Download the best available audio stream

    Convert audio to MP3

    Embed the YouTube thumbnail as cover art

    Work without a system-wide FFmpeg installation

Tech Stack

    Python

    Tkinter for the GUI

    yt-dlp for extracting and downloading media

    imageio-ffmpeg for bundled FFmpeg access

Requirements

    Python 3

    Internet connection

    Windows, macOS, or Linux

Installation

Clone the repository:

bash
git clone https://github.com/your-username/coverrip.git
cd coverrip

Create and activate a virtual environment (recommended):
Windows

bash
python -m venv .venv
.venv\Scripts\activate

macOS / Linux

bash
python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

bash
pip install -r requirements.txt

Run the App

bash
python CoverRIP.py

How It Works

    Paste a YouTube video URL.

    Choose the folder where the MP3 file should be saved.

    Click Download MP3.

    The app downloads the best available audio.

    The audio is converted to MP3.

    The video thumbnail is embedded as album art.

Project Structure

text
.
├── CoverRIP.py
├── requirements.txt
└── README.md

Dependency Notes

tkinter is part of the Python standard library in most Python installations, so it is usually not included in requirements.txt.

imageio-ffmpeg is used so the application can work without asking users to manually install FFmpeg or configure environment variables.
Troubleshooting
The app does not open

Make sure Python is installed correctly and that tkinter is available in your Python build.
Download fails on some videos

Some videos may be unavailable due to regional restrictions, age restrictions, removed content, or platform-side changes.
Thumbnail is not embedded

The thumbnail embedding step depends on successful post-processing. Updating yt-dlp and reinstalling dependencies often fixes this.
Legal Notice

Use this project only for content you have the right to download. Users are responsible for complying with YouTube's terms and applicable copyright laws.
License

This project is licensed under the MIT License. See the LICENSE file for details.