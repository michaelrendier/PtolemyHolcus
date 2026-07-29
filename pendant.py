#!/usr/bin/env python3
"""
pendant.py — Ask the Math for the Pendant
==========================================

The person speaks.
Their voice traces a path through S¹⁵.
The math is asked: what shape is this path?
The math answers with a 3D printable pendant.

That pendant IS their pathway.
That pendant IS their Ptolemy Holcus.
No two are alike. The shape is not designed — it is revealed.

Pipeline
────────
  Person speaks
      ↓
  PPhonon / QPhonon stream  (phonon.py)
      ↓
  SedenionPath in S¹⁵        (cad.py)
      ↓
  PtolemyPendant.ask()      ← asks the math
      ↓
  PendantGeometry            ← math answers
      ↓
  .stl  (3D print)
  .dxf  (laser cut flat)
  .svg  (preview)
  PSVG  <Pendant/> undefined operator

Pendant geometry
────────────────
  The pendant is a swept solid:
    cross-section at each moment = sedenion 16-gon at that phonon frame
    length axis = time / the path through S¹⁵
    twist = BAO wobble (e^πi rotation accumulated along path)

  OR (medallion mode):
    the single most energetic moment of the path
    extruded to 3mm thickness
    border ring + hole for chain

  The person chooses: pendant (swept) or medallion (peak moment).
  Either way the shape came from their voice. Their Ptolemy.

Usage
─────
  # from mic (real-time)
  python3 pendant.py --speak --stl my_pendant.stl

  # from existing phonon recording
  python3 pendant.py --from-frames frames.npy --stl my_pendant.stl

  # medallion (flat, laser-cuttable)
  python3 pendant.py --speak --medallion --dxf my_medallion.dxf

  # full output
  python3 pendant.py --speak --stl out.stl --dxf out.dxf --svg out.svg
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time
from typing import List, Optional, Tuple

import numpy as np

from cad import (
    CADOutput, SedenionShape, SedenionPath,
    Vec2, Vec3, Triangle,
    triangulate_polygon, extrude_polygon,
    dxf_header, dxf_footer, dxf_polyline, dxf_circle, dxf_text,
    _tri_normal,
)

# ── Pendant geometry constants ────────────────────────────────────────────────

BASE_R      = 8.0        # mm — base radius of 16-gon
AMPLITUDE   = 4.0        # mm — sedenion modulation depth
THICKNESS   = 3.0        # mm — extrusion depth
BORDER_R    = BASE_R + AMPLITUDE + 2.0   # mm — outer border ring
HOLE_R      = 1.2        # mm — chain hole radius
HOLE_OFFSET = BASE_R + AMPLITUDE + 0.8  # mm — chain hole from centre
CHAIN_HOLE_SEGMENTS = 16
TWIST_TURNS = 0.75       # pendant twist (3/4 turn along length)
N_SWEEP     = 32         # cross-sections along sweep axis


# ── PendantGeometry ───────────────────────────────────────────────────────────

class PendantGeometry(CADOutput):
    """
    The physical instantiation of a sedenion path.

    Medallion mode  : one cross-section (peak moment) extruded to thickness.
    Pendant mode    : swept solid — each frame is one cross-section.

    In both cases: the shape came from the person's voice.
    Not designed. Revealed.
    """

    def __init__(self, path: SedenionPath,
                 mode: str = 'medallion',
                 person_id: str = ''):
        self.path      = path
        self.mode      = mode          # 'medallion' | 'pendant'
        self.person_id = person_id
        self._verts:  List[Vec3]     = []
        self._tris:   List[Triangle] = []
        self._built   = False

    def name(self) -> str:
        return f'PtolemyPendant_{self.person_id or "anon"}'

    # ── build geometry ────────────────────────────────────────────────────────

    def _build(self) -> None:
        if self._built:
            return
        if self.mode == 'pendant':
            self._build_swept()
        else:
            self._build_medallion()
        self._built = True

    def _build_medallion(self) -> None:
        """
        Medallion: peak-energy sedenion shape extruded to THICKNESS.
        Border ring. Hole for chain at top.
        """
        sh   = self.path.peak_shape()
        pts  = sh.points()

        z_bot, z_top = 0.0, THICKNESS
        tris: List[Triangle] = []

        # ── bottom face (normal pointing down) ──
        bot = triangulate_polygon(pts, z_bot)
        for (a, b, c) in bot:
            tris.append((c, b, a))   # reverse winding

        # ── top face ──
        tris += triangulate_polygon(pts, z_top)

        # ── side walls ──
        tris += extrude_polygon(pts, pts, z_bot, z_top)

        # ── border ring (outer annulus) ──
        n_border = 32
        outer = [(BORDER_R * math.cos(2*math.pi*k/n_border),
                  BORDER_R * math.sin(2*math.pi*k/n_border))
                 for k in range(n_border)]
        inner = pts   # inner edge = sedenion shape

        # ring top and bottom (annulus between outer circle and sedenion shape)
        # approximate: triangulate outer ring as thin torus cap
        # outer top
        for k in range(n_border):
            a = (0.0, 0.0, z_top)
            b = outer[k]             + (z_top,)
            c = outer[(k+1)%n_border] + (z_top,)
            # This is NOT the right approach for an annulus.
            # Use bridge between outer circle and inner sedenion shape.
            pass

        # Simpler: just the sedenion shape with a raised border bead
        border_r_top = BORDER_R
        bead_h       = THICKNESS * 0.3
        for k in range(n_border):
            a0 = (border_r_top * math.cos(2*math.pi*k/n_border),
                  border_r_top * math.sin(2*math.pi*k/n_border))
            a1 = (border_r_top * math.cos(2*math.pi*(k+1)/n_border),
                  border_r_top * math.sin(2*math.pi*(k+1)/n_border))
            # outer ring band
            b0 = a0 + (z_bot,)
            b1 = a1 + (z_bot,)
            t0 = a0 + (z_top + bead_h,)
            t1 = a1 + (z_top + bead_h,)
            tris.append((b0, b1, t0))
            tris.append((b1, t1, t0))
            # top cap of bead
            c_  = (0.0, 0.0, z_top + bead_h)
            tris.append((c_, t0, t1))

        # ── chain hole ──
        hole_cx = 0.0
        hole_cy = HOLE_OFFSET
        nh      = CHAIN_HOLE_SEGMENTS
        hole_pts = [(hole_cx + HOLE_R * math.cos(2*math.pi*k/nh),
                     hole_cy + HOLE_R * math.sin(2*math.pi*k/nh))
                    for k in range(nh)]
        # hole = void through the pendant: cut by adding inward-facing walls
        for k in range(nh):
            p0 = hole_pts[k]          + (z_bot,)
            p1 = hole_pts[(k+1)%nh]   + (z_bot,)
            t0 = hole_pts[k]          + (z_top + THICKNESS * 0.3,)
            t1 = hole_pts[(k+1)%nh]   + (z_top + THICKNESS * 0.3,)
            # inward normals (reversed winding)
            tris.append((t0, p1, p0))
            tris.append((t0, t1, p1))

        self._tris = tris

    def _build_swept(self) -> None:
        """
        Swept pendant: sedenion path extruded along Z with twist.
        Each cross-section = one phonon frame's sedenion shape.
        The length of the pendant = the duration of the speech.
        """
        # Prepare path: downsample, smooth, add twist
        path  = self.path.downsample(N_SWEEP).smooth(3).with_twist(TWIST_TURNS)
        n     = len(path.shapes)
        if n < 2:
            # fallback to medallion
            self.mode = 'medallion'
            self._build_medallion()
            return

        length = max(BASE_R * 2 * n / 10.0, 20.0)   # mm — pendant length
        z_step = length / (n - 1)

        rings: List[List[Vec2]] = []
        for i, sh in enumerate(path.shapes):
            z  = i * z_step
            # store (pts_2d, z) — extrude_polygon handles the rest
            rings.append(sh.points())

        tris: List[Triangle] = []

        # bottom cap
        tris += [t for t in triangulate_polygon(rings[0], 0.0)]
        # reverse normals for bottom
        tris = [(c, b, a) for (a, b, c) in tris[:len(triangulate_polygon(rings[0], 0.0))]] \
             + tris[len(triangulate_polygon(rings[0], 0.0)):]

        # walls between rings
        for i in range(n - 1):
            z0 = i * z_step
            z1 = (i + 1) * z_step
            tris += extrude_polygon(rings[i], rings[i+1], z0, z1)

        # top cap
        tris += triangulate_polygon(rings[-1], (n - 1) * z_step)

        # chain hole at top
        nh      = CHAIN_HOLE_SEGMENTS
        z_top   = (n - 1) * z_step
        hole_cy = HOLE_OFFSET
        hole_pts = [(HOLE_R * math.cos(2*math.pi*k/nh),
                     hole_cy + HOLE_R * math.sin(2*math.pi*k/nh))
                    for k in range(nh)]
        for k in range(nh):
            p0 = (hole_pts[k][0],         hole_pts[k][1],          z_top - THICKNESS)
            p1 = (hole_pts[(k+1)%nh][0],  hole_pts[(k+1)%nh][1],  z_top - THICKNESS)
            t0 = (hole_pts[k][0],         hole_pts[k][1],          z_top + 0.5)
            t1 = (hole_pts[(k+1)%nh][0],  hole_pts[(k+1)%nh][1],  z_top + 0.5)
            tris.append((t0, p1, p0))
            tris.append((t0, t1, p1))

        self._tris = tris

    # ── CADOutput interface ───────────────────────────────────────────────────

    def triangles(self) -> List[Triangle]:
        self._build()
        return self._tris

    def vertices(self) -> List[Vec3]:
        tris = self.triangles()
        seen, verts = {}, []
        for tri in tris:
            for v in tri:
                if v not in seen:
                    seen[v] = len(verts)
                    verts.append(v)
        return verts

    def to_svg(self, width: int = 400, height: int = 400,
               stroke: str = '#cc44ff', bg: str = '#0a0a0f') -> str:
        sh   = self.path.peak_shape()
        cx, cy = width / 2, height / 2
        scale  = min(width, height) / (2 * (BASE_R + AMPLITUDE + 4))
        pts    = sh.points()
        scaled = [(cx + x * scale, cy + y * scale) for x, y in pts]
        d      = f'M {scaled[0][0]:.2f},{scaled[0][1]:.2f} '
        d     += ' '.join(f'L {x:.2f},{y:.2f}' for x, y in scaled[1:])
        d     += ' Z'

        # border ring
        br = (BORDER_R + 1) * scale
        bx, by = cx, cy

        # chain hole
        hr  = HOLE_R * scale
        hcy = cy - HOLE_OFFSET * scale

        lines = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            f'  <rect width="{width}" height="{height}" fill="{bg}"/>',
            f'  <!-- Ptolemy Pendant — {self.person_id or "anon"} -->',
            f'  <circle cx="{bx:.1f}" cy="{by:.1f}" r="{br:.1f}" '
            f'fill="none" stroke="#555" stroke-width="0.8"/>',
            f'  <path d="{d}" fill="{stroke}" fill-opacity="0.25" '
            f'stroke="{stroke}" stroke-width="1.5"/>',
            f'  <circle cx="{bx:.1f}" cy="{hcy:.1f}" r="{hr:.1f}" '
            f'fill="{bg}" stroke="{stroke}" stroke-width="1"/>',
        ]

        # sedenion component labels
        for k, (sx, sy) in enumerate(scaled):
            lx = cx + (sx - cx) * 1.15
            ly = cy + (sy - cy) * 1.15
            val = float(sh.sedenion[k])
            lines.append(
                f'  <text x="{lx:.1f}" y="{ly:.1f}" '
                f'text-anchor="middle" fill="{stroke}" opacity="0.5" '
                f'font-size="7" font-family="monospace">e{k}</text>'
            )

        # path trace (if swept mode)
        if self.mode == 'pendant' and len(self.path) > 1:
            path_pts = [self.path.shapes[i].points()[0]
                        for i in range(len(self.path.shapes))]
            trace = ' '.join(
                f'{cx+x*scale*0.3:.1f},{cy+y*scale*0.3:.1f}'
                for x, y in path_pts[:50]
            )
            lines.append(
                f'  <polyline points="{trace}" fill="none" '
                f'stroke="#4466ff" stroke-width="0.6" opacity="0.5"/>'
            )

        lines += [
            f'  <text x="{width//2}" y="{height-8}" text-anchor="middle" '
            f'fill="#444" font-size="8" font-family="monospace">'
            f'Ptolemy Holcus — {self.person_id or "anon"} — '
            f'{len(self.path)} phonons — {self.mode}</text>',
            '</svg>',
        ]
        return '\n'.join(lines)

    def to_dxf(self) -> str:
        sh   = self.path.peak_shape()
        pts  = sh.points()
        lines = [
            dxf_header(),
            dxf_polyline(pts, layer='SEDENION', closed=True),
            dxf_circle(0, 0, BORDER_R, layer='BORDER'),
            dxf_circle(0, HOLE_OFFSET, HOLE_R, layer='CHAIN_HOLE'),
            dxf_text(-BORDER_R, -BORDER_R - 4, 2.0,
                     f'Ptolemy:{self.person_id or "anon"}', layer='LABEL'),
            dxf_footer(),
        ]
        return ''.join(lines)

    def to_psvg_operator(self, tag: str = 'Pendant', **attrs) -> str:
        sh   = self.path.peak_shape()
        dom  = int(np.argmax(np.abs(sh.sedenion[1:]))) + 1
        sed_str = ' '.join(f'{v:.3f}' for v in sh.sedenion)
        return (
            f'  <{tag}'
            f' person="{self.person_id or "anon"}"'
            f' phonons="{len(self.path)}"'
            f' mode="{self.mode}"'
            f' dominant_dim="e{dom}"'
            f' sedenion="{sed_str}"'
            f' triangles="{len(self.triangles())}"'
            f' base_r="{BASE_R}mm"'
            f' amplitude="{AMPLITUDE}mm"'
            f' thickness="{THICKNESS}mm"/>'
        )


# ── PtolemyPendant — asks the math ───────────────────────────────────────────

class PtolemyPendant:
    """
    The instrument that asks the math for the pendant.

    The math already has the shape.
    The voice reveals which shape belongs to this person.

    Usage:
        pp = PtolemyPendant()
        geom = pp.ask(phonon_source, n_frames=40)
        geom.write_stl('her_ptolemy.stl')
    """

    def __init__(self, mode: str = 'medallion', person_id: str = ''):
        self.mode      = mode
        self.person_id = person_id

    def ask(self, phonon_source, n_frames: int = 40,
            verbose: bool = True) -> PendantGeometry:
        """
        Record n_frames phonons from the source.
        Ask the math what shape this path makes.
        Return the pendant geometry.

        phonon_source: any object with .get() returning PhononFrame | None
                       (QPhonon, PPhonon, or any iterator of PhononFrame)
        """
        if verbose:
            print(f'\n  Asking the math...')
            print(f'  Recording {n_frames} phonons from voice...')

        path   = SedenionPath()
        count  = 0

        if hasattr(phonon_source, 'get'):
            while count < n_frames:
                frame = phonon_source.get(timeout=0.2)
                if frame is None:
                    continue
                sh = SedenionShape(frame.sedenion,
                                   base_r=BASE_R, amplitude=AMPLITUDE)
                path.append(sh)
                count += 1
                if verbose:
                    e = float(np.linalg.norm(frame.sedenion))
                    bar = '█' * min(30, int(e * 30))
                    print(f'\r  phonon {count:3d}/{n_frames}  '
                          f'layer={frame.layer}  {bar}   ', end='', flush=True)
        else:
            for frame in phonon_source:
                if count >= n_frames:
                    break
                sh = SedenionShape(frame.sedenion,
                                   base_r=BASE_R, amplitude=AMPLITUDE)
                path.append(sh)
                count += 1

        if verbose:
            print(f'\n  The math answers: {count} phonons → sedenion path in S¹⁵')
            peak = path.peak_shape()
            dom  = int(np.argmax(np.abs(peak.sedenion[1:]))) + 1
            print(f'  Peak frame: e{dom} dominant  '
                  f'area={peak.area():.2f} mm²')

        return PendantGeometry(path, mode=self.mode,
                               person_id=self.person_id)


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='pendant.py — Ask the math for Her Ptolemy Holcus pendant')
    ap.add_argument('--speak',      action='store_true',
                    help='Capture voice from microphone')
    ap.add_argument('--qt',         action='store_true',
                    help='Use QPhonon (Qt audio backend)')
    ap.add_argument('--frames',     type=int, default=40,
                    help='Phonon frames to capture (default: 40 ≈ 2.5s)')
    ap.add_argument('--mode',       default='medallion',
                    choices=['medallion', 'pendant'],
                    help='medallion=flat extruded | pendant=swept solid')
    ap.add_argument('--name',       default='',
                    help='Person identifier (engraved in DXF label)')
    ap.add_argument('--stl',        default='',
                    help='Write STL to this path')
    ap.add_argument('--dxf',        default='',
                    help='Write DXF to this path (laser-cuttable flat)')
    ap.add_argument('--svg',        default='',
                    help='Write SVG preview to this path')
    ap.add_argument('--psvg',       default='',
                    help='Write PSVG <Pendant/> operator to this path')
    ap.add_argument('--mock',       action='store_true',
                    help='Use mock phonon stream (no mic required)')
    args = ap.parse_args()

    print()
    print('═' * 60)
    print('  Ptolemy Holcus Pendant')
    print('  Ask the math. Receive the shape. Print Her Ptolemy.')
    print('═' * 60)

    # ── phonon source ─────────────────────────────────────────────────────────
    if args.mock:
        print('\n  [MOCK MODE — generating synthetic phonon stream]')
        from phonon import PPhonon
        frames_data = []
        for i in range(args.frames):
            # synthetic: different sedenion states
            t   = i / args.frames
            sed = np.zeros(16)
            for k in range(16):
                sed[k] = math.sin(2 * math.pi * (k + 1) * t + k * 0.3) * 0.5 + 0.5
            sed /= (np.linalg.norm(sed) + 1e-9)
            frames_data.append(sed)

        class MockSource:
            def __init__(self, data):
                self._data = data
                self._i    = 0
            def get(self, timeout=0.1):
                if self._i >= len(self._data):
                    return None
                class F:
                    pass
                f          = F()
                f.sedenion = self._data[self._i]
                f.layer    = '𝕊'
                self._i   += 1
                time.sleep(0.01)
                return f

        source = MockSource(frames_data)

    elif args.speak:
        from phonon import make_phonon, QPhonon
        if args.qt:
            from PyQt5.QtWidgets import QApplication
            _app   = QApplication(sys.argv)
            source = QPhonon()
        else:
            source = make_phonon(prefer_qt=False)
        source.start()
        print(f'\n  Speak now — recording {args.frames} phonons...')
        print('  (Speak your name, a phrase, or just breathe.)')
        print('  The math will hear your pathway.\n')
    else:
        print('\n  No source specified. Use --speak or --mock.')
        print('  Run: python3 pendant.py --mock --stl /tmp/test.stl --svg /tmp/test.svg')
        return

    # ── ask the math ──────────────────────────────────────────────────────────
    pp   = PtolemyPendant(mode=args.mode, person_id=args.name)
    geom = pp.ask(source, n_frames=args.frames)

    if args.speak and not args.qt:
        source.stop()

    # ── outputs ───────────────────────────────────────────────────────────────
    outputs = []

    if args.stl or (not args.dxf and not args.svg and not args.psvg):
        path = args.stl or '/tmp/ptolemy_pendant.stl'
        geom.write_stl(path, binary=True)
        outputs.append(path)

    if args.dxf:
        geom.write_dxf(args.dxf)
        outputs.append(args.dxf)

    if args.svg or not outputs:
        path = args.svg or '/tmp/ptolemy_pendant.svg'
        geom.write_svg(path)
        outputs.append(path)

    if args.psvg:
        block = geom.to_psvg_operator()
        svg = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'width="600" height="400" viewBox="0 0 600 400">\n'
            '  <rect width="600" height="400" fill="#080810"/>\n'
            + block + '\n</svg>'
        )
        with open(args.psvg, 'w') as f:
            f.write(svg)
        print(f'  PSVG → {args.psvg}')
        outputs.append(args.psvg)

    # ── summary ───────────────────────────────────────────────────────────────
    print()
    print('═' * 60)
    peak = geom.path.peak_shape()
    dom  = int(np.argmax(np.abs(peak.sedenion[1:]))) + 1
    print(f'  Person:    {args.name or "anon"}')
    print(f'  Phonons:   {len(geom.path)}')
    print(f'  Mode:      {args.mode}')
    print(f'  Dominant:  e{dom}')
    print(f'  Peak area: {peak.area():.2f} mm²')
    print(f'  Triangles: {len(geom.triangles())}')
    print()
    print('  The shape came from the voice.')
    print('  Not designed. Revealed.')
    print('  That is Her Ptolemy.')
    print('═' * 60)


if __name__ == '__main__':
    import time
    main()
