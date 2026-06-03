# SENTINEL - AI GitHub Repository Analyzer

SENTINEL is a powerful AI-driven tool that uses 5 specialized agents to analyze any public GitHub repository for bugs, security vulnerabilities, architecture patterns, documentation gaps, and dependency risks.

## Architecture

```text
POST /analyze
    │
    ▼
orchestrator.py
    │
    ▼
asyncio.gather()
    │
    ├──► Code Quality Agent ──┐
    ├──► Security Agent ──────┤
    ├──► Architecture Agent ──┼──► Mercury-2 LLM
    ├──► Documentation Agent ─┤
    └──► Dependency Agent ────┘
                                  │
                                  ▼
                        AnalysisReport JSON
```

## Features
- **Code Quality Agent:** Finds bugs, bad practices, and missing error handling.
- **Security Agent:** Detects hardcoded secrets, SQL injection, and unsafe operations.
- **Architecture Agent:** Identifies god classes, circular dependencies, and refactoring needs.
- **Documentation Agent:** Flags missing docstrings and poor naming conventions.
- **Dependency Agent:** Analyzes `requirements.txt` for vulnerabilities and versioning issues.

## Tech Stack
- **Framework:** FastAPI
- **Concurrency:** Python asyncio
- **AI Model:** Mercury-2 LLM
- **Data Validation:** Pydantic
- **Deployment:** Docker
- **Frontend (Dashboard):** Streamlit

## Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**
   Create a `.env` file based on `.env.example` and add your keys:
   - `MERCURY_API_KEY`: Your Mercury-2 API key
   - `MERCURY_BASE_URL`: Base URL for the Mercury API
   - `SERVICE_API_KEY`: Key to authenticate against the Sentinel API
   - `GITHUB_TOKEN`: (Optional but recommended) Your GitHub Personal Access Token.

4. **Run the Application:**
   ```bash
   python main.py
   ```

## API Usage

### Health Check
`GET /`
Returns the status of the service.

### Analyze Repository
`POST /analyze`
**Headers:**
- `X-API-Key`: Your configured `SERVICE_API_KEY`

**Payload:**
```json
{
  "github_url": "https://github.com/owner/repo"
}
```
**Response:**
A detailed `AnalysisReport` JSON containing findings from all 5 agents.

## Docker Support
Build and run using Docker:
```bash
docker build -t sentinel .
docker run -p 8000:8000 --env-file .env sentinel
```
