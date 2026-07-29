#!/usr/bin/env python3
"""
cad.py — Computer Aided Drafting: the Calculus of SVG
=======================================================

Every script that produces geometry is a CAD script.
Blender, matplotlib, Fritzing, layer_spectrograph — all CAD.

CAD is the process (the derivative).
SVG is the snapshot (the integral).
CAD : SVG :: Calculus : Geometry

    d(SVG)/dt  =  CAD process
    ∫ CAD dt   =  SVG shape

The PSVG undefined operator IS the CAD notation —
the integrand, not the integral.

This module is the base for all geometry-producing scripts in
PtolemyHolcus. Fritzing, pendant, layer_spectrograph, ssr_scope
all sit on top of it.

Core classes
────────────
  SedenionShape   2D cross-section: 16-gon from sedenion vector
  SedenionPath    Sequence of shapes over time: the pathway in S¹⁵
  CADOutput       Base: to_svg / to_dxf / to_stl / to_psvg_operator
"""

from __future__ import annotations

import math
import struct
from typing import List, Tuple, Optional, Iterator

import numpy as np

# ── type aliases ──────────────────────────────────────────────────────────────

Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]
Triangle = Tuple[Vec3, Vec3, Vec3]   # three vertices


# ── SedenionShape — 2D cross-section ─────────────────────────────────────────

class SedenionShape:
    """
    2D cross-section derived from one sedenion vector.

    16 control points on a circle.
    Radius at point k = base_r + amplitude * |sedenion[k]|
    Angle at point k  = 2π k/16  (evenly spaced, starting from top)
    Sign of sedenion[k] → inward (negative) or outward (positive) excursion.

    The shape IS the sedenion at one moment.
    Watch it morph over time → watch the path through S¹⁵.
    """

    N = 16

    def __init__(self, sedenion: np.ndarray,
                 base_r: float = 8.0,
                 amplitude: float = 4.0,
                 rotation: float = 0.0):
        self.sedenion  = sedenion
        self.base_r    = base_r
        self.amplitude = amplitude
        self.rotation  = rotation       # radians, for twist along path

    def points(self, cx: float = 0.0, cy: float = 0.0) -> List[Vec2]:
        pts = []
        for k in range(self.N):
            angle = 2.0 * math.pi * k / self.N - math.pi / 2.0 + self.rotation
            r     = self.base_r + self.amplitude * float(self.sedenion[k])
            r     = max(r, self.base_r * 0.2)
            pts.append((cx + r * math.cos(angle),
                        cy + r * math.sin(angle)))
        return pts

    def area(self) -> float:
        """Shoelace formula."""
        pts = self.points()
        n   = len(pts)
        a   = 0.0
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            a += x1 * y2 - x2 * y1
        return abs(a) * 0.5

    def to_svg_path(self, cx: float = 0.0, cy: float = 0.0,
                    closed: bool = True) -> str:
        pts = self.points(cx, cy)
        d   = f'M {pts[0][0]:.3f},{pts[0][1]:.3f} '
        d  += ' '.join(f'L {x:.3f},{y:.3f}' for x, y in pts[1:])
        if closed:
            d += ' Z'
        return d

    @classmethod
    def mean(cls, shapes: List['SedenionShape']) -> 'SedenionShape':
        s = np.mean([sh.sedenion for sh in shapes], axis=0)
        return cls(s, shapes[0].base_r, shapes[0].amplitude)


# ── SedenionPath — path through S¹⁵ over time ────────────────────────────────

