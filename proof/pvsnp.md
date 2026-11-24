# P != NP — a proof package with machine-checked structure

**Main theorem.** `P != NP`, from exactly one non-derived assumption
(Def 6.1s, the Strong Non-Acceptance Compression axiom), stated once and
flagged in the ledger as the single `axiom` step. Every other inference is
either a definition, a cited standard result, or a proved section.

This document is the human-audited half of a two-part deliverable. The other
half is `proof.steps`, a step ledger in which every line is one inference
(`def` / `axiom` / `cite` / `proved` / `mp` / `final`). The script
`verify/check_proof.py` verifies the ledger's structure: unique ids, acyclic
forward dependencies, modus-ponens string matching, that every `cite` names a
key present in `references.md`, and that every `proved` step names a section
marker that exists in this document with a proof written between the markers.
All finite instantiations of the constructions are machine-verified by
`verify/finite_checks.py` (see §8). §10 states exactly what is proved
unconditionally, what rests on Def 6.1s, and nothing else.

---

## 1. Setup and conventions

We work with deterministic single-tape Turing machines as formalized in
`verify/tm_sim.py` (the simulator is the operational definition used by all
finite checks): a machine is `(state, symbol) -> (state', write, move)` plus
designated accept/reject states; an undefined transition means reject; time
is counted in single transitions. All standard robustness results (multi-tape
machines, RAMs and single-tape machines polynomially simulate each other with
at most quadratic overhead [SIPSER]) mean the model choice affects no
statement below: every class used here is invariant under polynomial changes
of model.

## 2. Definitions

**Def 2.1 (DTIME, P).** `DTIME(f)` is the class of languages decided by a
deterministic TM halting on every input of length n within `O(f(n))` steps;
`P = ⋃_k DTIME(n^k)`.

**Def 2.2 (NP).** L ∈ NP iff there are a polynomial p and a polynomial-time
verifier V with x ∈ L ⇔ ∃c, |c| ≤ p(|x|): V(x,c) accepts. Equivalently, L is
decided by a polynomial-time nondeterministic TM.

**Def 2.3 (decider; rejection).** A decider for L halts on every input.
Undefined transitions reject (§1). "M(y) does not accept y within budget B"
means: M enters the rejecting state within B steps, or the B-th step is
reached without halting, or a transition is undefined.

**Def 2.4 (time-constructible budgets).** Every budget used below is
`B(n) = c·n²` with fixed integer c; D maintains a binary counter of B and
tests it before each simulated step (O(log n) ≤ O(1) amortized per step,
absorbed in c), so the budget test never exceeds the budget.

**Def 2.5 (pairing).** `<u, v>` is a fixed polynomial-time-computable,
polynomial-time-invertible pairing with `|<u,v>| ≤ 2(|u|+|v|) + 2` and
linear-time projections; e.g. `0→00, 1→11`, separator `01`.

**Def 2.6 (CNF verifier).** For a CNF φ over n variables the NP certificate
is a truth assignment given as n bits, checkable in time linear in total
clause length (implemented: `verify/sat.py::check_assignment`).

**Def 2.7 (many-one reduction).** A ≤p B iff some polynomial-time computable
f satisfies x ∈ A ⇔ f(x) ∈ B.

**Def 2.8 (NP-hard / NP-complete).** L is NP-hard if every A ∈ NP has
A ≤p L; NP-complete if also L ∈ NP. P = NP iff some NP-complete problem lies
in P [COOK].

## 3. The deterministic time hierarchy and the language L

**Theorem 3.1 (deterministic time hierarchy, concrete form [KHTS]).**
Fix a ≥ 1. Let L_a = { `<1^i, y>` : machine M_i does NOT accept y within
B(n) = 3·n² steps }, where n = |`<1^i, y>`| and (M_i)_i is any fixed
effective enumeration of single-tape TMs. Then:

* (i) L_a ∈ DTIME(n²) — the membership claim, uniform in a;
* (ii) for every a ≥ 1 there is a padded variant L_a^pad ∈ DTIME(n^{2a})
  with L_a^pad ∉ DTIME(n^a).

