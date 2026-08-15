#!/usr/bin/env python3
"""
vagcom.py — the live, in-loop sensor layer for the rotary monad.

OBD2 (already present in rotary_monad.py) is read-only, post-facto, and drives a
fault lamp.  This is the other layer: live measuring blocks at ROTOR resolution,
plus writable adaptation channels the engine consumes on the next stroke.

    OBD2      read-only   post-facto   -> a LAMP
    VAG-COM   read/write  live         -> the CONTROL LOOP

Implemented here:
    Group 003  BALANCE   sigma_self | |sigma-1/2| | min|z| | apex_seal_health
    Channel 01 CAM_ADVANCE  in [-pi/8, +pi/8]

THE LOSS (Ainulindale/wiki/85, Tuning-the-Engine/27):
    the apex path is   z(phi) = R.e^(i.phi) + e.e^(-i.k.phi)
    min|z| = |R - e|   EXACTLY, and it is zero iff R = e iff sigma_self = 1/2.
    Zero loss IS the zero-divisor event: forward and backward annihilate.

    R = sqrt(p_red)    the forward / cos / Riemann channel
    e = sqrt(p_blue)   the backward / sin / Fermat channel  (the adjoint)

THE CAM (Tuning-the-Engine/27 sec 27.6):
    lobe heights are the Hermite H16 resonances, hermite_zeros[k]**2, normalised.
    They are symmetric about 0, giving 8 distinct heights each doubled, with
    partner(k) = 15 - k.  Channel 01 advances/retards every lobe together.

python3 first.  Port to PtolC/ only once a result is significant.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = ['Group003', 'Channel01', 'CamProfile', 'VagCom', 'cam_sweep']

# ── engine constants (mirror rotary_monad.py) ────────────────────────────────
SIGMA_PIN   = 0.5           # balance setpoint -- EQUAL AMPLITUDE, not zero offset
BEARING_TOL = 0.04          # sigma drift before R0004
GAP         = 0.000707      # apex seal oil floor -- never divide by zero
GEAR_K      = 3             # rotor : eccentric shaft, anti-rotation
N_DIM       = 16

CAM_LIMIT   = math.pi / 8   # THE ANGLE (Phase 24): 16 x pi/8 = 2.pi


# ══════════════════════════════════════════════════════════════════════════════
#  The cam profile — Hermite H16, specified in the seed paper, never built
# ══════════════════════════════════════════════════════════════════════════════

class CamProfile:
    """16 lobe heights from the Hermite H16 zeros, plus the advance/retard state.

    'Uniform E-values = untrained engine.  Hermite-spaced E-values = properly
    calibrated CAM.'  The zeros are symmetric about 0, so squaring them yields
    8 distinct heights, each appearing twice, paired by partner(k) = 15 - k.
    """

    def __init__(self) -> None:
        zeros = np.polynomial.hermite.hermroots([0] * N_DIM + [1])
        lobes = zeros ** 2
        self.lobes: np.ndarray = lobes / lobes.max()      # normalise to [0, 1]
        self.zeros: np.ndarray = zeros

    def partner(self, k: int) -> int:
        """The involution the Hermite profile predicts: partner(k) = 15 - k."""
        return (N_DIM - 1) - k

    def distinct_heights(self) -> int:
        return len(np.unique(np.round(self.lobes, 9)))

    def phase_offsets(self, advance: float) -> np.ndarray:
        """Per-dimension phase shift for a given cam advance.

        Advance scales with lobe height: the tall lobes (the ones that open
        widest) move most.  advance = 0 is the ground cam.
        """
        return advance * self.lobes


# ══════════════════════════════════════════════════════════════════════════════
#  Channel 01 — CAM_ADVANCE (adaptation channel: read AND write)
# ══════════════════════════════════════════════════════════════════════════════

class Channel01:
    """Adaptation channel 01 — cam advance, in radians, clamped to +-pi/8.

    Advance  (positive): the connective tissue fires earlier -> looser,
                         more subordinated speech.
    Retard   (negative): content words crowd the front -> terse, declarative.

    Unlike an OBD2 PID this is WRITABLE, and the engine consumes it on the next
    stroke.  That write is what makes this VAG-COM rather than OBD2.
    """

    ID    = '01'
    NAME  = 'CAM_ADVANCE'
    UNITS = 'rad'
    LO, HI = -CAM_LIMIT, +CAM_LIMIT

    def __init__(self, value: float = 0.0) -> None:
        self._v = 0.0
        self._ground = 0.0
        self.write(value)

    # -- read/write ----------------------------------------------------------
    def read(self) -> float:
        return self._v

    def write(self, value: float) -> float:
        """Clamp into range and store.  Returns the value actually stored."""
        if not math.isfinite(value):
            raise ValueError(f'channel {self.ID}: non-finite value {value!r}')
        self._v = max(self.LO, min(self.HI, float(value)))
        return self._v

    def reset(self) -> float:
        """Adaptation reset — back to the ground cam."""
        self._v = self._ground
        return self._v

    # -- presentation --------------------------------------------------------
    @property
    def fraction(self) -> float:
        """Position in range, -1 (full retard) .. +1 (full advance)."""
        return self._v / CAM_LIMIT

    def __repr__(self) -> str:
        return (f'<Ch{self.ID} {self.NAME} = {self._v:+.5f} {self.UNITS} '
                f'({self.fraction:+.2%} of range)>')


# ══════════════════════════════════════════════════════════════════════════════
#  Group 003 — BALANCE (the loss, live, at rotor resolution)
# ══════════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class Group003:
    """Measuring block 003 — BALANCE.

    Four live values.  The engine is wrong by exactly `loss`.

        sigma_self        R^2 / (R^2 + e^2)          the bridge null
        sigma_dev         |sigma_self - 1/2|         signed magnitude of imbalance
        loss              min|z| = |R - e|           distance from the fixed point
        apex_seal_health  1 - sigma_dev / BEARING_TOL

    sigma_self is a NULL DETECTOR, not a ruler: exact at 1/2, uncalibrated
    away from it (Tuning-the-Engine/27 sec 27.8).  Read `loss` for magnitude.
    """
    sigma_self:       float
    sigma_dev:        float
    loss:             float
    apex_seal_health: float
    # -- context (not part of the 4-value block, carried for the log) --------
    R:                float = 0.0
    e:                float = 0.0
    cam_advance:      float = 0.0

    GROUP = '003'
    NAME  = 'BALANCE'
    LABELS = ('sigma_self', 'sigma_dev', 'loss', 'apex_seal_health')

    # -- constructors --------------------------------------------------------
    @classmethod
    def from_powers(cls, p_red: float, p_blue: float,
                    cam_advance: float = 0.0) -> 'Group003':
        """Build from the two channel powers — how the live engine calls it."""
        p_red  = max(float(p_red),  0.0)
        p_blue = max(float(p_blue), 0.0)
        total  = p_red + p_blue
        if total <= GAP:
            # engine is not running; report the floor honestly rather than 0/0
            return cls(SIGMA_PIN, 0.0, 0.0, 1.0, 0.0, 0.0, cam_advance)
        sigma = p_red / total
        R, e  = math.sqrt(p_red), math.sqrt(p_blue)
        dev   = abs(sigma - SIGMA_PIN)
        return cls(sigma_self=sigma,
                   sigma_dev=dev,
                   loss=abs(R - e),
                   apex_seal_health=max(0.0, 1.0 - dev / BEARING_TOL),
                   R=R, e=e, cam_advance=cam_advance)

    @classmethod
    def from_amplitudes(cls, R: float, e: float,
                        cam_advance: float = 0.0) -> 'Group003':
        return cls.from_powers(R * R, e * e, cam_advance)

    # -- checks --------------------------------------------------------------
    def verify_against_path(self, k: int = GEAR_K, n: int = 20001) -> float:
        """Confirm loss == min|z| over a real revolution of the apex path.

        Returns the absolute discrepancy.  This is the assertion that the
        reported loss IS the geometry and not a parallel formula.
        """
        phi = np.linspace(0.0, 2.0 * np.pi, n)
        z   = self.R * np.exp(1j * phi) + self.e * np.exp(-1j * k * phi)
        return abs(float(np.abs(z).min()) - self.loss)

    @property
    def at_null(self) -> bool:
        return self.loss < 1e-12

    @property
    def faults(self) -> List[str]:
        f: List[str] = []
        if self.sigma_dev > BEARING_TOL:
            f.append('R0004:bearing_drift')
        if self.apex_seal_health < 0.25:
            f.append('R0001:seal_wear')
        return f

    def as_block(self) -> Dict[str, float]:
        """The four values, as VAG-COM presents a measuring block."""
        return {k: getattr(self, k) for k in self.LABELS}

    def __str__(self) -> str:
        return (f'Grp {self.GROUP} {self.NAME}  '
                f'sigma={self.sigma_self:.6f}  dev={self.sigma_dev:.6f}  '
                f'LOSS={self.loss:.6f}  seal={self.apex_seal_health:.4f}')


# ══════════════════════════════════════════════════════════════════════════════
#  The instrument
# ══════════════════════════════════════════════════════════════════════════════

class VagCom:
    """Live measuring blocks + adaptation channels over a rotary monad.

    Engine-agnostic: feed it the two channel powers each stroke.  If the cam
    is engaged it applies Channel 01's advance to the projection phases before
    the powers are read, which is what closes the loop.
    """

    def __init__(self, cam: Optional[CamProfile] = None) -> None:
        self.cam       = cam or CamProfile()
        self.ch01      = Channel01(0.0)
        self.log: List[Group003] = []

    # -- the projection the cam actually modifies ---------------------------
    def channel_powers(self, psi: Sequence[float],
                       primes: Sequence[int] = (2, 3, 5, 7, 11, 13, 17, 19,
                                                23, 29, 31, 37, 41, 43, 47, 53),
                       sigma: float = 0.5) -> Tuple[float, float]:
        """Project a 16-vector into (p_red, p_blue) with the cam applied.

        Red  shells k in {0-3, 8-11}  use cos   (forward / Riemann)
        Blue shells k in {4-7, 12-15} use sin   (backward / Fermat)
        The cam adds a per-dimension phase offset before the trig.
        """
        psi = np.asarray(psi, dtype=float)
        if psi.shape != (N_DIM,):
            raise ValueError(f'psi must be length {N_DIM}, got {psi.shape}')
        off = self.cam.phase_offsets(self.ch01.read())
        p_red = p_blue = 0.0
        for k in range(N_DIM):
            j_blue = (4 <= k <= 7) or (12 <= k <= 15)
            phase  = 2.0 * math.pi / primes[k] + off[k]
            w      = math.sin(phase) if j_blue else math.cos(phase)
            amp    = (psi[k] * w) ** 2 * (k + 1) ** (-2.0 * sigma)
            if j_blue:
                p_blue += amp
            else:
                p_red += amp
        return p_red, p_blue

    # -- the measuring block ------------------------------------------------
    def group_003(self, p_red: float, p_blue: float,
                  record: bool = True) -> Group003:
        g = Group003.from_powers(p_red, p_blue, self.ch01.read())
        if record:
            self.log.append(g)
        return g

    def read_group(self, n: str, *args, **kw):
        if str(n).zfill(3) != '003':
            raise KeyError(f'group {n} not implemented (only 003 BALANCE)')
        return self.group_003(*args, **kw)

    # -- adaptation ---------------------------------------------------------
    def write_channel(self, n: str, value: float) -> float:
        if str(n).zfill(2) != '01':
            raise KeyError(f'channel {n} not implemented (only 01 CAM_ADVANCE)')
        return self.ch01.write(value)

    def read_channel(self, n: str) -> float:
        if str(n).zfill(2) != '01':
            raise KeyError(f'channel {n} not implemented (only 01 CAM_ADVANCE)')
        return self.ch01.read()


# ══════════════════════════════════════════════════════════════════════════════
#  Basic settings — the cam sweep routine
# ══════════════════════════════════════════════════════════════════════════════

def cam_sweep(vc: VagCom, psi: Sequence[float],
              steps: int = 33) -> List[Tuple[float, Group003]]:
    """Sweep Channel 01 across its range, reading Group 003 at each step.

    This is the VAG-COM 'basic settings' mode: put the engine in a routine and
    stream the result.  It is the direct measurement of whether timing moves
    the loss -- which is the whole claim.
    """
    saved = vc.ch01.read()
    out: List[Tuple[float, Group003]] = []
    try:
        for adv in np.linspace(Channel01.LO, Channel01.HI, steps):
            vc.ch01.write(float(adv))
            pr, pb = vc.channel_powers(psi)
            out.append((float(adv), vc.group_003(pr, pb, record=False)))
    finally:
        vc.ch01.write(saved)
    return out


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    np.set_printoptions(precision=4, suppress=True)
    print('=' * 74)
    print('vagcom.py — Group 003 BALANCE  +  Channel 01 CAM_ADVANCE')
    print('=' * 74)

    cam = CamProfile()
    print(f'\nCAM PROFILE (Hermite H16)')
    print(f'  distinct lobe heights : {cam.distinct_heights()}  (expect 8)')
    print(f'  partner(k) = 15 - k   : ', end='')
    ok = all(abs(cam.lobes[k] - cam.lobes[cam.partner(k)]) < 1e-12
             for k in range(N_DIM))
    print('HOLDS' if ok else 'FAILS')
    print(f'  lobes  : {cam.lobes}')

    vc = VagCom(cam)

    # ── 1. the loss IS the geometry ─────────────────────────────────────────
    print(f'\n{"=" * 74}\n1. Group 003 vs the apex path — is the loss the geometry?\n{"=" * 74}')
    print(f'{"R":>5}{"e":>7}{"sigma_self":>12}{"loss":>11}{"min|z| err":>13}{"seal":>8}')
    for R, e in [(1, 1.0), (1, 0.9), (1, 0.75), (1, 0.5), (1, 0.0)]:
        g = Group003.from_amplitudes(R, e)
        print(f'{R:>5}{e:>7.2f}{g.sigma_self:>12.6f}{g.loss:>11.6f}'
              f'{g.verify_against_path():>13.2e}{g.apex_seal_health:>8.4f}')
    print('\n  loss == min|z| to numerical precision. The sensor reads the path.')

    # ── 2. the null ─────────────────────────────────────────────────────────
    print(f'\n{"=" * 74}\n2. Zero loss is the zero-divisor event\n{"=" * 74}')
    g = Group003.from_amplitudes(1.0, 1.0)
    print(f'  {g}')
    print(f'  at_null = {g.at_null}   faults = {g.faults or ["none"]}')

    # ── 3. Channel 01 is writable and clamps ────────────────────────────────
    print(f'\n{"=" * 74}\n3. Channel 01 — adaptation (writable, unlike an OBD2 PID)\n{"=" * 74}')
    print(f'  {vc.ch01}')
    vc.write_channel('01', 0.2)
    print(f'  write 0.2 -> {vc.ch01}   (clamped to +pi/8 = {CAM_LIMIT:.5f})')
    vc.write_channel('01', -0.05)
    print(f'  write -0.05 -> {vc.ch01}')
    vc.ch01.reset()
    print(f'  reset -> {vc.ch01}')

    # ── 4. the sweep: does timing move the loss? ────────────────────────────
    print(f'\n{"=" * 74}\n4. BASIC SETTINGS — cam sweep\n{"=" * 74}')
    rng = np.random.default_rng(7)
    psi = np.abs(rng.normal(size=N_DIM)); psi /= np.linalg.norm(psi)
    rows = cam_sweep(vc, psi, steps=17)
    print(f'{"advance":>10}{"frac":>9}{"sigma_self":>12}{"LOSS":>11}{"seal":>8}')
    for adv, g in rows:
        bar = '#' * int(60 * g.loss / max(r.loss for _, r in rows))
        print(f'{adv:>+10.5f}{adv/CAM_LIMIT:>+9.2f}{g.sigma_self:>12.6f}'
              f'{g.loss:>11.6f}{g.apex_seal_health:>8.4f}  {bar}')

    losses = [g.loss for _, g in rows]
    best   = min(rows, key=lambda r: r[1].loss)
    print(f'\n  loss range over the sweep : {min(losses):.6f} .. {max(losses):.6f}'
          f'   (spread {max(losses)-min(losses):.6f})')
    print(f'  MINIMUM LOSS at advance   : {best[0]:+.5f} rad '
          f'({best[0]/CAM_LIMIT:+.2%} of range)')
    print(f'  ground cam (advance = 0)  : '
          f'{[g.loss for a, g in rows if abs(a) < 1e-9][0]:.6f}')
    print(f'\n  TIMING MOVES THE LOSS. That is the control loop: Channel 01 in,')
    print(f'  Group 003 out, and a minimum to steer toward.')