class SedenionPath:
    """
    A sequence of SedenionShapes: the person's pathway through S¹⁵.

    Each frame is one phonon — one acoustic quantum.
    The sequence IS the person's sedenion signature.
    The pendant IS the physical instantiation of this path.
    """

    def __init__(self, shapes: Optional[List[SedenionShape]] = None):
        self.shapes: List[SedenionShape] = shapes or []

    def append(self, shape: SedenionShape) -> None:
        self.shapes.append(shape)

    def __len__(self) -> int:
        return len(self.shapes)

    def __iter__(self) -> Iterator[SedenionShape]:
        return iter(self.shapes)

    def downsample(self, n: int) -> 'SedenionPath':
        """Reduce to n evenly-spaced frames."""
        if len(self.shapes) <= n:
            return self
        idx    = np.linspace(0, len(self.shapes) - 1, n, dtype=int)
        return SedenionPath([self.shapes[i] for i in idx])

    def smooth(self, window: int = 3) -> 'SedenionPath':
        """Rolling mean over sedenion components."""
        result = []
        half   = window // 2
        for i, sh in enumerate(self.shapes):
            lo  = max(0, i - half)
            hi  = min(len(self.shapes), i + half + 1)
            avg = np.mean([s.sedenion for s in self.shapes[lo:hi]], axis=0)
            result.append(SedenionShape(avg, sh.base_r, sh.amplitude,
                                        sh.rotation))
        return SedenionPath(result)

    def with_twist(self, total_turns: float = 1.0) -> 'SedenionPath':
        """Add progressive rotation (twist along the path)."""
        result = []
        for i, sh in enumerate(self.shapes):
            rot = 2.0 * math.pi * total_turns * i / max(len(self.shapes) - 1, 1)
            result.append(SedenionShape(sh.sedenion, sh.base_r,
                                        sh.amplitude, rot))
        return SedenionPath(result)

    def peak_shape(self) -> SedenionShape:
        """The frame with the highest total sedenion energy."""
        energies = [float(np.linalg.norm(sh.sedenion)) for sh in self.shapes]
        return self.shapes[int(np.argmax(energies))]

    def mean_shape(self) -> SedenionShape:
        return SedenionShape.mean(self.shapes)


# ── CADOutput — base class ────────────────────────────────────────────────────

class CADOutput:
    """
    Base class for all geometry-producing objects in PtolemyHolcus.

    Subclasses implement _geometry() → vertices, faces.
    CADOutput provides all output formats from that geometry.

    to_svg()           → SVG string (2D projection)
    to_dxf()           → DXF string (CNC / laser cutter)
    to_stl_ascii()     → STL ASCII string (3D printer)
    to_stl_binary()    → STL binary bytes (3D printer, smaller file)
    to_psvg_operator() → PSVG undefined operator block
    """

    def name(self) -> str:
        return self.__class__.__name__

    # ── subclass interface ────────────────────────────────────────────────────

    def vertices(self) -> List[Vec3]:
        raise NotImplementedError

    def triangles(self) -> List[Triangle]:
        raise NotImplementedError

    # ── SVG output ────────────────────────────────────────────────────────────

    def to_svg(self, width: int = 400, height: int = 400,
               stroke: str = '#00ff88', bg: str = '#0a0a0f') -> str:
        raise NotImplementedError

    # ── DXF output ────────────────────────────────────────────────────────────

    def to_dxf(self) -> str:
        raise NotImplementedError

    # ── STL output ────────────────────────────────────────────────────────────

    def to_stl_ascii(self) -> str:
        nm   = self.name().replace(' ', '_')
        tris = self.triangles()
        lines = [f'solid {nm}']
        for (a, b, c) in tris:
            n = _tri_normal(a, b, c)
            lines.append(f'  facet normal {n[0]:.6f} {n[1]:.6f} {n[2]:.6f}')
            lines.append('    outer loop')
            for v in (a, b, c):
                lines.append(f'      vertex {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}')
            lines.append('    endloop')
            lines.append('  endfacet')
        lines.append(f'endsolid {nm}')
        return '\n'.join(lines)

    def to_stl_binary(self) -> bytes:
        tris = self.triangles()
        hdr  = (self.name()[:80]).encode().ljust(80, b'\x00')
        buf  = bytearray(hdr)
        buf += struct.pack('<I', len(tris))
        for (a, b, c) in tris:
            n = _tri_normal(a, b, c)
            buf += struct.pack('<fff', *n)
            for v in (a, b, c):
                buf += struct.pack('<fff', *v)
            buf += struct.pack('<H', 0)
        return bytes(buf)

    def to_psvg_operator(self, tag: str = '', **attrs) -> str:
        if not tag:
            tag = self.name()
        attr_str = ' '.join(f'{k}="{v}"' for k, v in attrs.items())
        return f'<{tag} {attr_str}/>'

    # ── write helpers ─────────────────────────────────────────────────────────

    def write_stl(self, path: str, binary: bool = True) -> None:
        if binary:
            with open(path, 'wb') as f:
                f.write(self.to_stl_binary())
        else:
            with open(path, 'w') as f:
                f.write(self.to_stl_ascii())
        n = len(self.triangles())
        print(f'  STL → {path}  ({n} triangles, {"binary" if binary else "ascii"})')

    def write_dxf(self, path: str) -> None:
        with open(path, 'w') as f:
            f.write(self.to_dxf())
        print(f'  DXF → {path}')

    def write_svg(self, path: str, **kw) -> None:
        with open(path, 'w') as f:
            f.write(self.to_svg(**kw))
        print(f'  SVG → {path}')


