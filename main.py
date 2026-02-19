from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from functools import partial
from backend.youtube import Youtube
from backend.summarize import Summarize
from backend.fast import Transcribe
import uvicorn
import uuid
import asyncio
import json
import os
from datetime import datetime
app = FastAPI()




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

HOME_PATH = Path.cwd()
JOB_FILE = "data.json"

with open(JOB_FILE, "r", encoding="utf-8") as f:
    jobs = json.load(f)

def save_jobs():
    with open(JOB_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=4)

app.mount("/static", StaticFiles(directory=str(HOME_PATH / "static")), name="static")

@app.get("/")
async def read_root():
    return FileResponse( str(HOME_PATH / "static/index.html"))

class VideoRequest(BaseModel):
    video_url: str
    typ: str



@app.post("/summarize")
async def summarize(request: VideoRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "queued","result":None,"created":str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),"input":request.video_url}
    save_jobs()
    asyncio.create_task(run_pipeline(request.video_url, request.typ, job_id))
    return {"job_id": job_id}


@app.get("/show")
async def show_all():
    return jobs



async def run_pipeline(video_url: str, typ: str, job_id: str):
    loop = asyncio.get_running_loop()

    try:
        youtube = Youtube(video_url)

        jobs[job_id]["status"] = "downloading"

        save_jobs()

        video_id = await loop.run_in_executor(None, youtube.download_video)
        
        video_summary = Summarize(video_id)
        transcribe = Transcribe(video_id, typ)
        
        jobs[job_id]["status"] = "transcribing"
        save_jobs()
        await loop.run_in_executor(None, transcribe.audio_to_txt)
        
        jobs[job_id]["status"] = "summarizing"
        save_jobs()
        summary = await loop.run_in_executor(None, video_summary.vtt_to_txt)
        
        jobs[job_id]["status"] = "done"
        jobs[job_id]["result"] = {"summary": summary}
        save_jobs()
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["result"] = str(e)
        save_jobs()
    finally:
        if video_id is not None:
            try:
                clear(video_id)
            except Exception as e:
                print(e)




@app.get("/events/jobs/{job_id}")
async def job_events(job_id: str):

    async def event_generator():
        last_payload = None
        while True:
            job = jobs.get(job_id)
            if not job:
                payload = {"status": "not_found"}
            else:
                payload = {"status": job.get("status")}
                if payload["status"] in ("done", "failed"):
                    payload["result"] = job.get("result")

            if payload != last_payload:
                data = json.dumps(payload, ensure_ascii=False)
                yield f"event: message\ndata: {data}\n\n"
                last_payload = payload

            if payload["status"] in ("done", "failed", "not_found"):
                break

            await asyncio.sleep(0.5)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)






def clear(video_id):
    (HOME_PATH / f"downloads/{video_id}.mp3").unlink()
    (HOME_PATH / f"{video_id}.vtt").unlink()

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

