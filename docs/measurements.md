# Measurements

All readings come from a digital caliper, photographed on a cutting mat with a 10 mm grid
(photos in [`reference-photos/`](reference-photos/); each file name contains its reading).
Nobody wrote down which feature each reading belonged to, so the "what was measured" column is an
**interpretation of the photo**. Confidence reflects how clear that interpretation is.

Coordinates follow the model: x = long axis through the slots, y = across (+y straight edge of the square,
−y hook side), z = thickness. Face A = short tubes, face B = long tubes.

## Caliper readings

| # | Reading (mm) | Photo | What was measured (interpretation) | Confidence | How it is used |
|---|---|---|---|---|---|
| 1 | **43.27** | 01 | Overall width across the part, from the hook tip to the straight edge of the square plate. Both jaws visibly touch those two points; the part lies face A up. | High | Anchor: overall y-extent. The traced hook region is compressed so that the model is exactly 43.27 wide. |
| 2 | **34.27** | 02 | Distance between the **inner** edges of the two oval slots (jaw tips inside the slots, jaws closed onto the edges nearest the square). | High | `slot_c2c = 34.27 + slot_len_x` = 34.27 + 5.7 = **40.0** |
| 3 | **40.37** | 08 | Jaw tips placed by eye in the middle of each oval slot, i.e. an approximate centre distance. | Medium | Cross-check only. The model uses 40.0 (−0.37). That is within what "by eye" placement can do, and consistent with reading 2 plus the slot length seen in the photos (5.4 to 5.8). |
| 4 | **14.15** | 07 | Oval slot next to the intact tube → tube bore, edge to edge (one jaw tip in the slot, the other in the bore). | Medium | Cross-check of the tube position. The model gives 13.76 (−0.4) with the guessed 7.0 mm bore. A smaller bore or a tube ~0.4 mm further out would close the gap. |
| 5 | **20.31** / **20.32** | 03, 04 | **Unclear.** The part is held in the air between the jaws. One jaw sits over the X-ribbed pocket area of face B, so it may be touching a rib rather than an outside edge. Two photos show the same reading from different angles. | Low | **Not used.** It does not match any outside width of the model: the arm is ≈ 22–26 mm wide there. If someone remembers what it was, add it here. |
| 6 | **3.06** | 05 | Thickness of the flat web (jaws on both faces of the plate, away from ribs and tubes). | High | `web_t = 3.06` |
| 7 | **5.91** | 09 | Total thickness clamped across the square-plate area: face A rim + web + face B frame. | Medium (exact clamp spot not visible) | `face_b_frame_h = 5.91 − web_t − face_a_rim_h` = 5.91 − 3.06 − 0.8 = **2.05** |

## Values measured from the photos

The mat grid was used to rectify photo 01 (and photo 10 as a cross-check) to a true top view.
See [`derivation.md`](derivation.md) for the method and the corrections applied.

| Feature | Model value | Source | Est. accuracy |
|---|---|---|---|
| Arm outline (hook + boss lobe) | `src/arm_outline.scad` | photo 01, corrected with readings 1 and 2 | ±0.5 mm near the square, ±1 mm at the hook end |
| Square plate | 34.0 × 33.7, centre at y = +1.35 | photo 01 (photo 10 agrees within 0.3 mm on x) | ±0.5 mm |
| Oval slot size | 5.7 (x) × 7.6 (y) | largest visible openings in photos 01 and 10 | ±0.3 mm |
| Tube centre | x = ±38.1, y = −9.45 | mean of photo 01 (38.23, −9.27), photo 10 (37.6, −9.45) and reading 4 with a 7.0 bore (38.45, −9.61) | ±0.5 mm |
| Pin centre | x = ±29.4, y = −11.25 | photo 01 (same offset from the tube as seen in the photo) | ±0.7 mm |
| Corner tabs | x = ±13.5, 6.5 wide, protrude 2.0 | photo 01 | ±0.5 mm |
| Overall length | 96.1 (result, not an input) | traced outline, mirrored | ±1.5 mm |

## Readings that are still missing

See the checklist in [`assumptions.md`](assumptions.md#what-to-measure-next).
