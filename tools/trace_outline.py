#!/usr/bin/env python3
"""
Regenerate src/arm_outline.scad from reference photo 01 (top view, part between caliper jaws).

Pipeline (see docs/derivation.md for the reasoning):
  1. Detect the 10 mm grid of the cutting mat and fit a homography (pixels <-> mat millimetres).
  2. Warp the region around the part to a metric top view (10 px/mm).
  3. Segment the teal plastic, extract the outer contour and the holes.
  4. Build the part frame: origin midway between the two oval slots, +u towards the intact arm,
     +v towards the straight ("convex") side of the square, -v towards the hooks.
  5. Correct the photo using caliper readings:
       - uniform scale so the slot centre distance equals OVAL_C2C,
       - compress the hook ("beak") region so the overall width equals OVERALL_WIDTH
         (the arm end was propped up on its long tube, so it looked bigger in the photo).
  6. Keep only the intact arm (u >= U_CUT), smooth + simplify it, write it as an OpenSCAD polygon.

Usage:
  python3 tools/trace_outline.py            # writes src/arm_outline.scad and docs/images/outline-derivation.png
Requirements: pip install -r tools/requirements.txt
"""
import json
import os
from collections import deque

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO = os.path.join(ROOT, "docs/reference-photos/01-top-view-caliper-width-43.27mm.jpg")
OUT_SCAD = os.path.join(ROOT, "src/arm_outline.scad")
OUT_PNG = os.path.join(ROOT, "docs/images/outline-derivation.png")
OUT_JSON = os.path.join(ROOT, "docs/images/outline-derivation.json")

# --- caliper anchors (mm) -------------------------------------------------------------
OVAL_C2C = 40.0        # 34.27 (slot inner edges) + 5.7 (slot length); the by-eye "centre" reading was 40.37
OVERALL_WIDTH = 43.27  # hook tip to the straight side of the square

# --- grid detection seeds for photo 01 (pixel coordinates in the original 1600x1200 image) -----
SEED = (1032.0, 842.0)          # intersection of two thick (5 cm) mat lines, right of the caliper
DIR1 = (0.975, -0.224)          # direction of one grid family in the image
DIR2 = (0.244, 0.970)           # direction of the other family
SPACING_PX = 65.0               # ~1 cm in pixels near the seed
GRID_ROI = (640, 560, 1590, 1150)   # only grow the lattice on clean mat (no caliper / protractor)
PART_BBOX_PX = (500, 400, 830, 990) # region of the photo that contains the part

PPMM = 10.0       # rectified image resolution (px per mm)
U_CUT = 16.5      # raw-frame u where the arm starts (the square itself is built parametrically)


def yellowness(img):
    b, g, r = [c.astype(np.float32) for c in cv2.split(img)]
    y = np.clip((r - b) - 10, 0, 60) / 60.0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    part = cv2.dilate(cv2.inRange(hsv, (86, 150, 60), (112, 255, 255)), np.ones((15, 15), np.uint8))
    y[part > 0] = 0
    steel = ((np.abs(r - b) < 25) & (r > 120)).astype(np.uint8)
    y[cv2.dilate(steel, np.ones((9, 9), np.uint8)) > 0] = 0
    return y


