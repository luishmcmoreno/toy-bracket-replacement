# AGENTS.md: instructions for AI coding agents

This repository holds ONE thing: a parametric OpenSCAD model of a replacement for a broken toy bracket,
plus the photos, measurements and scripts it was derived from. Keep it that way: do not add unrelated files.

Read these before changing anything:

1. `README.md`: what the part is, how to print it, which parameters matter.
2. `docs/measurements.md`: caliper readings and how each one is used.
3. `docs/assumptions.md`: every guessed value, with confidence and how to verify it.
4. `docs/derivation.md`: only if you need to touch the traced outline.

All code, comments, docs and commit messages are in **English**.

## Tools you need

| Tool | Needed for | Install |
|---|---|---|
| **OpenSCAD** (2021.01 or newer) | everything: render STL / PNG | macOS: `brew install --cask openscad` · Debian/Ubuntu: `sudo apt install openscad` · Fedora: `sudo dnf install openscad` · Windows: `winget install OpenSCAD.OpenSCAD` · or download from <https://openscad.org/downloads.html> |
| bash | `tools/render.sh` (optional) | built in on macOS/Linux; on Windows use Git Bash/WSL or run the `openscad` commands below directly |
| Python 3.9+ with OpenCV + NumPy | only to re-trace the outline from the photo | `python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt` |
| a slicer (Bambu Studio, PrusaSlicer, Cura, OrcaSlicer…) | printing | not needed by the agent |

Blender is **not** used. No GPU, no MCP server, no cloud service is required.

Check the install: `openscad --version`. On macOS the binary may only exist inside the app bundle:
`/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD`. Then set `OPENSCAD=/that/path` for `tools/render.sh`.

## Commands

```bash
tools/render.sh          # STL files + preview PNGs (about 1 min with OpenSCAD 2021.01)
tools/render.sh stl      # only stl/toy_bracket.stl and stl/toy_bracket_fit_template.stl
tools/render.sh png      # only docs/images/render-*.png
SCAD_ARGS='-D tube_id=7.2' tools/render.sh stl     # one-off override without editing the file

# Without bash:
openscad -D 'part="bracket"'      -o stl/toy_bracket.stl              src/toy_bracket.scad
openscad -D 'part="fit_template"' -o stl/toy_bracket_fit_template.stl src/toy_bracket.scad
openscad --render --imgsize=1200,800 --colorscheme=Tomorrow --camera=0,0,9,52,0,20,190 -o docs/images/render-face-b.png src/toy_bracket.scad

# Re-trace the arm outline from photo 01 (rarely needed):
.venv/bin/python tools/trace_outline.py   # rewrites src/arm_outline.scad + docs/images/outline-derivation.*
```

A good render prints three `ECHO` lines (tube centre distance, pin centre, total thickness) and, for the bracket,
`Simple: yes` and `Volumes: 2`. Treat any `WARNING` or `ERROR`, `Simple: no`, or a failed `assert` as a bug.
Newer OpenSCAD development snapshots have a much faster Manifold backend (see `openscad --help`);
2021.01 is fine, just slower (~20 s per STL).

## Repository layout

```
src/toy_bracket.scad      model; ALL parameters at the top (Customizer sections)
src/arm_outline.scad      GENERATED polygon of one arm; never hand-edit (use arm_outline_scale or re-trace)
stl/                      exported STL files; always re-export after changing src/
docs/measurements.md      caliper readings -> parameters
docs/assumptions.md       guesses -> parameters, confidence, how to verify
docs/derivation.md        photo -> outline method and cross-checks
docs/images/              renders + outline-derivation figure
docs/reference-photos/    original photos (cropped to the part); file names contain the caliper reading
tools/render.sh           export STL + PNG
tools/trace_outline.py    regenerate src/arm_outline.scad from docs/reference-photos/01-*.jpg
```

## Coordinate system (mm)

- **x**: long axis through both oval slots. Origin is midway between the slots. The part is **mirror-symmetric in x**.
- **y**: across. **+y** is the straight edge of the square plate. **−y** is the side the hooks point to.
- **z**: thickness. `z = 0` is the face A surface of the web, `z = web_t` the face B surface.
  Face A features go to negative z, face B features above `web_t`. The exported bracket is shifted up by
  `tube_len_a`, so the face A tube tips sit on the bed.
- **Face A** = short tubes/pins, flat square with a thin raised X and a shallow rim (photos 01, 10, 11, 12).
  **Face B** = long tubes/pins, square frame with deep X-ribbed pockets (photos 03, 06, 07, 08).

## Feature → parameter map

| Physical feature | Parameters |
|---|---|
| Web thickness | `web_t` |
| Square plate size / position | `square_x`, `square_y`, `square_y_centre`, `square_corner_r` |
| Square frame + X ribs on face B | `face_b_frame_h`, `face_b_frame_wall`, `face_b_rib_w` |
| Rim + thin X on face A | `face_a_rim_h`, `face_a_rim_w`, `face_a_rib_h`, `face_a_rib_w`, `face_a_details` |
| Oval slots | `slot_c2c`, `slot_len_x`, `slot_len_y`, rims: `slot_rim_w` |
| Tubes (pivot bosses) | `tube_x`, `tube_y`, `tube_od`, `tube_id`, `tube_len_a`, `tube_len_b` |
| Pins next to the tubes | `peg_d`, `peg_len_a`, `peg_len_b`; position: `tube_peg_span` (caliper, far side of tube to far side of pin) and `tube_peg_angle`. `peg_x` / `peg_y` are computed from these. |
| Fit template holes | `template_clearance` |
| Corner tabs on the hook side of the square | `lug_x`, `lug_w`, `lug_protrusion` |
| Hooked arm outline | `src/arm_outline.scad` (generated), `arm_outline_scale`, `outline_inner_fillet`, `outline_outer_round` |

## Workflow: the user reports a new measurement

1. Map the measurement to a parameter (table above; `docs/assumptions.md` has the exact definition of each guess).
   If it is ambiguous which feature was measured, ask, or state your interpretation explicitly.
2. Change the default value in `src/toy_bracket.scad`. Keep the comment and update its source, e.g. `(caliper, 2026-10-22)`.
3. Update the matching row in `docs/measurements.md` (new reading) and/or `docs/assumptions.md`
   (mark the guess as resolved). Keep the README parameter table in sync if the value appears there.
4. Run `tools/render.sh`. Check the ECHO lines, `Simple: yes`, and no warnings.
5. If you can view images, open `docs/images/render-*.png` and compare with `docs/reference-photos/`.
6. Commit source, STL files and docs together, with a message that says what was measured.

## Rules

- Keep the model parametric: no magic numbers inside modules; add a named parameter at the top instead.
- Keep it compatible with OpenSCAD 2021.01 (avoid language features or builtins added after it), because
  that is the stable release most package managers ship.
- Never hand-edit `src/arm_outline.scad`. To change the outline, adjust `arm_outline_scale`, or change the
  anchors in `tools/trace_outline.py` and re-run it.
- The STL files in `stl/` must always match the current source. Re-export after every change.
- Do not scale the whole model to "fix" one dimension. Find the parameter that controls that feature.
- Mirror symmetry in x is an assumption (see `docs/assumptions.md`). Do not break it unless a measurement
  of the broken fragment shows the two arms differ.
- Do not delete the reference photos or the derivation docs; they are the only record of the original.
