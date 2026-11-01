# A format-aware oracle can strictly require multiple reading depths

## Statement and scope

Use exactly the preceding stage's unknown-extraction, known-source model. A root has a persistent binary report, correct with probability r. Conditional on that report, extractions have accuracy p or q according to the format. Each completed block is fixed before its responses, serves one fact, and costs c plus its number of reads. The oracle knows the better format but **does not know p,q**. Two labelled calibration streams have first-order length M/log(1/delta) tending to alpha. All coefficients below concern expected **online** cost; the common already-acquired calibration resource is excluded.

**Proposition (strict necessity of depth mixing).** There is an admissible instance with one fact and all 27 format-composition actions of depths one through six such that every oracle-optimal allocation uses at least two distinct depths. This holds even though a feasible allocation witnessing the separation uses only the good format.

Specifically, set

\[
r=3/5,\quad p=19/20,\quad q=3/5,\quad\eta=1/40,
\quad\alpha=1,\quad d=1,\quad c=\ell=1,\quad L_{\max}=6.
\]

Let K_or be the unrestricted oracle coefficient, and K_L the coefficient when **all blocks have total depth L**, allowing any mixture of pure-good, pure-bad and mixed-format blocks at that depth. Then

\[
32.9477982818\ldots\ \le K_{\rm or}\le34
<41.3\le\min_{1\le L\le6}K_L.
\tag{1}
\]

The displayed left endpoint abbreviates the exact rational/log-interval bound stored in `DEPTH_MIXING_CERTIFICATE.json`; it is not an exact optimum. Thus every fixed-depth restriction costs at least 413/340 times the full optimum. The feasible mixed-depth design already reduces the coefficient by at least 73/413 (about 17.68%) relative to every fixed-depth design. These are controlled-model asymptotic coefficients, not finite-budget empirical performance numbers.

## Full source-block observation law

For action (a,b), the observed positive counts (s,t) have true law

\[
P^{+;a,b}_{p,q}(s,t)=\binom as\binom bt
\big[r p^s(1-p)^{a-s}q^t(1-q)^{b-t}
 +(1-r)(1-p)^s p^{a-s}(1-q)^t q^{b-t}\big].
\]

The opposite-truth law P^- replaces r by 1-r. The oracle alternative uses ordered extraction rates 1/2 <= v <= u <= 39/40 and the same known format assignment. Its calibration KL is

\[
C(u,v)=\operatorname{kl}(p,u)+\operatorname{kl}(q,v).
\]

For this one-fact model the exact information program is

\[
\min_{x\ge0}\sum_{a,b}(1+a+b)x_{a,b},\qquad
C(u,v)+\sum_{a,b}x_{a,b}D(P^{+;a,b}_{p,q}\Vert P^{-;a,b}_{u,v})\ge1
\quad\forall(u,v).
\tag{2}
\]

The prior expected-cost theorem supplies its operational meaning. The present proof establishes structure of (2), without assuming that pure-good actions are optimal.

## Feasible mixed-depth upper bound

Choose x_(1,0)=14 and x_(2,0)=2, with all other counts zero. Its cost is 2(14)+3(2)=34. Pure-good online laws do not depend on v, so minimizing calibration over v gives v=min(q,u) exactly. It remains to show

\[
f(u)=\operatorname{kl}(p,u)+\operatorname{kl}(q,\min(q,u))
+14D(P^{+;1,0}_{p,q}\Vert P^{-;1,0}_{u,u})
+2D(P^{+;2,0}_{p,q}\Vert P^{-;2,0}_{u,u})\ge1
\tag{3}
\]

for **every** u in [1/2,39/40]. The verifier partitions this entire interval into 950 cells of width 1/2000. It evaluates f at each midpoint using exact rational probabilities and rigorous logarithm intervals; it evaluates f' exactly as a rational number.

Here is a global curvature bound. For a binomial component Q of depth L, |Q'/Q| <= L/eta and |Q''/Q| <= L(L-1)/eta^2. These bounds also hold for the corresponding source mixture, by weighting the component scores by their posterior weights. Hence

\[
|\partial_u^2\log Q|\le L(2L-1)/\eta^2.
\]

