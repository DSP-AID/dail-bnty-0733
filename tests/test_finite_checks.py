"""End-to-end: the finite checks run clean on the shipped data (fast mode)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verify"))
import finite_checks  # noqa: E402


def test_finite_checks_fast(capsys):
    assert finite_checks.main(fast=True) == 0
    out = capsys.readouterr().out
    assert "ALL FINITE CHECKS PASSED" in out
