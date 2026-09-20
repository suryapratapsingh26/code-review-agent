import sys

from src.reviewer.graph import build_graph

repo = sys.argv[1]
pr_number = int(sys.argv[2])

graph = build_graph()
result = graph.invoke({"repo": repo, "pr_number": pr_number, "findings": []})

print(f"Fetched {len(result['diff_files'])} files")
print(f"Found {len(result['findings'])} findings")
for f in result["findings"]:
    print(f"[{f.severity}] {f.category} {f.file}:{f.line}")
    print(f"  {f.message}")
    if f.suggestion:
        print(f"  Suggestion: {f.suggestion}")