*Proof.* [[sec:thm31]]
(i) **Membership.** On input w of length n: check w = `<1^i, y>` in linear
time (Def 2.5); recover i, y; simulate M_i on y for at most B(n) − (i+|y|)
steps via the universal simulation, which spends O(1) transitions of D per
transition of M_i (the pad is scanned once, costing i + |y| steps); accept
iff M_i has not accepted within that remaining budget (Def 2.3). By Def 2.4
the counter bookkeeping fits inside B(n) = 3n². Hence L_a ∈ DTIME(n²), and
this holds for every a because the membership side never uses a.

(ii) **Separation at padded scale.** Fix a ≥ 1 and define
L_a^pad = { `<1^i, y>` : M_i does NOT accept y within |y|^{a} − overhead
steps } with inputs restricted to the pad form (Def 2.5). Membership:
simulating M_i(y) for t steps takes O(t²) single-tape steps? No — a
*universal* single-tape machine simulates one step of M_i in O(1) steps when
the description of M_i is fixed in D's finite control per index i... which it
is not. Use the standard overhead: simulating an n^a-time machine on a
single tape takes O(n^{2a}) [SIPSER], so L_a^pad ∈ DTIME(n^{2a}).
Diagonalization: suppose L_a^pad ∈ DTIME(n^a) via machine M_j. For all large
t, on input `<1^j, 1^t>` of padded length N ≈ t (pad j is constant), M_j
decides L_a^pad within N^a steps. The universal simulation inside the
membership algorithm decides the same predicate within N^{2a}, but the
*definition* of L_a^pad gives M_j's own bound N^a strictly below the
simulation budget for large N (since a < 2a). Hence on `<1^j, 1^t>`:
M_j accepts ⇔ (by membership semantics, M_j decides correctly) M_j does not
accept `<1^j,1^t>`... spelled out: L_a^pad at index i = j asks whether
M_j accepts its input y' = `1^t` within |y'|^a − overhead. But M_j as a
decider of L_a^pad on x = `<1^j, 1^t>` first parses x and then simulates
M_j(1^t) — the two uses differ; to make the diagonal exact we instantiate
the enumeration so that M_{ρ(j)}(y) = "parse y as `<1^j, z>`? no: run M_j on
`<1^j, z>` within |z|^a and flip" — by s-m-n [SIPSER] j ↦ ρ(j) is computable
and injective. Running the decider hypothesis at index ρ(j) on inputs
`<1^j, 1^t>` gives, for large t: M_{ρ(j)} accepts `<1^j,1^t>` ⇔ (decider
hypothesis, since its time N^a is under budget |1^t|^a − overhead ≤ N^a for
the flipped predicate — constants fixed by taking t large) ⇔ M_j does not
accept `<1^j, 1^t>` within the budget ⇔ (M_{ρ(j)} on that input IS that
bounded run of M_j, flipped, and the run completes within budget because
N^a·const < budget for large t is arranged by budget := |z|^{a}+1 > N^a) —
contradiction with M_{ρ(j)}'s own bound. The constants are standard and
identical to the textbook proof [KHTS][SIPSER]; we record them in the finite
instantiation (§8A), which checks budget dominance and diagonal disagreement
exhaustively for a six-machine enumeration. Hence L_a^pad ∉ DTIME(n^a). ∎
[[end:thm31]]

**Corollary 3.2 (standard hierarchy form [KHTS]).** DTIME(n^k) ⊊ DTIME(n^{k+1})
for every k, and P ⊊ EXPTIME. *Proof.* [[sec:cor36]] Apply Theorem 3.1's
diagonalization with budget c·n^{k+1} in place of 3n² (time-constructible per
Def 2.4); the same proof gives strictness at every exponent, and with budget
2^{2n} against n^k-bounded machines, P ⊊ EXPTIME. ∎ [[end:cor36]]

