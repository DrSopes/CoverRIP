import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

import yt_dlp
import imageio_ffmpeg


class YouTubeMP3App:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube a MP3")
        self.root.geometry("720x280")
        self.root.minsize(680, 250)

        self.url_var = tk.StringVar()
        self.folder_var = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.status_var = tk.StringVar(value="List.")
        self.title_var = tk.StringVar(value="")

        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=16)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="URL del vídeo:").pack(anchor="w")
        row1 = ttk.Frame(main)
        row1.pack(fill="x", pady=(6, 12))

        self.url_entry = ttk.Entry(row1, textvariable=self.url_var)
        self.url_entry.pack(side="left", fill="x", expand=True)
        self.url_entry.focus()

        ttk.Button(row1, text="Enganxa", command=self.pegar_portapapers).pack(side="left", padx=(8, 0))

        ttk.Label(main, text="Carpeta de destinació:").pack(anchor="w")
        row2 = ttk.Frame(main)
        row2.pack(fill="x", pady=(6, 12))

        self.folder_entry = ttk.Entry(row2, textvariable=self.folder_var)
        self.folder_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(row2, text="Tria carpeta", command=self.seleccionar_carpeta).pack(side="left", padx=(8, 0))

        row3 = ttk.Frame(main)
        row3.pack(fill="x", pady=(4, 10))

        self.download_btn = ttk.Button(row3, text="Descarrega MP3", command=self.iniciar_descarga)
        self.download_btn.pack(side="left")

        ttk.Button(row3, text="Surt", command=self.root.destroy).pack(side="right")

        ttk.Separator(main).pack(fill="x", pady=8)

        ttk.Label(main, text="Estat:").pack(anchor="w")
        ttk.Label(main, textvariable=self.status_var, foreground="blue").pack(anchor="w", pady=(4, 8))
        ttk.Label(main, textvariable=self.title_var, wraplength=660).pack(anchor="w")

    def pegar_portapapers(self):
        try:
            text = self.root.clipboard_get().strip()
            if text:
                self.url_var.set(text)
        except tk.TclError:
            pass

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(
            initialdir=self.folder_var.get() or str(Path.home()),
            title="Selecciona la carpeta de destinació"
        )
        if carpeta:
            self.folder_var.set(carpeta)

    def iniciar_descarga(self):
        url = self.url_var.get().strip()
        carpeta = self.folder_var.get().strip()

        if not url:
            messagebox.showwarning("Falta la URL", "Enganxa una URL de YouTube.")
            return

        if not carpeta:
            messagebox.showwarning("Falta la carpeta", "Selecciona una carpeta de destinació.")
            return

        self.download_btn.config(state="disabled")
        self.status_var.set("Preparant descàrrega...")
        self.title_var.set("")

        threading.Thread(target=self.descargar, args=(url, carpeta), daemon=True).start()

    def actualizar_estado(self, text):
        self.root.after(0, self.status_var.set, text)

    def actualizar_titulo(self, text):
        self.root.after(0, self.title_var.set, text)

    def habilitar_boto(self):
        self.root.after(0, lambda: self.download_btn.config(state="normal"))

    def hook_progreso(self, d):
        status = d.get("status")

        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                percent = downloaded * 100 / total
                self.actualizar_estado(f"Descarregant... {percent:.1f}%")
            else:
                self.actualizar_estado("Descarregant àudio...")

        elif status == "finished":
            self.actualizar_estado("Convertint a MP3 i afegint caràtula...")

    def descargar(self, url, carpeta):
        try:
            Path(carpeta).mkdir(parents=True, exist_ok=True)

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": str(Path(carpeta) / "%(title)s.%(ext)s"),
                "noplaylist": True,
                "writethumbnail": True,
                "prefer_ffmpeg": True,
                "ffmpeg_location": self.ffmpeg_exe,
                "progress_hooks": [self.hook_progreso],
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
                info = ydl.extract_info(url, download=True)
                title = info.get("title", "Arxiu descarregat")

            self.actualizar_estado("Descàrrega completada.")
            self.actualizar_titulo(f"Guardat: {title}")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Fet",
                    f"MP3 descarregat correctament.\n\nTítol: {title}\nCarpeta: {carpeta}"
                )
            )

        except Exception as e:
            self.actualizar_estado("Error en la descàrrega.")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        finally:
            self.habilitar_boto()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeMP3App(root)
    root.mainloop()