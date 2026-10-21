# Assumptions and guesses

The brief was "make a first model without asking for more measurements, and document every guess".
This file lists every value that is **not** a direct caliper reading. The values the second batch of
readings settled are listed under [Resolved since v1](#resolved-since-v1). For each one: why it was chosen,
how confident it is, and how to check it. Confidence: **H** = high, **M** = medium, **L** = low (pure estimate).

## Shape-level assumptions

| # | Assumption | Basis | Conf. | If wrong |
|---|---|---|---|---|
| A1 | The part is **mirror-symmetric** about the plane between the two slots. The broken arm is a mirror copy of the intact one. | Photo 12: the broken fragment held in place shows the same hook, tube and pin. Photo 01: slots, square and tabs are symmetric. | H | Measure the fragment and give the second arm its own outline/parameters. |
| A2 | The two faces have the **same tube/pin positions**. The tube and the pin go straight through the web. | Photo 09 (edge-on) and the fragment in photo 11 show each tube and pin as a single straight cylinder through the web. | H | — |
| A3 | Outer walls are vertical: **no draft angle** and no edge fillets, apart from small 2D roundings (`outline_inner_fillet`, `outline_outer_round`). | Injection-moulded originals have ~1° draft, which is irrelevant at this size. | M | Cosmetic only. |
| A4 | Ejector-pin marks and the small round dimples next to the slots on face B are **ignored**. | They look like moulding marks, not functional holes (photos 06, 07). | M | If one is a real hole for a pin or screw, add it. |
| A5 | The white stress marks (crazing) near the tube of the intact arm are damage, not shape. The outline tracer closes notches smaller than 2 mm. | Photo 01. | M | — |

## Guessed dimensions

| Parameter | v1 value | How it was estimated | Conf. | How to verify |
|---|---|---|---|---|
| `tube_len_b` | 12.0 | Broken fragment (photo 11, lying on the 10 mm grid): long side ≈ 12, short side ≈ 6.5, plus the web. Photo 09 shows the same ≈ 2 : 1 ratio. The side views in photos 16–19 hint at shorter tubes (long side 6–8, short side 3–5), so the two sources disagree. The fragment estimate is kept because it is the more direct view, and because a tube that is too long can be cut down. | L | Outside jaws along the tube, tip to tip (total length). Then depth rod from the face A web surface to the tube tip. |
| `tube_len_a` | 6.0 | Same as above | L | See above. `tube_len_b` = total − `web_t` − `tube_len_a`. |
| `peg_len_b` / `peg_len_a` | 9.0 / 4.5 | Fragment: the pin is ≈ 0.75 × the tube length on each side | L | Same two measurements on the pin. |
| `face_a_rim_h` | 0.8 | Visual: shallow rim around the square and the slots on face A (photo 11) | L | Depth rod or caliper step measurement. |
| `face_b_frame_h` | 2.05 | Derived: 5.91 (reading 7) − 3.06 − `face_a_rim_h`. If face A has no rim, it would be 2.85. | M | Depth rod from the frame top to the bottom of a pocket on face B. |
| `face_b_frame_wall`, `face_b_rib_w` | 1.5, 1.2 | Visual, photos 06 and 08 | L | Caliper on a rib. Cosmetic/stiffness only. |
| `face_a_rib_w`, `face_a_rib_h` | 0.9, 0.6 | Visual, photos 01 and 11 | L | Cosmetic. |
| `slot_rim_w` | 1.2 | Visual, both faces | L | Cosmetic. |
| `square_corner_r` | 2.0 | Visual, photo 01 | M | Cosmetic. |
| `slot_len_x` | 5.7 | Largest visible slot opening in photos 01/10 (5.4–5.8). Readings 2 and 3 together would imply 6.1. | M | Inside jaws along the long axis. Then set `slot_c2c = 34.27 + slot_len_x`. |
| X ribs | straight corner-to-corner diagonals of the square | Photos. The ribs measure 45.7° / 133.0° to the slot axis in **two independent photos**, so the inner panel is probably ~4 % taller than wide, or the X is slightly asymmetric. The model uses plain diagonals. | M | Cosmetic. |

## Resolved since v1

| Parameter | v1 guess | v2 value | Source |
|---|---|---|---|
| `tube_od` | 10.0 | 9.83 | reading 8 |
| `tube_id` | 7.0 | 7.9 | readings 11 and 12 (7.67 and 7.91) |
| `peg_d` | 4.7 | 4.92 | reading 13 |
| pin position | 8.88 from the tube centre | 7.93 (`tube_peg_span` = 15.30) | reading 9, confirmed by the v1 fit template (pin ≈ 1 mm off) |
| outline, slots, tube position | traced from photos | unchanged | v1 fit template matched the original |

## Known risks for the fit (most to least important)

1. **Tube and pin lengths** are still guesses (see the table above). A tube that is too long can stop the toy
   from closing. If that happens, cut or sand the tube down, or set `tube_len_a` / `tube_len_b` and re-print.
2. **Tube bore on the toy's post.** 7.9 is the original bore. If the printed part is tight on the post, raise
   `tube_id` by 0.2. If it wobbles, lower it.
3. **Hook tip**: the hook tip region was the most distorted part of the photos. Its overall width is anchored
   on reading 1, but its exact curve is only good to about ±1 mm. Check it with the v2 fit template.

## What to measure next

Ordered by how much each reading improves the part. Each line names the parameter it sets.

1. Tube: total length tip to tip (outside jaws along the tube), plus the protrusion on face A (depth rod) →
   `tube_len_a`, `tube_len_b`.
2. Pin: the same two measurements → `peg_len_a`, `peg_len_b`.
3. Slot length along the long axis → `slot_len_x`, then `slot_c2c = 34.27 + slot_len_x`.
4. Frame height on face B and rim height on face A → `face_b_frame_h`, `face_a_rim_h`.
5. Outside of the tube to the far end of the square plate, along the long axis. This checks `tube_x` and `square_x`:
   model value = `tube_x + tube_od/2 + square_x/2` = 38.1 + 4.92 + 17 = **60.0 mm**.
6. What reading 5 (20.31) was.

Or simply print the v2 `stl/toy_bracket_fit_template.stl` and lay it on the original again. That checks the
outline, slots, tube and pin positions in one go.
