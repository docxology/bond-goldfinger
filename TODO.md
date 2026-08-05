# goldfinger — TODO (GRAND SLAM)

Film package: Goldfinger (1964), mission codename GRAND SLAM. Local-only.

## Built (phase 4 deep improvement)

- **Three new pure algorithm modules** (each with a matching real-data test file):
  - `reserve_attack.py` — first-generation **speculative attack** on the gold
    peg (Flood–Garber, 1984): shadow floating rate, attack time, reserve drain,
    post-float depreciation. Macro-extension of the corner.
  - `vault_threat_network.py` — graph **penetration + network hardening**:
    Dijkstra minimum-effort intrusion path over a vault zone graph (weak path
    = secret tunnel), edge criticality, greedy budget-hardening allocation.
  - `laser_thermal.py` — **Gaussian-beam + Carslaw–Jaeger** laser engagement:
    Rayleigh range/defocusing, surface melt time, effective burn range.
- **Existing modules**: `market_attack`, `vault_security`, `laser_physics` (kept
  unchanged from phase 2).
- **Mission adapter deepened, surface frozen**: `mission.py` still exposes
  `MissionProvider` (film, 5 lifecycle methods), module-level `GADGETS`
  registry, and `register_market_gadgets`; now wraps six models, six assets,
  seven plan steps, six-gadget registration, and enriched outcome results
  (`corner`, `reserve`, `vault`, `vault_network`, `laser`, `laser_thermal`).
- **Manuscript plumbing**: `manuscript_variables.py` now emits **39 tokens**;
  `figures/plots.py` renders **six** concept figures; manuscript methodology /
  results / conclusion / abstract extended; `references.bib` + `99_references.md`
  gained real sources (Krugman 1979, Flood & Garber 1984, Dijkstra 1959,
  Carslaw & Jaeger 1959, Israeli & Wood 2002).
- **Tests**: 119 tests across the six modules + mission + protocol integration
  + manuscript variables (live token gate) + figures + scripts smoke; zero mocks.

## Verification (see run_verification notes in AGENTS.md)

- `uv run python -m pytest tests/ --cov=src/goldfinger --cov-fail-under=90`
  → 119 passed, ~96.6% coverage.
- `uv run ruff check src/ scripts/ tests/` + `ruff format --check` → clean.
- `uv run mypy src/goldfinger scripts` → clean.
- Lineage `template[_]code_project` → zero.

## Declared integration points

- **bond-api protocol**: implemented, discoverable by slug. If `bond-api`
  ever fails to import, the six pure modules
  (`market_attack`, `reserve_attack`, `vault_security`, `vault_threat_network`,
  `laser_physics`, `laser_thermal`) remain importable standalone; only
  `mission.py` is coupled.
- **Provenance helper**: outcome provenance currently uses the protocol's
  `bond_api.Provenance` directly. A later phase may delegate persistence to
  `bond_utilities.mission_io.record_provenance_outcome` once bond-utilities is
  converted at this level — acceptance: `record_provenance_outcome` writes a
  GRAND SLAM record under `output/data/`.
- **Publisher metadata** (`CITATION.cff`, `.zenodo.json`, `codemeta.json`) is
  prose-grade and omits fabricated DOIs/URLs (local-only tree). Populate real
  values only if a remote publication target is later authorized.

## Not in scope

- No remote push, no sibling-package changes.
