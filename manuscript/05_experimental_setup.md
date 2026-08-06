# Experimental Setup

## Reference intel

The deterministic reference parameters are **declared in the module
`REFERENCE_*` constants** in `src/goldfinger/`. Those constants are what the
domain core, the mission adapter, the figures, and the token map all read, and
every value below is injected from them as a generated variable, so a change to
the intel changes this section automatically.

`manuscript/config.yaml` carries a human-readable `grand_slam:` mirror of the
same numbers. Nothing loads that block at runtime — it is documentation, not
input — so its only guarantee is that
`tests/test_reference_intel.py` compares it key-for-key and value-for-value
against the module constants and fails if either side is edited alone.

**Market corner** (`market_attack.REFERENCE_MODEL`) — reference price
`${{MARKET_REFERENCE_PRICE}}`/oz clearing a normalized floatable-supply index
of `{{MARKET_SUPPLY_INDEX}}`; the corner sterilizes
`{{MARKET_FRACTION_REMOVED}}%` of that float against a constant demand
elasticity of `{{MARKET_ELASTICITY}}`. The tâtonnement runs `{{MARKET_STEPS}}`
steps at adjustment coefficient `{{MARKET_ADJUSTMENT}}`.

**Speculative reserve attack** (`reserve_attack.REFERENCE_ATTACK`) — a
normalised peg at parity `{{RESERVE_PARITY}}`, foreign interest rate
`{{RESERVE_FOREIGN_RATE}}`, money-demand semi-elasticity $\alpha$ =
`{{RESERVE_ALPHA}}`, initial domestic credit `{{RESERVE_CREDIT_0}}`, and
credit growth $\mu$ = `{{RESERVE_GROWTH}}`. The model validates its own
feasibility conditions ($0 < \alpha\mu < 1$, and initial credit small enough
that the peg has not already fallen) before computing an attack time.

**Vault — layered** (`vault_security.REFERENCE_RATINGS`) —
`{{VAULT_LAYER_COUNT}}` layers (perimeter, fence, guard response, vault door,
combination lock, gold storage), each rated in `[0,1]`, weighted by
`DEFAULT_WEIGHTS` and traversed in `LAYER_ORDER`.

**Vault — network** (`vault_threat_network.REFERENCE_GRAPH`) — an undirected
graph of `{{VAULT_ZONE_COUNT}}` defensive zones with intrusion-effort edge
costs. The reference intrusion problem is perimeter → gold chamber
(`REFERENCE_TARGET`); the reference defensive posture (`REFERENCE_HARDENING`)
is a budget of `{{VAULT_HARDENING_BUDGET}}` units buying
`{{VAULT_GAIN_PER_UNIT}}` effort each.

**Laser — scalar** (`laser_physics.REFERENCE_PHYSICS`) — power
`{{LASER_POWER_W}}` W onto a focused spot of `{{LASER_SPOT_AREA_M2}}` m²
against a steel plate of density `{{LASER_DENSITY_KGM3}}` kg/m³ and thickness
`{{LASER_THICKNESS_MM}}` mm, specific heat `{{LASER_SPECIFIC_HEAT}}` J/(kg·K),
$\Delta T$ = `{{LASER_DELTA_T_K}}` K, absorptivity `{{LASER_ABSORPTIVITY}}`.
A beam is classified *serious* at or above `{{LASER_SEVERITY_THRESHOLD_W}}` W.
This is the *same* plate as the thermal model below: the two modules shipped
different steel (specific heat 500 vs 460 J/(kg·K), and a $\Delta T$ that did
not equal that model's melt-minus-ambient span) until the constants were
reconciled, so $\Delta T$ is now exactly
`{{LASER_MELT_TEMP_K}}` K − `{{LASER_AMBIENT_K}}` K and
`tests/test_reference_intel.py` asserts the agreement.

**Laser — thermal** (`laser_thermal.REFERENCE_BEAM`) — an Nd:YAG-class
continuous-wave beam of wavelength `{{LASER_WAVELENGTH_NM}}` nm focused to a
waist of `{{LASER_WAIST_MM}}` mm, against steel of thermal conductivity
`{{LASER_CONDUCTIVITY}}` W/(m·K) melting at `{{LASER_MELT_TEMP_K}}` K from an
ambient of `{{LASER_AMBIENT_K}}` K, engaged within a
`{{LASER_THREAT_WINDOW_S}}` s threat window.

## Determinism policy

The mission declares a fixed seed of `{{GOLDFINGER_SEED}}` and performs **no**
random draws — the seed is recorded in provenance so a replay is auditable,
not because any sampling occurs. Persisted artifacts carry no wall-clock
dependence at all (`wall_time_s = 0.0` in provenance; no clock in the token
map). The manuscript's date is the committed `paper.date` from
`manuscript/config.yaml` — `MANUSCRIPT_DATE` = {{MANUSCRIPT_DATE}} — so
`GOLDFINGER_VERSION_HASH`, which hashes the full token map, identifies the
content rather than the run and is stable across regenerations. Figure output
is byte-deterministic for fixed inputs:
`tests/test_figures.py` renders **every** exported renderer twice — into two
separate directories and again over the same path — and compares the bytes,
parametrised over `figures.FIGURE_RENDERERS` so a renderer added later is
covered without anyone remembering to add it.

## Software environment

- Python: as resolved by `uv` (the package requires `>=3.10`)
- Dependencies: NumPy, Matplotlib, PyYAML, and the frozen `bond-api` protocol
  (a local path dependency declared in `pyproject.toml` under
  `[tool.uv.sources]`; the sibling `bond-api` package in this working tree)
- Dev: pytest, pytest-cov, mypy, ruff, types-PyYAML

## Mission adapter

The BOND-API `MissionProvider` (`src/goldfinger/mission.py`) wraps all
{{GOLDFINGER_MODULE_COUNT}} models and registers six gadgets
(`market_corner`, `reserve_attack`, `vault_defense`, `vault_hardening`,
`laser_threat`, `laser_thermal`) with a module-level `GadgetRegistry`. It is
discoverable by slug `goldfinger` on `sys.path` and drives the full
brief–recon–plan–execute–debrief lifecycle with deterministic provenance,
and persists the outcome as a schema-validated mission record (via
`bond-utilities`'s `record_provenance_outcome`) whose `input_hash` is a real
fingerprint of the reference intel, not a hand-typed literal — so two outcomes
from unchanged constants carry identical provenance and a one-value edit to
any constant is visible in the hash. The record writes no wall clock (its
`started_at` is a committed sentinel), so it is byte-identical on every run.
The adapter's public shape is frozen across phases; the mission internals
(assets, plan steps, outcome results, lessons) are what deepen.