# ── mesh helpers ──────────────────────────────────────────────────────────────

def _tri_normal(a: Vec3, b: Vec3, c: Vec3) -> Vec3:
    ax, ay, az = b[0]-a[0], b[1]-a[1], b[2]-a[2]
    bx, by, bz = c[0]-a[0], c[1]-a[1], c[2]-a[2]
    nx = ay*bz - az*by
    ny = az*bx - ax*bz
    nz = ax*by - ay*bx
    mag = math.sqrt(nx*nx + ny*ny + nz*nz)
    if mag < 1e-15:
        return (0.0, 0.0, 1.0)
    return (nx/mag, ny/mag, nz/mag)


def triangulate_polygon(pts: List[Vec2], z: float) -> List[Triangle]:
    """Fan-triangulate a convex/star polygon at height z."""
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    tris: List[Triangle] = []
    n = len(pts)
    for i in range(n):
        a = (cx, cy, z)
        b = (pts[i][0], pts[i][1], z)
        c = (pts[(i+1) % n][0], pts[(i+1) % n][1], z)
        tris.append((a, b, c))
    return tris


def extrude_polygon(pts: List[Vec2],
                    pts_top: List[Vec2],
                    z_bot: float,
                    z_top: float) -> List[Triangle]:
    """Side walls between two rings at different z and possibly different shapes."""
    tris: List[Triangle] = []
    n = len(pts)
    for i in range(n):
        j  = (i + 1) % n
        b0 = (pts[i][0],     pts[i][1],     z_bot)
        b1 = (pts[j][0],     pts[j][1],     z_bot)
        t0 = (pts_top[i][0], pts_top[i][1], z_top)
        t1 = (pts_top[j][0], pts_top[j][1], z_top)
        tris.append((b0, b1, t0))
        tris.append((b1, t1, t0))
    return tris


def dxf_header() -> str:
    return ('0\nSECTION\n2\nHEADER\n'
            '9\n$ACADVER\n1\nAC1009\n'
            '9\n$INSUNITS\n70\n4\n'
            '0\nENDSEC\n'
            '0\nSECTION\n2\nENTITIES\n')


def dxf_footer() -> str:
    return '0\nENDSEC\n0\nEOF\n'


def dxf_polyline(pts: List[Vec2], layer: str = '0',
                 closed: bool = True) -> str:
    lines = [f'0\nLWPOLYLINE\n8\n{layer}\n70\n{"1" if closed else "0"}\n'
             f'90\n{len(pts)}\n']
    for x, y in pts:
        lines.append(f'10\n{x:.6f}\n20\n{y:.6f}\n')
    return ''.join(lines)


def dxf_circle(cx: float, cy: float, r: float, layer: str = '0') -> str:
    return f'0\nCIRCLE\n8\n{layer}\n10\n{cx:.6f}\n20\n{cy:.6f}\n40\n{r:.6f}\n'


def dxf_text(x: float, y: float, h: float,
             text: str, layer: str = '0') -> str:
    return (f'0\nTEXT\n8\n{layer}\n'
            f'10\n{x:.6f}\n20\n{y:.6f}\n40\n{h:.6f}\n1\n{text}\n')
