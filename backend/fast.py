from faster_whisper import WhisperModel

class Transcribe:
    def __init__(self, video_id , cpu_or_gpu):
        self.video_id = video_id
        self.cpu_or_gpu = cpu_or_gpu

    @staticmethod
    def format_time(seconds: float):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02}:{minutes:02}:{secs:06.3f}"
    
    def audio_to_txt(self):
        model = WhisperModel("base", device=self.cpu_or_gpu)

        segments, info = model.transcribe(f"downloads/{self.video_id}.mp3")
    
    
        with open(f"{self.video_id}.vtt", "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n")
    
            for i, segment in enumerate(segments):
                start = segment.start
                end = segment.end
                text = segment.text.strip()
    
                f.write(f"{i+1}\n")
                f.write(f"{self.format_time(start)} --> {self.format_time(end)}\n")
                f.write(f"{text}\n\n")