def refine_intersection(Y, p, a1, a2, R=26, band=5):
    """Fit both grid lines locally around p and return their intersection (+ local directions)."""
    h, w = Y.shape
    p0 = p.copy()
    x0, y0 = int(p[0]) - R, int(p[1]) - R
    if x0 < 0 or y0 < 0 or x0 + 2 * R >= w or y0 + 2 * R >= h:
        return None
    ys, xs = np.mgrid[y0:y0 + 2 * R, x0:x0 + 2 * R]
    P = np.stack([xs, ys], -1).reshape(-1, 2).astype(float)
    wv = Y[y0:y0 + 2 * R, x0:x0 + 2 * R].reshape(-1)
    lines = []
    for a in (a1, a2):
        n = np.array([-a[1], a[0]])
        for _ in range(3):
            sel = (np.abs((P - p) @ n) < band) & (wv > 0.2)
            if sel.sum() < 15:
                return None
            ww = wv[sel]
            c = (P[sel] * ww[:, None]).sum(0) / ww.sum()
            C = ((P[sel] - c).T * ww) @ (P[sel] - c)
            dirv = np.linalg.eigh(C)[1][:, 1]
            n = np.array([-dirv[1], dirv[0]])
            p = p - ((p - c) @ n) * n
        lines.append((c, n, dirv))
    (c1, n1, v1), (c2, n2, v2) = lines
    try:
        q = np.linalg.solve(np.array([n1, n2]), np.array([n1 @ c1, n2 @ c2]))
    except np.linalg.LinAlgError:
        return None
    if np.linalg.norm(q - p0) > 9:
        return None
    return q, (v1 if v1 @ a1 > 0 else -v1), (v2 if v2 @ a2 > 0 else -v2)


def grid_homography(img):
    Y = yellowness(img)
    d1, d2 = np.array(DIR1), np.array(DIR2)
    d1, d2 = d1 / np.linalg.norm(d1), d2 / np.linalg.norm(d2)
    found = {(0, 0): refine_intersection(Y, np.array(SEED), d1, d2)}
    assert found[(0, 0)] is not None, "seed intersection not found"
    queue = deque([(0, 0)])
    while queue:
        i, j = queue.popleft()
        p, a1, a2 = found[(i, j)]
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = (i + di, j + dj)
            if k in found:
                continue
            prev = found.get((i - di, j - dj))
            step = (p - prev[0]) if prev else (a1 * SPACING_PX * di + a2 * SPACING_PX * dj)
            pred = p + step
            if not (GRID_ROI[0] <= pred[0] <= GRID_ROI[2] and GRID_ROI[1] <= pred[1] <= GRID_ROI[3]):
                continue
            q = refine_intersection(Y, pred, a1, a2)
            if q is None or not (0.75 * SPACING_PX < np.linalg.norm(q[0] - p) < 1.3 * SPACING_PX):
                continue
            found[k] = q
            queue.append(k)
    obj = np.float32([[k[0] * 10, k[1] * 10] for k in found])
    pix = np.float32([v[0] for v in found.values()])
    H, mask = cv2.findHomography(obj, pix, cv2.RANSAC, 2.0)
    err = np.linalg.norm(cv2.perspectiveTransform(obj.reshape(-1, 1, 2), H).reshape(-1, 2) - pix, axis=1)
    inl = mask.ravel() > 0
    print(f"grid: {len(found)} intersections, {inl.sum()} inliers, reprojection error "
          f"{err[inl].mean():.2f}px mean / {err[inl].max():.2f}px max")
    return H


def rectify(img, H):
    Hi = np.linalg.inv(H)
    bx = PART_BBOX_PX
    c = cv2.perspectiveTransform(np.float32([[bx[0], bx[1]], [bx[2], bx[1]], [bx[0], bx[3]], [bx[2], bx[3]]])
                                 .reshape(-1, 1, 2), Hi).reshape(-1, 2)
    x0, x1 = c[:, 0].min() - 6, c[:, 0].max() + 6
    y0, y1 = c[:, 1].min() - 6, c[:, 1].max() + 6
    p = cv2.perspectiveTransform(np.float32([[0, 0], [10, 0], [0, 10]]).reshape(-1, 1, 2), H).reshape(-1, 2)
    a, b = p[1] - p[0], p[2] - p[0]
    assert a[0] * b[1] - a[1] * b[0] > 0, "unexpected grid handedness (rectified image would be mirrored)"
    A = np.array([[1 / PPMM, 0, x0], [0, 1 / PPMM, y0], [0, 0, 1]])
    W, Hh = int((x1 - x0) * PPMM), int((y1 - y0) * PPMM)
    return cv2.warpPerspective(img, H @ A, (W, Hh), flags=cv2.INTER_CUBIC | cv2.WARP_INVERSE_MAP)


