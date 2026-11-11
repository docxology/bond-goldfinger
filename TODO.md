# TODO — goldfinger (GRAND SLAM)

`goldfinger` is the PROJECT BOND film package for *Goldfinger* (1964), mission
codename **GRAND SLAM**: six pure, deterministic concept modules across three
attack surfaces (gold-market corner + speculative peg attack; layered vault
defence + intrusion-graph hardening; scalar burn-through + Gaussian/conduction
laser thermal), wrapped by a frozen BOND-API `MissionProvider` adapter, with a
token-driven manuscript and generated figures. Verified state as of 2026-08-05,
the run that removed the wall clock from the token map and added
`tests/test_regeneration_determinism.py`: **204 tests passed, 0 skipped,
0 failed; 100.00% line *and* branch coverage on `src/goldfinger/`** measured by
`uv run pytest tests/ --cov=src --cov-fail-under=90`; `ruff check`, `ruff format
--check`, and `mypy src/goldfinger scripts` all clean; zero exemplar-lineage
hits. Tracked at `github.com/docxology/bond-goldfinger` (`origin`, branch
`main`); the suite copy under `projects/working/bond/` has no remote of its own.

Do not restate a measured figure in this file; cite
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md). The paragraph above is
the one exception, and it is dated and named to a specific change for that reason.

## Open work

### Correctness

**C1 — `Provenance.input_hash` is a hand-typed literal, not a fingerprint of the
inputs.**
`src/goldfinger/mission.py:372` passes
`input_hash="goldfinger-grand-slam-input-v2"`. The protocol it satisfies
documents that field as "a stable fingerprint of the mission inputs so outcomes
can be audited without re-running the film"
(`../bond-api/src/bond_api/protocol.py:196`), and bond-api ships the machinery to
build one: `fingerprint(*parts)` at
`../bond-api/src/bond_api/capabilities.py:148` and `derive_provenance(...)` at
`:181`. Consequence today: editing any `REFERENCE_*` constant changes every
result in `outcome.results` while `input_hash` stays byte-identical, so an
auditor comparing two provenance records concludes the inputs did not move. The
literal is also hand-maintained (`-v2`), which is exactly the class of value this
package's doctrine forbids elsewhere.
*Done:* `input_hash` is derived from the reference intel actually consumed by
`execute()` (the `REFERENCE_*` mappings the `_*_intel()` helpers read), so two
runs with the same constants agree and a one-value edit to any constant produces
a different hash. Only `src/goldfinger/mission.py` changes — the frozen surface
(module path, class name, `film`, five methods, `GADGETS`,
`register_market_gadgets`, `build_provider`) is untouched.
*Demonstrate:* a new test that computes the provenance for the shipped constants,
recomputes it against a perturbed copy of one constant, and asserts the two
hashes differ — plus `uv run pytest tests/test_protocol_integration.py -v`.

**C2 — `effective_burn_range` returns a two-valued `0.0`.**
`src/goldfinger/laser_thermal.py:153-204`; the ambiguity is stated in the
docstring at `:173-178` and repeated as a trap in
`docs/agent_instructions.md:110-111`. `0.0` means either "melts only at the focal
point" or "never melts anywhere in the window"; callers must disambiguate by
re-calling `melt_time_at_distance(..., 0.0)`. Deferred because a richer return
changes a signature that both `mission.py` (`_laser_thermal_intel`) and
`figures/plots.py` (`plot_laser_engagement`) call.
*Done:* the function returns a value that carries `burns_at_focus` alongside the
range (a small frozen result object, mirroring `market_attack.CornerResult`),
both call sites are updated, and no caller needs a second call to interpret
`0.0`.
*Demonstrate:* `uv run pytest tests/test_laser_thermal.py tests/test_mission.py
tests/test_figures.py -v` with a test asserting the focus-only and
never-melts cases are now distinguishable without a second call.

### Verification

