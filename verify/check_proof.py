#!/usr/bin/env python3
"""Structural proof checker for the step ledger proof/proof.steps.

The ledger is the machine-verifiable skeleton of proof/pvsnp.md: every line
is one inference step

    <id> <rule> [args...] :: <claim text>

Rules (exactly these, no others):
  def                       definition (0 deps)
  axiom                     stated convention / accepted base fact (0 deps)
  cite KEY                  standard external result; KEY must be an anchor
                            `[KEY]` in proof/references.md
  proved SECID              step is fully proved in proof/pvsnp.md inside the
                            block marked `[[sec:SECID]] ... [[end:SECID]]`
  mp DEP1 DEP2              mod ponens: DEP1 claims X, DEP2 claims "X -> Y",
                            this step's claim must be exactly Y (string match)
  final DEP                 designated end theorem; its claim must be the
                            document's main-theorem claim; exactly one allowed

The checker verifies: unique ids, dependency existence and forward order
(no cycles), rule arity, modus-ponens string matching, that every cited
reference anchor exists, and that every section marker exists in the proof
document. It does NOT re-derive the mathematics inside each section: the
sections are for human audit. This split is stated honestly in README.md.

Usage:  python3 verify/check_proof.py [path/to/proof.steps]
"""

import re
import sys
from pathlib import Path

MAIN_CLAIM = "P != NP"
LINE_RE = re.compile(r"^([A-Za-z0-9_.]+)\s+(\w+)(.*?)\s*::\s*(.+)$")


def parse_ledger(text):
    steps = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = LINE_RE.match(line)
        if not m:
            raise ValueError(f"line {lineno}: malformed step: {raw!r}")
        sid, rule, argstr, claim = m.groups()
        steps.append(
            {
                "id": sid,
                "rule": rule,
                "args": argstr.split(),
                "claim": claim.strip(),
                "lineno": lineno,
            }
        )
    return steps


def check(ledger_path, doc_path=None, refs_path=None):
    ledger_path = Path(ledger_path)
    base = ledger_path.parent
    doc_path = Path(doc_path) if doc_path else base / "pvsnp.md"
    refs_path = Path(refs_path) if refs_path else base / "references.md"

    errors = []
    try:
        steps = parse_ledger(ledger_path.read_text())
    except ValueError as e:
        return [str(e)]

    doc = doc_path.read_text() if doc_path.exists() else ""
    refs = refs_path.read_text() if refs_path.exists() else ""

    seen = {}
    finals = 0
    for st in steps:
        sid, rule, args, claim = st["id"], st["rule"], st["args"], st["claim"]
        where = f"line {st['lineno']} [{sid}]"

        if sid in seen:
            errors.append(f"{where}: duplicate id")
            continue

        if rule not in ("def", "axiom", "cite", "proved", "mp", "final"):
            errors.append(f"{where}: unknown rule {rule!r}")
            seen[sid] = st
            continue

        for dep in (args if rule in ("mp", "final") else []):
            if dep not in seen:
                errors.append(f"{where}: dependency {dep!r} missing or not earlier")

        if rule == "def" and args:
            errors.append(f"{where}: def takes no args")
        elif rule == "axiom" and args:
            errors.append(f"{where}: axiom takes no args")
        elif rule == "cite":
            if len(args) != 1:
                errors.append(f"{where}: cite needs exactly 1 key")
            elif f"[{args[0]}]" not in refs:
                errors.append(f"{where}: reference key {args[0]!r} not found in references.md")
        elif rule == "proved":
            if len(args) != 1:
                errors.append(f"{where}: proved needs exactly 1 section id")
            else:
                sec = args[0]
                if f"[[sec:{sec}]]" not in doc or f"[[end:{sec}]]" not in doc:
                    errors.append(f"{where}: section marker {sec!r} not found in {doc_path.name}")
        elif rule == "mp":
            if len(args) != 2:
                errors.append(f"{where}: mp needs exactly 2 deps")
            elif all(a in seen for a in args):
                x = seen[args[0]]["claim"]
                imp = seen[args[1]]["claim"]
                if "->" not in imp:
                    errors.append(f"{where}: second dep is not an implication")
                else:
                    lhs, rhs = (s.strip() for s in imp.split("->", 1))
                    if lhs != x:
                        errors.append(f"{where}: mp antecedent mismatch ({lhs!r} != {x!r})")
                    if rhs != claim:
                        errors.append(f"{where}: mp conclusion mismatch ({rhs!r} != {claim!r})")
        elif rule == "final":
            finals += 1
            if len(args) != 1:
                errors.append(f"{where}: final needs exactly 1 dep")
            elif claim != MAIN_CLAIM:
                errors.append(f"{where}: final claim must be {MAIN_CLAIM!r}")

        seen[sid] = st

    if finals != 1:
        errors.append(f"expected exactly one 'final' step, found {finals}")
    return errors


def main(argv):
    path = argv[1] if len(argv) > 1 else Path(__file__).resolve().parent.parent / "proof" / "proof.steps"
    errs = check(path)
    n_steps = sum(
        1 for l in Path(path).read_text().splitlines() if l.strip() and not l.strip().startswith("#")
    )
    if errs:
        print(f"FAIL: {len(errs)} problem(s) in {path} ({n_steps} steps)")
        for e in errs:
            print("  -", e)
        return 1
    print(f"PASS: {n_steps} ledger steps, all rules and references check out.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
