# Eval: Multi-agent graph vs. single-prompt baseline

Ran both pipelines against 4 real merged PRs from this repo (see `evals/dataset.py`), using Groq's `openai/gpt-oss-120b`.

| PR | baseline findings | graph raw | graph final | graph LLM calls |
|---|---|---|---|---|
| models + state (#2) | 0 | 1 | 1 | 3 |
| GitHub fetch tool (#4) | 1 | 6 | 6 | 4 |
| first reviewer node (#6) | 2 | 6 | 6 | 4 |
| parallel specialists (#10) | 0 | 5 | 5 | 4 |
| **Total** | **3** | **18** | **18** | — |

**Findings:** the multi-agent graph found 18 issues across the 4 PRs vs. 3 from a single general-purpose prompt on the same diffs — a 6x increase. This matches the hypothesis behind splitting into specialists: a reviewer told to look only for security problems (or only bugs, or only maintainability) catches more than one reviewer told to look for everything at once.

**Verifier:** no hallucinated findings were detected in either pipeline on this run (0 out of 21 total findings pointed at a file/line that didn't exist in the diff). The verifier's deduplication logic (same file+line+category) has been confirmed working in isolated testing — it dropped a real duplicate `sys.argv` finding in an earlier manual run on PR #4, where it reduced 7 raw findings to 6.

**Cost:** the graph makes 3-4 LLM calls per PR (triage + up to 3 specialists) vs. 1 for the baseline — roughly 3-4x the API cost for roughly 6x the findings. Triage leans toward running all three specialists when uncertain, by design (see `TRIAGE_PROMPT`), so the cost savings from triage are modest on these PRs; it would matter more on a larger, more varied dataset with some genuinely trivial PRs (typo fixes, version bumps).

**Known limitation:** the model used (`openai/gpt-oss-120b` via Groq) occasionally fails to produce valid structured output under load — a `BadRequestError` rather than the `RateLimitError` the retry logic was originally built for. Both are now caught and retried (see `_invoke_with_retry` in `src/reviewer/nodes/reviewer.py`), but on rare occasions the model fails 5 times in a row and the call still raises.