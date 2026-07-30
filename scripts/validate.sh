#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
linus_python="${LINUS_PYTHON:-python3}"

"$linus_python" -m unittest discover -s "$repo_root/tests" -v
"$linus_python" -m py_compile "$repo_root/hooks/linus_runtime.py"

"$linus_python" - "$repo_root" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
json_paths = [
    root / ".codex-plugin/plugin.json",
    root / ".claude-plugin/plugin.json",
    root / ".claude-plugin/marketplace.json",
    root / ".factory-plugin/plugin.json",
    root / ".factory-plugin/marketplace.json",
    root / ".github/plugin/marketplace.json",
    root / "gemini-extension.json",
    root / "hooks/hooks.json",
    root / "marketplace.example.json",
]
documents = {}
for path in json_paths:
    documents[path] = json.loads(path.read_text(encoding="utf-8"))

versions = {
    documents[root / ".codex-plugin/plugin.json"]["version"],
    documents[root / ".claude-plugin/plugin.json"]["version"],
    documents[root / ".factory-plugin/plugin.json"]["version"],
    documents[root / ".github/plugin/marketplace.json"]["metadata"]["version"],
    documents[root / ".github/plugin/marketplace.json"]["plugins"][0]["version"],
    documents[root / "gemini-extension.json"]["version"],
}
if len(versions) != 1:
    raise SystemExit(f"Version mismatch across plugin manifests: {sorted(versions)}")

hook_events = set(documents[root / "hooks/hooks.json"]["hooks"])
expected_events = {
    "SessionStart",
    "UserPromptSubmit",
    "SubagentStart",
    "Stop",
    "SessionEnd",
}
if hook_events != expected_events:
    raise SystemExit(
        f"Unexpected hook events: expected {sorted(expected_events)}, "
        f"found {sorted(hook_events)}"
    )

skill_path = root / "skills/linus-level/SKILL.md"
skill_text = skill_path.read_text(encoding="utf-8")
frontmatter_match = re.match(r"\A---\n(.*?)\n---\n", skill_text, re.DOTALL)
if not frontmatter_match:
    raise SystemExit("SKILL.md frontmatter is missing or malformed")
frontmatter_keys = {
    line.split(":", 1)[0].strip()
    for line in frontmatter_match.group(1).splitlines()
    if ":" in line
}
if frontmatter_keys != {"name", "description"}:
    raise SystemExit(
        "SKILL.md frontmatter must contain only name and description; "
        f"found {sorted(frontmatter_keys)}"
    )

for reference in sorted(set(re.findall(r"`(references/[^`]+\.md)`", skill_text))):
    if not (skill_path.parent / reference).is_file():
        raise SystemExit(f"Missing referenced skill file: {reference}")

print(f"Static validation passed for Linus Level {next(iter(versions))}.")
PY

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$repo_root"
else
  printf '%s\n' "Claude CLI not found; skipped Claude marketplace validation."
fi

printf '%s\n' "Linus Level validation passed."
