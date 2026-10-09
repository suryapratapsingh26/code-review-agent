from ..diff import valid_lines
from ..models import Finding
from ..state import ReviewState

SEVERITY_RANK = {"low": 0, "medium": 1, "high": 2}


def verify_findings(findings: list[Finding], diff_files: list[dict]) -> list[Finding]:
    lines_by_file = {
        f["filename"]: valid_lines(f["patch"])
        for f in diff_files
        if f.get("patch")
    }

    checked = []
    for f in findings:
        valid = lines_by_file.get(f.file)
        if valid is not None and f.line in valid:
            checked.append(f)
        # else: hallucinated file or line number, drop silently

    best_by_location: dict[tuple[str, int, str], Finding] = {}
    for f in checked:
        key = (f.file, f.line, f.category)
        current = best_by_location.get(key)
        if current is None or SEVERITY_RANK[f.severity] > SEVERITY_RANK[current.severity]:
            best_by_location[key] = f

    return list(best_by_location.values())


def verifier_node(state: ReviewState) -> dict:
    final = verify_findings(state["findings"], state["diff_files"])
    return {"final_findings": final}