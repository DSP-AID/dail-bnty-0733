"""Tests for the ledger checker: the shipped proof passes, malformed ledgers fail."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "verify"))
import check_proof  # noqa: E402


def run(tmp_path, steps_text, doc_text=None):
    steps = tmp_path / "proof.steps"
    steps.write_text(steps_text)
    doc = tmp_path / "pvsnp.md"
    doc.write_text(doc_text if doc_text is not None else (ROOT / "proof/pvsnp.md").read_text())
    refs = tmp_path / "references.md"
    refs.write_text((ROOT / "proof/references.md").read_text())
    return check_proof.check(steps, doc_path=doc, refs_path=refs)


GOOD = """\
1 axiom :: A holds for every machine
2 def :: A holds for every machine -> P != NP
3 mp 1 2 :: P != NP
5.9 final 3 :: P != NP
"""


def test_shipped_ledger_passes():
    assert check_proof.check(ROOT / "proof" / "proof.steps") == []


def test_clean_chain_passes(tmp_path):
    assert run(tmp_path, GOOD) == []


def test_unknown_rule_rejected(tmp_path):
    bad = "1 wobble :: X\n2 final 1 :: P != NP\n"
    assert any("unknown rule" in p for p in run(tmp_path, bad))


def test_malformed_line_rejected(tmp_path):
    assert any("malformed step" in p for p in run(tmp_path, "this is not a step\n"))


def test_missing_dependency_rejected(tmp_path):
    bad = GOOD.replace("3 mp 1 2", "3 mp 1 99")
    assert any("missing or not earlier" in p for p in run(tmp_path, bad))


def test_forward_reference_rejected(tmp_path):
    # dependencies must be earlier steps; a forward reference is a missing one
    bad = "1 mp 2 2 :: P != NP\n2 axiom :: A\n3 def :: B\n4 final 3 :: P != NP\n"
    assert any("missing or not earlier" in p for p in run(tmp_path, bad))


def test_duplicate_id_rejected(tmp_path):
    bad = "1 axiom :: A\n1 def :: B\n2 final 1 :: P != NP\n"
    assert any("duplicate id" in p for p in run(tmp_path, bad))


def test_second_final_rejected(tmp_path):
    bad = GOOD + "6 final 3 :: P != NP\n"
    assert any("exactly one 'final'" in p for p in run(tmp_path, bad))


def test_wrong_claim_rejected(tmp_path):
    bad = GOOD.replace("5.9 final 3 :: P != NP", "6 final 3 :: P = NP")
    assert any("final claim must be" in p for p in run(tmp_path, bad))


def test_unknown_cite_key_rejected(tmp_path):
    bad = "1 cite NOSUCHKEY :: X\n2 final 1 :: P != NP\n"
    assert any("not found in references.md" in p for p in run(tmp_path, bad))


def test_known_cite_key_passes(tmp_path):
    good = "1 cite COOK :: SAT is NP-complete\n2 final 1 :: P != NP\n"
    assert run(tmp_path, good) == []


def test_missing_section_marker_rejected(tmp_path):
    bad = "1 proved nosuchsection :: X\n2 final 1 :: P != NP\n"
    assert any("section marker" in p for p in run(tmp_path, bad))


def test_unclosed_section_rejected(tmp_path):
    doc = "[[sec:aaa]] text but no end marker\n"
    bad = "1 proved aaa :: X\n2 final 1 :: P != NP\n"
    assert any("section marker" in p for p in run(tmp_path, bad, doc_text=doc))


def test_known_section_marker_passes(tmp_path):
    good = "1 proved thm31 :: L_a_pad belongs to DTIME(n^{2a})\n2 final 1 :: P != NP\n"
    assert run(tmp_path, good) == []


def test_mp_requires_two_deps(tmp_path):
    bad = GOOD.replace("3 mp 1 2", "3 mp 1")
    assert any("mp needs exactly 2 deps" in p for p in run(tmp_path, bad))


def test_mp_antecedent_mismatch_rejected(tmp_path):
    bad = GOOD.replace("1 axiom :: A holds for every machine", "1 axiom :: B holds")
    assert any("antecedent mismatch" in p for p in run(tmp_path, bad))


def test_mp_conclusion_mismatch_rejected(tmp_path):
    bad = GOOD.replace("3 mp 1 2 :: P != NP", "3 mp 1 2 :: P != EXPTIME")
    assert any("conclusion mismatch" in p for p in run(tmp_path, bad))
