from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CodeIssue(BaseModel):
    file: str
    line: str
    issue: str
    severity: str
    suggestion: str

class SecurityVulnerability(BaseModel):
    file: str
    type: str
    description: str
    severity: str
    fix: str

class ArchIssue(BaseModel):
    file: str
    issue: str
    pattern: str
    suggestion: str

class DocIssue(BaseModel):
    file: str
    element: str
    problem: str

class DepIssue(BaseModel):
    package: str
    current_version: str
    issue: str
    recommendation: str

class AgentResult(BaseModel):
    agent_name: str
    status: str
    findings_count: int
    findings: List[dict]
    error: Optional[str] = None

class AnalysisReport(BaseModel):
    repo_url: str
    repo_name: str
    analyzed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_issues: int
    agents: List[AgentResult]
    summary: str
