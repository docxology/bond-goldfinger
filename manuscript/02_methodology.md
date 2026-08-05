# Methodology

The GRAND SLAM models each reduce one operational concept to a closed-form
relation and a deterministic iterative update. All {{GOLDFINGER_MODULE_COUNT}}
are pure functions of their inputs — no I/O, no random draws, no wall-clock
dependence. The three attack surfaces are presented in pairs: the closed-form
model first, then the structural model that captures what the closed form
cannot.

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
$P^*/P_0 - 1$. Because the trajectory approaches $P^*$ geometrically and
attains it only in the limit, convergence is reported as the relative residual
$|P_n - P^*|/P^*$ tested against a tolerance
({{MARKET_CONVERGENCE_TOLERANCE}}), never by exact float equality. For the
reference intel ($f$ = {{MARKET_FRACTION_REMOVED}}%, $\eta$ =
{{MARKET_ELASTICITY}}, $P_0$ = ${{MARKET_REFERENCE_PRICE}}$) the gain resolves
to the results in Section [Results].

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

## Macroeconomic attack: speculative attack on the gold peg

The phase-4 deepening adds the monetary-system front. Money demand is linear
in the interest rate, $m_t - p_t = -\alpha i_t$; purchasing-power parity and
uncovered interest parity link the price level and interest rate to the
exchange rate. With domestic credit growing exponentially,
$D_t = D_0 e^{\mu t}$, the fixed peg forces reserves to drain,

$$R_t = (\bar{S} - \alpha i^\ast) - D_0 e^{\mu t},$$

while the rational-expectations **shadow floating rate** (the rate that would
prevail once reserves are gone) is

$$\tilde{s}_t = \frac{D_0 e^{\mu t}}{1 - \alpha\mu} + \alpha i^\ast.$$

Under perfect foresight speculators attack exactly when the shadow rate
crosses the fixed parity, at

$$t^\ast = \frac{1}{\mu}\ln\frac{(1-\alpha\mu)(\bar{S} - \alpha i^\ast)}{D_0},$$

which precedes the gradual reserve-exhaustion time
$t_B = (1/\mu)\ln((\bar{S}-\alpha i^\ast)/D_0)$ — the attack is sudden. The
post-float depreciation is the shadow rate at $t_B$ relative to parity.

## Network vault defense: penetration and hardening

The layered ratings in the previous section measure *strength*; the network
model treats the vault as an undirected weighted graph of zones with
intrusion-effort edges. The intruder's **minimum-effort path** (Dijkstra) from
the perimeter to the gold chamber, and the **edge criticality** (how much
removing each edge raises that minimum), capture where the vault is truly weak
— here the secret tunnel. Given a hardening budget, a greedy marginal-gain
allocation raises the edge whose lift most increases the minimum path,
``gain_per_unit`` per unit, until the budget is spent, maximising the effort
an intruder must pay.

## Laser thermal engagement: beam focus and heat conduction

The scalar burn-through model ignores beam divergence and conduction. A
Gaussian beam of waist $w_0$ and wavelength $\lambda$ has Rayleigh range
$z_R = \pi w_0^2/\lambda$ and spot radius
$w(z) = w_0\sqrt{1+(z/z_R)^2}$, so absorbed intensity
$I_a = a P/(\pi w^2)$ falls with range. Under constant flux the surface heats
by the Carslaw–Jaeger law,

$$T(0,t) = T_\mathrm{amb} + \frac{2 I_a}{\sqrt{\pi k\rho c}}\sqrt{t},$$

giving the melt time $t_\mathrm{melt} = \frac{\pi}{4}\frac{k\rho c
\,(T_\mathrm{melt}-T_\mathrm{amb})^2}{I_a^2}$. The **effective burn range** is
the greatest distance at which the defocused beam still melts the target
within a threat window.

