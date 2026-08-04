# Introduction

The 1964 film *Goldfinger* dramatizes a plausibly dangerous scheme: corner
the gold market by destroying the floatable supply, strike a fortress vault,
and deploy an industrial laser as the coup de grâce. This report strips the
drama to its *quantitative skeleton* and builds the three specialised models a
mission planner would actually run, each as a small, deterministic,
well-tested module:

1. **Market cornering** (`market_attack`) — the economics of a deliberate
   supply shock. Removing a fraction of the floatable supply shifts the
   market-clearing price along a constant-elasticity demand curve, and a
   tatonnement process traces how price converges to the new equilibrium.
2. **Vault defense** (`vault_security`) — a Fort Knox-style layered
   assessment. Concentric defensive layers are scored and combined, and the
   sequential-penetration probability of an intruder is computed by the
   product rule of defense-in-depth.
3. **Laser threat** (`laser_physics`) — the physics of laser penetration. An
   energy-balance model determines how long a beam of a given power takes to
   burn through a plate of a given material.

These three modules are the *pure domain core*: they depend only on standard
types and NumPy, contain no I/O, draw no random numbers, and are trivially
reproducible. Around them sits a thin mission adapter that implements the
frozen BOND-API protocol (the suite's canonical `MissionProvider` contract),
so the model set can be discovered, orchestrated, and debriefed uniformly
across the 27-film fleet.

The design priorities are **determinism** (a fixed seed, no wall-clock
dependence in persisted results), **honesty** (real computation and real
data throughout; no mocked dependencies), and **measurability** (every
headline number in this manuscript is injected as a generated variable rather
than typed by hand).
