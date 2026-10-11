# Code Review Agent

This is an AI tool that automatically reviews GitHub pull requests. You run it from the command line and tell it which PR to look at (just the repo name and PR number — no link-pasting, no UI). It reads the code changes, finds problems like bugs, security issues, and messy code, and posts comments right on the PR, the same way a human reviewer would.

## How it works

The review happens in steps:

1. **Fetch** — grabs the changed files and the diff from GitHub.
2. **Triage** — a quick AI check decides which kinds of review actually matter for this PR. A tiny typo fix doesn't need a full security review.
3. **Specialist reviewers** — three focused AI reviewers run at the same time, each looking for only one thing:
   - a **security** reviewer (unsafe code, leaked secrets, injection attacks)
   - a **bug** reviewer (logic errors, crashes, bad error handling)
   - a **maintainability** reviewer (messy code, magic numbers, confusing logic)
4. **Verifier** — double-checks every finding against the real code. If the AI made up a line number, or two reviewers flagged the exact same thing, this step cleans that up.
5. **Publish** — posts the final list as real comments on the GitHub PR. By default it only prints what it *would* post, so nothing goes live by accident.

```
fetch → triage → (security + bug + maintainability) → verifier → publish
```

## See it in action

This agent reviewed its own code and posted real comments here: [PR #4](https://github.com/suryapratapsingh26/code-review-agent/pull/4)

## Running it yourself

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file with:

```
GITHUB_TOKEN=a GitHub token (read-only is fine)
GROQ_API_KEY=your Groq API key
GITHUB_WRITE_TOKEN=a GitHub token with write access (only needed if you want to actually post comments)
```

Then run it on any PR:

```
python run_graph.py owner/repo 123
```

This just shows what it found — nothing gets posted. To actually post the comments for real:

```
python run_graph.py owner/repo 123 --publish
```