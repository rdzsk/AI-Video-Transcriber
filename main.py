from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
from backend.pipe import Pipeline
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    video_url:str
    typ:str

@app.post("/summarize")
async def summarize(request: VideoRequest):
    pipeline = Pipeline(request.video_url,request.typ)
    result = pipeline.run()
    return result

if __name__ == "__main__":
    uvicorn.run("main:app",reload=True) 
