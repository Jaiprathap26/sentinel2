import os
import time
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models import AgentResult, DocIssue

def analyze(files: list) -> AgentResult:
    api_key = os.getenv("MERCURY_API_KEY")
    base_url = os.getenv("MERCURY_BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key, 
        base_url=base_url, 
        model="mercury-2"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical documentation specialist. Find functions/classes without docstrings and unclear variable names (single letters, 'temp', 'data', 'x', etc). Return only a JSON list: [{{'file': 'filename', 'element': 'name_of_element', 'problem': 'description of documentation gap'}}]"),
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
            print(f"Error in Documentation Agent for {file['path']}: {e}")
            continue

    return AgentResult(
        agent_name="Documentation",
        status="Success",
        findings_count=len(findings),
        findings=findings
    )
