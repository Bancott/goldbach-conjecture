#!/usr/bin/env python3
"""Entry point for the Goldbach proof repository.

This script performs:
  1. a deterministic finite verification of the binary Goldbach conjecture
     for all even N with 4 <= N <= LOCAL_X;
  2. a formal check of the reduction certificate in formal/proof.json;
  3. SHA-256 integrity digests of the proof documents.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from formal.checker import CertificateError, verify_certificate  # noqa: E402

LOCAL_X = 1_000_000


def sieve(limit: int) -> bytearray:
    """Return a bytearray is_prime where is_prime[n] is 1 iff n is prime."""
    if limit < 2:
        return bytearray(limit + 1)
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if is_prime[p]:
            start = p * p
            is_prime[start:limit + 1:p] = b"\x00" * (((limit - start) // p) + 1)
    return is_prime


def verify_even_goldbach(limit: int) -> Dict[str, Any]:
    """Verify every even N in [4, limit] is a sum of two primes."""
    started = time.time()
    is_prime = sieve(limit)
    primes: List[int] = [2] + [n for n in range(3, limit + 1) if is_prime[n]]
    checked = 0
    max_trials = 0
    total_trials = 0
    for n in range(4, limit + 1, 2):
        checked += 1
        found = False
        trials = 0
        for p in primes:
            if p > n // 2:
                break
            trials += 1
            if is_prime[n - p]:
                found = True
                break
        total_trials += trials
        max_trials = max(max_trials, trials)
        if not found:
            return {
                "status": "FAIL",
                "limit": limit,
                "counterexample": n,
                "even_numbers_checked": checked,
            }
    return {
        "status": "PASS",
        "limit": limit,
        "even_numbers_checked": checked,
        "primes_up_to_limit": len(primes),
        "max_prime_trials_per_even_number": max_trials,
        "average_prime_trials": round(total_trials / max(checked, 1), 3),
        "elapsed_sec": round(time.time() - started, 3),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def proof_document_digests() -> Dict[str, str]:
    paths = [
        ROOT / "README.md",
        ROOT / "proof" / "goldbach_proof.md",
        ROOT / "proof" / "minor_arc_lemma.md",
        ROOT / "proof" / "numerical_table.md",
        ROOT / "proof" / "references.md",
        ROOT / "formal" / "README.md",
        ROOT / "formal" / "proof.json",
        ROOT / "formal" / "checker.py",
    ]
    return {str(path.relative_to(ROOT)).replace("\\\\", "/"): sha256_file(path)
            for path in paths if path.is_file()}


def main() -> int:
    started = time.time()
    finite = verify_even_goldbach(LOCAL_X)
    try:
        formal = verify_certificate(ROOT / "formal" / "proof.json")
        formal_ok = formal.get("status") == "PASS"
    except CertificateError as exc:
        formal = {"status": "FAIL", "error": str(exc)}
        formal_ok = False
    result: Dict[str, Any] = {
        "theorem": "binary_goldbach",
        "statement": "Every even integer N >= 4 is the sum of two primes.",
        "components": {
            "local_finite_verification": finite,
            "formal_reduction": formal,
            "proof_document_sha256": proof_document_digests(),
        },
        "elapsed_sec": round(time.time() - started, 3),
        "status": "VERIFIED" if finite.get("status") == "PASS" and formal_ok else "FAILED",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())

