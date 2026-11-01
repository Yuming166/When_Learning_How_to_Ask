# Independent adversarial audit: source cost and format sharing

Date: 2026-10-31. Scope is exactly `MODEL_AND_SCOPE.md`: known fixed \(r,p,q\), a finite completed-block menu, no root revisits or within-block adaptation, and roots purchased separately for individual facts. The earlier `web_native_theory_20261031` snapshot was not edited. This report contains mathematical proofs and deterministic finite checks; no empirical worlds, model calls, training, or confirmation experiments were used.

**Verdict.** The proposed oracle-threshold equivalence is valid, including tied optimal depths. The maximum over the entire set of oracle-optimal depths is essential. Finite source-depth caps can preserve a strictly positive relative premium even when source activation cost tends to infinity. Conversely, for every fixed interior \(r\) and \(p>q\), a sufficiently large *finite* cap permits zero leading-order premium for singleton groups at sufficiently large but finite activation cost. The numerical threshold quantity is not universally monotone in depth or source cost; a rigorous interval-certified counterexample appears below. Monotonicity of the integer minimum sharing-group size is not established or refuted here.

## 1. Notation and the finite-action information program

For a pure block of length \(L\), let
\[
 P_{a,L}^{+}(s)=\binom Ls\{r a^s(1-a)^{L-s}+(1-r)(1-a)^s a^{L-s}\},
 \qquad P_{a,L}^{-}(s)=P_{a,L}^{+}(L-s).
\]
The count is sufficient. Define
\[
 A_L=D(P_{p,L}^{+}\Vert P_{p,L}^{-}),\quad
 U_L=D(P_{p,L}^{+}\Vert P_{q,L}^{+}),\quad
 V_L=D(P_{p,L}^{+}\Vert P_{q,L}^{-}),
\]
\[
 I(c)=\max_{1\le L\le L_{\max}}\frac{A_L}{c+\ell L},
 \qquad
 \mathcal M(c)=\mathop{\rm argmax}_{1\le L\le L_{\max}}
                \frac{A_L}{c+\ell L}.
\]

