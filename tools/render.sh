#!/usr/bin/env bash
# Render the STL files and the preview images used in the README.
# Usage:  tools/render.sh            (all outputs)
#         tools/render.sh stl        (only STL files)
#         tools/render.sh png        (only preview images)
# Extra OpenSCAD overrides can be passed through the environment, e.g.
#         SCAD_ARGS='-D tube_id=7.2 -D web_t=3.2' tools/render.sh stl
set -euo pipefail
cd "$(dirname "$0")/.."

OPENSCAD="${OPENSCAD:-openscad}"
SRC=src/toy_bracket.scad
SCAD_ARGS="${SCAD_ARGS:-}"
what="${1:-all}"

command -v "$OPENSCAD" >/dev/null || { echo "OpenSCAD not found. Install it (see AGENTS.md) or set OPENSCAD=/path/to/openscad"; exit 1; }

if [[ "$what" == all || "$what" == stl ]]; then
  echo "== STL: bracket"
  # shellcheck disable=SC2086
  "$OPENSCAD" $SCAD_ARGS -D 'part="bracket"' -o stl/toy_bracket.stl "$SRC"
  echo "== STL: fit template"
  # shellcheck disable=SC2086
  "$OPENSCAD" $SCAD_ARGS -D 'part="fit_template"' -o stl/toy_bracket_fit_template.stl "$SRC"
fi

if [[ "$what" == all || "$what" == png ]]; then
  common=(--render --imgsize=1200,800 --colorscheme=Tomorrow --projection=p)
  echo "== PNG: face B (long tubes up)"
  # shellcheck disable=SC2086
  "$OPENSCAD" $SCAD_ARGS "${common[@]}" --camera=0,0,9,52,0,20,190 -o docs/images/render-face-b.png "$SRC"
  echo "== PNG: face A (short tubes)"
  # shellcheck disable=SC2086
  "$OPENSCAD" $SCAD_ARGS "${common[@]}" --camera=0,0,9,128,0,200,190 -o docs/images/render-face-a.png "$SRC"
  echo "== PNG: top view (orthographic, face B up)"
  # shellcheck disable=SC2086
  "$OPENSCAD" $SCAD_ARGS --render --imgsize=1200,700 --colorscheme=Tomorrow --projection=o \
    --camera=0,-3,9,0,0,0,170 -o docs/images/render-top.png "$SRC"
fi
echo "done"
