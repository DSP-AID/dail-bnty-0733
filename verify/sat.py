"""DIMACS CNF parsing, brute-force decision and NP certificate checking.

Real public example families used by finite_checks.py:
  * pigeonhole PHP(m+1, m) — classic unsatisfiable CNFs (proof §8 data)
  * seeded random 3-SAT near the phase transition (ratio ~4.26)
"""


def parse_dimacs(path):
    """Return (num_vars, clauses) with clauses as tuples of signed ints."""
    n = None
    clauses = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line[0] == "c":
                continue
            if line[0] == "p":
                _, _, nvars, _ = line.split()
                n = int(nvars)
            elif line[0].isdigit() or line[0] == "-":
                lits = [int(t) for t in line.split() if t != "0"]
                if lits:
                    clauses.append(tuple(lits))
    if n is None:
        raise ValueError(f"{path}: missing p-line")
    return n, clauses


def check_assignment(n, clauses, assignment):
    """Deterministic polynomial-time NP verifier (Def. 2.6 of proof doc).

    assignment: dict var(1..n) -> bool. Returns True iff every clause is
    satisfied. Runs in O(sum of clause lengths) = linear time.
    """
    for clause in clauses:
        if not any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause):
            return False
    return True


def compile_clauses(clauses):
    """(pos_mask, neg_mask) per clause for the fast exhaustive scan."""
    compiled = []
    for clause in clauses:
        pm = nm = 0
        for lit in clause:
            if lit > 0:
                pm |= 1 << (lit - 1)
            else:
                nm |= 1 << (-lit - 1)
        compiled.append((pm, nm))
    return compiled


def brute_force(n, clauses):
    """Exhaustive decision: returns None or a satisfying assignment dict.

    Fast path uses compiled bitmasks; any found witness is re-checked with the
    honest linear-time verifier check_assignment() before being returned.
    """
    full = (1 << n) - 1
    for mask in range(1 << n):
        for pm, nm in compile_clauses_cache(clauses):
            if not (mask & pm) and not (full ^ mask) & nm:
                break
        else:
            assign = {v: bool(mask & (1 << (v - 1))) for v in range(1, n + 1)}
            assert check_assignment(n, clauses, assign)
            return assign
    return None


_CACHE = {}


def compile_clauses_cache(clauses):
    key = hash(tuple(clauses))
    if key not in _CACHE:
        _CACHE[key] = compile_clauses(clauses)
    return _CACHE[key]


def write_dimacs(path, n, clauses, comment):
    with open(path, "w") as fh:
        fh.write(f"c {comment}\n")
        fh.write(f"p cnf {n} {len(clauses)}\n")
        for clause in clauses:
            fh.write(" ".join(str(l) for l in clause) + " 0\n")


def pigeonhole(pigeons, holes):
    """PHP(pigeons, holes) CNF. var x_{i,j} = pigeons[i] -> hole j."""
    def var(i, j):
        return (i - 1) * holes + j

    clauses = []
    for i in range(1, pigeons + 1):
        clauses.append(tuple(var(i, j) for j in range(1, holes + 1)))
    for j in range(1, holes + 1):
        for a in range(1, pigeons + 1):
            for b in range(a + 1, pigeons + 1):
                clauses.append((-var(a, j), -var(b, j)))
    return pigeons * holes, clauses


def random_3sat(n, m, seed):
    """Seeded uniform random 3-CNF (each clause: distinct vars, random signs)."""
    import random

    rng = random.Random(seed)
    clauses = []
    for _ in range(m):
        vs = rng.sample(range(1, n + 1), 3)
        clauses.append(tuple(v * rng.choice((1, -1)) for v in vs))
    return n, clauses
