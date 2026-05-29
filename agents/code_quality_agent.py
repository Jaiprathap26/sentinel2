import os
import time
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import AgentResult, CodeIssue

def analyze(files: list) -> AgentResult:
    api_key = os.getenv("MERCURY_API_KEY")
    base_url = os.getenv("MERCURY_BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key, 
        base_url=base_url, 
        model="mercury-2"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Python code quality reviewer. Analyze the provided code for bugs, undefined variables, missing error handling, and bad practices. Return only a JSON list of issues following this structure: [{{'file': 'filename', 'line': 'line_number', 'issue': 'description', 'severity': 'Low/Medium/High', 'suggestion': 'how to fix'}}]"),
        ("human", "File: {path}\nContent:\n{content}")
    ])
    
    findings = []
    for file in files:
        try:
            chain = prompt | llm
            # Retry logic
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
                # Basic JSON extraction in case the model adds chatter
                content = response.content
                if "[" in content and "]" in content:
                    content = content[content.find("["):content.rfind("]")+1]
                
                file_issues = json.loads(content)
                findings.extend(file_issues)
        except Exception as e:
            print(f"Error in Code Quality Agent for {file['path']}: {e}")
            continue

    return AgentResult(
        agent_name="Code Quality",
        status="Success",
        findings_count=len(findings),
        findings=findings
    )
