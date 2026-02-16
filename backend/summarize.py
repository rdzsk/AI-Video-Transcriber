from google import genai
import os 

class Summarize:
    def __init__(self,video_id):
        self.video_id = video_id
        self.API = os.getenv("GEMINI_API")

        self.client = genai.Client(api_key=self.API)


    def vtt_to_txt(self):
        with open(f"{self.video_id}.vtt",'rb') as f:
            file = f.read()
        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=f"Make a summarize with timecodes in markdown (LANGUAGE SAME WITH TEXT): {file}",
        )
        return response.text
