import sys
from collections import defaultdict

from src.reviewer.graph import build_graph

repo = sys.argv[1]
pr_number = int(sys.argv[2])

graph = build_graph()
result = graph.invoke({"repo": repo, "pr_number": pr_number, "findings": []})

print(f"Fetched {len(result['diff_files'])} files")
print(f"Found {len(result['findings'])} findings")

by_category = defaultdict(list)
for f in result["findings"]:
    by_category[f.category].append(f)

for category in ("security", "bug", "maintainability"):
    findings = by_category[category]
    print(f"\n-- {category} ({len(findings)}) --")
    for f in findings:
        print(f"[{f.severity}] {f.file}:{f.line}")
        print(f"  {f.message}")
        if f.suggestion:
            print(f"  Suggestion: {f.suggestion}")