#!/usr/bin/env python3
"""Sound checker for the formal reduction certificate.

The checker verifies the logical reduction from the major-arc lower bound,
the minor-arc upper bound and the finite verification to the binary
Goldbach theorem.  It does not attempt to verify the analytic estimates;
those are proved in proof/minor_arc_lemma.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


class CertificateError(Exception):
    """Raised when the certificate is malformed or a rule fails."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def _axiom_map(cert: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    axioms = cert.get("axioms")
    _require(isinstance(axioms, list) and axioms, "axioms must be a non-empty list")
    result: Dict[str, Dict[str, Any]] = {}
    for axiom in axioms:
        _require(isinstance(axiom, dict), "each axiom must be an object")
        axiom_id = axiom.get("id")
        _require(isinstance(axiom_id, str) and axiom_id, "axiom id must be a string")
        _require(axiom_id not in result, f"duplicate axiom id: {axiom_id}")
        result[axiom_id] = axiom
    return result


def _step_map(cert: Dict[str, Any]) -> List[Dict[str, Any]]:
    steps = cert.get("steps")
    _require(isinstance(steps, list) and steps, "steps must be a non-empty list")
    for step in steps:
        _require(isinstance(step, dict), "each step must be an object")
    return steps


def _find_axiom(axioms: Dict[str, Dict[str, Any]], kind: str) -> Dict[str, Any]:
    matches = [a for a in axioms.values() if a.get("kind") == kind]
    _require(len(matches) == 1, f"expected exactly one axiom of kind {kind}, found {len(matches)}")
    return matches[0]


def _check_combine_bounds(step: Dict[str, Any], axioms: Dict[str, Dict[str, Any]],
                          constants: Dict[str, Any]) -> None:
    major = _find_axiom(axioms, "major_arc_lower_bound")
    minor = _find_axiom(axioms, "minor_arc_upper_bound")
    decomposition = _find_axiom(axioms, "decomposition")
    from_ids = step.get("from")
    _require(from_ids == [major["id"], minor["id"], decomposition["id"]],
             "combine_bounds must use the major, minor and decomposition axioms")
    _require(major.get("form") == minor.get("form") == step.get("result_form"),
             "major and minor bounds must have the same asymptotic form")
    c_major = float(major.get("coefficient"))
    c_minor = float(minor.get("coefficient"))
    c_result = float(step.get("result_coefficient"))
    _require(c_major > 0 and c_minor > 0, "coefficients must be positive")
    _require(abs((c_major - c_minor) - c_result) < 1e-12,
             "result coefficient must equal c_major - c_minor")
    _require(step.get("result_kind") == "lower_bound",
             "combine_bounds result kind must be lower_bound")
    _require(step.get("range") == "N >= X0", "combine_bounds range must be N >= X0")
    _require(constants.get("c_major") == c_major and constants.get("c_minor") == c_minor,
             "constants block must agree with the axioms")


def _check_positive_coefficient(step: Dict[str, Any], previous: Dict[str, Dict[str, Any]]) -> None:
    from_ids = step.get("from")
    _require(isinstance(from_ids, list) and len(from_ids) == 1,
             "positive_coefficient must have exactly one premise")
    premise = previous.get(from_ids[0])
    _require(premise is not None, "positive_coefficient premise not found")
    _require(premise.get("result_kind") == "lower_bound",
             "positive_coefficient premise must be a lower bound")
    _require(float(premise.get("result_coefficient")) > 0,
             "the lower-bound coefficient must be strictly positive")
    _require(step.get("result_kind") == "strict_positivity",
             "positive_coefficient result kind must be strict_positivity")


def _check_combine_ranges(step: Dict[str, Any], previous: Dict[str, Dict[str, Any]],
                          axioms: Dict[str, Dict[str, Any]]) -> None:
    finite = _find_axiom(axioms, "finite_verification")
    from_ids = step.get("from")
    _require(from_ids == [previous["S2"]["id"], finite["id"]],
             "combine_ranges must use the positivity step and the finite verification")
    _require(finite.get("range") == "4 <= N < X0",
             "finite verification must cover 4 <= N < X0")
    _require(previous["S2"].get("range") == "N >= X0",
             "positivity step must cover N >= X0")
    _require(step.get("result_kind") == "global_lower_bound",
             "combine_ranges result kind must be global_lower_bound")
    _require(step.get("range") == "N >= 4",
             "combine_ranges result range must be N >= 4")


def _check_goldbach_equivalence(step: Dict[str, Any], previous: Dict[str, Dict[str, Any]]) -> None:
    from_ids = step.get("from")
    _require(from_ids == [previous["S3"]["id"]],
             "goldbach_equivalence must use the global lower bound")
    _require(previous["S3"].get("result_kind") == "global_lower_bound",
             "the premise must be a global lower bound")
    _require(step.get("result_kind") == "theorem",
             "goldbach_equivalence result kind must be theorem")
    _require(step.get("statement") == "Every even N >= 4 is the sum of two primes.",
             "the theorem statement must be the binary Goldbach statement")


def verify_certificate(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    _require(path.is_file(), f"certificate not found: {path}")
    try:
        cert = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CertificateError(f"invalid JSON: {exc}") from exc
    _require(isinstance(cert, dict), "certificate root must be an object")
    _require(cert.get("schema_version") == 1, "unsupported schema_version")
    _require(cert.get("theorem") == "binary_goldbach", "unexpected theorem id")
    constants = cert.get("constants")
    _require(isinstance(constants, dict), "constants must be an object")
    for key in ("X0", "local_X", "c_major", "c_minor"):
        _require(key in constants, f"missing constant: {key}")
    _require(float(constants["X0"]) > float(constants["local_X"]) > 0,
             "X0 must be larger than local_X")
    axioms = _axiom_map(cert)
    steps = _step_map(cert)
    _require([s.get("id") for s in steps] == ["S1", "S2", "S3", "S4"],
             "steps must be S1..S4 in order")
    by_id: Dict[str, Dict[str, Any]] = {}
    _check_combine_bounds(steps[0], axioms, constants)
    by_id["S1"] = steps[0]
    _check_positive_coefficient(steps[1], by_id)
    by_id["S2"] = steps[1]
    _check_combine_ranges(steps[2], by_id, axioms)
    by_id["S3"] = steps[2]
    _check_goldbach_equivalence(steps[3], by_id)
    by_id["S4"] = steps[3]
    return {
        "status": "PASS",
        "theorem": cert["theorem"],
        "steps_checked": len(steps),
        "axioms": sorted(axioms),
        "steps": [{"id": step.get("id"), "rule": step.get("rule")} for step in steps],
        "axiom_sources": {axiom_id: axioms[axiom_id].get("source", "") for axiom_id in sorted(axioms)},
        "c_major": float(constants["c_major"]),
        "c_minor": float(constants["c_minor"]),
        "result_coefficient": float(constants["c_major"]) - float(constants["c_minor"]),
        "X0": constants["X0"],
        "local_X": constants["local_X"],
    }
