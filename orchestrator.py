import os
import asyncio
from datetime import datetime
from typing import Optional, Callable, Awaitable
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

async def run_analysis(github_url: str, on_progress: Optional[Callable[[dict], Awaitable[None]]] = None) -> AnalysisReport:
    """
    Orchestrates the analysis by calling the reader and all 5 agents in parallel.
    """
    # 1. Read Repo (Synchronous call, typically fast enough or could be wrapped too)
    repo_data = read_repo(github_url)
    files = repo_data["files"]
    requirements = repo_data["requirements"]
    repo_name = repo_data["repo_name"]

    # 2. Helper to run agent with progress reporting
    async def run_agent(agent_fn, agent_name, *args):
        if on_progress:
            await on_progress({"event": "agent_start", "agent": agent_name})
        
        # Agents are currently synchronous, so we run them in a thread pool
        result = await asyncio.to_thread(agent_fn, *args)
        
        if on_progress:
            await on_progress({"event": "agent_done", "agent": agent_name, "findings": result.findings_count})
        return result

    # 3. Run all agents in parallel
    tasks = [
        run_agent(code_quality_agent.analyze, "Code Quality", files),
        run_agent(security_agent.analyze, "Security", files),
        run_agent(architecture_agent.analyze, "Architecture", files),
        run_agent(documentation_agent.analyze, "Documentation", files),
        run_agent(dependency_agent.analyze, "Dependency", requirements)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results to handle exceptions gracefully
    processed_results = []
    agent_names = ["Code Quality", "Security", "Architecture", "Documentation", "Dependency"]
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append(
                AgentResult(
                    agent_name=agent_names[i],
                    status="failed",
                    findings_count=0,
                    findings=[],
                    error=str(result)
                )
            )
        else:
            processed_results.append(result)

    results = processed_results

    # 4. Calculate Totals
    total_issues = sum(r.findings_count for r in results)

    # 5. Generate Summary using Mercury
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
        # Using ainvoke for async LLM call
        summary_response = await llm.ainvoke(summary_prompt)
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
