# tests/ — real data, real computation

Sixteen modules: a per-concept suite for each domain module, plus `test_figures.py`,
`test_manuscript_variables.py`, `test_guards_and_contracts.py`, `test_protocol_integration.py`,
`test_package_metadata.py`, `test_reference_intel.py`, `test_regeneration_determinism.py`
and `test_scripts_smoke.py`.

## Rules

- **No mock framework anywhere** — no `unittest.mock`, no `MagicMock`, no monkey-patching.
  Tests use real computation on fixed or deterministically generated data.
- **A new domain module needs its own suite**, in the same style as its peers: physics,
  boundaries, validation branches and determinism.
- **`test_regeneration_determinism.py` keeps derived artifacts byte-identical** across runs:
  it runs the real generator CLIs twice across a wall-clock gap in a scratch copy and compares
  every byte, and it carries a positive control that reintroduces the clock and shows the
  comparison go red. When you regenerate, this suite is the check that you introduced no drift.
- **`test_reference_intel.py` pins the read-only `grand_slam:` mirror** in
  `manuscript/config.yaml` to the `REFERENCE_*` constants (and pins the shared physical
  constants across the two laser modules); a new constant that skips the mirror fails here.
- **`test_guards_and_contracts.py` and `test_protocol_integration.py` protect the layer
  contract and the frozen discovery surface**; loosening one to admit a shortcut defeats it.
- **Every gate must be able to fail.** State the input that turns a new assertion red, and
  prefer shipping that input as a positive-control test.
- Coverage floor 90% line and branch: `uv run python -m pytest tests/ --cov=src --cov-fail-under=90`. Focused runs: `uv run python -m pytest tests/test_<module>.py -v`.