def segment(rect):
    hsv = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
    m = cv2.inRange(hsv, (86, 150, 60), (112, 255, 255))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    m = np.where(lab == 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]), 255, 0).astype(np.uint8)
    # white stress marks (crazing) near the broken areas are not teal and leave notches in the
    # outline; a 2 mm closing fills them without touching the large-scale curves
    closed = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21)))
    co, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    outer = max(co, key=cv2.contourArea)[:, 0, :] / PPMM
    cs, hier = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    holes = []
    for i, c in enumerate(cs):
        area = cv2.contourArea(c) / PPMM ** 2
        if hier[0][i][3] == -1:
            continue
        elif area > 20:   # ignore specular highlights; keep slots + tube bore
            (cx, cy), (w, h), _ = cv2.minAreaRect(c)
            holes.append({"centre": np.array([cx, cy]) / PPMM, "size": sorted([w / PPMM, h / PPMM]), "area": area})
    return outer, holes


def smooth_closed(P, sigma_pts=8, step=0.6, eps=0.04):
    """Gaussian-smooth an open polyline, resample by arc length, Douglas-Peucker simplify."""
    k = np.arange(-3 * sigma_pts, 3 * sigma_pts + 1)
    g = np.exp(-0.5 * (k / sigma_pts) ** 2)
    g /= g.sum()
    pad = np.vstack([np.repeat(P[:1], len(k), 0), P, np.repeat(P[-1:], len(k), 0)])
    S = np.stack([np.convolve(pad[:, i], g, mode="same")[len(k):-len(k)] for i in range(2)], 1)
    d = np.r_[0, np.cumsum(np.linalg.norm(np.diff(S, axis=0), axis=1))]
    t = np.arange(0, d[-1], step)
    R = np.stack([np.interp(t, d, S[:, i]) for i in range(2)], 1)
    R = cv2.approxPolyDP(np.float32(R).reshape(-1, 1, 2), eps, False).reshape(-1, 2)
    return R


