# goldfinger — TODO (GRAND SLAM)

Film package: Goldfinger (1964), mission codename GRAND SLAM. Local-only.

## Built (phase 2)

- **Pure domain core** (`src/goldfinger/`), each with a matching real-data
  test file:
  - `market_attack.py` — Operation Grand Slam gold-market cornering model
    (constant-elasticity inverse demand + tatonnement shock dynamics),
    `effective_supply`, `shocked_equilibrium_price`, `price_gain`,
    `simulate_corner`, `corner_valuation`.
  - `vault_security.py` — Fort Knox-style layered defense assessment
    (`layered_security_score`, `penetration_probability`,
    `expected_breach_time`, `weakest_layer`, `marginal_improvements`,
    `vault_security_verdict`).
  - `laser_physics.py` — laser threat physics (`burn_through_time`,
    `power_for_burn_through`, `max_burn_thickness`, `laser_threat_severity`).
- **Mission adapter** `src/goldfinger/mission.py` — implements the FROZEN
  `bond_api.MissionProvider` (brief/recon/plan/execute/debrief), registers
  gadgets (`market_corner`, `vault_defense`, `laser_threat`) with a
  `GadgetRegistry`, discoverable by slug `goldfinger`.
- **Manuscript plumbing** — `manuscript_variables.py` ({{TOKEN}} hydration,
  25 tokens), `figures/plots.py` (3 concept figures), `manuscript/` identity +
  numbered prose sections.
- **Thin CLIs** — `scripts/brief|recon|plan|execute|debrief.py` +
  `z_generate_manuscript_variables.py`.
- **Tests** — 79 tests across market/vault/laser + mission + protocol
  integration + manuscript variables (live token gate) + figures + scripts
  smoke; zero mocks.

## Verification (see run_verification notes in AGENTS.md)

- `uv run python -m pytest tests/ --cov=src/goldfinger --cov-fail-under=90`
  → 79 passed, ~97% coverage.
- `uv run ruff check src/ scripts/ tests/` + `ruff format --check` → clean.
- `uv run mypy src/goldfinger scripts` → clean.
- Lineage `template[_]code_project` → zero (only the split-pattern grep in
  docs; no real strings).

## Declared integration points

- **bond-api protocol**: implemented, discoverable by slug. If `bond-api`
  ever fails to import, the pure core (`market_attack`, `vault_security`,
  `laser_physics`) remains importable standalone; only `mission.py` is
  coupled.
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
