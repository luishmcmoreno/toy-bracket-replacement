# Measurements

All readings come from a digital caliper. Readings 1–7 were photographed on a cutting mat with a 10 mm grid,
readings 8–14 on fabric (photos in [`reference-photos/`](reference-photos/); each file name contains its reading).
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
| 4 | **14.15** | 07 | Oval slot next to the intact tube → tube bore, edge to edge (one jaw tip in the slot, the other in the bore). | Medium | Cross-check only. The model gives 13.2 with the measured 7.9 bore. Reading 10 (12.84) looks like the same measurement and lands on the other side, so the two together bracket the model. See the note below the table. |
| 5 | **20.31** / **20.32** | 03, 04 | **Unclear.** The part is held in the air between the jaws. One jaw sits over the X-ribbed pocket area of face B, so it may be touching a rib rather than an outside edge. Two photos show the same reading from different angles. | Low | **Not used.** It does not match any outside width of the model: the arm is ≈ 22–26 mm wide there. If someone remembers what it was, add it here. |
| 6 | **3.06** | 05 | Thickness of the flat web (jaws on both faces of the plate, away from ribs and tubes). | High | `web_t = 3.06` |
| 7 | **5.91** | 09 | Total thickness clamped across the square-plate area: face A rim + web + face B frame. | Medium (exact clamp spot not visible) | `face_b_frame_h = 5.91 − web_t − face_a_rim_h` = 5.91 − 3.06 − 0.8 = **2.05** |

### Second batch (after the v1 fit template was tried on the original)

| # | Reading (mm) | Photo | What was measured (interpretation) | Confidence | How it is used |
|---|---|---|---|---|---|
| 8 | **9.83** | 13 | Tube outside diameter. The outside jaws are closed across the intact tube. | High | `tube_od = 9.83` |
| 9 | **15.30** | 14 | Far side of the tube to far side of the pin. The outside jaws clamp both, roughly along the line through their centres. | High | `tube_peg_span = 15.30`, so the pin centre is 15.30 − 9.83/2 − 4.92/2 = **7.93** from the tube centre (v1 had 8.88). If the jaws were not exactly on the centre line, the true distance is slightly larger, never smaller. |
| 10 | **12.84** | 16 | Face B up. One jaw tip in the oval slot, the other in the tube bore: slot edge to bore edge, like reading 4. The display is motion-blurred; the gap between the jaws in the photo also measures ≈ 12.8 using the tube as scale. | Low | Cross-check only, see the note below. |
| 11 | **7.67** | 17 | Tube bore, with the small inside jaws in the bore of the long (face B) end of the tube. | Medium | Lower bound for `tube_id`. Inside jaws tend to read a bore slightly small when they are not exactly on a diameter. |
| 12 | **0.96** | 18 | Tube wall thickness at the face A end: one jaw in the bore, the other on the outside. | Medium | 9.83 − 2 × 0.96 = **7.91**. Together with reading 11: `tube_id = 7.9`. The bore must slide over a hollow post of the toy (photo 20), and FDM prints holes 0.1–0.3 mm small, so the upper value is used. |
| 13 | **4.92** | 15 | Pin diameter. The outside jaws are closed across the pin. | High | `peg_d = 4.92` |
| 14 | **6.04** | 19 | Face A up. One jaw tip in the tube bore, the other jaw past the pin: bore wall to the far side of the pin. | Low | Cross-check only. On the centre line it should read 7.93 − 3.95 + 2.46 = 6.44. 6.04 fits if the jaws were about 18° off that line, which is plausible from the photo. It is not used because reading 9 is the cleaner measurement. |

**Readings 4 and 10 (slot to bore).** Both put one jaw in the slot and one in the bore. A flat jaw inside a
round hole stops short of the wall, which adds a few tenths of a millimetre, and holding the jaws off the
shortest line between the holes takes some away. That is why the same measurement gave 14.15 once and 12.84
the other time. The model value (13.2) sits between them, and the fit template (below) shows the tube in the right
place, so `tube_x` / `tube_y` are unchanged.

## Fit check with the v1 template

Photos 20 and 21: the 1 mm v1 fit template laid over the original part, which sits in the toy (the toy's
orange posts go through the oval slot and into the tube bore).

- Outline, oval slot and tube: match. The original tube shows through the template's tube hole all round.
- **Pin: about 1 mm off.** The original pin (light teal) shows only on the tube side of the template's
  pin hole, with a dark crescent on the other side (arrow in photo 21). So the real pin is closer to the tube than
  in v1. This matches reading 9, which moves the pin 0.95 mm towards the tube. Fixed in v2.
- A small piece of the original shows next to the hook tip. The template could not sit flat (it rested on the
  pin), so this is not conclusive. Re-check it with the v2 template.

## Values measured from the photos

The mat grid was used to rectify photo 01 (and photo 10 as a cross-check) to a true top view.
See [`derivation.md`](derivation.md) for the method and the corrections applied.

| Feature | Model value | Source | Est. accuracy |
|---|---|---|---|
| Arm outline (hook + boss lobe) | `src/arm_outline.scad` | photo 01, corrected with readings 1 and 2 | ±0.5 mm near the square, ±1 mm at the hook end |
| Square plate | 34.0 × 33.7, centre at y = +1.35 | photo 01 (photo 10 agrees within 0.3 mm on x) | ±0.5 mm |
| Oval slot size | 5.7 (x) × 7.6 (y) | largest visible openings in photos 01 and 10 | ±0.3 mm |
| Tube centre | x = ±38.1, y = −9.45 | mean of photo 01 (38.23, −9.27), photo 10 (37.6, −9.45) and reading 4 with the v1 guess of a 7.0 bore (38.45, −9.61). Confirmed by the fit template. | ±0.5 mm |
| Pin centre | x = ±30.34, y = −11.06 (computed) | distance from the tube centre: reading 9 (7.93). Direction (`tube_peg_angle` = 191.7°): photo 01 | ±0.3 mm |
| Corner tabs | x = ±13.5, 6.5 wide, protrude 2.0 | photo 01 | ±0.5 mm |
| Overall length | 96.1 (result, not an input) | traced outline, mirrored | ±1.5 mm |

## Readings that are still missing

See the checklist in [`assumptions.md`](assumptions.md#what-to-measure-next).