Each raw calibration KL has second derivative at most 1/eta^2. The profiled second stream is constant above q and has derivative zero at q; its first derivative is continuous, so the same Taylor bound remains valid across the join. Consequently f' is globally Lipschitz with constant

\[
B=[2+14(1)(1)+2(2)(3)]/\eta^2=44800.
\]

If u_0 is a cell midpoint and h=1/4000, throughout its cell

\[
f(u)\ge f(u_0)-|f'(u_0)|h-Bh^2/2.
\]

The smallest certified lower bound exceeds 1.0285716211. This proves continuous feasibility; no convexity or finite-grid extrapolation is assumed.

## Exclude every fixed depth, including all format mixtures

For any fixed alternative, any nonnegative multiplier y satisfying

\[
y D(P^{+;a,b}_{p,q}\Vert P^{-;a,b}_{u,v})\le1+a+b
\]

for every allowed action implies the lower bound y[1-C(u,v)] on its information-program cost. This is just multiplying one valid constraint and applying the action-wise inequalities; the alternative need not be least favorable.

For L=1, take u=v=1/2 and y=100. This closure point is a limit of admissible strict alternatives, so continuity justifies its constraint. Both depth-one action inequalities are strict, with minimum slack above .37113. The resulting lower bound exceeds 48.52325.

For each L=2,...,6, take (u,v)=(p,q) and y=413/10. Calibration KL is then zero. Exact interval arithmetic verifies the inequalities for **all L+1 format compositions**, with smallest slack above .0028817. Therefore K_L >=41.3 at every such depth. Across the six comparisons every one of the 27 actions is checked.

These lower bounds allow arbitrary mixtures of formats across roots as long as total depth stays fixed. They therefore exclude a stronger comparator than a single pure-good action. With d=1, there is also no ambiguity about assigning different fixed depths to different facts.

The full program attains its optimum: it has a finite feasible allocation, finitely many actions of positive cost, and closed continuous constraints. Its bounded cost sublevels are compact. Since all one-depth allocations cost at least 41.3 while a feasible two-depth allocation costs 34, **every full optimum has at least two depths**.

For the optional full-menu lower bound, use (u,v)=(73/80,3/5) and y=3329/100. The same exact inequalities hold for all 27 actions, with minimum slack above .0004732, giving the left bound in (1).

## Why depth has an additional purpose when extraction rates are unknown

For two same-format extractions of one root,

\[
\Pr(Y_1=Y_2)=p^2+(1-p)^2.
\]

This depends on extraction accuracy but not on the truth or source accuracy. Repeated extraction therefore supplies information about the observation channel, in addition to information about the fact. Independent roots provide additional independent source reports. The certified instance requires balancing those two kinds of information.

For contrast, revealing p,q in this **same instance** makes the unique cost-optimal action pure-good depth one; the verifier compares its known-rate truth KL per cost against all other 26 actions. Finite calibration changes the optimal depth structure, rather than merely rescaling a known-rate coefficient. The mixed-depth witness is not asserted to be the exact optimal allocation, and the agreement identity alone is not a proof of its optimality.

## Consequences and non-consequences

1. A universal rule “select one optimal oracle depth and substitute it into the sharing threshold” is false under unknown extraction rates and finite calibration.
2. This result does **not** refute pure-good-format optimality. Both depths of the feasible witness use the good format, and the full optimum might do so as well.
3. It does **not** rule out every scalar smallest-group criterion. Such a reduction must be derived for the appropriate optimal depth-profile set; a selected-depth plug-in is insufficient.
4. The exact oracle-optimal-set feasibility condition from the previous stage remains valid. Any later algorithm must retain depth allocation unless a rigorously stated restriction makes a simpler oracle sufficient.
5. Multiple-action optimal design is established generally; the contribution here is a specific persistent-source counterexample with continuous-parameter bounds and a strict setup-cost comparison. Priority and empirical Web validity are not established by this proof.

`certify_depth_mixing.py` is a standalone verifier within the repository and writes its structured certificate. Its read-only logarithm helper is hash-bound to the previous stage. All search results remain separately labelled discovery relaxations.
