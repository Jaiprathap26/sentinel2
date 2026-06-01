from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import orchestrator
import json
import os
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
        # Await the async run_analysis
        report = await orchestrator.run_analysis(request.github_url)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/analyze/stream")
async def analyze_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        # 1. Receive initial message with github_url
        data = await websocket.receive_text()
        request_json = json.loads(data)
        github_url = request_json.get("github_url")
        
        if not github_url:
            await websocket.send_text(json.dumps({"error": "github_url is required"}))
            await websocket.close()
            return

        # 2. Define progress callback for the orchestrator
        async def on_progress(event_dict: dict):
            await websocket.send_text(json.dumps(event_dict))

        # 3. Run analysis with progress reporting
        report = await orchestrator.run_analysis(github_url, on_progress=on_progress)

        # 4. Send completion event
        # Note: AnalysisReport needs to be converted to dict for JSON serialization
        await websocket.send_text(json.dumps({
            "event": "complete", 
            "report": report.model_dump()
        }))
        
    except WebSocketDisconnect:
        print("WebSocket client disconnected")
    except Exception as e:
        error_msg = {"event": "error", "detail": str(e)}
        await websocket.send_text(json.dumps(error_msg))
    finally:
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
