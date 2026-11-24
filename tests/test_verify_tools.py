"""Tests for the CNF tooling and the TM simulator used by finite_checks.py."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verify"))
import sat  # noqa: E402
import tm_sim  # noqa: E402


# --- SAT --------------------------------------------------------------------


def test_parse_write_roundtrip(tmp_path):
    n, clauses = sat.pigeonhole(3, 2)
    path = tmp_path / "x.dimacs"
    sat.write_dimacs(path, n, clauses, "roundtrip")
    n2, clauses2 = sat.parse_dimacs(str(path))
    assert n2 == n
    assert set(clauses2) == set(clauses)


def test_parse_real_data_file():
    n, clauses = sat.parse_dimacs(str(ROOT / "data" / "php_4_3.dimacs"))
    assert n == 12
    assert len(clauses) == 22


def test_php_known_statuses():
    for p, h in [(2, 1), (3, 2), (4, 3)]:
        n, clauses = sat.pigeonhole(p, h)
        assert sat.brute_force(n, clauses) is None, f"PHP({p},{h}) must be UNSAT"
    n, clauses = sat.pigeonhole(2, 2)
    assert sat.brute_force(n, clauses) is not None


def test_verifier_agrees_with_brute_force():
    for seed in range(6):
        n, clauses = sat.random_3sat(10, 42, seed=seed)
        model = sat.brute_force(n, clauses)
        if model is None:
            continue
        assert sat.check_assignment(n, clauses, model), f"seed {seed}: bad model"


def test_check_assignment_rejects_garbage():
    n, clauses = sat.pigeonhole(2, 1)
    assert not sat.check_assignment(n, clauses, {v: False for v in range(1, n + 1)})


def test_random_3sat_shape():
    n, clauses = sat.random_3sat(15, 64, seed=3)
    assert n == 15 and len(clauses) == 64
    for cl in clauses:
        assert len(cl) == 3
        assert all(abs(lit) <= n and lit != 0 for lit in cl)


def test_manifest_statuses_reproducible():
    import json

    manifest = json.loads((ROOT / "data" / "instances.json").read_text())
    assert manifest, "manifest must not be empty"
    for case in manifest:
        path = ROOT / "data" / case["file"]
        n, clauses = sat.parse_dimacs(str(path))
        status = "SAT" if sat.brute_force(n, clauses) is not None else "UNSAT"
        assert status == case["status"], case["file"]


# --- TM simulator -------------------------------------------------------------

# accepts exactly the unary strings 1^(3k): move right counting mod 3
TM_MOD3 = tm_sim.TM(
    "mod3",
    {
        ("q0", "1"): ("q1", "1", "R"),
        ("q1", "1"): ("q2", "1", "R"),
        ("q2", "1"): ("q0", "1", "R"),
        ("q0", "_"): (tm_sim.ACCEPT, "_", "S"),
        ("q1", "_"): (tm_sim.REJECT, "_", "S"),
        ("q2", "_"): (tm_sim.REJECT, "_", "S"),
    },
)


def test_tm_accepts_rejects():
    assert TM_MOD3.run("111", 100)[0] is True
    assert TM_MOD3.run("11", 100)[0] is False
    assert TM_MOD3.run("", 100)[0] is True


def test_tm_budget_exceeded_is_non_acceptance():
    accepted, steps = TM_MOD3.run("1" * 30, 5)
    assert accepted is False and steps == 5


def test_tm_undefined_move_rejects():
    stalled = tm_sim.TM("stall", {("q0", "0"): ("q0", "0", "R")})
    assert stalled.run("001", 50) == (False, 2)


def test_unary_pad():
    assert tm_sim.unary(4) == "1111"