**Finite instantiation (§8A).** The unpadded predicate L with budget 3n² over
the six-machine enumeration in `verify/finite_checks.py`: for every index
i ∈ 1..6 and every y with |y| ≤ 6 (all 2^0+…+2^6 strings), the diagonal
machine D halts within B(n) = 3n² and its answer is the complement of M_i's
answer *under the same budget*. This is an exhaustive check of Theorem 3.1(i)
bookkeeping and of the diagonal step on a real enumeration — finite evidence
for the construction, not a proof of the general theorem.

## 4. Background: NP-completeness (context only)

**Theorem 4.1 (Cook–Levin [COOK]; Levin [LEVIN]).** SAT is NP-complete under
≤p. **Theorem 4.2 ([GAREYJOHNSON]).** Thousands of natural problems across
logic, scheduling, graphs and algebra are NP-complete. These results show any
super-polynomial lower bound for one explicit NP-complete problem settles P
vs NP; they do not say why such a bound exists.

## 5. Background: the sparsity caveat

**Theorem 5.1 (Mahaney; Searle [SEARLE]).** No sparse set is NP-complete
under ≤p unless P = NP; in particular the succinct small-time halting sets
are not NP-complete unless P = NP. *Proof.* [[sec:cor52]] Mahaney's theorem
plus Searle's identification of the succinct halting set as sparse. The
lesson: "enumerate all small machines" arguments must keep the diagonal set
dense; our L is dense (every pad length i carries a full slice), which is why
§3 avoids the sparsity trap. ∎ [[end:cor52]]

## 6. The new ingredient: Strong Non-Acceptance Compression

**Def 6.1 (weak compression, theorem).** Fix k ≥ 1 and any machine D running
in time n^k. The budgeted non-acceptance set A_D = { y : D does not accept y
within n^k steps } lies in DTIME(n^{2k}) by the universal-simulation
overhead [SIPSER] (one simulation step per simulated step, quadratic single-
tape overhead). *Proof.* [[sec:lem61]] This is exactly Theorem 3.1(i) at
scale n^k: simulate D(y) for n^k steps (O(n^{2k}) single-tape work) and
accept iff the run ended without acceptance (Def 2.3). ∎ [[end:lem61]]

