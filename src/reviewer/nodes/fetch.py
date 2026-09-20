from ..github import fetch_pr_files
from ..state import ReviewState


def fetch_node(state: ReviewState) -> dict:
    files = fetch_pr_files(state["repo"], state["pr_number"])
    return {"diff_files": files}