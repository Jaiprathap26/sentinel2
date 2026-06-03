from loguru import logger
import os
from github import Github, GithubException
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

def read_repo(github_url: str) -> dict:
    """
    Parses GitHub URL, extracts owner/repo, and reads .py files and requirements.txt.
    """
    try:
        path = urlparse(github_url).path.strip("/")
        parts = path.split("/")
        if len(parts) < 2:
            raise ValueError("Invalid GitHub URL. Expected format: https://github.com/owner/repo")
        
        owner, repo_name = parts[0], parts[1]
        
        token = os.getenv("GITHUB_TOKEN")
        g = Github(token) if token else Github()
        
        repo = g.get_repo(f"{owner}/{repo_name}")
        
        files_data = []
        requirements_content = ""
        
        # Get all contents recursively
        contents = repo.get_contents("")
        py_files_count = 0
        
        while contents and py_files_count < 20:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                if file_content.name == "requirements.txt":
                    requirements_content = file_content.decoded_content.decode("utf-8")
                
                if file_content.name.endswith(".py") and py_files_count < 20:
                    try:
                        decoded = file_content.decoded_content.decode("utf-8")
                        files_data.append({
                            "path": file_content.path,
                            "content": decoded
                        })
                        py_files_count += 1
                    except Exception:
                        continue # Skip binary or non-utf8 files
        
        return {
            "files": files_data,
            "requirements": requirements_content,
            "repo_name": f"{owner}/{repo_name}"
        }
    except Exception as e:
        logger.error(f"Error reading repo: {e}")
        raise e
