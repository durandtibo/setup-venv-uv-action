#!/usr/bin/env python3
"""Rewrite the table of the inputs of README.md from action.yaml.

The table is the text between the lines ``<!-- inputs:start -->`` and
``<!-- inputs:end -->`` of the README. Names, descriptions, required flags and
defaults come from ``action.yaml``, so that they cannot drift apart.
Quoted tokens of a description ('true') become code spans (`true`).

Usage: scripts/generate-readme-inputs.py ACTION_YAML README_MD
"""

import re
import sys
from pathlib import Path

START = "<!-- inputs:start -->"
END = "<!-- inputs:end -->"


def read_inputs(action: str) -> list[dict[str, str]]:
    """Read the inputs of a simple ``inputs:`` block (one scalar per line)."""
    block = re.search(r"^inputs:\n(.*?)^\S", action, flags=re.S | re.M)
    if block is None:
        sys.exit("no 'inputs:' block in action.yaml")
    inputs = []
    for entry in re.split(r"(?m)^  (?=[a-z][a-z-]*:\n)", block.group(1))[1:]:
        name = entry.split(":", 1)[0]
        fields = dict(re.findall(r'(?m)^    (\w+): "?(.*?)"?$', entry))
        inputs.append({"name": name, **fields})
    return inputs


def render(inputs: list[dict[str, str]]) -> str:
    """Render the Markdown table."""
    lines = [
        "| Input | Description | Required | Default |",
        "| --- | --- | --- | --- |",
    ]
    for item in inputs:
        description = re.sub(r"'([^']*)'", r"`\1`", item["description"])
        required = "Yes" if item.get("required") == "true" else "No"
        default = f'`"{item.get("default", "")}"`'
        lines.append(f"| `{item['name']}` | {description} | {required} | {default} |")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    inputs = read_inputs(Path(sys.argv[1]).read_text())
    readme_path = Path(sys.argv[2])
    readme = readme_path.read_text()
    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", flags=re.S)
    if not pattern.search(readme):
        sys.exit(f"{START} and {END} not found in {readme_path}")
    table = f"{START}\n\n{render(inputs)}\n\n{END}"
    readme_path.write_text(pattern.sub(lambda _: table, readme))


if __name__ == "__main__":
    main()
