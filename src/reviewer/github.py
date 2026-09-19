import httpx

from .config import GITHUB_TOKEN

API = "https://api.github.com"


def _headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_pr_files(repo: str, pr_number: int) -> list[dict]:
    """Return the changed files of a PR, each with its diff patch.

    repo is "owner/name". patch is None for binary or very large files.
    """
    files: list[dict] = []
    page = 1
    with httpx.Client(headers=_headers(), timeout=30) as client:
        while True:
            resp = client.get(
                f"{API}/repos/{repo}/pulls/{pr_number}/files",
                params={"per_page": 100, "page": page},
            )
            resp.raise_for_status()
            batch = resp.json()
            for f in batch:
                files.append(
                    {
                        "filename": f["filename"],
                        "status": f["status"],
                        "additions": f["additions"],
                        "deletions": f["deletions"],
                        "patch": f.get("patch"),
                    }
                )
            if len(batch) < 100:
                break
            page += 1
    return files