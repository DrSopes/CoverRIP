import json
import re
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import imageio_ffmpeg
import yt_dlp
from mutagen.id3 import COMM, TALB, TDRC, TIT2, TPE1, ID3
from mutagen.mp3 import MP3

APP_NAME = "CoverRIP ✝️"
AUTHOR = "Dr.Sopes"
SETTINGS_FILE = Path(__file__).with_name("coverrip_settings.json")


def safe_filename(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r'[<>:"/\\|?*]', "_", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" .")
    return text[:180] or "audio"


def looks_like_youtube_url(text: str) -> bool:
    text = (text or "").strip().lower()
    return (
        "youtube.com/watch" in text
        or "youtube.com/shorts/" in text
        or "youtu.be/" in text
        or "music.youtube.com/" in text
    )


class CoverRIPApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} — {AUTHOR}")
        self.root.geometry("920x660")
        self.root.minsize(820, 600)

        self.settings = self.load_settings()

        self.url_var = tk.StringVar()
        self.folder_var = tk.StringVar(
            value=self.settings.get("last_folder", str(Path.home() / "Downloads"))
        )
        self.status_var = tk.StringVar(value="Ready.")
        self.source_title_var = tk.StringVar(value="")
        self.source_channel_var = tk.StringVar(value="")
        self.source_duration_var = tk.StringVar(value="")
        self.output_name_var = tk.StringVar(value="")

        self.meta_title_var = tk.StringVar(value="")
        self.meta_artist_var = tk.StringVar(value="")
        self.meta_album_var = tk.StringVar(value="")
        self.meta_year_var = tk.StringVar(value="")
        self.meta_comment_var = tk.StringVar(
            value=self.settings.get("last_comment", "Downloaded with CoverRIP")
        )

        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

        self.url_trace_job = None
        self.analysis_in_progress = False
        self.last_analyzed_url = ""
        self.analysis_token = 0

        self._build_ui()
        self._bind_events()

    def load_settings(self):
        try:
            if SETTINGS_FILE.exists():
                return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def save_settings(self):
        data = {
            "last_folder": self.folder_var.get().strip(),
            "last_comment": self.meta_comment_var.get().strip(),
        }
        try:
            SETTINGS_FILE.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
        except Exception:
            pass

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=14)
        main.pack(fill="both", expand=True)

        title = ttk.Label(main, text=APP_NAME, font=("Segoe UI", 16, "bold"))
        title.pack(anchor="w")

        subtitle = ttk.Label(
            main,
            text="Download YouTube audio to MP3 with cover art and editable metadata",
            foreground="#555555"
        )
        subtitle.pack(anchor="w", pady=(0, 12))

        url_box = ttk.LabelFrame(main, text="Source", padding=10)
        url_box.pack(fill="x", pady=(0, 10))

        ttk.Label(url_box, text="YouTube URL").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(url_box, textvariable=self.url_var)
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        self.url_entry.focus()

        ttk.Button(url_box, text="Paste", command=self.paste_clipboard).grid(row=0, column=2, sticky="ew")
        ttk.Button(url_box, text="Refresh", command=lambda: self.start_analyze(force=True)).grid(row=0, column=3, sticky="ew", padx=(8, 0))

        url_box.columnconfigure(1, weight=1)

        dest_box = ttk.LabelFrame(main, text="Destination", padding=10)
        dest_box.pack(fill="x", pady=(0, 10))

        ttk.Label(dest_box, text="Folder").grid(row=0, column=0, sticky="w")
        self.folder_entry = ttk.Entry(dest_box, textvariable=self.folder_var)
        self.folder_entry.grid(row=0, column=1, sticky="ew", padx=(8, 8))
        ttk.Button(dest_box, text="Browse", command=self.select_folder).grid(row=0, column=2, sticky="ew")

        ttk.Label(dest_box, text="File name").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.output_entry = ttk.Entry(dest_box, textvariable=self.output_name_var)
        self.output_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(8, 0), pady=(10, 0))

        ttk.Label(dest_box, text="Final path preview").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.final_path_label = ttk.Label(dest_box, text="", foreground="#004a99")
        self.final_path_label.grid(row=2, column=1, columnspan=2, sticky="w", padx=(8, 0), pady=(10, 0))

        dest_box.columnconfigure(1, weight=1)

        source_box = ttk.LabelFrame(main, text="Detected from YouTube", padding=10)
        source_box.pack(fill="x", pady=(0, 10))

        ttk.Label(source_box, text="Title").grid(row=0, column=0, sticky="w")
        ttk.Label(source_box, textvariable=self.source_title_var, wraplength=650).grid(row=0, column=1, sticky="w", padx=(8, 0))

        ttk.Label(source_box, text="Channel").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Label(source_box, textvariable=self.source_channel_var, wraplength=650).grid(row=1, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        ttk.Label(source_box, text="Duration").grid(row=2, column=0, sticky="w", pady=(6, 0))
        ttk.Label(source_box, textvariable=self.source_duration_var).grid(row=2, column=1, sticky="w", padx=(8, 0), pady=(6, 0))

        source_box.columnconfigure(1, weight=1)

        meta_box = ttk.LabelFrame(main, text="Editable metadata before saving", padding=10)
        meta_box.pack(fill="both", expand=True, pady=(0, 10))

        ttk.Label(meta_box, text="Title").grid(row=0, column=0, sticky="w")
        ttk.Entry(meta_box, textvariable=self.meta_title_var).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(meta_box, text="Artist").grid(row=1, column=0, sticky="w")
        ttk.Entry(meta_box, textvariable=self.meta_artist_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(meta_box, text="Album").grid(row=2, column=0, sticky="w")
        ttk.Entry(meta_box, textvariable=self.meta_album_var).grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(meta_box, text="Year").grid(row=3, column=0, sticky="w")
        ttk.Entry(meta_box, textvariable=self.meta_year_var).grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=4)

        ttk.Label(meta_box, text="Comment").grid(row=4, column=0, sticky="w")
        ttk.Entry(meta_box, textvariable=self.meta_comment_var).grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=4)

        meta_box.columnconfigure(1, weight=1)

        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(2, 8))

        self.download_btn = ttk.Button(actions, text="Download MP3", command=self.start_download)
        self.download_btn.pack(side="left")

        ttk.Button(actions, text="Exit", command=self.on_close).pack(side="right")

        ttk.Separator(main).pack(fill="x", pady=8)
        ttk.Label(main, text="Status").pack(anchor="w")
        ttk.Label(main, textvariable=self.status_var, foreground="#005bbb").pack(anchor="w", pady=(4, 0))

        self.update_final_path_preview()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _bind_events(self):
        self.url_var.trace_add("write", self.on_url_changed)
        self.folder_var.trace_add("write", lambda *args: self.on_settings_related_change())
        self.output_name_var.trace_add("write", lambda *args: self.update_final_path_preview())

    def on_settings_related_change(self):
        self.update_final_path_preview()
        self.save_settings()

    def update_final_path_preview(self):
        folder = self.folder_var.get().strip()
        filename = self.output_name_var.get().strip()

        if filename and not filename.lower().endswith(".mp3"):
            filename += ".mp3"

        if folder and filename:
            self.final_path_label.config(text=str(Path(folder) / filename))
        elif folder:
            self.final_path_label.config(text=str(Path(folder)))
        else:
            self.final_path_label.config(text="")

    def paste_clipboard(self):
        try:
            text = self.root.clipboard_get().strip()
            if text:
                self.url_var.set(text)
        except tk.TclError:
            pass

    def select_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.folder_var.get() or str(Path.home()),
            title="Select destination folder"
        )
        if folder:
            self.folder_var.set(folder)
            self.save_settings()

    def set_status(self, text):
        self.root.after(0, self.status_var.set, text)

    def toggle_download(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.root.after(0, lambda: self.download_btn.config(state=state))

    def on_url_changed(self, *args):
        if self.url_trace_job:
            self.root.after_cancel(self.url_trace_job)
            self.url_trace_job = None

        url = self.url_var.get().strip()

        if not url:
            self.last_analyzed_url = ""
            self.source_title_var.set("")
            self.source_channel_var.set("")
            self.source_duration_var.set("")
            self.set_status("Ready.")
            return

        self.set_status("Waiting for URL analysis...")
        self.url_trace_job = self.root.after(850, self.auto_analyze_url)

    def auto_analyze_url(self):
        self.url_trace_job = None
        self.start_analyze(force=False)

    def start_analyze(self, force=False):
        url = self.url_var.get().strip()

        if not url:
            return

        if not looks_like_youtube_url(url):
            self.set_status("Paste a valid YouTube URL.")
            return

        if self.analysis_in_progress and not force:
            return

        if url == self.last_analyzed_url and not force:
            return

        self.analysis_in_progress = True
        self.analysis_token += 1
        token = self.analysis_token
        self.set_status("Analyzing URL...")

        threading.Thread(
            target=self.analyze_url,
            args=(url, token),
            daemon=True
        ).start()

    def analyze_url(self, url, token):
        try:
            ydl_opts = {
                "quiet": True,
                "noplaylist": True,
                "skip_download": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            if token != self.analysis_token:
                return

            source_title = info.get("title") or ""
            source_channel = info.get("uploader") or info.get("channel") or ""
            duration_seconds = info.get("duration")
            duration_text = self.format_duration(duration_seconds)

            meta_title = info.get("track") or info.get("title") or ""
            meta_artist = info.get("artist") or info.get("uploader") or info.get("channel") or ""
            meta_album = info.get("album") or info.get("playlist_title") or info.get("channel") or ""
            meta_year = ""

            if info.get("release_year"):
                meta_year = str(info["release_year"])
            else:
                upload_date = info.get("upload_date")
                if upload_date and len(upload_date) >= 4:
                    meta_year = upload_date[:4]

            default_filename = self.build_default_filename(meta_title, meta_artist)

            def apply_result():
                if url != self.url_var.get().strip():
                    return

                self.source_title_var.set(source_title)
                self.source_channel_var.set(source_channel)
                self.source_duration_var.set(duration_text)

                self.meta_title_var.set(meta_title)
                self.meta_artist_var.set(meta_artist)
                self.meta_album_var.set(meta_album)
                self.meta_year_var.set(meta_year)
                if not self.meta_comment_var.get().strip():
                    self.meta_comment_var.set("Downloaded with CoverRIP")

                if not self.output_name_var.get().strip() or force_overwrite_name_from_url(self.last_analyzed_url, url, self.output_name_var.get().strip()):
                    self.output_name_var.set(default_filename)

                self.update_final_path_preview()
                self.status_var.set("Metadata loaded automatically. Review and download when ready.")

            self.root.after(0, apply_result)
            self.last_analyzed_url = url

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Analyze error", str(e)))
            self.set_status("Could not analyze the URL.")
        finally:
            self.analysis_in_progress = False

    def build_default_filename(self, title, artist):
        title = safe_filename(title)
        artist = safe_filename(artist)

        if artist and title:
            return f"{artist} - {title}.mp3"
        if title:
            return f"{title}.mp3"
        return "audio.mp3"

    def format_duration(self, seconds):
        if not seconds:
            return ""
        try:
            seconds = int(seconds)
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            if h > 0:
                return f"{h}:{m:02d}:{s:02d}"
            return f"{m}:{s:02d}"
        except Exception:
            return ""

    def progress_hook(self, d):
        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                percent = downloaded * 100 / total
                self.set_status(f"Downloading audio... {percent:.1f}%")
            else:
                self.set_status("Downloading audio...")
        elif status == "finished":
            self.set_status("Converting to MP3 and embedding thumbnail...")

    def write_metadata(self, mp3_path: Path):
        audio = MP3(mp3_path)
        if audio.tags is None:
            audio.add_tags()
            audio.save()

        tags = ID3(mp3_path)

        tags.delall("TIT2")
        tags.delall("TPE1")
        tags.delall("TALB")
        tags.delall("TDRC")
        tags.delall("COMM")

        title = self.meta_title_var.get().strip()
        artist = self.meta_artist_var.get().strip()
        album = self.meta_album_var.get().strip()
        year = self.meta_year_var.get().strip()
        comment = self.meta_comment_var.get().strip()

        if title:
            tags.add(TIT2(encoding=3, text=title))
        if artist:
            tags.add(TPE1(encoding=3, text=artist))
        if album:
            tags.add(TALB(encoding=3, text=album))
        if year:
            tags.add(TDRC(encoding=3, text=year))
        if comment:
            tags.add(COMM(encoding=3, lang="eng", desc="", text=comment))

        tags.save(v2_version=3)

    def start_download(self):
        url = self.url_var.get().strip()
        folder = self.folder_var.get().strip()
        filename = self.output_name_var.get().strip()

        if not url:
            messagebox.showwarning("Missing URL", "Paste a YouTube URL first.")
            return

        if not looks_like_youtube_url(url):
            messagebox.showwarning("Invalid URL", "Paste a valid YouTube URL.")
            return

        if not folder:
            messagebox.showwarning("Missing folder", "Select a destination folder.")
            return

        if not filename:
            messagebox.showwarning("Missing file name", "Enter the final file name.")
            return

        self.save_settings()
        self.toggle_download(False)
        self.set_status("Starting download...")

        threading.Thread(target=self.download_audio, daemon=True).start()

    def download_audio(self):
        try:
            url = self.url_var.get().strip()
            folder = Path(self.folder_var.get().strip())
            folder.mkdir(parents=True, exist_ok=True)

            filename = self.output_name_var.get().strip()
            if filename.lower().endswith(".mp3"):
                filename = filename[:-4]

            filename = safe_filename(filename)
            outtmpl = str(folder / f"{filename}.%(ext)s")

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "noplaylist": True,
                "writethumbnail": True,
                "prefer_ffmpeg": True,
                "ffmpeg_location": self.ffmpeg_exe,
                "progress_hooks": [self.progress_hook],
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "0",
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": True,
                    },
                    {
                        "key": "EmbedThumbnail",
                    },
                ],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)

            final_mp3 = folder / f"{filename}.mp3"

            if not final_mp3.exists():
                matches = sorted(
                    folder.glob(f"{filename}*.mp3"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                if not matches:
                    raise FileNotFoundError("The MP3 file was not found after download.")
                final_mp3 = matches[0]

            self.set_status("Writing edited metadata...")
            self.write_metadata(final_mp3)

            self.set_status("Done.")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Completed",
                    f"Saved file:\n{final_mp3.name}\n\nFolder:\n{final_mp3.parent}"
                )
            )

        except Exception as e:
            self.set_status("Download failed.")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))

    def on_close(self):
        self.save_settings()
        self.root.destroy()


def force_overwrite_name_from_url(previous_url: str, current_url: str, current_name: str) -> bool:
    if not current_name.strip():
        return True
    return previous_url != current_url


if __name__ == "__main__":
    root = tk.Tk()
    app = CoverRIPApp(root)
    root.mainloop()
