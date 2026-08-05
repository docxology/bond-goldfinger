# Scope and Related Work

## Scope

This work is a **quantitative modelling exercise** inspired by the *Goldfinger*
(1964) plot; it is not a physical market, monetary, or security assessment.
The scope boundary of each of the {{GOLDFINGER_MODULE_COUNT}} models is stated
below, because a model whose limits are unstated is a model whose numbers
cannot be trusted.

- **Market corner** (`market_attack`) assumes constant-elasticity demand and a
  single sterile supply shock. It abstracts away bid–ask microstructure,
  storage and carry costs, competing arbitrageurs, and policy responses; the
  closed-form jump is therefore an upper bound on what a real corner achieves
  against a market that observes the trader's own order flow [3]. It is
  deliberately closed-form and deterministic.
- **Speculative reserve attack** (`reserve_attack`) is the *linear*
  first-generation crisis model: perfect foresight, purchasing-power parity,
  uncovered interest parity, and exogenous exponential credit growth. It has no
  second-generation self-fulfilling multiple equilibria, no sterilisation
  policy, no risk premium, and no stochastic credit process. The attack time it
  reports is the deterministic one implied by those assumptions, not a
  forecast.
- **Vault — layered** (`vault_security`) treats layers as *independent* stops
  whose stopping probability equals their rating. Real security is correlated
  (one insider defeats several layers at once), adaptive, and human, and the
  ratings themselves are analyst inputs, so the composite score is an
  assessment aid rather than a measurement.
- **Vault — network** (`vault_threat_network`) models intrusion as a
  static shortest-path problem with additive, known, symmetric edge efforts.
  It has no detection/response dynamics, no intruder uncertainty about the
  graph, and no defender response during the intrusion. The hardening
  allocation is a *greedy* approximation to shortest-path improvement, which
  is not guaranteed optimal — it is reported as a lower bound on achievable
  effort lift.
- **Laser — scalar** (`laser_physics`) is a thermal energy-balance
  approximation. It neglects plasma shielding, radiative and convective
  losses, and latent heat of fusion, so burn-through times are
  order-of-magnitude threat estimates, not certified engineering values.
- **Laser — thermal** (`laser_thermal`) adds the beam optics and conduction
  the scalar model omits — Gaussian defocusing with range, and the
  semi-infinite-solid surface temperature under constant flux. It still
  assumes a semi-infinite solid (no back-face effects on a finite plate),
  temperature-independent material properties, constant absorptivity, and no
  atmospheric attenuation or thermal blooming along the path. Its effective
  burn range is scanned on a fixed grid, so it is quantised to the scan step.

These limitations are features for a mission-planning sandbox: they keep the
models auditable and replayable, and they make the numbers honest — each is a
clearly-stated approximation, not a fabricated precision.

## Related work

The models implement standard, well-understood literatures rather than novel
theory. Full citations are in `99_references.md`.

- **Market cornering and supply shocks.** The constant-elasticity
  inverse-demand and tâtonnement price-adjustment framework goes back to
  Walras [1] and Hicks [2]; Kyle [3] supplies the strategic-trader price-impact
  view that a closed-form corner deliberately abstracts away.
- **Currency crises and speculative attacks.** Krugman [4] introduced the
  first-generation balance-of-payments crisis; Flood and Garber [5] give the
  linear closed forms — shadow floating rate, attack time, and the gap to
  gradual reserve exhaustion — that `reserve_attack` implements directly.
- **Physical protection systems.** Garcia [6] is the standard treatment of
  layered physical protection, adversary sequence diagrams, and detection/delay
  path analysis; it underwrites both the weighted layer score and the decision
  to model the adversary's route as a weighted graph.
- **Network penetration and hardening.** Dijkstra [7] provides the
  shortest-path search; Israeli and Wood [8] formalise shortest-path
  interdiction and improvement, the problem the greedy budget allocation
  approximates.
- **Laser–material interaction.** Steen and Mazumder [9] give the
  continuous-wave energy-balance model; Carslaw and Jaeger [10] the
  constant-surface-flux conduction solution; Siegman [11] the Gaussian-beam
  propagation that sets the spot radius with range.

The contribution of this package is not new theory but a *disciplined,
testable, deterministic implementation* of these concepts as pure modules plus
a protocol-compliant mission adapter [12], reproducible end to end.
