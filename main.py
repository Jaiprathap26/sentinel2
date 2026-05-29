from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import orchestrator
from models import AnalysisReport

app = FastAPI(title="SENTINEL - AI GitHub Analyzer", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    github_url: str

@app.get("/")
async def root():
    return {"status": "SENTINEL is online", "version": "1.0.0"}

@app.post("/analyze", response_model=AnalysisReport)
async def analyze_repo(request: AnalysisRequest):
    try:
        report = orchestrator.run_analysis(request.github_url)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
