import sys

from src.reviewer.github import fetch_pr_files
from src.reviewer.nodes.reviewer import review_files

repo = sys.argv[1]
pr_number = int(sys.argv[2])

files = fetch_pr_files(repo, pr_number)
print(f"Fetched {len(files)} files")

findings = review_files(files)
print(f"Found {len(findings)} findings")
for f in findings:
    print(f"[{f.severity}] {f.category} {f.file}:{f.line}")
    print(f"  {f.message}")
    if f.suggestion:
        print(f"  Suggestion: {f.suggestion}")