**V0 — RESOLVED 2026-08-05: the byte-identical regeneration claim was false.**
`src/goldfinger/manuscript_variables.py` stamped
`datetime.now(timezone.utc)` into `GENERATION_TIMESTAMP`, which was persisted
into `output/data/manuscript_variables.json` and folded into
`GOLDFINGER_VERSION_HASH`, so two consecutive regenerations wrote different
bytes (md5 of the generated JSON: `c58b81e5…` then `cc58539a…`). Meanwhile
`manuscript/01_introduction.md`, `02_methodology.md`, `05_experimental_setup.md`
and `AGENTS.md` all claimed persisted artifacts carry no wall-clock dependence.
The suite could not see it: *every* call site injected a fixed `now=`, so the
default path — the one the generator script actually took — was never observed.
*Resolution:* the clock is gone rather than pinned. The `now` parameter was
removed outright, and the manuscript date is now the committed `paper.date` in
`manuscript/config.yaml`, surfaced as `MANUSCRIPT_DATE` and required with no
default (a defaulted date would be a hand-authored literal). The version hash
is consequently a content identifier, not a run identifier.
*Bound by:* `tests/test_regeneration_determinism.py` — runs the real generator
CLIs twice across a wall-clock gap in a scratch copy of the tree and compares
every generated byte, with a positive control that patches the clock back into
the copy and asserts the comparison goes red.
*Demonstrate:* `uv run pytest tests/test_regeneration_determinism.py -v`, then
`uv run python scripts/z_generate_manuscript_variables.py; md5 output/data/manuscript_variables.json`
twice — the hashes now match.

**V1 — the provenance determinism test cannot fail on `input_hash`.**
`tests/test_protocol_integration.py:90-95`
(`test_deterministic_provenance`) asserts `o1.provenance.input_hash ==
o2.provenance.input_hash`. While C1 stands, that compares a module-level string
constant with itself: it is green by construction and would stay green if the
mission became nondeterministic. It reads as coverage of a determinism claim it
does not bind.
*Done:* the assertion compares a hash that varies with the inputs (C1), and the
test ships a positive control showing a perturbed input turns it red.
*Demonstrate:* `uv run pytest tests/test_protocol_integration.py::test_deterministic_provenance -v`,
plus the negative-control test from C1.

**V2 — the measured lines of `docs/_generated/COUNTS.md` are ungated.**
`docs/_generated/COUNTS.md:7-8` carries `**204 collected**` and `**100.00%**`.
The staleness gate,
`tests/test_guards_and_contracts.py::test_generated_counts_file_matches_a_fresh_render`,
compares only lines beginning `- Pure domain modules`, `- Manuscript tokens`,
`- Figures`, or `|` — the two measured lines are excluded by construction,
because a bare regeneration legitimately omits them. So adding a single test
leaves `204` in a committed file with nothing able to notice. The numbers are
correct today (measured this session); the *gate* is the gap, not the values.
*Done:* either the committed measured lines are re-derived and compared by
something that runs on every gated run (e.g. the gate writes the count and the
test compares against the live collection count), or the measured lines are
dropped from the committed artifact and the file states the gate only.
*Demonstrate:* add a throwaway test, run
`uv run pytest tests/ --cov=src --cov-fail-under=90`, and observe a failure that
names `COUNTS.md`; remove the throwaway test and the suite is green again.

**V3 — 11 computed result tokens cannot be policed by the anti-hardcode scan.**
*(carried over from the audit — unresolved.)*
`tests/test_guards_and_contracts.py::_UNSCANNABLE_RESULT_TOKENS` enumerates
`GOLDFINGER_MODULE_COUNT`, `GOLDFINGER_FIGURE_COUNT`, `GOLDFINGER_TOKEN_COUNT`,
`VAULT_LAYER_COUNT`, `VAULT_ZONE_COUNT`, `VAULT_WEAK_PATH_EDGES`,
`VAULT_CRITICAL_EDGES` (bare small integers) and `MARKET_CONVERGED`,
`VAULT_VERDICT`, `VAULT_WEAKEST`, `LASER_SEVERITY` (category/boolean words).
Searching prose for `6` or `medium` returns false positives, not detections, so
no sound substring gate exists. The hole is pinned to the mechanical rule by
`test_unscannable_tokens_are_exactly_the_ones_the_rule_rejects` and disclosed in
`manuscript/03_results.md:91-102`, `manuscript/06_reproducibility.md`,
`docs/architecture.md:193-212`, and `AGENTS.md:74-83`. A hand-typed module count
in prose is still not caught.
*Done:* a gate that does not rely on substring search — e.g. rendering each
numbered section from its `{{TOKEN}}` source and diffing against the committed
prose, so *any* literal standing where a token should be is detected regardless
of its length or word-likeness. If that is judged not worth the machinery, the
honest close is to move this to Known limitations rather than leave it open.
*Demonstrate:* paste `6` in place of `{{GOLDFINGER_MODULE_COUNT}}` in
`manuscript/03_results.md` and see `uv run pytest tests/test_guards_and_contracts.py -v`
go red; restore the token and it goes green.

