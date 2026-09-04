#!/usr/bin/env python3
"""
superformula_svg.py — a stylus/pencil/flashlight that traces room shapes into
SVG, for tweaking the spider-web geometry by hand.

Gielis' superformula (2003) — ONE closed plane curve from six knobs:

    r(theta) = ( |cos(m*theta/4) / a| ** n2  +  |sin(m*theta/4) / b| ** n3 ) ** (-1/n1)

    m   angular symmetry order — how many lobes / spokes
    n1  the REAL axis: the outer envelope exponent (-1/n1). Isotropic
        inflate <-> pinch. This is e0 / the vacuum scale — it points
        nowhere, it scales the whole boundary.
    n2  exponent on the cos channel  (= J_red)
    n3  exponent on the sin channel  (= J_blue)
    a   scale of the cos channel     (the semi-axis toward 0 / pi)
    b   scale of the sin channel     (the semi-axis toward pi/2)

So the 6 knobs factor as: one mode number (m), one real envelope (n1), and
TWO imaginary channels — (a, n2) on cos/red and (b, n3) on sin/blue. Exactly
ptol.c's J_red (cos) / J_blue (sin) split, at the two-term (C-level) case.

THE 12 COMPONENTS (the Superformula reel): a 3-D supershape is the spherical
product of TWO superformulas — one for theta (the SECTION, longitude) and one
for phi (the PROFILE, latitude):

    x = r_theta(theta) cos theta * r_phi(phi) cos phi
    y = r_theta(theta) sin theta * r_phi(phi) cos phi
    z =                            r_phi(phi) sin phi

6 (section) + 6 (profile) = 12.  "applied once per angle", theta = section,
phi = profile.

THE 16 AXES (1 real + 15 imaginary): generalise the two-term sum to one term
per sedenion shell k = 1..15 — cos on the J_red shells {0-3, 8-11}, sin on the
J_blue shells {4-7, 12-15}, prime frequencies P_k = {2,3,5,...,53}:

    r(theta) = ( sum_{k=1}^{15} |trig_k(theta * 2pi / P_k) / a_k| ** n_k ) ** (-1/n0)

n0 (from e0) is the one real envelope; the 15 (a_k, n_k) pairs are the shape
channels. The room does not need fitting: ptol.c's projection already IS the
parameter vector — feed the 16 normalised scalars in as `sedenion_room(v)`.

It is a MANIFOLD MAPPING. 2-D: S^1 -> R^2 (a 1-manifold, the boundary curve).
Spherical product: S^2 -> R^3 (a 2-manifold). Sedenion: the 15-torus of
imaginary phases into R^16, projected down to draw.

    PENCIL     = evaluate r(theta0) at ONE angle -> a single ray (parabolic).
    FLASHLIGHT = sweep theta in [0, 2pi) -> the whole closed boundary.
"""
from __future__ import annotations

import math
from typing import List, Optional, Sequence, Tuple

PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)
_J_BLUE = frozenset({4, 5, 6, 7, 12, 13, 14, 15})   # sin channel; the rest = cos


# ── the 6-knob curve ────────────────────────────────────────────────────────
def superformula(theta: float, m: float, n1: float, n2: float, n3: float,
                 a: float = 1.0, b: float = 1.0) -> float:
    t = m * theta / 4.0
    c = abs(math.cos(t) / a) ** n2
    s = abs(math.sin(t) / b) ** n3
    base = c + s
    if base <= 0.0:
        return 0.0
    return base ** (-1.0 / n1)


def curve(m: float, n1: float, n2: float, n3: float, a: float = 1.0,
          b: float = 1.0, samples: int = 720) -> List[Tuple[float, float]]:
    pts = []
    for i in range(samples):
        th = 2.0 * math.pi * i / samples
        r = superformula(th, m, n1, n2, n3, a, b)
        pts.append((r * math.cos(th), r * math.sin(th)))
    return pts


# ── the 12-knob 3-D supershape (spherical product) ──────────────────────────
def supershape(section: Sequence[float], profile: Sequence[float],
               n_lon: int = 120, n_lat: int = 60) -> List[Tuple[float, float, float]]:
    """section / profile are each (m, n1, n2, n3, a, b)."""
    out = []
    for j in range(n_lat + 1):
        phi = -math.pi / 2.0 + math.pi * j / n_lat
        rp = superformula(phi, *profile)
        for i in range(n_lon):
            th = -math.pi + 2.0 * math.pi * i / n_lon
            rt = superformula(th, *section)
            out.append((rt * math.cos(th) * rp * math.cos(phi),
                        rt * math.sin(th) * rp * math.cos(phi),
                        rp * math.sin(phi)))
    return out


