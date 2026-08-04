# Methodology

The GRAND SLAM models each reduce one operational concept to a closed-form
relation and a deterministic iterative update. All three are pure functions of
their inputs.

## Market cornering: supply shock to price dynamics

Let $\mathcal{S}_0$ be the floatable supply clearing at a reference price
$P_0$. Cornering removes a fraction $f \in [0,1)$ of that supply, leaving the
effective supply

$$\mathcal{S}_\mathrm{eff} = \mathcal{S}_0 (1-f).$$

With constant-elasticity demand $Q_d(P) = k P^{-\eta}$ (elasticity
$\eta > 0$), market clearing pins the shocked equilibrium price to

$$P^* = P_0 \left(\frac{\mathcal{S}_0}{\mathcal{S}_\mathrm{eff}}\right)^{1/\eta}.$$

Price does not jump; it adjusts toward $P^*$ by a discrete tatonnement with
coefficient $\lambda \in (0,2)$,

$$P_{t+1} = P_t + \lambda\,(P^* - P_t),$$

which converges monotonically for $\lambda < 1$. The fractional corner gain is
$P^*/P_0 - 1$. For the reference intel ($f$ = {{MARKET_FRACTION_REMOVED}}%,
$\eta$ = {{MARKET_ELASTICITY}}, $P_0$ = ${{MARKET_REFERENCE_PRICE}}$) the gain
resolves to the results in Section [Results].

## Vault defense: layered security scoring

A vault is defended by $\ell$ concentric layers ranked
$\mathcal{L}_1, \dots, \mathcal{L}_\ell$. Each layer $i$ receives a rating
$r_i \in [0,1]$ (assessed strength) and a weight $w_i \ge 0$. The composite
defense-in-depth score is the weighted average

$$S = \frac{\sum_i r_i w_i}{\sum_i w_i} \in [0,1].$$

Under a sequential-penetration model an intruder must defeat layers in order;
if each layer stops the intruder with probability equal to its rating, the
overall breach probability is the product of the pass-through rates,

$$P_\mathrm{breach} = \prod_i (1 - r_i).$$

The expected time to breach (or stall) telescopes as
$E[T] = t \sum_i \prod_{j<i}(1-r_j)$ over the rated layers. Fortification
priority is ranked by the marginal composite gain of raising each layer by a
fixed $\delta$.

## Laser threat: burn-through time vs material and power

A continuous-wave laser of power $P$ focuses onto a spot of area $A$; the
target absorbs a fraction $a \in (0,1]$ of the beam. The material column under
the spot has mass $m = \rho A d$ (density $\rho$, thickness $d$); raising it
by $\Delta T$ (specific heat $c$) requires

$$Q = \rho A d c \Delta T.$$

Equating this to the absorbed power $P_\mathrm{abs} = a P$ gives the
burn-through time

$$t_\mathrm{burn} = \frac{\rho A d c \Delta T}{a P}.$$

The same relation inverts for required power and for maximum burnable
thickness, so any pair of (power, time, thickness) determines the third.