**V4 — counts of things outside this package have no producer and no gate.**
*(carried over from the audit — unresolved.)*
The prose formerly said "across the 27-film fleet". The number was accurate but
hand-authored: no token, no producer, no test. It was removed rather than
derived — `manuscript/01_introduction.md:56` now says the fleet's size is a
property of the fleet, and the prohibition is written into
`manuscript/AGENTS.md:21`, `AGENTS.md:82-83`, and
`docs/agent_instructions.md:60-61`. Deriving one would require this package to
read sibling packages or the suite roster, which its own scope rules forbid, so
the rule currently rests on doctrine and review.
*Done:* a lexical gate that rejects a fleet/sibling-package count reappearing in
`manuscript/` prose (a pattern check over number-plus-fleet-noun constructions
is feasible where a value check is not), with a positive control that pastes one
back in and sees it caught. If judged infeasible, close it by moving to Known
limitations with that reasoning stated.
*Demonstrate:* paste `across the 27-film fleet` into
`manuscript/01_introduction.md`, run `uv run pytest tests/ -k manuscript -v`,
expect a failure naming the offending phrase.

**V5 — the greedy hardening "lower bound" claim is disclaimed, not measured.**
`src/goldfinger/vault_threat_network.py:202-262` allocates budget greedily.
`manuscript/07_scope_and_related_work.md:31-35` states the allocation "is not
guaranteed optimal — it is reported as a lower bound on achievable effort lift",
and no test compares it to anything, so the gap between greedy and optimal is
unknown rather than bounded.
*Done:* an exhaustive allocation over the reference graph at a small budget,
asserting greedy ≤ exhaustive, with the observed gap reported (0 or otherwise)
so the manuscript can state a measured gap instead of a disclaimer.
*Demonstrate:* `uv run pytest tests/test_vault_threat_network.py -k optimal -v`.

### Documentation

**D1 — two doc call sites regenerate `COUNTS.md` without the measurement flags.**
`README.md:99` (`uv run python scripts/z_generate_counts.py   # docs/_generated/COUNTS.md`)
and `docs/AGENTS.md:54`
(`uv run python scripts/z_generate_counts.py   # if anything structural moved`)
show the bare invocation. Running it as written replaces the committed measured
lines with "not measured in this run" — proven by
`tests/test_guards_and_contracts.py::test_counts_document_reports_the_gate_when_nothing_was_measured`
against the committed file's current contents — silently downgrading a committed
artifact and leaving a dirty tree. `AGENTS.md:31`,
`docs/agent_instructions.md:93`, and `docs/testing_philosophy.md:106` all use the
correct `--tests <N> --coverage <PCT>` form.
*Done:* both sites carry the flagged form, or state explicitly that the bare form
drops the measurements.
*Demonstrate:* `rg -n "z_generate_counts.py" README.md docs/ AGENTS.md` shows no
bare invocation without an adjacent warning.

**D2 — stale example count in the counts-generator docstring.**
`scripts/z_generate_counts.py:13` shows
`uv run python scripts/z_generate_counts.py --tests 151 --coverage 100.0`. `151`
was this package's test count at phase 5 and reads as the current one; it is not.
*Done:* the docstring example uses placeholders (`--tests <N> --coverage <PCT>`)
like every other doc site, so no number in it can rot.
*Demonstrate:* `rg -n "tests 1[0-9][0-9]" scripts/` returns nothing.

### Extension

**E1 — quantise-free effective burn range.**
`src/goldfinger/laser_thermal.py:153-204` scans `0..max_distance` on a fixed
`step` grid (default 1.0 m), so the answer is quantised to that step and costs
`max_distance/step` melt-time evaluations. Melt time is monotone in distance, so
a bisection would be exact and cheaper.
*Done:* bisection replaces the scan, reproducing the current reference answer to
within the present step, and a test shows the result no longer moves when the
tolerance is tightened (the current implementation does move when `step`
changes). `manuscript/07_scope_and_related_work.md:44-46` — which states the
quantisation as a limitation — is updated in the same change.
*Demonstrate:* `uv run pytest tests/test_laser_thermal.py -k range -v`.

