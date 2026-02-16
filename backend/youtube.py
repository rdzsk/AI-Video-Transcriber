import yt_dlp
from pathlib import Path
class Youtube:
    def __init__(self,video_url):
        self.video_url = video_url

    def download_video(self) -> str:
        output_dir = Path("downloads")
        output_dir.mkdir(exist_ok=True)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "js_runtimes": {"node": {}},
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "64",
                }
            ],
            "postprocessor_args": [
                "-ac", "1",
                "-ar", "16000",
            ],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.video_url, download=True)
            return info["id"]

