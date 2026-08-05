# Architecture — goldfinger (GRAND SLAM)

The package follows the PROJECT BOND layer contract: a pure, infrastructure-free
domain core wrapped by a thin protocol adapter, with thin CLIs on top. Three
attack surfaces, two modules each — one closed-form, one structural.

```
                  ┌──────────────────────────────────────┐
                  │ bond_api.protocol / registry (FROZEN) │
                  │ MissionProvider, run_mission,         │
                  │ GadgetRegistry                        │
                  └──────────────────▲───────────────────┘
                                     │ implements (the ONLY bond_api import)
                  ┌──────────────────┴───────────────────┐
                  │ src/goldfinger/mission.py             │
                  │ MissionProvider adapter · GADGETS     │
                  └──────────────────▲───────────────────┘
                                     │ uses
   ┌──────────────────────┬──────────┴───────────┬──────────────────────┐
   │ MACRO ATTACK         │ VAULT DEFENSE        │ LASER THREAT         │
   │ market_attack        │ vault_security       │ laser_physics        │
   │ reserve_attack       │ vault_threat_network │ laser_thermal        │
   └──────────┬───────────┴──────────┬───────────┴───────────┬──────────┘
              │      PURE DOMAIN CORE — no I/O, no bond_api, deterministic
              └─────────────────────┬────────────────────────┘
                                    ▼
                  ┌──────────────────────────────────────┐
                  │ manuscript_variables.py  {{TOKEN}}s   │
                  │ figures/plots.py         renderers    │
                  └──────────────────┬───────────────────┘
                                     ▼
                           scripts/ (thin CLIs)
                  brief | recon | plan | execute | debrief
                  z_generate_manuscript_variables · z_generate_counts
```

Dependency direction is strictly downward. The concept modules import nothing
from each other; the adapter imports all of them; the token map and the figures
import the concept modules but never the adapter, so they stay importable when
`bond-api` is absent.

## Module responsibilities

### Macroeconomic attack

**`market_attack.py`** — Operation Grand Slam as a supply shock.
`effective_supply` sterilises a fraction of the float; `shocked_equilibrium_price`
clears the residual supply against constant-elasticity demand
($P^* = P_0 (S_0/S_\text{eff})^{1/\eta}$); `price_gain` returns the fractional
appreciation; `simulate_corner` runs the tâtonnement update
$P_{t+1} = P_t + \lambda(P^*-P_t)$ and returns a frozen `CornerResult` (shocked
price, gain, full trajectory); `convergence_residual` and `has_converged` test
settlement against `CONVERGENCE_TOLERANCE` — a *relative* residual, never exact
float equality, because tâtonnement reaches $P^*$ only in the limit.
`corner_valuation` prices a seized stockpile. Reference intel:
`REFERENCE_MODEL`.

**`reserve_attack.py`** — the first-generation speculative attack (Flood–Garber).
`surface_money` gives the constant money stock the peg implies; `domestic_credit`
grows credit exponentially; `reserve_level` drains reserves under the fixed
regime; `shadow_rate` is the rational-expectations floating rate that would
prevail post-abandonment; `attack_time` is the instant the shadow rate reaches
parity; `reserve_floor_time` is the *later* gradual-exhaustion time, and the gap
between the two is the model's headline — the attack is sudden.
`floating_depreciation` prices the post-float collapse; `simulate_reserve_crisis`
traces both paths. `_require_stable_peg` enforces the model's feasibility
conditions ($0 < \alpha\mu < 1$; initial credit small enough that the peg has
not already fallen) on every entry point. Reference intel: `REFERENCE_ATTACK`.

### Vault defense

**`vault_security.py`** — layered defense-in-depth. `layered_security_score` is
the weighted average of per-layer ratings; `penetration_probability` applies the
product rule $\prod(1-r_i)$ over `LAYER_ORDER`; `expected_breach_time`
telescopes the sequential attempt; `weakest_layer` returns the lowest-rated
layer in traversal order (a uniformly perfect vault is valid and yields the
first layer); `marginal_improvements` ranks fortification priority by composite
gain; `vault_security_verdict` bins the score. Reference intel:
`REFERENCE_RATINGS`, `DEFAULT_WEIGHTS`, `LAYER_ORDER`.

**`vault_threat_network.py`** — the adversary's *route*, which ratings cannot
express. `minimum_effort_path` is a deterministic Dijkstra (explicit
canonical-order tie-breaking, so there is no heap-ordering ambiguity) over an
undirected zone graph; `path_effort` sums a given route; `edge_criticality`
ranks shortest-path edges by how much removing each raises the minimum effort
(unreachable ⇒ `inf`); `harden_network` greedily spends a budget, raising at
each step the edge whose lift most increases the minimum effort. Reference
intel: `REFERENCE_GRAPH`, `REFERENCE_TARGET`, `REFERENCE_HARDENING`,
`VAULT_NODE_ORDER`.

### Laser threat

**`laser_physics.py`** — scalar energy balance. `energy_to_burn` is the heat
load of the material column under the spot; `absorbed_power` applies
absorptivity; `burn_through_time` divides the two; `power_for_burn_through` and
`max_burn_thickness` are its inverses; `laser_threat_severity` bins power
against a threshold. Reference intel: `REFERENCE_PHYSICS`.

**`laser_thermal.py`** — the spatio-temporal picture. `rayleigh_range` and
`spot_radius_at_distance` give Gaussian defocusing; `power_density` converts
that spot to absorbed flux; `thermal_surface_temperature` is the Carslaw–Jaeger
constant-flux solution; `surface_melt_time` inverts it; `melt_time_at_distance`
composes optics with conduction; `effective_burn_range` scans range for the
farthest point that still melts within a threat window. Reference intel:
`REFERENCE_BEAM`.

