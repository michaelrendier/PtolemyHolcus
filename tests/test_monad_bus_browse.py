"""
Unit tests — monad_bus (governor + language-blind backend) and monad_browse,
plus the harness.search/browse routing. Smoke + unit scope: no network here
(fetch is monkeypatched); the network smoke lives in the scratchpad.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

import monad_bus
import monad_browse


# ── ResourceGovernor ─────────────────────────────────────────────────────

def test_ceiling_is_ram_plus_half_ram_swap():
    g = monad_bus.ResourceGovernor()
    mi = monad_bus._meminfo()
    assert g.CEILING == mi['MemTotal'] + min(mi['SwapTotal'], mi['MemTotal'] // 2)


def test_ceiling_swap_rule_caps_at_half_ram(monkeypatch):
    monkeypatch.setattr(monad_bus, '_meminfo', lambda: {
        'MemTotal': 8 * 1024 ** 3, 'MemAvailable': 4 * 1024 ** 3,
        'SwapTotal': 32 * 1024 ** 3, 'SwapFree': 32 * 1024 ** 3})
    g = monad_bus.ResourceGovernor()
    assert g.CEILING == 8 * 1024 ** 3 + 4 * 1024 ** 3      # swap credited at ½ RAM only


def test_admit_rejects_over_ceiling():
    g = monad_bus.ResourceGovernor(max_slots=8)
    assert not g.admit(monad_bus.Job('huge', ram_peak=g.CEILING + 1))
    assert g.admit(monad_bus.Job('ok', ram_peak=4096))


def test_admit_rejects_when_slots_full():
    g = monad_bus.ResourceGovernor(max_slots=1)
    with g.guard(monad_bus.Job('a', ram_peak=1)):
        assert not g.admit(monad_bus.Job('b', ram_peak=1))
        assert g.snapshot()['running'] == 1
    assert g.admit(monad_bus.Job('c', ram_peak=1))
    assert g.snapshot()['running'] == 0


def test_admit_rejects_over_bandwidth():
    g = monad_bus.ResourceGovernor(max_slots=8, bw_cap=1000.0)
    assert not g.admit(monad_bus.Job('fat', bw_cost=1001.0))
    assert g.admit(monad_bus.Job('thin', bw_cost=10.0))


def test_guard_frees_slot_on_exception():
    g = monad_bus.ResourceGovernor(max_slots=2)
    with pytest.raises(ValueError):
        with g.guard(monad_bus.Job('x', ram_peak=1)):
            raise ValueError('boom')
    assert g.snapshot()['running'] == 0


def test_headroom_ok_for_bare_monad():
    g = monad_bus.ResourceGovernor()
    assert g.headroom_ok(1024) is True
    assert g.headroom_ok(g.CEILING * 10) is False


# ── language-blind backend loader ────────────────────────────────────────

def test_load_monad_c_absent_is_null_not_raise(tmp_path):
    be, rpt = monad_bus.load_monad(
        'c', fifo=str(tmp_path / 'no.fifo'), sock=str(tmp_path / 'no.sock'),
        spool=str(tmp_path / 'spool'))
    assert rpt['chosen'] == 'null'
    assert be.alive() is False
    assert be.learn('warn not fault') == 0           # no-op, never raises


def test_load_monad_python_or_null(tmp_path):
    # In this repo the python monad imports heavy deps; either it loads or we
    # get Null — both are valid, neither raises.
    be, rpt = monad_bus.load_monad(
        'python', fifo=str(tmp_path / 'no.fifo'), sock=str(tmp_path / 'no.sock'),
        spool=str(tmp_path / 'spool'))
    assert rpt['chosen'] in ('python:RotaryBoxKiteMonad', 'null')
    assert isinstance(be.learn('the quick brown fox jumps over'), int)
    assert be.learn('') >= 0


def test_c_backend_alive_tracks_a_reader(tmp_path):
    fifo = tmp_path / 'live.fifo'
    os.mkfifo(fifo)
    be = monad_bus.CMonadBackend(str(fifo), str(tmp_path / 's'), str(tmp_path / 'sp'))
    # a FIFO with no reader is NOT a live daemon
    assert be.alive() is False
    rfd = os.open(str(fifo), os.O_RDONLY | os.O_NONBLOCK)
    try:
        assert be.alive() is True                    # reader present → daemon-like
        assert be.learn('alpha beta gamma delta') == 4
    finally:
        os.close(rfd)
    # no reader again → learn() falls through to the spool, still counts words
    assert be.learn('one two three') == 3
    assert (tmp_path / 'sp').read_text().startswith('web\n')


# ── monad_browse ─────────────────────────────────────────────────────────

def test_search_url_shapes():
    u = monad_browse.search_url('box kite algebra')
    assert u.startswith('https://') and 'box' in u and 'kite' in u
    assert monad_browse.search_url('x', 'wiki').startswith('https://en.wikipedia.org')


def test_strip_html_removes_tags_and_scripts():
    html = (b"<html><head><style>x{}</style></head><body><h1>Title</h1>"
            b"<p>Hello <a href='/x'>world</a> this is prose.</p>"
            b"<script>evil()</script></body></html>")
    prose = monad_browse.strip_html(html, 'text/html', 'http://t')
    assert 'Hello' in prose and 'world' in prose and 'prose' in prose
    assert '<' not in prose and 'evil()' not in prose and 'x{}' not in prose


def test_estimate_ram_blowup():
    assert monad_browse.estimate_ram(1_000_000, is_html=True) == 6_000_000
    assert monad_browse.estimate_ram(1_000_000, is_html=False) == 2_000_000
    assert monad_browse.estimate_ram(1) == 64 * 1024          # floor dominates


# ── harness.search / browse routing ──────────────────────────────────────

class _FakeFetched:
    status = 200
    url_final = 'http://x/'
    content_type = 'text/html'
    body = b"<p>hello dedup world from a fake page with several words</p>"
    nbytes = len(body)
    error = ''


def test_harness_browse_fetches_once_then_dedups(monkeypatch):
    import harness
    h = harness.Harness()
    calls = {'n': 0}

    def fake_fetch(url, **kw):
        calls['n'] += 1
        return _FakeFetched()

    monkeypatch.setattr('monad_browse.fetch', fake_fetch)
    r1 = h.browse('http://x/', ttl=100)
    r2 = h.browse('http://x/', ttl=100)
    assert calls['n'] == 1
    assert r2.data == 'deduped'
    assert r1.handled_by == 'harness.browse'


def test_harness_browse_dedup_expires(monkeypatch):
    import harness
    h = harness.Harness()
    calls = {'n': 0}
    monkeypatch.setattr('monad_browse.fetch',
                        lambda url, **kw: (calls.__setitem__('n', calls['n'] + 1)
                                           or _FakeFetched()))
    h.browse('http://y/', ttl=0.01)
    time.sleep(0.02)
    h.browse('http://y/', ttl=0.01)
    assert calls['n'] == 2


def test_harness_browse_http_error_is_faceresult_not_raise(monkeypatch):
    import harness
    h = harness.Harness()

    class Err:
        status = 503
        url_final = 'http://e/'
        content_type = ''
        body = b''
        nbytes = 0
        error = 'HTTP 503'

    monkeypatch.setattr('monad_browse.fetch', lambda url, **kw: Err())
    r = h.browse('http://e/')
    assert r.ok is False and '503' in str(r.error)


def test_harness_load_monad_reports(tmp_path, monkeypatch):
    import harness
    monkeypatch.setattr(harness, 'OBSERVE_FIFO', str(tmp_path / 'no.fifo'))
    monkeypatch.setattr(harness, 'PTOLEMY_SOCKET', str(tmp_path / 'no.sock'))
    monkeypatch.setattr(harness, 'OBSERVE_SPOOL', str(tmp_path / 'spool'))
    h = harness.Harness()
    rpt = h.load_monad('c')                       # daemon absent → null, no raise
    assert rpt['chosen'] == 'null' and rpt['alive'] is False
    assert h.backend is not None


def test_harness_governor_is_lazy_and_has_ceiling():
    import harness
    h = harness.Harness()
    assert h._governor is None
    g = h.governor
    assert g is not None and g.CEILING > 0
    assert h.governor is g                        # same instance on 2nd access
