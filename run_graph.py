import sys
from collections import defaultdict

from src.reviewer.graph import build_graph

repo = sys.argv[1]
pr_number = int(sys.argv[2])
publish = "--publish" in sys.argv

graph = build_graph()
result = graph.invoke({"repo": repo, "pr_number": pr_number, "findings": [], "dry_run": not publish})

print(f"Fetched {len(result['diff_files'])} files")
print(f"Reviewers run: {result['reviewers_to_run']}")
raw_count = len(result["findings"])
final_count = len(result["final_findings"])
print(f"Raw findings: {raw_count}, after verification: {final_count} (dropped {raw_count - final_count})")

by_category = defaultdict(list)
for f in result["final_findings"]:
    by_category[f.category].append(f)

for category in ("security", "bug", "maintainability"):
    findings = by_category[category]
    print(f"\n-- {category} ({len(findings)}) --")
    for f in findings:
        print(f"[{f.severity}] {f.file}:{f.line}")
        print(f"  {f.message}")
        if f.suggestion:
            print(f"  Suggestion: {f.suggestion}")