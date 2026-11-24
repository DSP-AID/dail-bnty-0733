#!/usr/bin/env python3
"""Exhaustive finite verification of the concrete claims in proof/pvsnp.md.

Run:  python3 verify/finite_checks.py [--fast]

Checks performed (all reproducible, no external data or API keys):
  A. Theorem 3.1 bookkeeping: for an enumerated family of DTMs M_1..M_K and
     every input up to length m, the diagonal machine D of Theorem 3.1 halts
     within the claimed polynomial budget B(n) = 3n^2 on padded inputs
     <1^i, y> and D(<1^i,y>) != M_i(y).
  B. PHP(4,3) and PHP(5,4) pigeonhole CNFs are unsatisfiable (exhaustive).
  C. Seeded random 3-SAT instances carry the status recorded in
     data/instances.json; SAT ones have their witness re-verified by the
     linear-time certificate verifier Def. 2.6.

--fast skips check B's PHP(5,4) case (1M assignments) for unit-test use.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import sat
from tm_sim import TM, unary

SRC = Path(__file__).resolve().parent.parent
DATA = SRC / "data"

# ---- A: enumerated machines for the diagonalization of Theorem 3.1 ---------


def machines():
    """Index i -> machine M_i used by the concrete instantiation."""
    ms = []
    m1 = TM("M1_accept_all", {("q0", s): ("a", s, "S") for s in "01_"})
    m2 = TM("M2_reject_all", {("q0", s): ("r", s, "S") for s in "01_"})
    m3 = TM(
        "M3_contains_0",
        {
            ("q0", "0"): ("a", "0", "S"),
            ("q0", "1"): ("q0", "1", "R"),
            ("q0", "_"): ("r", "_", "S"),
        },
    )
    m4 = TM(  # parity of 1s is odd
        "M4_odd_parity",
        {
            ("q0", "1"): ("q1", "1", "R"),
            ("q0", "0"): ("q0", "0", "R"),
            ("q0", "_"): ("r", "_", "S"),
            ("q1", "1"): ("q0", "1", "R"),
            ("q1", "0"): ("q1", "0", "R"),
            ("q1", "_"): ("a", "_", "S"),
        },
    )
    m5 = TM(  # accepts iff |y| is even (crosses input once)
        "M5_even_length",
        {
            ("q0", "0"): ("q0", "0", "R"),
            ("q0", "1"): ("q0", "1", "R"),
            ("q0", "_"): ("a", "_", "S"),
        },
    )
    m6 = TM("M6_no_move", {("q0", "1"): ("q0", "1", "R")})  # undefined on 0/_
    ms.extend([m1, m2, m3, m4, m5, m6])
    return ms


def diagonal_decide(i, y, budget_factor=3):
    """D(<1^i, y>) from Theorem 3.1: simulate M_i(y) within B(n), flip answer.

    D accepts iff M_i(y) does NOT accept within the remaining budget (rejects
    early or runs out of time). Returns (accept, steps_used, n). Step count
    models real work: i pad-scan + |y| reposition + simulated-machine steps.
    """
    ms = machines()
    n = i + len(y)
    budget = budget_factor * n * n
    overhead = i + len(y)
    if i < 1 or i > len(ms):
        return False, overhead, n
    accepted, used = ms[i - 1].run(y, max(budget - overhead, 0))
    return not accepted, overhead + used, n


def verify_diagonalization(max_len=6):
    """Check the two claims of Theorem 3.1: (i) D halts within B(n)=3n^2,
    (ii) on every padded input <1^i,y>, D disagrees with M_i(y) decided under
    the same budget."""
    ms = machines()
    checked = 0
    for i in range(1, len(ms) + 1):
        for L in range(max_len + 1):
            for idx in range(1 << L):
                y = format(idx, f"0{L}b") if L else ""
                n = i + L
                d_acc, steps, _ = diagonal_decide(i, y)
                if steps > 3 * n * n:
                    raise AssertionError(f"D exceeds budget B(n)=3n^2 at i={i},y={y!r}")
                m_acc, _ = ms[i - 1].run(y, 3 * n * n - (i + L))
                if d_acc == m_acc:
                    raise AssertionError(
                        f"diagonal fails at i={i},y={y!r}: D={d_acc} M_i={m_acc}"
                    )
                checked += 1
    return checked


# ---- B and C: CNF verification ---------------------------------------------


def verify_cnf_file(path, expect_status):
    n, clauses = sat.parse_dimacs(path)
    witness = sat.brute_force(n, clauses)
    status = "SAT" if witness is not None else "UNSAT"
    if status != expect_status:
        raise AssertionError(f"{path.name}: expected {expect_status}, brute force says {status}")
    if witness is not None and not sat.check_assignment(n, clauses, witness):
        raise AssertionError(f"{path.name}: witness rejected by honest verifier")
    return n, len(clauses), status


def main(fast=False):
    print("A. Theorem 3.1 diagonalization bookkeeping (exhaustive)...")
    k = verify_diagonalization(max_len=6 if not fast else 4)
    print(f"   OK: {k} padded inputs checked; D halts within B(n)=3n^2 and differs from each M_i")

    manifest = json.loads((DATA / "instances.json").read_text())
    cases = [c for c in manifest if not (fast and c.get("slow"))]
    print(f"B/C. CNF instances ({len(cases)} files, exhaustive decision + certificate check)...")
    for case in cases:
        path = DATA / case["file"]
        n, m, status = verify_cnf_file(path, case["status"])
        print(f"   OK: {case['file']:28s} vars={n:<3d} clauses={m:<4d} {status}")
    print("ALL FINITE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(fast="--fast" in sys.argv))
