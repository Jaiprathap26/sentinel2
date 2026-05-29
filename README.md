# SENTINEL - AI GitHub Repository Analyzer

SENTINEL is a powerful AI-driven tool that uses 5 specialized agents to analyze any public GitHub repository for bugs, security vulnerabilities, architecture patterns, documentation gaps, and dependency risks.

## Features
- **Code Quality Agent:** Finds bugs, bad practices, and missing error handling.
- **Security Agent:** Detects hardcoded secrets, SQL injection, and unsafe operations.
- **Architecture Agent:** Identifies god classes, circular dependencies, and refactoring needs.
- **Documentation Agent:** Flags missing docstrings and poor naming conventions.
- **Dependency Agent:** Analyzes `requirements.txt` for vulnerabilities and versioning issues.

## Setup

1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**
   Create a `.env` file based on `.env.example` and add your keys:
   - `GROQ_API_KEY`: Get from [Groq Console](https://console.groq.com/)
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
