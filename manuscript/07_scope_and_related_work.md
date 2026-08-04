# Scope and Related Work

## Scope

This work is a **quantitative modelling exercise** inspired by the *Goldfinger*
(1964) plot; it is not a physical market or security assessment. Scope
boundaries:

- The market model assumes constant-elasticity demand and a single sterile
  supply shock; it abstracts away bid–ask microstructure, storage costs,
  competing arbitrageurs, and policy responses. It is deliberately closed-form
  and deterministic.
- The vault model treats layers as independent stops with probabilities equal
  to their ratings; real security is correlated, adaptive, and human, and the
  ratings themselves are analyst inputs.
- The laser model is a thermal energy-balance approximation; it neglects
  plasma shielding, beam divergence over range, radiative losses, and phase
  change (latent heat), so burn-through times are order-of-magnitude threats,
  not certified engineering values.

These limitations are features for a mission-planning sandbox: they keep the
models auditable and replayable, and they make the numbers honest — each is a
clearly-stated approximation, not a fabricated precision.

## Related work

The models draw on standard, well-understood literatures rather than novel
theory:

- **Market cornering / supply shocks**: the constant-elasticity inverse-demand
  and tatonnement price-adjustment framework dates to the classical
  Walrasian adjustment literature; the cornering setting appears in commodity
  market analyses of hoarding and sterilization.
- **Defense-in-depth**: layered-security scoring and product-rule penetration
  probabilities are standard in risk analysis and vault/access-control
  engineering (sequential-independent-barrier models).
- **Laser material interaction**: the energy-balance (heat-load) burn-through
  approximation is the elementary continuous-wave model underlying laser
  cutting and drilling estimates.

The contribution of this package is not new theory but a *disciplined,
testable, deterministic implementation* of these three concepts as pure
modules plus a protocol-compliant mission adapter, reproducible end to end.
