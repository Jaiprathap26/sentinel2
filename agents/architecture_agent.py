import os
import time
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import AgentResult, ArchIssue

def analyze(files: list) -> AgentResult:
    api_key = os.getenv("MERCURY_API_KEY")
    base_url = os.getenv("MERCURY_BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key, 
        base_url=base_url, 
        model="mercury-2"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a software architect. Identify god classes, circular dependencies, long functions (>40 lines), and poor separation of concerns. Return only a JSON list: [{{'file': 'filename', 'issue': 'description', 'pattern': 'anti-pattern_name', 'suggestion': 'how to refactor'}}]"),
        ("human", "File: {path}\nContent:\n{content}")
    ])
    
    findings = []
    for file in files:
        try:
            chain = prompt | llm
            response = None
            for attempt in range(2):
                try:
                    response = chain.invoke({"path": file["path"], "content": file["content"]})
                    break
                except Exception as e:
                    if "rate_limit" in str(e).lower() and attempt == 0:
                        time.sleep(2)
                        continue
                    raise e
            
            if response:
                content = response.content
                if "[" in content and "]" in content:
                    content = content[content.find("["):content.rfind("]")+1]
                file_findings = json.loads(content)
                findings.extend(file_findings)
        except Exception as e:
            print(f"Error in Architecture Agent for {file['path']}: {e}")
            continue

    return AgentResult(
        agent_name="Architecture",
        status="Success",
        findings_count=len(findings),
        findings=findings
    )
