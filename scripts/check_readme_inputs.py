r"""Check that the README documents the inputs and outputs of ``action.yaml``.

The check fails when an input or an output of the action is missing from the
tables of ``README.md``, when the README documents one that does not exist, or
when the default of an input differs between the two files. The order of the
rows is not checked. It only uses the standard library, so that it runs
without installing anything, and it reads ``action.yaml`` line by line, which
is enough for the flat ``inputs`` and ``outputs`` sections of the action.

Usage:
    python3 scripts/check_readme_inputs.py [ACTION_YAML [README_MD]]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

NAME_PATTERN = re.compile(r"^  ([a-z][a-z0-9-]*):\s*$")
DEFAULT_PATTERN = re.compile(r"^    default:\s*(.*?)\s*$")


def unquote(value: str) -> str:
    r"""Remove the backticks and the quotes around a value.

    Args:
        value: The value, such as ``"auto"`` or ```"auto"```.

    Returns:
        The value without the surrounding backticks and quotes.
    """
    return value.strip().strip("`").strip().strip("\"'")


def read_action(path: Path) -> tuple[dict[str, str | None], list[str]]:
    r"""Read the inputs (with their defaults) and the outputs of an action.

    Args:
        path: The path to ``action.yaml``.

    Returns:
        The input names mapped to their default (``None`` if there is none),
        in the order of the file, and the output names.
    """
    inputs: dict[str, str | None] = {}
    outputs: list[str] = []
    section = None
    current = None
    for line in path.read_text().splitlines():
        if re.match(r"^[a-z]+:", line):
            section = line.split(":")[0]
            current = None
        elif section in {"inputs", "outputs"}:
            match = NAME_PATTERN.match(line)
            if match:
                current = match.group(1)
                if section == "inputs":
                    inputs[current] = None
                else:
                    outputs.append(current)
            elif section == "inputs" and current:
                match = DEFAULT_PATTERN.match(line)
                if match:
                    inputs[current] = unquote(match.group(1))
    return inputs, outputs


def read_table(text: str, heading: str) -> list[list[str]]:
    r"""Read the rows of the table that follows a heading of the README.

    Args:
        text: The content of the README.
        heading: The heading of the section, such as ``Inputs``.

    Returns:
        The rows of the table, each as a list of cells, without the header.
    """
    match = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not match:
        return []
    rows = [
        [cell.strip() for cell in line.strip().strip("|").split("|")]
        for line in match.group(1).splitlines()
        if line.startswith("|")
    ]
    return [row for row in rows[2:] if row]


def compare_names(kind: str, documented: list[str], expected: list[str], readme: Path) -> list[str]:
    r"""Compare the names documented in the README with the names of the action.

    Args:
        kind: ``input`` or ``output``.
        documented: The names in the table of the README.
        expected: The names in ``action.yaml``.
        readme: The path to the README, for the messages.

    Returns:
        The error messages. The list is empty if the names are the same.
    """
    errors = [f"the {kind} '{n}' is not documented in {readme}" for n in expected if n not in documented]
    errors += [f"{readme} documents the {kind} '{n}', which the action does not have" for n in documented if n not in expected]
    errors += [f"the {kind} '{n}' is documented twice in {readme}" for n in set(documented) if documented.count(n) > 1]
    return errors


def main(argv: list[str]) -> int:
    r"""Run the check.

    Args:
        argv: The optional paths to ``action.yaml`` and ``README.md``.

    Returns:
        ``0`` if the README is consistent with the action, ``1`` otherwise.
    """
    action = Path(argv[1] if len(argv) > 1 else "action.yaml")
    readme = Path(argv[2] if len(argv) > 2 else "README.md")
    inputs, outputs = read_action(action)
    text = readme.read_text()
    input_rows = read_table(text, "Inputs")
    output_rows = read_table(text, "Outputs")

    errors = []
    errors += compare_names("input", [unquote(row[0]) for row in input_rows], list(inputs), readme)
    for row in input_rows:
        name = unquote(row[0])
        if name in inputs and unquote(row[-1]) != (inputs[name] or ""):
            errors.append(
                f"default of '{name}': {readme} says {row[-1]}, {action} says {inputs[name]!r}"
            )
    errors += compare_names("output", [unquote(row[0]) for row in output_rows], outputs, readme)

    for error in errors:
        print(f"::error title=README out of date::{error}")
    if not errors:
        print(f"{readme} documents the {len(inputs)} inputs and {len(outputs)} outputs of {action}.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