def main():
    img = cv2.imread(PHOTO)
    assert img is not None, PHOTO
    H = grid_homography(img)
    rect = rectify(img, H)
    outer, holes = segment(rect)

    # slots = the two elongated mid-size holes; tube bore = the roundest big one
    holes.sort(key=lambda h: h["area"])
    bore = max(holes, key=lambda h: h["area"])
    slots = sorted([h for h in holes if h is not bore and 25 < h["area"] < 45], key=lambda h: -h["area"])[:2]
    assert len(slots) == 2, holes
    # +u points towards the slot closest to the tube bore (the intact arm)
    a, b = slots[0]["centre"], slots[1]["centre"]
    if np.linalg.norm(a - bore["centre"]) > np.linalg.norm(b - bore["centre"]):
        a, b = b, a
    centre = (a + b) / 2
    u = (a - b) / np.linalg.norm(a - b)
    v = np.array([-u[1], u[0]])
    raw = np.stack([(outer - centre) @ u, (outer - centre) @ v], 1)
    if raw[:, 1].min() > -raw[:, 1].max():   # make -v the hook side (hook tip is the extreme point)
        v = -v
        raw[:, 1] *= -1
    raw_c2c = np.linalg.norm(a - b)
    s = OVAL_C2C / raw_c2c
    T = raw * s

    def frame(p):
        return np.array([(p - centre) @ u, (p - centre) @ v]) * s

    bore_t = frame(bore["centre"])
    conv = np.median(T[(T[:, 1] > 14) & (T[:, 0] > 1) & (T[:, 0] < 12), 1])
    lug = np.median(T[(T[:, 1] < -13) & (np.abs(T[:, 0]) < 8), 1])

    # arm = contiguous run of contour points with u >= U_CUT (raw)
    m = raw[:, 0] >= U_CUT
    idx = np.where(m)[0]
    br = np.where(np.diff(idx) > 1)[0]
    if len(br):
        T = np.roll(T, -idx[br[0] + 1], axis=0)
        raw = np.roll(raw, -idx[br[0] + 1], axis=0)
        idx = np.where(raw[:, 0] >= U_CUT)[0]
    arm = smooth_closed(T[idx[0]:idx[-1] + 1])

    # hook compression: scale the part of the arm beyond the square's hook-side edge
    # (done after smoothing so the hook tip lands exactly on the caliper width)
    beak_now = arm[:, 1].min()
    beak_target = conv - OVERALL_WIDTH
    k = (beak_target - lug) / (beak_now - lug)
    sel = arm[:, 1] < lug
    arm[sel, 1] = lug + (arm[sel, 1] - lug) * k
    # close the polygon inside the square (hidden by the union with the square plate)
    ucl = U_CUT * s - 3.0
    poly = np.vstack([arm, [[ucl, arm[-1, 1]], [ucl, arm[0, 1]]]])
    if cv2.contourArea(np.float32(poly)) < 0:
        poly = poly[::-1]

    info = {
        "photo": os.path.relpath(PHOTO, ROOT),
        "raw_slot_c2c_mm": round(float(raw_c2c), 3),
        "scale_applied": round(float(s), 4),
        "hook_compression_factor": round(float(k), 4),
        "square_straight_edge_v": round(float(conv), 2),
        "square_hook_edge_v": round(float(lug), 2),
        "tube_bore_centre_from_photo": [round(float(x), 2) for x in bore_t],
        "hook_tip_v_before": round(float(beak_now), 2),
        "hook_tip_v_after": round(float(beak_target), 2),
        "arm_points": len(poly),
    }
    print(json.dumps(info, indent=2))
    with open(OUT_JSON, "w") as f:
        json.dump(info, f, indent=2)

    with open(OUT_SCAD, "w") as f:
        f.write("// GENERATED by tools/trace_outline.py - do not edit by hand.\n")
        f.write("// Outline of ONE intact arm (hook + tube boss area) in the part frame, millimetres.\n")
        f.write("// Origin: midpoint between the two oval slots. +u (x) towards this arm, -v (y) towards the hook.\n")
        f.write(f"// Source photo: {info['photo']}; scale {info['scale_applied']}, "
                f"hook compression {info['hook_compression_factor']}.\n")
        f.write("arm_outline_points = [\n")
        f.write(",\n".join(f"  [{p[0]:.3f}, {p[1]:.3f}]" for p in poly))
        f.write("\n];\n")
    print("wrote", os.path.relpath(OUT_SCAD, ROOT))

    # debug overlay: corrected outline (green) on top of raw outline (red), 10 px/mm
    S = 12
    W, Hh = int(60 * S), int(60 * S)
    canvas = np.full((Hh, W, 3), 255, np.uint8)
    def to_px(q):
        return np.int32(np.c_[(q[:, 0] + 2) * S, (32 - q[:, 1]) * S]).reshape(-1, 1, 2)
    for gx in range(-2, 58, 5):
        cv2.line(canvas, (int((gx + 2) * S), 0), (int((gx + 2) * S), Hh), (225, 225, 225), 1)
    for gy in range(-28, 32, 5):
        cv2.line(canvas, (0, int((32 - gy) * S)), (W, int((32 - gy) * S)), (225, 225, 225), 1)
    cv2.polylines(canvas, [to_px(raw)], True, (60, 60, 230), 1, cv2.LINE_AA)
    cv2.polylines(canvas, [to_px(poly)], True, (40, 160, 40), 2, cv2.LINE_AA)
    cv2.circle(canvas, tuple(to_px(bore_t[None])[0, 0]), 3, (200, 0, 0), -1)
    cv2.putText(canvas, "red: raw photo trace   green: corrected arm outline   grid: 5 mm", (10, Hh - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imwrite(OUT_PNG, canvas)
    print("wrote", os.path.relpath(OUT_PNG, ROOT))


if __name__ == "__main__":
    main()
