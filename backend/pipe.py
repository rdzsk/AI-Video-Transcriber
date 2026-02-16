import os
from pathlib import Path
from backend.youtube import Youtube
from backend.summarize import Summarize
from backend.fast import Transcribe


class Pipeline:
    def __init__(self,video_url,cpu_or_gpu):

        self.video_url = video_url
        youtube = Youtube(video_url)

        self.cpu_or_gpu = cpu_or_gpu
        self.project_root = Path.cwd()
        self.download_dir = self.project_root / "downloads"

        self.video_id =youtube.download_video() 
        self.video_file=self.download_dir/f"{self.video_id}.mp3"

    def run(self):
        try:
            video_summary = Summarize(self.video_id)

            transcribe = Transcribe(self.video_id ,self.cpu_or_gpu)

            transcribe.audio_to_txt()
            return {
                "summary":video_summary.vtt_to_txt()
            }
        except Exception as e:
            print(f"ERROR: {e}")

        finally:
            Path(self.video_file).unlink()
            Path(self.project_root / f"{self.video_id}.vtt").unlink()