# ── the 16-axis version: parameters straight off a sedenion projection ──────
def sedenion_room(v: Sequence[float], samples: int = 720, eps: float = 1e-3,
                  exp: float = 2.0) -> List[Tuple[float, float]]:
    """v = 16 (normalised) sedenion scalars. e0 sets the envelope; e1..e15 are
    the shape channels — cos on J_red shells, sin on J_blue, prime freqs.
    A big |v[k]| tightens spoke k (a_k = 1/|v[k]|)."""
    if len(v) < 16:
        raise ValueError("need 16 sedenion scalars")
    n0 = max(0.2, abs(v[0]) * 4.0)                       # e0 -> real envelope
    a = [max(eps, abs(v[k])) for k in range(16)]
    pts = []
    for i in range(samples):
        th = 2.0 * math.pi * i / samples
        acc = 0.0
        for k in range(1, 16):
            trig = math.sin if k in _J_BLUE else math.cos
            acc += abs(trig(th * 2.0 * math.pi / PRIMES[k]) / (a[k])) ** exp
        r = acc ** (-1.0 / n0) if acc > 0.0 else 0.0
        pts.append((r * math.cos(th), r * math.sin(th)))
    return pts


# ── stylus -> SVG ──────────────────────────────────────────────────────────
def _fit(pts: Sequence[Tuple[float, float]], w: int, h: int, pad: int
         ) -> List[Tuple[float, float]]:
    xs = [p[0] for p in pts] or [0.0]
    ys = [p[1] for p in pts] or [0.0]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sx = (w - 2 * pad) / (x1 - x0 or 1.0)
    sy = (h - 2 * pad) / (y1 - y0 or 1.0)
    s = min(sx, sy)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    return [(w / 2.0 + (x - cx) * s, h / 2.0 - (y - cy) * s) for x, y in pts]


def to_svg(pts: Sequence[Tuple[float, float]], w: int = 480, h: int = 480,
           pad: int = 24, stroke: str = "#40a060", mode: str = "flashlight",
           pencil_angle: float = math.pi / 4.0, closed: bool = True) -> str:
    P = _fit(list(pts), w, h, pad)
    body = [f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}">',
            f'  <rect width="{w}" height="{h}" fill="#0a0a0a"/>']
    if mode == "pencil":
        i = int((pencil_angle % (2 * math.pi)) / (2 * math.pi) * len(P)) % len(P)
        px, py = P[i]
        body.append(f'  <line x1="{w/2:.1f}" y1="{h/2:.1f}" x2="{px:.2f}" '
                    f'y2="{py:.2f}" stroke="{stroke}" stroke-width="1.5"/>')
        body.append(f'  <circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="{stroke}"/>')
    else:
        d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in P) + (" Z" if closed else "")
        body.append(f'  <path d="{d}" fill="none" stroke="{stroke}" stroke-width="1.4"/>')
    body.append(f'  <circle cx="{w/2:.1f}" cy="{h/2:.1f}" r="2" fill="#806020"/>')
    body.append('</svg>')
    return "\n".join(body)


def verify() -> dict:
    circle = curve(m=0, n1=1, n2=2, n3=2, a=1, b=1, samples=360)
    rs = [math.hypot(x, y) for x, y in circle]
    is_circle = max(rs) - min(rs) < 1e-6            # m=0 -> a unit circle
    star = curve(m=6, n1=0.4, n2=0.4, n3=0.4, a=1, b=1)   # 6-fold, pinched
    r_star = [math.hypot(x, y) for x, y in star]
    six_fold = (max(r_star) / min(r_star)) > 1.5
    svg = to_svg(sedenion_room([0.9] + [0.2] * 15))
    pod = to_svg(curve(m=2, n1=0.30, n2=0.30, n3=0.30), mode="pencil")
    ok = (is_circle and six_fold and svg.startswith("<?xml") and "path" in svg
          and "line" in pod)
    return {"ok": ok, "m0_is_circle": is_circle, "m6_lobed": six_fold,
            "svg_bytes": len(svg), "pencil_ok": "line" in pod}


if __name__ == "__main__":
    import json
    import sys
    print(json.dumps(verify(), indent=2))
    if "--emit" in sys.argv:
        # a hyper-lemniscate seedpod, like the reel
        pod = curve(m=2, n1=0.30, n2=0.30, n3=0.30, a=1.0, b=1.0)
        open("superformula_pod.svg", "w").write(to_svg(pod))
        print("wrote superformula_pod.svg")