For a true state \(h=(\theta,z)\), the cost-weighted finite-action information program is
\[
 K(h;c)=\min_{x\ge0}\sum_e(c+\ell L_e)x_e
 \quad\text{subject to}\quad
 \sum_e x_e D(P_h^e\Vert P_{h'}^e)\ge1
 \quad\text{for every }h'\text{ with }\theta'\ne\theta.
\]
All mixed blocks are included among the actions \(e\). This report proves the exact comparison of this program with its oracle counterpart. Interpreting its value as an optimal leading expected-cost coefficient additionally requires the finite-action sequential-design achievability argument. That argument is standard in this known-level finite-state identifiable model, but should still be stated in the main theory rather than hidden inside the algebra below.

The program is feasible: querying both formats separates every pair of distinct states, including \(q=1/2\). It attains its optimum because every action cost is positive and a feasible bounded cost sublevel is compact. Thus if the oracle optimum is unattainable by the unknown-format program, the inequality of optimal values is strict, not merely an absent optimizer with equal infima.

## 2. Strict dominance of every finite block containing bad-format queries

**Lemma 1.** At a fixed finite total depth \(L\), the pure-good block has strictly larger truth-flip KL than every block containing at least one bad-format query.

**Proof.** Start with \(L\) independent conditional-on-root extractions of accuracy \(p\). Each query designated as bad can be independently passed through an additional binary symmetric channel with correctness
\[
 \gamma=\frac{1+(2q-1)/(2p-1)}2\in[1/2,1).
\]
The resulting accuracy is exactly \(q\). Thus the mixed block is a truth-independent stochastic postprocessing of the pure-good block, so KL cannot increase.

Strictness is important. All original vector outcomes have positive probability, because \(r,p\) are interior. The pure-good likelihood ratio is strictly increasing in the total number of positive extractions. At least one coordinate is passed through a channel with positive flip probability, so some output has positive probability from original vectors differing in that coordinate and therefore having different likelihood ratios. The equality condition for KL data processing fails. Observing the format-specific counts loses no additional likelihood information: permutations within either format leave the mixed-block likelihood unchanged. Hence the comparison applies to the actual recorded observations, not merely to an artificially richer vector observation. This also covers a pure-bad block and \(q=1/2\).

Consequently the oracle uses only pure-good blocks, and its optimal cost coefficient is
\[
 K_{\rm or}(c)=\frac d{I(c)}.
\]
Every oracle-optimal allocation, and only such allocations, has support on pure-good depths in \(\mathcal M(c)\) and obeys
\[
 \sum_{L\in\mathcal M(c)}x_{j,L}A_L=1
 \quad\text{for each fact }j.
\tag{OF}
\]
To see necessity directly, the alternative flipping fact \(j\) alone requires at least one unit of truth KL for that fact. The rate of any action is at most \(I(c)\). Equality in the resulting summed lower bound requires equality for every fact and requires every positive-weight action to attain the best rate. Strict mixed-block dominance leaves exactly the support described in (OF).

## 3. Ordering of the two type-flip divergences

**Lemma 2.** \(U_L>0\), and \(V_L\ge U_L\) for every finite \(L\ge1\). The latter inequality is strict if \(q>1/2\), and an equality if \(q=1/2\).

Positivity of \(U_L\) follows because the two distributions have different means when \(p>q\) and \(r>1/2\). For the second claim, let
\[
 f(s)=\log\frac{P_{q,L}^{+}(s)}{P_{q,L}^{-}(s)}.
\]
Then \(f(L-s)=-f(s)\), and when \(q>1/2\), \(f(s)>0\) for \(s>L/2\). Moreover
\[
 P_{p,L}^{+}(s)-P_{p,L}^{+}(L-s)
 =(2r-1)\binom Ls
 \{p^s(1-p)^{L-s}-(1-p)^s p^{L-s}\}>0
\]
for \(s>L/2\). Pairing reflected terms gives
\[
 V_L-U_L
 =\sum_{s>L/2}
  \{P_{p,L}^{+}(s)-P_{p,L}^{+}(L-s)\}f(s)>0.
\]
If \(q=1/2\), the two \(q\)-laws coincide, so \(V_L=U_L\).

This lemma justifies reducing a type-flipped group's truth errors to a single flipped fact. Without it, the reduction would have an unproved hole.

## 4. Complete oracle-face criterion, including ties

Define
\[
 \Gamma_{k,L}=\frac{V_L+(k-1)U_L}{A_L}.
\]

**Theorem.** In the specified finite-menu model,
\[
 \boxed{K(h;c)=K_{\rm or}(c)
 \quad\Longleftrightarrow\quad
 \max_{L\in\mathcal M(c)}\Gamma_{k_{\min},L}\ge1.}
\]

**Proof, reduction of all alternatives.** On an oracle-optimal allocation, a group whose type is unchanged supplies exactly one unit of KL for each fact whose truth is flipped, by (OF). Such an alternative is already separated if it flips at least one fact in any unchanged-type group.

For a group \(g\) of size \(k\) whose type is flipped, a fact with unchanged truth contributes \(U_L\), and a fact with flipped truth contributes \(V_L\), at true pure-good depth \(L\). Since \(V_L\ge U_L\), among truth-changing alternatives for this group it suffices to check each possible single flipped fact \(j\):
\[
 \sum_{i\in S_g}\sum_L x_{i,L}U_L
 +\sum_L x_{j,L}(V_L-U_L)\ge1.
\tag{G_j}
\]
Additional truth flips cannot reduce the divergence. Type changes in other groups add nonnegative divergence. Conversely, the alternative changing only this group's type and fact \(j\)'s truth is allowed, so every constraint \((G_j)\) is necessary. These checks therefore cover *all* wrong-truth alternatives, not just a selected subset.

Set \(y_{i,L}=x_{i,L}A_L\). For each fact, \(y_{i,L}\ge0\) and \(\sum_L y_{i,L}=1\). Averaging the \(k\) constraints \((G_j)\) yields
\[
 \frac1k\sum_{i\in S_g}\sum_{L\in\mathcal M(c)}
 y_{i,L}\Gamma_{k,L}\ge1.
\]
The left side is a convex combination of \(\Gamma_{k,L}\). Hence a necessary condition for feasibility on the oracle face is
\(\max_{L\in\mathcal M(c)}\Gamma_{k,L}\ge1\).

For sufficiency, choose a maximizing depth \(L_g\) in the tied oracle set and give every fact in the group \(x_{j,L_g}=1/A_{L_g}\). This satisfies (OF), and every \((G_j)\) becomes \(\Gamma_{k,L_g}\ge1\). More generally, symmetrizing any oracle-face allocation over permutations of the group's facts gives a common depth mixture, with its criterion equal to a convex average of the same \(\Gamma\)'s. Thus mixtures cannot do better than the largest tied value for existence of a feasible oracle allocation.

Finally, \(U_L\ge0\) makes \(\Gamma_{k,L}\) nondecreasing in the group size \(k\). Therefore the smallest group is the binding existence condition across groups. A maximizing depth for the smallest group can itself be used in every larger group. Compact attainment of both finite programs turns absence of a feasible oracle-face allocation into strict \(K>K_{\rm or}\). This proves both directions.

**Tie interpretation.** The maximum means that *some* oracle-optimal allocation also solves the unknown-format problem. It does not license an arbitrary oracle tie break. Other tied allocations can fail the nuisance-type constraints. A theorem about every chosen oracle optimizer would need the corresponding minimum, or an explicit allocation-selection rule. Ties must be represented before examining outcomes.

For a unique optimal depth, the criterion reduces to the proposed \(\Gamma_{k_{\min},L_*}\ge1\). At a fixed depth, the smallest integer group size is
\[
 k_{\rm req}(L)=\max\left\{1,
 \left\lceil1+\frac{A_L-V_L}{U_L}\right\rceil\right\},
\]
with exact comparisons at integer boundaries. This is valid since \(U_L>0\).

## 5. Source cost, depth caps, and eventual singleton equality

For every interior \(r,p\), \(A_L\) is strictly increasing in \(L\) and tends to
\[
 \kappa(r)=\operatorname{kl}(r,1-r).
\]
Strictness follows from the positive conditional KL of the next extraction after every finite history: the two truth hypotheses induce different posterior probabilities for the root sign, and \(p>1/2\). Convergence follows because increasingly many extractions recover the root sign, while root data processing is an upper bound.

For a fixed cap \(H=L_{\max}\), define
\[
 C_H=\max\left\{0,
 \max_{1\le L<H}
 \ell\frac{H A_L-L A_H}{A_H-A_L}\right\}.
\]
The inner maximum is empty for \(H=1\). For \(c>C_H\), the cap \(H\) is the unique oracle-optimal depth. This follows by cross-multiplying each comparison \(A_H/(c+\ell H)>A_L/(c+\ell L)\). In particular:

- If \(\Gamma_{k_{\min},H}\ge1\), then every sufficiently large **finite** activation cost has zero first-order premium.
- If \(\Gamma_{k_{\min},H}<1\), then every sufficiently large activation cost still has a strictly positive premium. Raising cost cannot overcome a failed fixed cap.

The failed-cap conclusion is stronger than lack of exact equality. Divide all LP costs by \(c\). Their coefficients converge to 1 as \(c\to\infty\). Since the menu is finite, positive objective coefficients give bounded sublevel sets, and the optimal values converge to those of the unit-cost-per-block programs. In that limit the oracle uniquely uses pure-good cap-depth blocks: smaller depths have lower \(A_L\), and every mixed block is strictly dominated. The same oracle-face theorem therefore gives
\[
 \Gamma_{k_{\min},H}<1
 \quad\Longrightarrow\quad
 \lim_{c\to\infty}\frac{K(h;c)}{K_{\rm or}(c)}>1.
\]

Nevertheless, a sufficiently large finite cap can always remove this obstruction for fixed \(r<1,p>q\). Here is a direct proof. Let \(\Delta=p-q>0\), take \(\varepsilon=\Delta/3\), and let \(T_L\) mean that the empirical positive fraction is within \(\varepsilon\) of either \(p\) or \(1-p\). Then
\[
 P_{p,L}^{+}(T_L)\ge1-2e^{-2L\varepsilon^2},
 \qquad
 P_{q,L}^{+}(T_L)\le2e^{-2L(\Delta-\varepsilon)^2}.
\]
Both inequalities follow by conditioning on the latent root and applying the elementary Bernoulli concentration bound. The two possible \(q\)-means are at least \(\Delta\) from both relevant \(p\)-clusters; this uses \(q\ge1/2\). Binary data processing and the entropy bound yield
\[
 U_L\ge P_{p,L}^{+}(T_L)
       \{2L(\Delta-\varepsilon)^2-\log2\}-\log2
 \longrightarrow\infty.
\]
Since \(V_L\ge U_L\) and \(A_L\le\kappa(r)<\infty\),
\[
 \Gamma_{1,L}=V_L/A_L\longrightarrow\infty.
\]
Thus one can choose a finite cap \(H\) with \(\Gamma_{1,H}\ge1\), fix it before inference, and then choose finite \(c>C_H\). Even singleton groups have \(K=K_{\rm or}\) in this model. This is a finite-cap, finite-cost statement about the leading \(\log(1/\delta)\) coefficient, not equality of finite-\(\delta\) expected costs.

The phenomenon relies on extracting two kinds of information from one source block: factual information saturates at \(\kappa(r)\), but distinguishing extraction levels \(p\) and \(q\) continues to accumulate. A truth-plus-type alternative may therefore become easier to reject than the same-type truth alternative. It is incorrect to assume \(V_L<A_L\) at all depths merely because that inequality holds for one extraction.

## 6. A certified counterexample to monotonicity of Gamma

The oracle's optimal depth is nondecreasing with activation cost: for \(L_2>L_1\), the comparison of their information rates has the sign of
\[
 c(A_{L_2}-A_{L_1})
 +\ell(L_1 A_{L_2}-L_2 A_{L_1}),
\]
which is strictly increasing in \(c\). This single-crossing fact does **not** imply that the selected \(\Gamma\) is nondecreasing.

Take exactly
\[
 r=17/20,\qquad p=39/40,\qquad q=487/500,
 \qquad \ell=1,\quad L_{\max}=3.
\]
At \(c=15\), the unique oracle depth is 2; at \(c=25\), it is 3. The relevant values are

| Quantity | Depth 2 | Depth 3 |
|---|---:|---:|
| \(A_L\) | 1.15111391951971585741661483214445 | 1.20330561853915199133693412465928 |
| \(U_L\) | 0.0000379174470647140220224859688940 | 0.0000585334545010919150735522067654 |
| \(V_L\) | 1.15095143421249850847383011294691 | 1.20311274244173868100517234493657 |
| \(\Gamma_{1,L}\) | 0.999858845154713146569694156783099 | 0.999839711462789089672698566961365 |
| \(\Gamma_{2,L}\) | 0.999891784941489884079107152911405 | 0.999888355343112820921272075238886 |

Thus both \(\Gamma_1\) and \(\Gamma_2\) decrease as the oracle moves from depth 2 to 3. This refutes universal monotonicity of these quantities with either depth or cost. It does **not** refute monotonicity of the integer minimum sharing-group threshold or the yes/no equality indicator: in this example \(k_{\rm req}\) changes from 6 to 5.

The executable `certified_counterexample.py` and its generated `certified_counterexample.json` retain the exact-rational check, numerical displays, and source hash. The executable completed with `PASS_EXACT_RATIONAL_INTERVAL_CERTIFICATE`. The equivalent standalone standard-library calculation below certifies the signs with exact rational intervals. It uses
\(\log x=2\sum_{j\ge0}z^{2j+1}/(2j+1)\), \(z=(x-1)/(x+1)\), and bounds the positive tail by its geometric envelope. All comparisons in the assertions are exact rational comparisons; floating point is used only to display a lower bound after certification. This calculation was executed successfully.

```python
from fractions import Fraction as F
from math import comb

def log_bounds(x, n=80):
    if x < 1:
        lo, hi = log_bounds(1 / x, n)
        return -hi, -lo
    z = (x - 1) / (x + 1)
    z2, power, lo = z * z, z, F(0)
    for j in range(n):
        lo += 2 * power / (2 * j + 1)
        power *= z2
    hi = lo + 2 * power / ((2 * n + 1) * (1 - z2))
    return lo, hi

def kl_bounds(P, Q):
    lo = hi = F(0)
    for p, q in zip(P, Q):
        a, b = log_bounds(p / q)
        lo += p * a
        hi += p * b
    return lo, hi

r, p, q = F(17, 20), F(39, 40), F(487, 500)
def law(L, a):
    return [comb(L, i) * (r * a**i * (1-a)**(L-i)
            + (1-r) * (1-a)**i * a**(L-i))
            for i in range(L + 1)]

bounds = {}
for L in (1, 2, 3):
    P, Q = law(L, p), law(L, q)
    bounds[L] = (kl_bounds(P, P[::-1]),
                 kl_bounds(P, Q), kl_bounds(P, Q[::-1]))

def gamma_bounds(L, k):
    A, U, V = bounds[L]
    return ((V[0] + (k-1)*U[0]) / A[1],
            (V[1] + (k-1)*U[1]) / A[0])

for k in (1, 2):
    old, new = gamma_bounds(2, k), gamma_bounds(3, k)
    assert old[0] > new[1]
    print(k, float(old[0] - new[1]))
# Positive certified margins: 1.9133691924056897e-5, 3.429598377063158e-6.

for c, chosen in ((15, 2), (25, 3)):
    lower = bounds[chosen][0][0] / (c + chosen)
    assert all(lower > bounds[L][0][1] / (c + L)
               for L in (1, 2, 3) if L != chosen)
```

No broader numerical search is used as proof of a monotonicity statement. The interval counterexample establishes exactly the two failures claimed above.

## 7. Boundary cases and failure modes

- **\(q=1/2\):** \(V_L=U_L\); the group condition becomes \(kU_L/A_L\ge1\). All strict pure-good dominance and cap arguments remain valid.
- **\(r\downarrow1/2\):** the theorem is for every fixed \(r>1/2\). At \(r=1/2\), truth is unidentifiable and \(A_L=0\); ratios and finite expected correct-recovery statements cease to apply. This boundary cannot be substituted into the formulas.
- **\(r\uparrow1\):** eventual singleton equality is not uniform in \(r\). At exactly \(r=1\), \(A_L=L\operatorname{kl}(p,1-p)\), \(U_L=L\operatorname{kl}(p,q)\), and \(V_L=L\operatorname{kl}(p,1-q)\). The \(\Gamma\) ratios no longer depend on depth. In particular \(V_L<A_L\) for \(q<p\), so the singleton conclusion fails at this noiseless-source boundary. Finite factual information saturation is essential.
- **\(p\downarrow q\):** the strict domain has \(U_L>0\). At exactly \(p=q\), formats are identical, the nuisance disappears, and \(U_L=0,V_L=A_L\), so zero premium is immediate. The ceiling formula involving division by \(U_L\) must not be used there. Quantitative cap/cost requirements need not remain bounded as the gap closes.
- **\(c=0\):** all costs remain positive because \(\ell>0,L\ge1\), so the theorem and compactness proof apply. No unproved assertion that depth 1 is always oracle-optimal at \(c=0\) is needed for the theorem.
- **Mixed blocks:** they must remain in the learner's full LP and may matter when there is a positive premium. Their exclusion is proved only for the oracle-optimal face. Restricting the learner to pure blocks globally would be a different problem.
- **Known levels and finite menu:** the result does not include the original unknown \(p,q\), offline calibration, source reliability estimation, arbitrary root revisits, within-root adaptive stopping, or shared purchases across facts. Each extension changes the information constraints or action class.
- **Asymptotic coefficient versus computation:** an LP identity does not prove that an approximate implemented planner and practical stopping rule attain the ideal coefficient. The appropriate finite-state achievability and a valid stopping rule must remain separate from computational experiments.

## 8. Recommendation and novelty boundary

This is a complete restricted-model oracle-face characterization, conditional only on the separately stated standard finite-action leading-coefficient theorem. Its strongest structural message is that costly acquisition of independent provenance can change whether sharing is needed at all, because source-truth information saturates while extraction-format information does not. The failed-cap relative-premium result prevents overstating that message.

The cost-sensitive KL program, change-of-measure lower bound, and generic controlled-testing achievability are standard ingredients and should not be advertised as new. Strict channel degradation is also standard. The specific reduction to the tied-depth smallest-group criterion, together with the finite-cap dichotomy and the singleton consequence, is the candidate contribution requiring the focused literature audit. It is suitable for consideration as a narrowly scoped theory extension in the current paper; it does not justify replacing the original model or claiming realistic Web validation.
