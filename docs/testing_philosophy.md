# Testing Philosophy — goldfinger (GRAND SLAM)

## Principles

1. **Real data + computation only — zero mocks.** No `MagicMock`,
   `unittest.mock`, `mocker.patch`, or `create_autospec`. Deterministic fakes
   (when needed at all) implement the *real* protocol.
2. **Deterministic.** Fixed seeds, fixed inputs, asserted exact values /
   closed-form hand-vectors. No untracked RNG, no wall-clock assertions.
3. **Coverage-gated.** `--cov=src/goldfinger --cov-fail-under=90` (currently
   ~97% line+branch). Tests do not count toward coverage.
4. **Per-concept test files.** Each pure module has a matching
   `test_<module>.py` exercising hand-vector values, invariants, inverse
   round-trips, and every error branch.

## What each file covers

- `test_market_attack.py` — supply-shock math, hand optics, monotonicity,
  tatonnement convergence/divergence, provenance determinism.
- `test_vault_security.py` — weighted-average scores, product-rule
  penetration, expected breach time, weakest-layer ranking, verdict
  thresholds, marginal-improvement ordering.
- `test_laser_physics.py` — energy hand-vector, power/time/thickness
  round-trips, inverse power scaling, threat severity boundaries.
- `test_mission.py` + `test_protocol_integration.py` — provider lifecycle,
  determinism, protocol conformance, slug discovery, serialization round-trip,
  gadget registration.
- `test_manuscript_variables.py` — config loading, token completeness, and the
  **live token cross-reference gate** (every `{{TOKEN}}` in `manuscript/[0-9]*.md`
  must exist in `generate_variables()`).
- `test_figures.py` — PNG render + determinism.
- `test_scripts_smoke.py` — subprocess runs of the thin CLIs via
  `sys.executable`, `cwd=project_root`.

## Error branches

Every `TypeError` / `ValueError` guard in the pure modules is exercised by an
explicit test (out-of-range ratings, non-positive physics, invalid adjustment,
empty layers, etc.), keeping line + branch coverage high through real calls.
