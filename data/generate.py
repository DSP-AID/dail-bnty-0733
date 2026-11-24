#!/usr/bin/env python3
"""Regenerate data/*.dimacs and data/instances.json (deterministic, offline).

Run:  python3 data/generate.py
Statuses are decided by exhaustive search at generation time, so the shipped
manifest is exactly reproducible by verify/finite_checks.py on any machine.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "verify"))
import sat  # noqa: E402

HERE = Path(__file__).resolve().parent
RATIO = 4.26  # random 3-SAT phase transition


def main():
    manifest = []

    def emit(name, n, clauses, comment, slow=False):
        path = HERE / f"{name}.dimacs"
        sat.write_dimacs(path, n, clauses, comment)
        status = "SAT" if sat.brute_force(n, clauses) is not None else "UNSAT"
        manifest.append(
            {"file": f"{name}.dimacs", "status": status, "slow": slow,
             "vars": n, "clauses": len(clauses), "comment": comment}
        )
        print(f"  {name}.dimacs: n={n} m={len(clauses)} -> {status}")

    print("generating...")
    n, cl = sat.pigeonhole(4, 3)
    emit("php_4_3", n, cl, "PHP(4,3) pigeonhole CNF - classic UNSAT family [GAREYJOHNSON]")
    n, cl = sat.pigeonhole(5, 4)
    emit("php_5_4", n, cl, "PHP(5,4) pigeonhole CNF - classic UNSAT family [GAREYJOHNSON]", slow=True)

    for k, seed in enumerate([1, 2, 3, 7, 11]):
        n = 12 + k  # 12..16 variables at ratio 4.26
        m = round(RATIO * n)
        n, cl = sat.random_3sat(n, m, seed=seed)
        emit(f"rand3sat_r{n}", n, cl, f"random 3-SAT n={n} m={m} ratio={RATIO} seed={seed}")

    (HERE / "instances.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(manifest)} entries to instances.json")


if __name__ == "__main__":
    main()
