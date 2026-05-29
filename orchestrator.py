import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from github_reader import read_repo
from agents import (
    code_quality_agent,
    security_agent,
    architecture_agent,
    documentation_agent,
    dependency_agent
)
from models import AnalysisReport, AgentResult

def run_analysis(github_url: str) -> AnalysisReport:
    """
    Orchestrates the analysis by calling the reader and all 5 agents sequentially.
    """
    # 1. Read Repo
    repo_data = read_repo(github_url)
    files = repo_data["files"]
    requirements = repo_data["requirements"]
    repo_name = repo_data["repo_name"]

    # 2. Run Agents Sequentially
    results = []
    
    print("Running Code Quality Agent...")
    results.append(code_quality_agent.analyze(files))
    
    print("Running Security Agent...")
    results.append(security_agent.analyze(files))
    
    print("Running Architecture Agent...")
    results.append(architecture_agent.analyze(files))
    
    print("Running Documentation Agent...")
    results.append(documentation_agent.analyze(files))
    
    print("Running Dependency Agent...")
    results.append(dependency_agent.analyze(requirements))

    # 3. Calculate Totals
    total_issues = sum(r.findings_count for r in results)

    # 4. Generate Summary using Mercury
    api_key = os.getenv("MERCURY_API_KEY")
    base_url = os.getenv("MERCURY_BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key, 
        base_url=base_url, 
        model="mercury-2"
    )
    
    summary_prompt = f"""
    Based on {total_issues} issues found across 5 analysis categories (Code Quality, Security, Architecture, Documentation, Dependencies) 
    in the repository {repo_name}, provide a concise 2-sentence overall assessment summary.
    """
    
    try:
        summary_response = llm.invoke(summary_prompt)
        summary = summary_response.content.strip()
    except Exception as e:
        summary = f"Analysis completed with {total_issues} total issues found. Summary generation failed due to: {e}"

    return AnalysisReport(
        repo_url=github_url,
        repo_name=repo_name,
        total_issues=total_issues,
        agents=results,
        summary=summary
    )