### Adapter and plumbing

**`mission.py`** — the BOND-API `MissionProvider`. See the next section.

**`manuscript_variables.py`** — `generate_variables()` reads
`manuscript/config.yaml` and the module `REFERENCE_*` constants and returns the
`{{TOKEN}} → value` map declared by `GOLDFINGER_TOKENS`;
`concept_module_names()` derives the module list from the package directory;
`render_counts_markdown()` renders `docs/_generated/COUNTS.md`.

**`figures/plots.py`** — one renderer per concept model, listed in
`figures.FIGURE_RENDERERS`, each writing a deterministic PNG to
`output/figures/`.

**`__init__.py`** — the public API plus the shared mission constants (`FILM`,
`CODENAME`, `MISSION_SEED`, `LASER_SEVERITY_THRESHOLD_W`,
`LASER_STANDOFF_RANGE_M`) that the adapter and the token map both read, so a
provenance record and the manuscript cannot report different values.

**`scripts/`** — thin CLIs, one per mission phase plus two generators. They
bootstrap `sys.path` (`# noqa: E402`), call into `src/`, and print. No business
logic lives here.

## How mission.py implements the frozen MissionProvider

`mission.py` is the only module in the package that imports `bond_api`. It
implements the protocol *structurally* — no inheritance. Discovery in
`bond_api.discovery` imports `goldfinger.mission` and binds the
`MissionProvider` class whose `film` attribute matches the slug.

| Stage | Implementation |
|---|---|
| `film` | Class attribute `"goldfinger"` — must equal the package slug or discovery rejects it |
| `brief()` | A `MissionBrief` with the codename, the objectives, one `Asset` per concept model (payload = that model's `REFERENCE_*` intel), and determinism/locality `Constraint`s |
| `recon(request)` | A `ReconReport` of `Finding`s echoing the goal and asserting the model set, determinism, and scope boundary |
| `plan(brief)` | A `MissionPlan` of `Step`s — one per model plus a synthesis step — each naming the asset it consumes by index into `brief.assets` |
| `execute(plan)` | Calls the private `_*_intel()` helpers, assembles `results` keyed `corner` / `reserve` / `vault` / `vault_network` / `laser` / `laser_thermal`, and returns a `MissionOutcome` with `Provenance` (package version, seed, input hash, `wall_time_s = 0.0`) |
| `debrief(outcome)` | A `Debrief` wrapping the outcome plus the standing lessons |

Two module-level names complete the contract: `GADGETS` (a `GadgetRegistry` the
mission registers into) and `register_market_gadgets(registry=GADGETS)`, which
registers the concept callables `market_corner`, `reserve_attack`,
`vault_defense`, `vault_hardening`, `laser_threat`, and `laser_thermal`. The
constructor calls the hook, so a discovered provider is ready to use.

### What is frozen and what may change

**Frozen** — consumed by bond-cli, the coordinator reconcile, and the
orchestrator across the fleet. Changing any of these breaks other packages:

- the module path `goldfinger.mission` and the class name `MissionProvider`
- the `film` attribute value
- the five lifecycle method names and their signatures
- the module-level `GADGETS` name and the `register_market_gadgets` hook
- `build_provider()`

**Free to deepen** — all internal: the objective and lesson text, the number and
content of assets and plan steps, the `results` payload, the `_*_intel()`
helpers, and every concept module behind them.

`tests/test_protocol_integration.py` pins the frozen half; the deepening half is
covered by `tests/test_mission.py`.

## Data flow and the single source of truth

The **module `REFERENCE_*` constants are the source of truth.** The adapter,
`manuscript_variables.py`, and `figures/plots.py` all read those constants —
none of them repeats a literal — so the mission outcome, the numbered prose,
and the figures cannot disagree.

`manuscript/config.yaml` (`grand_slam:`) is a *mirror* of those constants for
human reading. No code path loads it: `load_mission_config` reads the file for
identity and publication metadata only, and `generate_variables` takes every
intel value from the imported constants. That mirror was previously described
as the single source of truth from which "every value is injected", which was
false — editing `grand_slam.market.reference_price` changed nothing. It is now
enforced instead of asserted: `tests/test_reference_intel.py` compares the
block against all six constants key-for-key and value-for-value (including the
undirected zone graph), and requires the block to declare exactly the six
sub-blocks, so a new `REFERENCE_*` constant cannot ship unmirrored.

The two laser models are held to one physical target by the same file:
`REFERENCE_PHYSICS` and `REFERENCE_BEAM` must agree on density, specific heat,
absorptivity, and power, and the scalar model's `delta_temperature` must equal
the thermal model's `melt_temp - ambient`.

### What the anti-hardcode gate does and does not cover

`test_no_computed_result_value_is_hardcoded_in_the_prose` scans the rendered
manuscript files — the numbered sections **and** `preamble.md` — for pasted
result values. Its scope is defined by a three-way partition of
`GOLDFINGER_TOKENS` (identity / declared input / computed result) that
`test_every_token_is_classified_exactly_once` forces to be total, so a new
token cannot escape classification.

Within the computed class, a token is scanned when its value is a numeric
literal of at least three characters. Bare small integers (module, figure,
token, layer, zone, and edge counts) and categorical words (`medium`,
`serious`, `fence`, `true`) are **not scanned** — searching prose for `6` or
`medium` produces false positives, not detections. They are enumerated with
reasons in `_UNSCANNABLE_RESULT_TOKENS`, and
`test_unscannable_tokens_are_exactly_the_ones_the_rule_rejects` pins that list
to the rule. So the honest statement is: *no scannable computed result value
appears as a prose literal, and a per-token positive control proves each of
those values is detectable; hand-typed counts and category words remain
unguarded by this scan.*
