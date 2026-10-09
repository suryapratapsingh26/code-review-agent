import httpx

from .config import GITHUB_TOKEN, GITHUB_WRITE_TOKEN

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


def post_review(repo: str, pr_number: int, findings: list, dry_run: bool = True) -> dict | None:
    """Post final_findings as a single GitHub review with one comment per finding.

    Each Finding becomes one inline review comment. dry_run=True (the default)
    prints what would be posted and makes no API call.
    """
    if not findings:
        if dry_run:
            print("[dry-run] No findings to post.")
        return None

    comments = [
        {
            "path": f.file,
            "line": f.line,
            "body": f"**[{f.severity}] {f.category}**: {f.message}"
            + (f"\n\nSuggestion: {f.suggestion}" if f.suggestion else ""),
        }
        for f in findings
    ]
    body = f"Automated review: {len(findings)} finding(s)."

    if dry_run:
        print(f"[dry-run] Would post a review with {len(comments)} comment(s):")
        for c in comments:
            print(f"  {c['path']}:{c['line']} - {c['body'][:80]}")
        return None

    write_headers = _headers()
    write_headers["Authorization"] = f"Bearer {GITHUB_WRITE_TOKEN}"
    with httpx.Client(headers=write_headers, timeout=30) as client:
        resp = client.post(
            f"{API}/repos/{repo}/pulls/{pr_number}/reviews",
            json={"body": body, "event": "COMMENT", "comments": comments},
        )
        resp.raise_for_status()
        return resp.json()