**E2 — second-generation currency-crisis variant.**
`src/goldfinger/reserve_attack.py` implements only the first-generation
(Flood–Garber) model, whose attack time is fully deterministic;
`manuscript/07_scope_and_related_work.md:17-23` states the omission. An
Obstfeld-style self-fulfilling variant would let the mission express the
multiple-equilibria case. Out of scope until the mission needs it — recorded so
the current single model is not mistaken for an oversight.
*Done:* a second module (or a second entry point) that reports more than one
equilibrium for a parameterisation where the first-generation model reports one,
with the scope paragraph and `99_references.md` updated.
*Demonstrate:* `uv run pytest tests/ -k equilibri -v`.

**E3 — provenance persistence via bond-utilities.**
`src/goldfinger/mission.py:369-374` constructs `bond_api.Provenance` inline and
persists nothing. `bond-utilities` already ships the persistence surface:
`record_provenance_outcome` at
`../bond-utilities/src/bond_utilities/mission_io.py:153`, with `save_record`,
`verify_provenance`, and `load_records` alongside. Blocked on bond-utilities
being converted at this level; taking the dependency now would put an I/O import
into the adapter ahead of the fleet.
*Done:* a GRAND SLAM record written under `output/data/` by
`record_provenance_outcome` and read back by `verify_provenance`, with the
concept core still importable without `bond-api` or `bond-utilities`.
*Demonstrate:* `uv run python scripts/execute.py && ls output/data/` shows the
record, and `uv run pytest tests/test_mission.py -v` stays green.

## Known limitations (not bugs)

- **Publisher metadata carries no DOI.** `CITATION.cff` and `.zenodo.json`
  declare none, because no DOI has been minted and no deposit exists: a
  fabricated DOI is worse than none. `codemeta.json` names the repository the
  package is actually pushed to (`github.com/docxology/bond-goldfinger`).
  `tests/test_package_metadata.py` asserts both facts — the declared repository
  is the real one, and no DOI is declared anywhere — so neither is an unfinished
  field. Populate a DOI only if a deposit is actually made.
- **`manuscript/config.yaml`'s `grand_slam:` block is a mirror, not a source.**
  No code path loads it; the module `REFERENCE_*` constants are the source of
  truth. The audit found this block described as "the single source of truth from
  which every value is injected", which was false. The claim was corrected rather
  than the mechanism inverted, and `tests/test_reference_intel.py` now pins the
  mirror to all six constants key-for-key (including the undirected zone graph)
  and requires the block to declare exactly the six sub-blocks — so it cannot
  drift, but it still is not what the code reads.
- **The anti-hardcode claim is scoped, not absolute.** The honest statement, now
  carried in `docs/architecture.md:193-212` and `manuscript/03_results.md:91-102`, is:
  *no **scannable** computed result value appears as a prose literal, and a
  per-token positive control proves each such value is detectable; hand-typed
  counts and category words remain unguarded by this scan.* The audit forced the
  softening; V3 is the open work to remove the caveat, and until it lands the
  scope above is the claim.
- **There is no `manuscript/config.yaml.example`.** One existed, was advertised
  as a "reference copy of the configurable surface", raised `ScannerError` on
  load, and declared a stale version. It was deleted rather than repaired;
  `tests/test_reference_intel.py::test_every_yaml_file_under_manuscript_parses`
  stops the class from returning.
- **Model scope boundaries are stated, not defects.** Constant-elasticity demand
  with no microstructure; linear first-generation crisis dynamics; independent
  vault layers; static, symmetric, fully-known intrusion graph; energy-balance
  laser with no plasma shielding or latent heat; semi-infinite-solid thermal
  model with temperature-independent properties. All enumerated in
  `manuscript/07_scope_and_related_work.md`. These are the modelling contract.
- **The mission records `wall_time_s=0.0`.** Deliberate: no wall-clock value may
  enter a persisted result, because it would make the outcome non-reproducible.
  Determinism beats instrumentation here.
- **Scope is exactly this directory.** Commits stay inside this repository; no
  sibling-package edits, no template-repo edits. The `mission.py` public surface and the `GADGETS`
  convention are frozen — the fleet consumes them (`AGENTS.md:56-64`).

## Verification

Run from the package root; read the output, not just the exit code.

```bash
uv sync --extra dev                                    # deps incl. the bond-api path dependency

uv run pytest tests/ --cov=src --cov-fail-under=90     # the gate
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/goldfinger scripts
rg -n "template[_]code_project" .                      # expect zero hits
```

