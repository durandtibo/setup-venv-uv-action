#!/usr/bin/env bash
# Prints the workflow that tests the last stable release of the action, derived
# from the workflow that tests the local action (uses: ./).
#
# Usage: scripts/generate-stable-workflow.sh LOCAL_WORKFLOW STABLE_WORKFLOW
#
# The generated workflow differs from LOCAL_WORKFLOW by:
# - the header comment and the name,
# - the 'uses: ./' lines, which point to the release,
# - the jobs that are preceded by a '# local-only' comment line (at the indentation
#   of the jobs): they test an input or a behaviour added after the release, so they
#   are not copied.
# The release (the pinned 'uses:' value and its ratchet comment) is read from the
# existing STABLE_WORKFLOW: to bump the release, edit one of its 'uses:' lines and
# run 'make generate-stable-workflow'.
set -euo pipefail

if [ "$#" -ne 2 ]; then
	echo "usage: $0 LOCAL_WORKFLOW STABLE_WORKFLOW" >&2
	exit 2
fi
local_workflow="$1"
stable_workflow="$2"

uses="$(grep -m 1 -E '^[[:space:]]*uses: durandtibo/setup-venv-uv-action@' "${stable_workflow}" |
	sed -E 's/^[[:space:]]*uses: //')"
if [ -z "${uses}" ]; then
	echo "no 'uses: durandtibo/setup-venv-uv-action@...' line in ${stable_workflow}" >&2
	exit 1
fi
release="${uses##*@}"

body="$(awk -v uses="${uses}" '
	/^name:/ { started = 1; print "name: Test Stable Action"; next }
	!started { next }
	/^  # local-only[[:space:]]*$/ { pending = 1; next }
	/^  [a-z][a-z0-9-]*:[[:space:]]*$/ { skip = pending; pending = 0 }
	skip { next }
	{ sub(/uses: \.\/[[:space:]]*$/, "uses: " uses); print }
' "${local_workflow}")"

cat <<EOF2
# Tests the last stable release (durandtibo/setup-venv-uv-action@${release}) across
# Linux/macOS and the inputs of the action. Detects regressions in the published action.
# Generated from test-local.yaml by 'make generate-stable-workflow': do not edit it
# by hand. A job of test-local.yaml that tests an input or a behaviour added after
# the tested release has a '# local-only' comment above it: it is not copied here
# until the release is bumped.

${body}
EOF2
