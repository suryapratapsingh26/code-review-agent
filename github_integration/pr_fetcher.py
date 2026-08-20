import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def parse_pr_url(pr_url: str):
    """
    Extracts owner, repo, and PR number from a GitHub PR URL.
    Example: https://github.com/owner/repo/pull/5
    """
    parts = pr_url.rstrip("/").split("/")
    owner = parts[-4]
    repo = parts[-3]
    pr_number = parts[-1]
    return owner, repo, pr_number


def fetch_pr_diff(pr_url: str):
    """
    Fetches the diff and changed files for a given GitHub PR URL.
    Returns a dict matching our ReviewState shape: diff, files_changed.
    """
    owner, repo, pr_number = parse_pr_url(pr_url)

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }

    diff_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    response = requests.get(diff_url, headers=headers)
    response.raise_for_status()
    diff_text = response.text

    files_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
    files_response = requests.get(files_url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}"})
    files_response.raise_for_status()
    files_data = files_response.json()
    files_changed = [f["filename"] for f in files_data]

    return {
        "diff": diff_text,
        "files_changed": files_changed
    }