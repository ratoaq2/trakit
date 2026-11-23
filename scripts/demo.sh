#!/bin/bash
# Record docs/images/demo.gif with VHS in a container, with trakit from this repository.
# Usage: scripts/demo.sh. See the demo-gif skill.

set -e

# Git Bash: do not change the container paths into Windows paths
export MSYS_NO_PATHCONV=1

repo=$(pwd -W 2>/dev/null || pwd)
engine=$(command -v podman || command -v docker)
# Podman on WSL: crun fails with "controller `pids` is not available"
opts=()
[[ "$engine" == *podman* ]] && opts=(--cgroups=disabled)

"$engine" build -q -t localhost/trakit-vhs -f scripts/demo.Dockerfile .
"$engine" run --rm "${opts[@]}" -v "$repo:/repo" -w /repo localhost/trakit-vhs scripts/demo.tape
