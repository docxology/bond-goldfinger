# src/ — pure domain core, thin adapter, derived surface

Six pure domain modules across three attack surfaces (`market_attack.py`,
`reserve_attack.py`, `vault_security.py`, `vault_threat_network.py`, `laser_physics.py`,
`laser_thermal.py`), the `mission.py` adapter, the derived layer
(`manuscript_variables.py`, `figures/`) and `__init__.py`.

## Rules

- **Keep the layer contract.** The six domain modules are pure: no I/O, no `bond_api`, no
  infrastructure imports, deterministic, importable standalone. `mission.py` is the **only**
  module that imports `bond_api`; `manuscript_variables.py` and `figures/` derive from the
  domain and may do file I/O, but never import the adapter.
- **The pure core must keep working without `bond-api`.** Confine that import so a failure of
  the path dependency never blocks the science.
- **Protocol stability.** The discovery surface is frozen: module path `goldfinger.mission`,
  class `MissionProvider`, the `film` value, the five lifecycle methods, the module-level
  `GADGETS` registry, `register_market_gadgets` and `build_provider`. bond-cli, the
  coordinator reconcile and the orchestrator consume them across the fleet; deepen inside the
  package instead. `tests/test_protocol_integration.py` is the tripwire.
- **`__init__.py` is the public API** plus the shared mission constants the adapter and the
  token map both read; do not put logic there that belongs to a module.
- **`REFERENCE_*` constants are the single source of truth** for reference intel. The adapter,
  the token map and the figures all read them; never repeat a literal elsewhere. The
  read-only `grand_slam:` mirror in `manuscript/config.yaml` is pinned to those constants by
  `tests/test_reference_intel.py`, so a new constant must be added to the mirror.
- **No clock anywhere in a persisted artifact.** Do not add a `now=` parameter to buy
  determinism back: an injectable clock is still a clock, and the injection sites are where
  the leak hides. Dates come from committed config (`paper.date`, surfaced as
  `MANUSCRIPT_DATE`, with no default).
- Deterministic and mock-free; coverage floor 90% line and branch on `src/goldfinger/`.
