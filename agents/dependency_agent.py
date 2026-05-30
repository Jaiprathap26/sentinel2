import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import AgentResult, DepIssue
from .utils import extract_json

def analyze(requirements: str) -> AgentResult:
    if not requirements:
        return AgentResult(agent_name="Dependencies", status="Success", findings_count=0, findings=[])

    api_key = os.getenv("MERCURY_API_KEY")
    base_url = os.getenv("MERCURY_BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key, 
        base_url=base_url, 
        model="mercury-2"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a DevOps engineer specializing in supply chain security. Review the requirements.txt and flag outdated packages, known vulnerable versions, and missing version pins. Return only a JSON list: [{{'package': 'name', 'current_version': 'version', 'issue': 'description', 'recommendation': 'how to fix'}}]"),
        ("human", "Requirements Content:\n{content}")
    ])
    
    findings = []
    try:
        chain = prompt | llm
        response = None
        for attempt in range(2):
            try:
                response = chain.invoke({"content": requirements})
                break
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt == 0:
                    time.sleep(2)
                    continue
                raise e
        
        if response:
            findings = extract_json(response.content)
    except Exception as e:
        print(f"Error in Dependency Agent: {e}")
        return AgentResult(agent_name="Dependencies", status="Error", findings_count=0, findings=[])

    return AgentResult(
        agent_name="Dependencies",
        status="Success",
        findings_count=len(findings),
        findings=findings
    )
