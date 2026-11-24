"""Minimal single-tape deterministic Turing machine simulator.

Used by finite_checks.py to exhaustively verify the step-budget bookkeeping
claims of Theorem 3.1 (Deterministic Time Hierarchy) in proof/pvsnp.md.
"""

REJECT = "r"
ACCEPT = "a"


class TM:
    """Single-tape DTM. transitions: (state, symbol) -> (new_state, write, move).

    move in {"L", "R", "S"}. Halting states are ACCEPT and REJECT.
    Tape is left-infinite (blank to the left of position 0); input is
    written on cells 0..len(input)-1, head starts at cell 0 in state "q0".
    """

    def __init__(self, name, transitions, alphabet="01"):
        self.name = name
        self.transitions = dict(transitions)
        self.alphabet = alphabet + "_"  # blank

    def run(self, input_str, step_budget):
        """Return (accepted: bool, steps_used: int).

        If the machine has not halted within step_budget steps the result is
        (False, step_budget) and the caller must treat it as 'did not accept
        within budget' (see Def. 2.4 of the proof document).
        """
        tape = list(input_str) + ["_"] * (len(input_str) + 4)
        head = 0
        state = "q0"
        steps = 0
        while state not in (ACCEPT, REJECT):
            if steps >= step_budget:
                return False, steps
            sym = tape[head] if 0 <= head < len(tape) else "_"
            try:
                ns, w, mv = self.transitions[(state, sym)]
            except KeyError:
                return False, steps  # undefined move => reject (Def. 2.3)
            if 0 <= head < len(tape):
                tape[head] = w
            steps += 1
            if mv == "L":
                head -= 1
            elif mv == "R":
                head += 1
            state = ns
        return state == ACCEPT, steps


def unary(i):
    """Unary pad of Theorem 3.1: 1^i."""
    return "1" * i
