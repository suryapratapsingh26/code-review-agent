import re

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def annotate_patch(patch: str) -> str:
    """Prefix each line of a diff patch with its line number in the NEW file.

    Added (+) and context lines get a number. Removed (-) lines are not in
    the new file, so they get no number.
    """
    out = []
    new_line = 0
    for raw in patch.splitlines():
        match = HUNK_RE.match(raw)
        if match:
            new_line = int(match.group(1))  # where this block starts in the new file
            out.append(raw)
        elif raw.startswith("-"):
            out.append(f"     {raw}")
        elif raw.startswith(("+", " ")) or raw == "":
            out.append(f"{new_line:>4} {raw}")
            new_line += 1
        else:
            out.append(raw)  # e.g. "\ No newline at end of file"
    return "\n".join(out)