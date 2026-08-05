# Introduction

The 1964 film *Goldfinger* dramatizes a plausibly dangerous scheme: corner the
gold market by destroying the floatable supply, strike a fortress vault, and
deploy an industrial laser as the coup de grâce. This report strips the drama
to its *quantitative skeleton* and builds the models a mission planner would
actually run — {{GOLDFINGER_MODULE_COUNT}} small, deterministic, well-tested
modules organised along three attack surfaces. Each surface carries one
closed-form model and one structural model that the closed form cannot
express.

## Macroeconomic attack

1. **Market cornering** (`market_attack`) — the economics of a deliberate
   supply shock. Removing a fraction of the floatable supply shifts the
   market-clearing price along a constant-elasticity demand curve, and a
   tâtonnement process traces how price converges to the new equilibrium.
2. **Speculative reserve attack** (`reserve_attack`) — the monetary front. The
   same accumulation is turned against the gold peg itself: under the
   first-generation crisis model, exponential domestic-credit growth drains
   the central bank's reserves and speculators collapse the peg the instant
   the shadow floating rate reaches parity. The corner raises the price; the
   attack breaks the institution that fixes it.

## Vault defense

3. **Layered assessment** (`vault_security`) — a Fort Knox-style
   defense-in-depth score. Concentric defensive layers are rated and weighted
   into a composite, and the sequential-penetration probability of an intruder
   is computed by the product rule over the traversal order.
4. **Network penetration and hardening** (`vault_threat_network`) — the
   structural front. Ratings measure how strong each layer is, but not which
   *route* an intruder takes. Treating the vault as a weighted zone graph, a
   shortest-path search finds the minimum-effort intrusion route (the film's
   secret tunnel), edge criticality identifies which zone transitions actually
   matter, and a greedy budget allocation raises the effort the intruder must
   pay.

## Laser threat

5. **Burn-through physics** (`laser_physics`) — an energy-balance model
   determining how long a beam of a given power takes to burn through a plate
   of a given material, plus its inverses for required power and maximum
   burnable thickness.
6. **Thermal engagement** (`laser_thermal`) — the spatio-temporal front. A
   Gaussian beam defocuses with range, so absorbed intensity falls; the
   Carslaw–Jaeger constant-flux solution converts that intensity into a
   surface melt time, and the two together bound the beam's effective
   engagement range within a threat window.

These {{GOLDFINGER_MODULE_COUNT}} modules are the *pure domain core*: they
depend only on the standard library and NumPy, contain no I/O, draw no random
numbers, and are trivially reproducible. Around them sits a thin mission
adapter that implements the frozen BOND-API protocol (the suite's canonical
`MissionProvider` contract), so the model set can be discovered, orchestrated,
and debriefed uniformly across the film fleet. (The fleet's size is a property
of the suite, not of this package; it is deliberately not stated here, because
this package can neither derive it nor gate it without reaching into sibling
packages. The suite roster is authoritative.) The adapter's public shape —
the film slug, the five lifecycle methods, and the module-level gadget
registry — is frozen across phases; only its internals deepen.

The design priorities are **determinism** (a declared seed of
{{GOLDFINGER_SEED}}, no random draws, no wall-clock dependence in persisted
results), **honesty** (real computation and real data throughout; no mocked
dependencies), and **measurability** (every headline number in this manuscript
is injected as one of {{GOLDFINGER_TOKEN_COUNT}} generated variables rather
than typed by hand — including the module count in this paragraph, which is
derived from the package directory rather than declared).
