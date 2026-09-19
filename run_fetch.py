import sys

from src.reviewer.github import fetch_pr_files

repo = sys.argv[1]
pr_number = int(sys.argv[2])

files = fetch_pr_files(repo, pr_number)
print(f"Fetched {len(files)} files")
for f in files:
    print(f["status"], f["filename"], f"+{f['additions']} -{f['deletions']}")
    print((f["patch"] or "<no patch>")[:300])
    print("-" * 40)