#!/usr/bin/env python3
"""cam3.py — the sedenion camshaft AT THE CENTRE OF THE ROTOR.

    THE CRANK AND THE CAMSHAFT ARE THE SAME SHAFT.

That is the whole architecture and it is what makes this a Wankel rather than a
piston engine. A real Wankel has no valves and no camshaft: port timing is done
by the rotor's own faces sweeping past the intake and exhaust ports. There is
nothing to advance or retard, because there is no second shaft to advance it
against.

CORRECTION, 2026-08-17. An earlier version of this file (and vagcom.py's
Channel 01) modelled a TDI cam: an independent timing shaft carrying its own
writable advance, applied as a phase offset against the crank. That is a piston
engine's architecture. In this engine there is ONE angle, theta, and the sixteen
sedenion lobes are rigidly indexed to it because they are cut into the rotor's
internal axis. Advancing them is not a control input -- it is just turning the
rotor.

WHAT IS ACTUALLY ADJUSTABLE

Not timing. The trochoid:

    apex path      z(phi) = R.e^{i.phi} + e.e^{-i.k.phi}          k = 3
    the loss       min|z| = |R - e|   EXACTLY
    the null       zero loss  <=>  R = e  <=>  sigma_self = 1/2

    R = sqrt(p_red)     forward / cos / Riemann
    e = sqrt(p_blue)    backward / sin / Fermat  (the adjoint)

R and e are the generating radius and the eccentricity -- the two numbers that
define the rotor's shape and therefore its port timing. Timing is a CONSEQUENCE
of geometry here, not a free parameter laid on top of it. (Verified in
vagcom.Group003.verify_against_path: reported loss == min|z| to numerical
precision.)

WHY THREE PHASES ARE NOT IMPOSED

A Wankel rotor is a triangle. Three apexes, three faces, each face running a
complete four-stroke cycle per rotor revolution -- three power strokes per
revolution, 120 degrees apart. The three-phase structure IS the rotor's
geometry. It is not an electrical analogy borrowed and dropped on top; the 120
degrees was already in rotary_monad.py's firing order for exactly this reason:

    theta =   0 deg   intake     J_blue face opens
    theta = 120 deg   leading    [J_blue, J_red] fires
    theta = 240 deg   trailing   [J_red, J_green] fires

GEARING. The eccentric shaft turns 3x for every rotor revolution (GEAR_K = 3,
the 3:2 internal gear set). So one shaft angle theta drives both: rotor phase is
theta / 3, and face f sits at rotor phase + 2.pi.f/3.

THE LOSS IS THE NEUTRAL CURRENT. In a balanced three-phase system the neutral
carries zero, and that is this framework's own conservation law read as a
circuit:

    J_red + J_blue + J_green = 0            (wiki 47, the three Silmarils)
    |J_red + J_blue + J_green| = the NEUTRAL = the loss

Group 003's |R - e| is the two-phase closure of a 2-cycle; the neutral is the
closure of a 3-cycle. Currents are SIGNED -- powers cannot sum to zero, and the
conservation law is about currents.

python3 first. Port to PtolC/ only once a result is significant.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ['Trochoid', 'RotorCam', 'Group004', 'FACE', 'face_map',
           'shaft_sweep', 'trochoid_sweep', 'N_FACE', 'GEAR_K']

# ── constants (mirror rotary_monad.py / vagcom.py) ───────────────────────────
SIGMA_PIN = 0.5
GAP       = 0.000707
N_DIM     = 16
N_FACE    = 3                  # a Wankel rotor is a triangle
GEAR_K    = 3                  # eccentric shaft : rotor, the 3:2 gear set

#: the three rotor faces, 120 degrees apart in the ROTOR frame
FACE: Dict[str, float] = {
    'blue':  0.0,
    'red':   2.0 * math.pi / 3.0,
    'green': 4.0 * math.pi / 3.0,
}
_ORDER = ('blue', 'red', 'green')


def face_map(symmetric: bool = True) -> Dict[int, str]:
    """Assign the 16 sedenion dimensions to rotor faces.

    ``symmetric=True`` (the default, and the only assignment consistent with a
    three-faced rotor): e0 is the AXIS and carries no face. The 15 imaginary
    units divide evenly, **5 per face** -- 15 = 3 x 5. e0 sitting at the centre
    doing no work matches wiki 87's fulcrum result directly: a fulcrum does no
    work.

    ``symmetric=False`` reproduces rotary_monad._project_sedenion's map
    (e1-7 blue, e8-14 red, e15 green). **That map is 7/7/1 and is therefore NOT
    three-fold symmetric**, so it cannot be the three faces of one rotor -- it is
    a two-octonion split with a leftover, which is a different object. Kept here
    only so the two can be compared; do not use it for rotor geometry.

    :param symmetric: use the 5/5/5 rotor-symmetric assignment.
    :rtype: dict
    """
    if not symmetric:
        return ({0: 'axis'} | {k: 'blue' for k in range(1, 8)}
                | {k: 'red' for k in range(8, 15)} | {15: 'green'})
    m: Dict[int, str] = {0: 'axis'}
    for k in range(1, N_DIM):
        m[k] = _ORDER[(k - 1) % N_FACE]
    return m


# ══════════════════════════════════════════════════════════════════════════════
#  The trochoid — the ONLY adjustable. Timing follows from it.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Trochoid:
    """The rotor's generating radius R and eccentricity e.

    These two numbers are the engine's geometry, and its timing is a consequence
    of them rather than a separate input. K = R/e is the trochoid constant; real
    Wankels run K ~ 7. The null is R = e (K = 1), which is the zero-divisor
    event, not a buildable engine -- worth stating plainly, because the machine
    is tuned TOWARD a condition it cannot occupy.
    """
    R: float = 1.0
    e: float = 1.0

    @classmethod
    def from_powers(cls, p_red: float, p_blue: float) -> 'Trochoid':
        return cls(R=math.sqrt(max(p_red, 0.0)), e=math.sqrt(max(p_blue, 0.0)))

    @property
    def K(self) -> float:
        return self.R / self.e if self.e > GAP else float('inf')

    @property
    def loss(self) -> float:
        """min|z| over the apex path, in closed form: |R - e|."""
        return abs(self.R - self.e)

    @property
    def sigma_self(self) -> float:
        t = self.R ** 2 + self.e ** 2
        return (self.R ** 2 / t) if t > GAP else SIGMA_PIN

    def apex_path(self, n: int = 2001, k: int = GEAR_K) -> np.ndarray:
        phi = np.linspace(0.0, 2.0 * np.pi, n)
        return self.R * np.exp(1j * phi) + self.e * np.exp(-1j * k * phi)

    def verify_loss(self, n: int = 20001) -> float:
        """|min|z| numerically  -  |R - e||. Asserts the closed form IS the path."""
        return abs(float(np.abs(self.apex_path(n)).min()) - self.loss)


# ══════════════════════════════════════════════════════════════════════════════
#  The rotor cam — lobes cut into the rotor's internal axis
# ══════════════════════════════════════════════════════════════════════════════

class RotorCam:
    """Hermite H16 lobes fixed to the rotor's internal axis. No independent phase.

    The lobe heights are the H16 zeros squared and normalised: 8 distinct
    heights, each appearing twice under partner(k) = 15 - k. That involution is
    ``k XOR 15``, the all-four-generations complement (strut 15) -- the element
    the Fano pencil converges on. Not designed in; it follows from the Hermite
    symmetry being even.

    Because the cam IS the crank, ``lift`` takes only the shaft angle. There is
    no advance argument, deliberately: adding one would rebuild the TDI.
    """

    def __init__(self, symmetric: bool = True) -> None:
        zeros = np.polynomial.hermite.hermroots([0] * N_DIM + [1])
        lobes = zeros ** 2
        self.zeros: np.ndarray = zeros
        self.lobes: np.ndarray = lobes / lobes.max()
        self.map: Dict[int, str] = face_map(symmetric)
        self.symmetric = symmetric

    @staticmethod
    def partner(k: int) -> int:
        return (N_DIM - 1) - k

    def face_of(self, k: int) -> str:
        return self.map[k]

    def face_dims(self, face: str) -> List[int]:
        return [k for k in range(N_DIM) if self.map[k] == face]

    def rotor_phase(self, theta: float) -> float:
        """Rotor angle from shaft angle. One shaft, 3:1 gearing."""
        return theta / GEAR_K

    def lift(self, theta: float) -> np.ndarray:
        """Per-dimension lobe lift at shaft angle ``theta``.

        lift[k] = lobes[k] * (1 + cos(rotor_phase + face_phase)) / 2

        Bounded in [0, lobes[k]] -- a cam lobe lifts, it does not pull. The face
        phase is what puts the three faces 120 degrees apart, and the rotor phase
        is theta/3, so the whole pattern is rigidly geared to the one shaft.
        """
        rp = self.rotor_phase(theta)
        out = np.zeros(N_DIM)
        for k in range(N_DIM):
            f = self.map[k]
            if f == 'axis':
                continue                    # e0 is the axis: no lift, no work
            out[k] = self.lobes[k] * (1.0 + math.cos(rp + FACE[f])) * 0.5
        return out


# ══════════════════════════════════════════════════════════════════════════════
#  Variable PORT timing — the control input. Ptol watches here and regulates here.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class PortTiming:
    """Variable port timing. The Wankel's actual VVT, and it is NOT cam-side.

    The cam is rigidly geared to the crank (they are one shaft), so nothing about
    the rotor's lobes can be advanced. But a rotary DOES have variable timing --
    it lives in the HOUSING, as variable intake ports. Mazda shipped this: the
    13B's 6PI six-port induction and the Renesis variable intake both open and
    close auxiliary ports to shift *effective* port timing without any camshaft
    existing anywhere in the engine.

    So the control input is WHEN each face is allowed to couple, not when a lobe
    lifts. That is the whole distinction, and it is why this class sits apart from
    RotorCam.

    Angles are in the ROTOR frame, radians, measured from face TDC.

        Channel 04  INTAKE_PHASE    shifts both intake edges together
        Channel 05  EXHAUST_PHASE   shifts both exhaust edges together
        Channel 06  DURATION_TRIM   widens/narrows both windows together

    OVERLAP IS THE HAZARD. Overlap is the angular window where intake and exhaust
    are open at the same time. Cody, this session: "one valve at a time... both
    valves open -> catastrophic drop", corrected to "that's loss of compression,
    not oil pressure -- air intake and exhaust manifolds". So overlap is the thing
    the regulator must bound, and compression is the term that punishes it.
    """
    intake_phase:   float = 0.0
    exhaust_phase:  float = 0.0
    duration_trim:  float = 0.0

    #: base half-width of each port window, radians of rotor angle
    BASE_DURATION = 2.0 * math.pi / 6.0        # 60 deg half-width
    PHASE_LIMIT   = math.pi / 8                # THE ANGLE, same clamp as Ch01
    TRIM_LIMIT    = math.pi / 12

    _CH = {'04': 'intake_phase', '05': 'exhaust_phase', '06': 'duration_trim'}

    def __post_init__(self) -> None:
        self.intake_phase  = self._clamp(self.intake_phase,  self.PHASE_LIMIT)
        self.exhaust_phase = self._clamp(self.exhaust_phase, self.PHASE_LIMIT)
        self.duration_trim = self._clamp(self.duration_trim, self.TRIM_LIMIT)

    @staticmethod
    def _clamp(v: float, lim: float) -> float:
        if not math.isfinite(v):
            raise ValueError(f'port timing: non-finite {v!r}')
        return max(-lim, min(lim, float(v)))

    def write_channel(self, n: str, v: float) -> float:
        key = str(n).zfill(2)
        if key not in self._CH:
            raise KeyError(f'channel {n} not implemented (04/05/06 only)')
        lim = self.TRIM_LIMIT if key == '06' else self.PHASE_LIMIT
        setattr(self, self._CH[key], self._clamp(v, lim))
        return getattr(self, self._CH[key])

    def read_channel(self, n: str) -> float:
        key = str(n).zfill(2)
        if key not in self._CH:
            raise KeyError(f'channel {n} not implemented (04/05/06 only)')
        return getattr(self, self._CH[key])

    def reset(self) -> None:
        self.intake_phase = self.exhaust_phase = self.duration_trim = 0.0

    @property
    def duration(self) -> float:
        return max(GAP, self.BASE_DURATION + self.duration_trim)

    @property
    def overlap(self) -> float:
        """Angular window where intake and exhaust are both open. >= 0.

        The two windows are centred a half-turn apart at nominal timing; the
        phase channels move them toward or away from each other.
        """
        centre_gap = abs(math.pi + self.exhaust_phase - self.intake_phase)
        return max(0.0, 2.0 * self.duration - centre_gap)

    @property
    def compression(self) -> float:
        """Compression retained, in [0, 1]. Collapses as overlap opens.

        **MODELLING CHOICE, not a derived law.** The functional form is chosen to
        be steep because the established behaviour is a *catastrophic* drop when
        both ports are open, not a gentle taper. Anything quantitative resting on
        the exact curve needs the curve derived first.
        """
        if self.overlap <= 0.0:
            return 1.0
        return math.exp(-6.0 * self.overlap / self.BASE_DURATION)

    def window(self, rotor_phase: float, face: str) -> float:
        """Is face ``face`` coupled at this rotor phase? Smooth gate in [0, 1].

        Raised-cosine rather than a hard edge: a port opens over an angle, and a
        discontinuous gate would put a step in the current and make the neutral
        unreadable.
        """
        centre = FACE[face] + self.intake_phase
        d = (rotor_phase - centre + math.pi) % (2.0 * math.pi) - math.pi
        if abs(d) >= self.duration:
            return 0.0
        return 0.5 * (1.0 + math.cos(math.pi * d / self.duration))


@dataclass(frozen=True)
class Group005:
    """Measuring block 005 — COMPRESSION. What overlap is costing.

        overlap      angular window with both ports open
        compression  retained compression in [0, 1]
        duration     current port half-width
    """
    overlap:     float
    compression: float
    duration:    float

    GROUP = '005'
    NAME  = 'COMPRESSION'
    LABELS = ('overlap', 'compression', 'duration')

    @classmethod
    def from_ports(cls, p: PortTiming) -> 'Group005':
        return cls(p.overlap, p.compression, p.duration)

    @property
    def faults(self) -> List[str]:
        f: List[str] = []
        if self.compression < 0.5:
            f.append('R0002:compression_loss')
        if self.overlap > 0.0:
            f.append('R0003:port_overlap')
        return f

    def __str__(self) -> str:
        return (f'Grp {self.GROUP} {self.NAME}  overlap={self.overlap:.6f} '
                f'compression={self.compression:.6f} dur={self.duration:.6f}')


# ══════════════════════════════════════════════════════════════════════════════
#  Group 004 — THREE-PHASE BALANCE. The loss is the neutral current.
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Group004:
    """Measuring block 004 — THREE_PHASE. The engine is wrong by ``neutral``."""
    j_blue:    float
    j_red:     float
    j_green:   float
    neutral:   float
    loss:      float
    imbalance: float
    theta:     float = 0.0

    GROUP = '004'
    NAME  = 'THREE_PHASE'
    LABELS = ('j_blue', 'j_red', 'j_green', 'neutral')

    @classmethod
    def from_currents(cls, b: float, r: float, g: float,
                      theta: float = 0.0) -> 'Group004':
        n = b + r + g
        mag = abs(b) + abs(r) + abs(g)
        return cls(b, r, g, n, abs(n),
                   (abs(n) / mag) if mag > GAP else 0.0, theta)

    @property
    def at_null(self) -> bool:
        return self.loss < 1e-12

    def as_block(self) -> Dict[str, float]:
        return {k: getattr(self, k) for k in self.LABELS}

    def __str__(self) -> str:
        return (f'Grp {self.GROUP} {self.NAME}  b={self.j_blue:+.6f} '
                f'r={self.j_red:+.6f} g={self.j_green:+.6f}  '
                f'NEUTRAL={self.neutral:+.6f}  imb={self.imbalance:.4f}')


# ══════════════════════════════════════════════════════════════════════════════
#  The engine
# ══════════════════════════════════════════════════════════════════════════════

class Wankel:
    """The rotary monad: one shaft, three faces, sixteen lobes on the axis."""

    PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53)

    def __init__(self, troch: Optional[Trochoid] = None,
                 cam: Optional[RotorCam] = None,
                 ports: Optional[PortTiming] = None) -> None:
        self.troch = troch or Trochoid()
        self.cam = cam or RotorCam()
        self.ports = ports or PortTiming()
        self.log: List[Group004] = []

    def currents(self, psi: Sequence[float], theta: float,
                 sigma: float = SIGMA_PIN) -> Tuple[float, float, float]:
        """Project psi into the three SIGNED face currents at shaft angle theta.

        Three factors multiply, and they are three different things:
          lift[k]              the cam -- rigidly geared, NOT adjustable
          ports.window(...)    variable port timing -- the control input
          ports.compression    what overlap is costing, applied to all faces
        """
        psi = np.asarray(psi, dtype=float)
        if psi.shape != (N_DIM,):
            raise ValueError(f'psi must be length {N_DIM}, got {psi.shape}')
        lift = self.cam.lift(theta)
        rp = self.cam.rotor_phase(theta)
        comp = self.ports.compression
        acc = {'blue': 0.0, 'red': 0.0, 'green': 0.0}
        for k in range(N_DIM):
            f = self.cam.map[k]
            if f == 'axis':
                continue
            gate = self.ports.window(rp, f)
            if gate <= 0.0:
                continue
            phase = 2.0 * math.pi / self.PRIMES[k] + FACE[f]
            w = math.cos(phase) if f == 'red' else math.sin(phase)
            acc[f] += psi[k] * w * lift[k] * gate * comp * (k + 1) ** (-sigma)
        return acc['blue'], acc['red'], acc['green']

    def group_004(self, psi: Sequence[float], theta: float,
                  record: bool = True) -> Group004:
        b, r, g = self.currents(psi, theta)
        blk = Group004.from_currents(b, r, g, theta)
        if record:
            self.log.append(blk)
        return blk

    def group_005(self) -> Group005:
        return Group005.from_ports(self.ports)

    # -- A) WATCH -----------------------------------------------------------
    def watch(self, psi: Sequence[float], steps: int = 72) -> Dict[str, float]:
        """Read-only snapshot over one rotor revolution. The OBD2 layer.

        Post-facto and non-intervening: this is the lamp, not the loop.
        """
        rows = shaft_sweep(self, psi, revs=1.0, steps=steps)
        g5 = self.group_005()
        rms = float(np.sqrt(np.mean([g.neutral ** 2 for g in rows])))
        return {
            'neutral_rms':   rms,
            'neutral_peak':  max(abs(g.neutral) for g in rows),
            'imbalance_max': max(g.imbalance for g in rows),
            'overlap':       g5.overlap,
            'compression':   g5.compression,
            'trochoid_loss': self.troch.loss,
            'faults':        len(g5.faults),
        }

    # -- B) REGULATE --------------------------------------------------------
    def regulate(self, psi: Sequence[float], iters: int = 40,
                 steps: int = 36, verbose: bool = False) -> List[Dict[str, float]]:
        """Steer port timing to minimise neutral RMS while holding compression.

        Coordinate descent on channels 04/05/06. The objective is deliberately
        constrained rather than penalised: a candidate that drops compression
        below 0.5 is REJECTED outright, because a compression-loss engine is not
        a better-tuned engine, it is a broken one. Optimising a weighted sum
        would happily trade compression for balance.

        :returns: the trace, one row per accepted move.
        """
        def cost(p: PortTiming) -> float:
            saved, self.ports = self.ports, p
            try:
                if p.compression < 0.5:
                    return float('inf')          # constraint, not penalty
                rows = shaft_sweep(self, psi, revs=1.0, steps=steps)
                return float(np.sqrt(np.mean([g.neutral ** 2 for g in rows])))
            finally:
                self.ports = saved

        chans = ('04', '05', '06')
        cur = cost(self.ports)
        trace = [{'iter': 0, 'cost': cur, 'ch04': self.ports.intake_phase,
                  'ch05': self.ports.exhaust_phase, 'ch06': self.ports.duration_trim,
                  'compression': self.ports.compression}]
        step = PortTiming.PHASE_LIMIT / 4.0
        for it in range(1, iters + 1):
            improved = False
            for ch in chans:
                for sgn in (+1.0, -1.0):
                    trial = PortTiming(self.ports.intake_phase,
                                       self.ports.exhaust_phase,
                                       self.ports.duration_trim)
                    trial.write_channel(ch, trial.read_channel(ch) + sgn * step)
                    c = cost(trial)
                    if c < cur - 1e-15:
                        cur, self.ports, improved = c, trial, True
                        trace.append({'iter': it, 'cost': cur,
                                      'ch04': trial.intake_phase,
                                      'ch05': trial.exhaust_phase,
                                      'ch06': trial.duration_trim,
                                      'compression': trial.compression})
                        if verbose:
                            print(f'   it{it:>3} ch{ch} -> cost {cur:.9f} '
                                  f'comp {trial.compression:.4f}')
                        break
            if not improved:
                step *= 0.5
                if step < 1e-6:
                    break
        return trace


def shaft_sweep(w: Wankel, psi: Sequence[float], revs: float = 1.0,
                steps: int = 36) -> List[Group004]:
    """Sweep the ONE shaft angle. ``revs`` counts ROTOR revolutions."""
    end = revs * GEAR_K * 2.0 * math.pi
    return [w.group_004(psi, t, record=False)
            for t in np.linspace(0.0, end, steps, endpoint=False)]


def trochoid_sweep(psi: Sequence[float], cam: RotorCam,
                   steps: int = 17) -> List[Tuple[float, float, float]]:
    """Sweep the trochoid constant K = R/e.

    Reports neutral **RMS**, not min. Using min here was a real error and it is
    worth recording why: the port windows are raised cosines that reach exactly
    zero at their edges, so at every gate boundary all three faces are shut and
    the neutral is identically zero. ``min|neutral|`` therefore returns 0.0 for
    every K -- a dead engine has perfect balance. RMS cannot be gamed that way.

    :returns: list of ``(K, trochoid_loss, neutral_rms_over_a_revolution)``.
    """
    out = []
    for K in np.linspace(1.0, 9.0, steps):
        tr = Trochoid(R=K, e=1.0)
        w = Wankel(tr, cam)
        rows = shaft_sweep(w, psi, revs=1.0, steps=36)
        rms = float(np.sqrt(np.mean([g.neutral ** 2 for g in rows])))
        out.append((float(K), tr.loss, rms))
    return out


def gate_coverage(w: 'Wankel', steps: int = 720) -> Dict[str, float]:
    """What fraction of a rotor revolution has 0, 1, or >1 faces coupled.

    A rotary should run ONE face at a time (Cody: "one valve at a time... both
    valves open -> catastrophic drop"). This measures whether the port windows
    actually achieve that, or whether they leave dead spots and double-openings.
    """
    n0 = n1 = n2 = 0
    for rp in np.linspace(0.0, 2.0 * math.pi, steps, endpoint=False):
        opens = sum(1 for f in _ORDER if w.ports.window(float(rp), f) > 1e-9)
        if opens == 0:
            n0 += 1
        elif opens == 1:
            n1 += 1
        else:
            n2 += 1
    return {'none': n0 / steps, 'one': n1 / steps, 'multi': n2 / steps}


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    np.set_printoptions(precision=4, suppress=True)
    print('=' * 78)
    print('cam3.py — SEDENION CAMSHAFT AT THE CENTRE OF THE ROTOR')
    print('        crank == camshaft == ONE shaft.  No advance channel exists.')
    print('=' * 78)

    cam = RotorCam(symmetric=True)
    print('\n1. ROTOR GEOMETRY')
    print(f'   faces                 : {N_FACE} (a Wankel rotor is a triangle)')
    print(f'   gearing               : {GEAR_K}:1 eccentric shaft : rotor')
    for f in _ORDER:
        d = cam.face_dims(f)
        print(f'   face {f:<6} dims      : {d}  ({len(d)} lobes)')
    print(f'   axis (no work)        : {cam.face_dims("axis")}')
    ok = all(len(cam.face_dims(f)) == 5 for f in _ORDER)
    print(f'   5 lobes per face      : {ok}   (15 imaginaries / 3 faces = 5)')
    xor15 = all(cam.partner(k) == (k ^ 15) for k in range(N_DIM))
    print(f'   partner(k) == k XOR 15: {xor15}  <- all-generations complement')

    print('\n   THE ASYMMETRY THIS EXPOSES:')
    asym = RotorCam(symmetric=False)
    print(f'   rotary_monad map sizes: ' +
          ', '.join(f'{f}={len(asym.face_dims(f))}' for f in _ORDER))
    print('   7/7/1 is NOT three-fold symmetric -> cannot be 3 faces of one rotor.')
    print('   It is a two-octonion split with a leftover. Different object.')

    # ── 2. the trochoid is the adjustable, and the loss is closed-form ──────
    print(f'\n{"=" * 78}\n2. THE TROCHOID — the only adjustable. Is |R-e| the path?\n{"=" * 78}')
    print(f'   {"K=R/e":>8}{"R":>7}{"e":>7}{"sigma_self":>12}{"loss |R-e|":>12}{"min|z| err":>13}')
    for K in (1.0, 1.5, 3.0, 7.0):
        tr = Trochoid(R=K, e=1.0)
        print(f'   {tr.K:>8.3f}{tr.R:>7.2f}{tr.e:>7.2f}{tr.sigma_self:>12.6f}'
              f'{tr.loss:>12.6f}{tr.verify_loss():>13.2e}')
    print('\n   closed form == the geometry. K=1 (R=e) is the null: loss 0, sigma 1/2.')
    print('   Real Wankels run K~7. The engine is tuned TOWARD a state it cannot occupy.')

    rng = np.random.default_rng(7)
    psi = np.abs(rng.normal(size=N_DIM)); psi /= np.linalg.norm(psi)

    # ── 3. one shaft drives everything: theta dependence ────────────────────
    print(f'\n{"=" * 78}\n3. ONE SHAFT — does the neutral move with theta alone?\n{"=" * 78}')
    w = Wankel(Trochoid(R=7.0, e=1.0), cam)
    rows = shaft_sweep(w, psi, revs=1.0, steps=12)
    print(f'   {"shaft":>8}{"rotor":>8}{"j_blue":>11}{"j_red":>11}{"j_green":>11}{"NEUTRAL":>11}')
    for g in rows:
        print(f'   {math.degrees(g.theta):>8.1f}{math.degrees(g.theta/GEAR_K):>8.1f}'
              f'{g.j_blue:>11.6f}{g.j_red:>11.6f}{g.j_green:>11.6f}{g.neutral:>11.6f}')
    sp = max(g.loss for g in rows) - min(g.loss for g in rows)
    print(f'\n   neutral spread over one ROTOR revolution : {sp:.6e}')
    print(f'   THETA DEPENDENCE: {"PRESENT" if sp > 1e-12 else "ABSENT"} '
          f'(no advance channel was used -- there is none)')

    # ── 4. three power strokes per rotor revolution ─────────────────────────
    print(f'\n{"=" * 78}\n4. THREE POWER STROKES PER ROTOR REVOLUTION?\n{"=" * 78}')
    fine = shaft_sweep(w, psi, revs=1.0, steps=360)
    ne = np.array([g.neutral for g in fine])
    sign_changes = int(np.sum(np.diff(np.sign(ne)) != 0))
    print(f'   neutral sign changes over one rotor revolution : {sign_changes}')
    print(f'   (a balanced 3-phase neutral crosses zero 2x per phase = 6 for 3 faces)')
    for f in _ORDER:
        col = np.array([getattr(g, f'j_{f}') for g in fine])
        pk = int(np.argmax(np.abs(col)))     # |current| -- argmax on the SIGNED
        # column returned index 0 for every face, because red and green run
        # negative and the max of a signed array with negatives is a zeroed
        # (gated-off) sample. That was a defect in this diagnostic, not a
        # degenerate engine: the faces really are 120 deg apart.
        print(f'   face {f:<6} peaks at rotor {math.degrees(fine[pk].theta/GEAR_K):>6.1f} deg'
              f'   (|j| = {abs(col[pk]):.6f})')
    gc = gate_coverage(w)
    print(f'\n   gate coverage over a revolution: '
          f'none={gc["none"]:.3f}  one={gc["one"]:.3f}  multi={gc["multi"]:.3f}')
    print(f'   ONE face at a time: {"HOLDS" if gc["multi"] < 1e-9 else "VIOLATED"}'
          f'   dead spots: {gc["none"]:.3f}')

    # ── 5. does the trochoid steer the neutral? ─────────────────────────────
    print(f'\n{"=" * 78}\n5. TROCHOID SWEEP — does geometry steer the neutral?\n{"=" * 78}')
    ts = trochoid_sweep(psi, cam, steps=9)
    print(f'   {"K":>7}{"|R-e|":>11}{"neutral RMS":>15}')
    for K, tl, mn in ts:
        print(f'   {K:>7.2f}{tl:>11.6f}{mn:>15.9f}')
    best = min(ts, key=lambda r: r[2])
    print(f'\n   min neutral RMS at K = {best[0]:.2f}')
    print(f'   NOTE: the neutral here is driven by the LOBE PATTERN, not by K --')
    print(f'   K scales R and e, which sets |R-e|, a SEPARATE loss. Two losses,')
    print(f'   two mechanisms. Do not conflate them.')

    # ── 6. VARIABLE PORT TIMING — the real VVT, housing-side ────────────────
    print(f'\n{"=" * 78}\n6. VARIABLE PORT TIMING — overlap and compression\n{"=" * 78}')
    print(f'   {"ch04":>9}{"ch05":>9}{"ch06":>9}{"overlap":>10}{"compression":>13}  faults')
    for i, e, d in [(0.0, 0.0, 0.0), (0.2, 0.0, 0.0), (0.0, 0.0, 0.25),
                    (0.39, -0.39, 0.26), (-0.2, 0.2, 0.0)]:
        p = PortTiming(i, e, d)
        g5 = Group005.from_ports(p)
        print(f'   {p.intake_phase:>+9.4f}{p.exhaust_phase:>+9.4f}'
              f'{p.duration_trim:>+9.4f}{g5.overlap:>10.5f}{g5.compression:>13.6f}'
              f'  {",".join(g5.faults) or "none"}')
    print('\n   overlap > 0 == both ports open == compression collapses.')
    print('   The regulator treats compression < 0.5 as a REJECT, not a penalty.')

    # ── 7. A) WATCH ─────────────────────────────────────────────────────────
    print(f'\n{"=" * 78}\n7. A) WATCH — read-only, post-facto. The lamp.\n{"=" * 78}')
    w = Wankel(Trochoid(R=7.0, e=1.0), cam, PortTiming())
    for label, p in [('nominal', PortTiming()),
                     ('intake advanced', PortTiming(0.30, 0.0, 0.0)),
                     ('wide duration', PortTiming(0.0, 0.0, 0.26))]:
        w.ports = p
        s = w.watch(psi)
        print(f'   {label:<18} neutral_rms={s["neutral_rms"]:.6f} '
              f'peak={s["neutral_peak"]:.6f} comp={s["compression"]:.4f} '
              f'faults={s["faults"]}')

    # ── 8. B) REGULATE ──────────────────────────────────────────────────────
    print(f'\n{"=" * 78}\n8. B) REGULATE — close the loop on the ports\n{"=" * 78}')
    w.ports = PortTiming(0.30, -0.10, 0.05)          # start detuned
    before = w.watch(psi)
    print(f'   before: neutral_rms={before["neutral_rms"]:.9f} '
          f'comp={before["compression"]:.4f} '
          f'ch04={w.ports.intake_phase:+.5f} ch05={w.ports.exhaust_phase:+.5f} '
          f'ch06={w.ports.duration_trim:+.5f}')
    trace = w.regulate(psi, iters=40, steps=36)
    after = w.watch(psi)
    print(f'   after : neutral_rms={after["neutral_rms"]:.9f} '
          f'comp={after["compression"]:.4f} '
          f'ch04={w.ports.intake_phase:+.5f} ch05={w.ports.exhaust_phase:+.5f} '
          f'ch06={w.ports.duration_trim:+.5f}')
    print(f'   accepted moves: {len(trace) - 1}')
    if before['neutral_rms'] > 0:
        print(f'   reduction: {100 * (1 - after["neutral_rms"] / before["neutral_rms"]):.2f}%')
    print(f'   compression held >= 0.5 throughout: '
          f'{all(t["compression"] >= 0.5 for t in trace)}')

    print(f'\n{"=" * 78}')
    print('   ONE shaft. THREE faces at 120 deg. FIVE lobes each. e0 on the axis.')
    print('   The CAM is geometry -- rigidly geared, not a control input.')
    print('   The PORTS are the control input -- watch on 004/005, regulate on 04/05/06.')
    print('=' * 78)
