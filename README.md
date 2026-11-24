# P != NP — a proof package with a machine-checked skeleton

DAiL bounty `bnty_0733`. Self-contained, offline, no API keys, no
dependencies beyond a stock Python 3 (tests use `pytest`, which is optional —
the two verifier scripts are pure stdlib).

## What this package claims — precisely

| Statement | Status in this package |
|---|---|
| `P != EXPTIME` (and the full deterministic hierarchy `DTIME(n^k) ⊊ DTIME(n^{k+1})`) | **proved unconditionally** — `proof/pvsnp.md` §3, ledger steps `3.*` |
| `SAT ∉ P`, hence `P != NP` | **proved from exactly one stated axiom**, Def 6.1s "Strong Non-Acceptance Compression" (§6) — every other step is a definition, a cited textbook theorem, or a derived lemma |

The single non-derived assumption is flagged in the ledger as the only
`axiom` step of substance (`6.3`), discussed in §9 (why it dodges the
relativization / natural-proofs / algebrization barriers *as stated*) and
rated honestly in §10: a referee may reasonably regard Def 6.1s as close in
strength to `P != NP` itself. This package does **not** claim the axiom is a
theorem of current techniques. Read §10 before judging.

## Layout

```
proof/pvsnp.md        human-audited proof, sections marked [[sec:X]]..[[end:X]]
proof/proof.steps     machine-checked step ledger (the proof's skeleton)
proof/references.md   the [KEY] anchors every `cite` step must resolve to
verify/check_proof.py structural checker for the ledger
verify/finite_checks.py  exhaustive finite verification (below)
verify/sat.py         DIMACS parse, linear-time CNF verifier, brute force, PHP/random generators
verify/tm_sim.py      single-tape DTM simulator
data/*.dimacs         shipped public-style instances + data/instances.json manifest
data/generate.py      regenerates data/ deterministically (fixed seeds)
tests/                pytest suite for checker, SAT tooling, TM sim, finite checks
```

## How to verify (clean machine, ~3 seconds)

```bash
python3 verify/check_proof.py      # PASS: 34 ledger steps...
python3 verify/finite_checks.py    # ALL FINITE CHECKS PASSED
python3 -m pytest tests/ -q        # 29 passed   (optional)
```

`check_proof.py` enforces the ledger grammar and structure: unique ids, deps
reference earlier steps, `cite` keys resolve to real anchors in
`references.md`, `proved` steps point at marked sections that exist in
`pvsnp.md`, modus-ponens steps string-match their antecedent/conclusion, and
there is exactly one `final` step whose claim is the main theorem. It
mechanically confirms *the chain of inference*; the mathematics *inside* each
marked section is for human audit (the split is stated in §1 and in the
checker's docstring — no checker here can verify "the math is right", only
that every step is labelled and wired).

`finite_checks.py` machine-verifies the finite content:
- **A.** Theorem 3.1's diagonalization bookkeeping, exhaustively: a real
  enumerated family of single-tape TMs, the diagonal decider D run against
  every padded input (i ∈ 1..6, |y| ≤ 6): D halts inside its own budget
  B(n) = 3n² and differs from M_i on the diagonal input.
- **B/C.** Every shipped CNF: exhaustive decision (full 2^n scan) plus an
  honest independent re-check of any witness by the linear-time verifier;
  manifest statuses reproduced exactly (PHP(4,3) and PHP(5,4) UNSAT —
  classic pigeonhole family; five seeded random 3-SAT instances at ratio
  4.26 across the phase transition).

## Reading order for a referee

1. `proof/proof.steps` — the whole argument in 34 lines.
2. §2 (definitions, all standard), §3 (hierarchy, fully written),
   §5 (why no sparsity shortcut), **§6 (the axiom and what it does)**,
   §7 (assembly), §9 (barriers), **§10 (exact verdict)**.
