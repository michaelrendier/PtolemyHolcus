#!/usr/bin/env python3
"""generational_lineage_engine.py — the anatomy of σ in ∅_RB.

Canonical engine now lives in the house package as engines/e10_generational_lineage.py
(the e01–e09 contract: a run(verbose=True) that returns a dict). This shim keeps
the original path working and re-exports the public surface.

    from generational_lineage_engine import run, GenerationalLineageEngine, \
        sigma_self, sigma_rb, sigma_rb_independent
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engines.e10_generational_lineage import (   # noqa: E402,F401
    GenerationalLineageEngine,
    Relation,
    Status,
    cd_mul,
    main,
    run,
    sigma_rb,
    sigma_rb_independent,
    sigma_self,
)

if __name__ == '__main__':
    main()