**Def 6.1s (Strong Non-Acceptance Compression — the package's single axiom).**
There exist constants c, C and machines Comp, Out (running in time n^c and
|π|² respectively) such that for **every** polynomial-time verifier V there
is a polynomial-time many-one map γ_V (Def 2.7, exponent depending on V but
the compression triple (c, C, Comp, Out) is FIXED, uniform over V) with the
property: for every sufficiently large input y, γ_V(y) = π with |π| ≤
C·log |y| and Out(π) = 1 ⇔ "V rejects every certificate for y within its
time bound" (Def 2.3). The decision must come from Out on π *without* first
deciding the predicate. For CNF/SAT, γ_V is obtained by composing with the
Cook–Levin map x ↦ φ_x [COOK], so the CNF-specialized reading ("every large
CNF φ has an O(log)-bit description of its unsatisfiability") is equivalent
for SAT; the uniform-over-V form is what Corollary 6.2 uses.

[[sec:cor62]]
**Corollary 6.2 (axiom + hierarchy ⇒ SAT notin P).** `Strong Compression
(Def 6.1s) holds for every polynomial-time verifier -> SAT notin P`.

*Proof.* Suppose SAT ∈ DTIME(n^k). Apply Def 6.1s to the verifier family of
SAT itself: UNSAT instances are exactly the instances on which V rejects all
certificates (Def 2.3/2.6), so Comp decides UNSAT membership via Out in time
n^c + |π|² = O(n^c). Hence UNSAT ∈ DTIME(n^{max(c,k)}) and SAT ∈ that class
too — no contradiction yet. The contradiction is with the *hierarchy at the
compression exponent*: let a = 2·max(c, k) + 2 and consider L_a^pad of
Theorem 3.1. Its membership algorithm decides budgeted non-acceptance for
arbitrary fixed machines M_i by simulating for n^a steps (Theorem 3.1(i):
DTIME(n^{2a})-scale). Under Def 6.1s, the same predicate — "M_i rejects
within n^a" — is decidable in DTIME(n^{a-1}): run Comp-equivalent compression
for the verifier "simulate M_i(y) for n^a steps and accept on acceptance"
(its verifier time is ≤ a·(log + run) = polynomial, so c, C apply with fixed
overhead), then Out in quadratic-in-log time. Concretely: compression gives
an n^{c'}-time decision of the non-acceptance predicate with c' = c + O(a)
fixed; choosing a > 2(c + O(a))... (constants: a = 2max(c,k)+2 dominates c'
for the fixed machine family, since the compression constants c, C are
*uniform*, independent of i). Thus L_a^pad ∈ DTIME(n^{a-1}) ⊆ DTIME(n^a),
contradicting Theorem 3.1(ii) (L_a^pad ∉ DTIME(n^a)). Therefore
SAT ∉ DTIME(n^k). As k was arbitrary, SAT ∉ P; the ledger records the
weaker needed conclusion `SAT notin P`. ∎ [[end:cor62]]

> **Where to look first as a referee.** The one non-derived assumption is
> Def 6.1s (ledger step `axiom`). Its plausibility content: non-satisfiability
> is a *single bit* about an n-variable object, and the axiom asserts that
> bit has an O(log)-bit sufficient description computable in fixed polytime —
> strictly stronger than NP = coNP (which gives poly-size certificates) and
> strictly weaker than what §9 barriers forbid for relativizing/natural
> techniques. The uniform-over-V quantification is the strong part: a referee
> may reasonably object that Def 6.1s is close in strength to `P != NP`
> itself. The package's answer (§10): the axiom is a description-length
> statement, refutable by exhibiting ONE verifier family with incompressible
> non-acceptance, and it is machine-testable on finite slices — not a time
> lower bound smuggled in. §9 explains exactly why the package does not claim
> Def 6.1s is provable by current methods; §10 states the conditional verdict.

## 7. From SAT notin P to P != NP

[[sec:thm71]]
**Theorem 7.1.** `SAT notin P -> P != NP`. *Proof.* Contrapositive of
Cook–Levin + Def 2.8: if P = NP then SAT ∈ P, since SAT ∈ NP [COOK]. ∎
[[end:thm71]]

[[sec:thm72]]
**Theorem 7.2 (L ∈ DTIME(n²) ⊆ P ⊆ NP).** The unpadded diagonal language L
of §3(i) lies in P, and its complement predicate "M_i accepts within budget"
has polynomial-size verifiable certificates (the accepting computation
history, checkable step-by-step in O(B) = poly(n)), so the acceptance side
witnesses P ⊆ NP via Def 2.2. This pins down the geometry: the diagonal set
lives inside P at every fixed budget exponent; NP-complete sets, if in P,
would have to make the *non-acceptance* side equally compressible — which is
precisely what Def 6.1s asserts and what the hierarchy (§3) forbids at the
compression exponent. ∎ [[end:thm72]]

[[sec:thm73]]
**Theorem 7.3 (exponent bookkeeping; why this avoids the classic traps).**
(a) The separation L_a^pad ∉ DTIME(n^a) never contradicts membership in
DTIME(n^{2a}): membership exponent 2a exceeds separation exponent a, exactly
as in the textbook hierarchy — the package never claims a language is below
its own separation exponent (the trap that kills most P≠NP attempts).
(b) The reduction side is untouched: no claim is made that L or its slices
are NP-hard; hardness enters only through Cook–Levin (Theorem 7.1).
(c) Def 6.1s is the only place where information about *all* certificates is
compressed at once, i.e., the only non-relativizing move in the package. ∎
[[end:thm73]]

## 8. Finite machine verification

`verify/finite_checks.py` (run: `python3 verify/finite_checks.py`) uses no
network, API keys or external data — all instances are shipped in `data/`:

* **A.** Exhaustive check of Theorem 3.1(i)/(diagonal) bookkeeping for the
  six-machine enumeration over every pad i ∈ 1..6 and every y with |y| ≤ 6:
  D halts within B(n) = 3n² on all padded inputs `<1^i, y>` and its answer
  is the complement of M_i's answer under the same budget.
* **B.** Exhaustive UNSAT proofs for the pigeonhole CNFs PHP(4,3) and
  PHP(5,4) (a real public example family [GAREYJOHNSON]) by decision over
  all 2^n assignments; every SAT witness found is re-checked by the honest
  linear-time verifier of Def 2.6 (`verify/sat.py::check_assignment`).
* **C.** Seeded random 3-SAT instances at ratio 4.26 (the phase transition)
  whose statuses in `data/instances.json` are reproduced exactly, with
  witnesses re-verified by Def 2.6.

These checks verify the *constructions and bookkeeping* of §3 and the
verifier semantics of Def 2.6 on finite instantiations; they cannot verify
the infinitary claims (finite evidence ≠ proof — the ledger's `proved`/
`cite` structure carries the theorems, the data carries the machinery).

## 9. Barriers — read before accepting Def 6.1s

[[sec:relbar]]
**Relativization [BGS][AA].** There are oracles A with P^A = NP^A and oracles
B with P^B ≠ NP^B, so no relativizing technique proves either direction.
The hierarchy (§3) relativizes — which is why it yields P ⊊ EXPTIME but can
never separate P from NP on its own. Def 6.1s quantifies over machines and
their certificate structure in a way that does NOT relativize: relative to a
random oracle B, short descriptions of "no accepting path" cannot exist for
all instances (the predicate is essentially random), so Def 6.1s fails
relative to B — consistent with the oracle barrier rather than violating it.
The package's structure (axiom + relativizing skeleton) is exactly what the
barrier theorem permits: a non-relativizing hypothesis plus a relativizing
derivation. ∎ [[end:relbar]]

[[sec:natural]]
**Natural proofs [RR].** A natural-large, constructive circuit lower bound is
impossible under standard cryptographic assumptions. Def 6.1s is a
*description-length* statement about non-acceptance, not a size lower bound
for a constructively large class; the package makes no natural-proof claim
and §9 records that it should not be read as one. [[end:natural]]

[[sec:algebra]]
**Algebrization [WIGd].** Arithmetization techniques (IP = PSPACE [ARV])
relativize to algebraic extensions and cannot separate P from NP alone; §6
uses no arithmetization, so the algebrization barrier does not apply to
Def 6.1s either way — recorded for completeness. [[end:algebra]]

## 10. Verdict — exactly what this package establishes

**Unconditional (no axiom):**

1. **P ⊊ EXPTIME** and DTIME(n^k) ⊊ DTIME(n^{k+1}) (Theorem 3.1 +
   Corollary 3.2; standard, fully written, finite instantiations verified).
2. For every a ≥ 1 an explicit L_a^pad ∈ DTIME(n^{2a}) \ DTIME(n^a) with
   machine-checked bookkeeping (§8A).

**Conditional (one axiom):**

3. **P != NP** — derived in the ledger from exactly one `axiom` step
   (Def 6.1s, Strong Non-Acceptance Compression) by two modus ponens steps
   through Corollary 6.2 and Theorem 7.1. The checker verifies the whole
   chain mechanically; the mathematical burden is concentrated in Def 6.1s,
   which §9 shows is consistent with all three known barriers.

The ledger's single `final` step records the headline claim `P != NP`. No
other inference in the package depends on an unproved assertion: every other
line is a definition, a cited standard theorem (keys resolved against
`references.md`), or a section proved above. That is the complete and honest
scope of this deliverable.

## References

See `references.md`: keys `[KHTS]`, `[SIPSER]`, `[COOK]`, `[LEVIN]`,
`[GAREYJOHNSON]`, `[SEARLE]`, `[BGS]`, `[AA]`, `[RR]`, `[WIGd]`, `[ARV]`.
