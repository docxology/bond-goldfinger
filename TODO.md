# goldfinger — TODO (GRAND SLAM)

Film package: Goldfinger (1964), mission codename GRAND SLAM. Local-only tree.

Only *open* work belongs in this file. Completed work is described in
[`README.md`](README.md) and [`docs/architecture.md`](docs/architecture.md);
current measured counts are in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md). Do not restate a
measured figure here — it will rot.

## Open — modelling

- [ ] **Disambiguate `effective_burn_range`'s `0.0` return.** It currently means
      either "melts only at focus" or "never melts within the window". The
      docstring says so and callers can disambiguate with
      `melt_time_at_distance(..., 0.0)`, but a richer return (a small result
      object carrying `burns_at_focus`) would remove the trap. Deferred because
      it changes a signature the mission adapter and figures both call.
- [ ] **Quantise-free effective burn range.** The range is found by scanning a
      fixed `step` grid, so the answer is quantised to that step. A bisection on
      the monotone melt-time-vs-distance curve would be exact and faster.
      Acceptance: same reference answer to within the current step, and a test
      showing the bisection result is step-independent.
- [ ] **Optimality gap for `harden_network`.** The greedy allocation is a lower
      bound on what the budget could buy; the manuscript says so. Adding an
      exact solve for small graphs (brute force over allocations) would let the
      package report the actual gap instead of only disclaiming it.
      Acceptance: a test comparing greedy against exhaustive on the reference
      graph at a small budget.
- [ ] **Second-generation currency-crisis variant.** `reserve_attack` implements
      only the first-generation (Flood–Garber) model, whose attack time is fully
      deterministic. An Obstfeld-style self-fulfilling variant would let the
      mission express the multiple-equilibria case. Out of scope until the
      package needs it; noted so the current limitation is not mistaken for an
      oversight.

## Open — packaging and integration

- [ ] **Provenance persistence via bond-utilities.** Outcome provenance uses
      `bond_api.Provenance` directly. A later phase may delegate persistence to
      `bond_utilities.mission_io.record_provenance_outcome` once bond-utilities
      is converted at this level. Acceptance: `record_provenance_outcome` writes
      a GRAND SLAM record under `output/data/`.
- [ ] **Publisher metadata.** `CITATION.cff`, `.zenodo.json`, and
      `codemeta.json` are prose-grade and deliberately omit DOIs and repository
      URLs, because this is a local-only tree with no remote and a fabricated
      DOI would be worse than none. Populate real values only if a publication
      target is authorised.
- [ ] **`COUNTS.md` measured lines.** The committed file states the enforced
      gate rather than a measured test count, because no automation reruns the
      gate on commit. `scripts/z_generate_counts.py --tests N --coverage PCT`
      fills those lines when a gated run supplies real numbers; wiring that into
      a pre-commit step would let the file carry measurements safely.

## Not in scope

- No remote push, no sibling-package changes, no template-repo changes.
- No change to the frozen `mission.py` public surface or the `GADGETS`
  convention — the fleet consumes them (see [`AGENTS.md`](AGENTS.md)).