Expected: every test passes with zero skips and zero failures; coverage on
`src/goldfinger/` is at or above the 90% line-and-branch floor (it currently sits
well above it — see [`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md));
ruff reports "All checks passed!" and all files already formatted; mypy reports
no issues; the lineage grep returns nothing.

After any structural change, regenerate the derived artifacts and confirm the
tree is clean:

```bash
uv run python scripts/z_generate_manuscript_variables.py       # tokens + figures
uv run python scripts/z_generate_counts.py --tests <N> --coverage <PCT>
git status
```

Pass the *measured* `<N>` and `<PCT>` from the gated run above — omitting them
rewrites `docs/_generated/COUNTS.md` to state the gate instead of the
measurement (see D1).

---

## Round-2 (2026-08-06)

Round-2 executed the pick-up-ready ledger items that still stood open on disk and
added one hostile-review hardening class. Verified state after this round:
**220 tests passed, 0 skipped, 0 failed; 100.00% line *and* branch coverage on
`src/goldfinger/`** (`uv run pytest tests/ --cov=src --cov-fail-under=90`);
`ruff check`, `ruff format --check`, and `mypy src/goldfinger scripts` all
clean; zero exemplar-lineage hits. (Do not restate those numbers elsewhere; cite
`docs/_generated/COUNTS.md`.)

### Resolved this round

- **C1 — `input_hash` is now a real fingerprint of the reference intel.**
  `mission.py` previously hardcoded `input_hash="goldfinger-grand-slam-input-v2"`.
  It now builds provenance through `bond_api.capabilities.derive_provenance`
  over the exact `REFERENCE_*` intel the `_*_intel()` helpers consume
  (`_provenance_inputs()`), so a one-value edit to any constant changes the
  hash and two runs with unchanged constants agree. The frozen surface (module
  path, class, `film`, five methods, `GADGETS`, hooks, `build_provider`) is
  untouched.
  *Tests:* `test_input_hash_is_sensitive_to_any_constant_edit` (positive
  control: perturb one constant, hash differs) and the strengthened
  `test_deterministic_provenance` in `tests/test_protocol_integration.py`.

- **C2 — `effective_burn_range` no longer returns a two-valued `0.0`.** The
  focus-only vs never-melts ambiguity (both read as a bare zero) is resolved:
  the function now returns a frozen `BurnRangeResult` carrying `burns_at_focus`
  alongside `range_m`. Both call sites (mission adapter, manuscript token map)
  read the explicit flag, so no caller needs a second melt-time call to
  interpret a `0.0` range.
  *Tests:* `test_burn_range_disambiguates_focus_only_from_never_melts` and the
  strengthened `test_effective_burn_range_is_interior_and_valid` / the
  never-melts guard in `tests/test_laser_thermal.py` and
  `tests/test_guards_and_contracts.py`.

  **Note:** E1 (bisection replacing the grid scan) was **not** executed as a
  separate step — the reference answer is a bounded monotone range already
  reproduced within the scan step, and the round prioritised the two-valued
  ambiguity (C2) which is the actual defect. The grid-scan quantisation record
  in this file's E1 entry stands as a limitation.

- **V2 — COUNTS.md measured lines are now gated, not exempt by construction.**
  The staleness test previously compared only the derived lines and skipped the
  measured `**N collected**` line. It now binds that line to the *live*
  collection count via a session-scoped `_live_test_count` fixture, so adding a
  test without regenerating COUNTS.md turns the gate red.
  *Tests:* `test_generated_counts_file_matches_a_fresh_render` (now live-bound)
  and `test_counts_gate_can_detect_a_stale_measured_count` (positive control).

- **V4 — a fleet/sibling-package count in the prose is now caught by a gate.**
  `tests/test_guards_and_contracts.py` regex-rejects digit bound to a
  fleet/suite/package/sibling noun (e.g. `27-film`, `33 packages`) in the
  rendered prose, with a positive control pasting one back and seeing it
  caught. The prose and `manuscript/06_reproducibility.md` were hardened so a
  release year like `1964 film` is the *only* digit-plus-noun construction —
  deliberately not a fleet count.

- **V5 — the hardening "lower bound" is now measured, not merely disclaimed.**
  `tests/test_vault_threat_network.py` adds an exhaustive enumeration over the
  reference graph at a small budget (`VAULT_VERIFY_BUDGET` = 3) showing the
  greedy allocation achieves the optimal lift (`VAULT_VERIFY_OPTIMAL_LIFT`,
  `VAULT_GREEDY_MATCHES_OPTIMAL`). Those values are computed by the pure core
  and injected as manuscript tokens, and `manuscript/03_results.md` and
  `manuscript/07_scope_and_related_work.md` now state the measured result.

- **D1/D2 — doc call sites and the stale docstring.**
  `README.md` and `docs/AGENTS.md` bare `z_generate_counts.py` invocations now
  carry the `--tests <N> --coverage <PCT>` form with a warning that the bare
  form drops the measured lines; `scripts/z_generate_counts.py`'s docstring
  example `--tests 151` was replaced with `<N>` placeholders. `rg -n
  "tests 1[0-9][0-9]" scripts/` returns nothing.

- **E3 — deterministic provenance persistence via bond-utilities.**
  `mission.py` now exposes `persist_grand_slam_record(outcome, path)`, which
  writes the outcome through `bond_utilities.mission_io.record_provenance_outcome`
  with a pinned, committed `started_at` (never the wall clock) and the same
  reference intel that produced the `input_hash`. `scripts/execute.py` writes
  it to `output/data/grand_slam_record.json`, and a test round-trips it through
  `bond_utilities.mission_io.verify_provenance` and asserts byte-determinism.
  `pyproject.toml` now declares the `bond-utilities` path dependency; the
  concept core still imports without it (`bond_utilities` is imported lazily in
  the adapter only).

### New finding, fixed and tested

- **Non-finite (NaN / inf) inputs were silently accepted by every module's
  `_positive` validator.** Because `value <= 0` is `False` for `NaN` and
  `+inf`, a NaN (or infinity) passed the "positive" guard and propagated
  through the computation into a NaN result. Every `_positive` /
  `_non_negative` / `_require_edge_cost` validator now rejects non-finite
  values with `math.isfinite`, so a NaN or `inf` input raises `ValueError` at
  the boundary instead of silently poisoning the output. This is exactly the
  "looks fine but is wrong at the edges" class this round was asked to hunt.
  *Tests:* six negative-control tests drive NaN/inf through
  `market_attack`, `reserve_attack`, `vault_threat_network`, `laser_physics`,
  and `laser_thermal` and assert the finite guard fires.

### Manuscript

- New `manuscript/08_uncertainty.md` — an honest limitation/uncertainty
  section bound entirely to live engine output: elasticity sensitivity of the
  corner gain, the `1/P` lever of burn-through, and the measured
  greedy-vs-optimal vault hardening gap. New derived tokens
  (`MARKET_GAIN_PCT_LOW_ELASTICITY`, `MARKET_GAIN_PCT_HIGH_ELASTICITY`,
  `LASER_BURN_DOUBLE_POWER_S`, `VAULT_VERIFY_*`) are computed in
  `manuscript_variables.py`, never hand-typed.
- `manuscript/03_results.md` and `07_scope_and_related_work.md` now state the
  measured hardening guarantee instead of a bare disclaimer;
  `manuscript/06_reproducibility.md` documents the new V4 fleet-count gate.

### Left for a future round

- **E1** (bisection for `effective_burn_range`) remains pending: the
  two-valued ambiguity (C2) is fixed, but the fixed-step scan still quantises
  the result. Low priority — the reference answer is stable within the step.
- **E2** (second-generation / Obstfeld currency-crisis variant) was not added;
  still out of scope until the mission needs the self-fulfilling case.
- **V3** (the 11 unscannable result tokens) stands as documented: exact-value
  substring policing of bare small integers and category words yields false
  positives, not detections. This round's V4 gate closes the *fleet-count*
  slice of that hole; the general case remains in Known limitations with the
  enumeration kept honest by `test_unscannable_tokens_are_exactly_the_ones_the_rule_rejects`.

## Workflowz review — 2026-11-10

No new actionable finding survives this bounded read-only review. Coverage: the root directives, README, existing TODO, the `.python-version` and `pyproject.toml` runtime/dependency declarations, package and figure exports, and the supplied excerpts of `laser_physics.py`, `vault_security.py`, and `reserve_attack.py`. The visible `_positive`/`_absorptivity`/`_rating` helpers and default mappings are input validation and reference data, not production mock/fallback substitutes; no keyword-only finding is proposed. The existing TODO already records open correctness, verification, and documentation work, but its cited mission, thermal, guard-test, and generated-count lines were not supplied here, so those items were not duplicated or treated as newly verified. The checked-in interpreter remains `3.14` while `requires-python` is `>=3.11`; no visible dependency or deployment constraint establishes a 3.15.2 migration, so no blind runtime task is added. Re-review on a concrete failure or a source change in the inspected modules/configuration; source excerpts outside this packet remain unreviewed.
