import sys
import io

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import time

from src.reviewer.diff import valid_lines
from src.reviewer.github import fetch_pr_files
from src.reviewer.graph import build_graph
from evals.baseline import baseline_review
from evals.dataset import DATASET


def hallucination_count(findings, diff_files) -> int:
    lines_by_file = {f["filename"]: valid_lines(f["patch"]) for f in diff_files if f.get("patch")}
    bad = 0
    for f in findings:
        valid = lines_by_file.get(f.file)
        if valid is None or f.line not in valid:
            bad += 1
    return bad


def run():
    graph = build_graph()
    rows = []

    for i, entry in enumerate(DATASET):
        if i > 0:
            print("(pausing to stay under Groq's per-minute rate limit...)")
            time.sleep(30)

        repo, pr_number, label = entry["repo"], entry["pr_number"], entry["label"]
        print(f"--- Running: {label} (PR #{pr_number}) ---")
        diff_files = fetch_pr_files(repo, pr_number)

        t0 = time.time()
        baseline_findings = baseline_review(diff_files)
        baseline_time = time.time() - t0
        baseline_bad = hallucination_count(baseline_findings, diff_files)

        t0 = time.time()
        result = graph.invoke({
            "repo": repo, "pr_number": pr_number, "findings": [], "dry_run": True,
        })
        graph_time = time.time() - t0
        graph_findings = result["findings"]
        graph_final = result["final_findings"]
        graph_calls = 1 + len(result["reviewers_to_run"])

        rows.append({
            "label": label,
            "baseline_count": len(baseline_findings),
            "baseline_bad": baseline_bad,
            "baseline_time": baseline_time,
            "graph_raw_count": len(graph_findings),
            "graph_final_count": len(graph_final),
            "graph_calls": graph_calls,
            "graph_time": graph_time,
        })
        print(f"  done: baseline={len(baseline_findings)}, graph_raw={len(graph_findings)}, graph_final={len(graph_final)}")

    print()
    print(f"{'PR':<22} {'baseline':>10} {'base-bad':>9} {'graph-raw':>10} {'graph-final':>12} {'graph-calls':>12}")
    for r in rows:
        print(f"{r['label']:<22} {r['baseline_count']:>10} {r['baseline_bad']:>9} "
              f"{r['graph_raw_count']:>10} {r['graph_final_count']:>12} {r['graph_calls']:>12}")

    total_baseline = sum(r["baseline_count"] for r in rows)
    total_baseline_bad = sum(r["baseline_bad"] for r in rows)
    total_graph_raw = sum(r["graph_raw_count"] for r in rows)
    total_graph_final = sum(r["graph_final_count"] for r in rows)
    total_baseline_time = sum(r["baseline_time"] for r in rows)
    total_graph_time = sum(r["graph_time"] for r in rows)

    print()
    print(f"Totals: baseline findings={total_baseline} (hallucinated={total_baseline_bad}), "
          f"graph raw={total_graph_raw}, graph final={total_graph_final}")
    print(f"Time: baseline={total_baseline_time:.1f}s, graph={total_graph_time:.1f}s")


if __name__ == "__main__":
    run()