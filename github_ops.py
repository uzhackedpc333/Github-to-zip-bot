import requests
import re
from config import GITHUB_TOKEN

def parse_url(url: str):
    """Extracts owner and repo from a GitHub URL."""
    match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$', url)
    return (match.group(1), match.group(2)) if match else (None, None)

def get_latest_zipball(owner: str, repo: str) -> dict:
    """Gets the DIRECT DOWNLOAD URL for the latest commit zip."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        response = requests.get(url, headers=headers, params={"per_page": 1}, timeout=10)
        response.raise_for_status()
        data = response.json()[0]
        return {
            "sha": data["sha"],
            "message": data["commit"]["message"].split('\n')[0],
            "zip_url": f"https://api.github.com/repos/{owner}/{repo}/zipball/{data['sha']}"
        }
    except Exception:
        return None
