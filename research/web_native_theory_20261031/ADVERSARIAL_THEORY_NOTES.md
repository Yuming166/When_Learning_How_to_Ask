# Independent adversarial notes: provenance roots and query reliability

Date: 2026-10-31. This is a mathematical exploration, not an empirical result or an independent literature review. No historical experiment was changed; no model, provider, training, or benchmark-world calls were made. The supplied mission is treated as proposed research scope, not as evidence that its proposed conclusions are true.

## 1. Minimal model and distinctions

Start with **one factual bit**, \(\theta\in\{-1,+1\}\). Under hypothesis \(\theta\), independent roots obey

\[
 V_i=\theta Z_i,\qquad \Pr(Z_i=+1)=r_i\in(1/2,1).
\]

Repeated extraction from root \(i\) returns \(Y_{it}=V_i E_{it}\), with independent extraction errors \(\Pr(E_{it}=+1)=a\in(1/2,1)\). The errors are independent of roots and truth. Unless noted otherwise, \(r_i\) and \(a\) are known. Policies choose roots, repeat queries, and stop using the observed transcript and independent randomization only. They do not see \(V_i\), \(\theta\), or future errors.

The accuracy of one answer against factual truth is

\[
 \rho_i=r_i a+(1-r_i)(1-a)
       =\frac{1+(2r_i-1)(2a-1)}2.
\]

Extraction accuracy \(a\), root factual accuracy \(r_i\), and observed factual accuracy \(\rho_i\) are different parameters. In particular,

\[
 \operatorname{Cov}(Y_{it},Y_{iu}\mid\theta)
 =(2a-1)^2\{1-(2r_i-1)^2\}>0\quad(t\ne u).
\]

Thus fresh extraction calls do not establish conditional independence relative to factual truth. Multiple pages sharing a root do not provide extra independent \(Z_i\)'s.

## 2. Finite-root saturation: complete statements and proof

Write \(P_+,P_-\) for transcript laws under the two truths and

\[
 \kappa(r)=\operatorname{kl}(r,1-r)
          =(2r-1)\log\frac r{1-r}.
\]

**Proposition 1.** For a fixed pool of \(S<\infty\) roots and any adaptive extraction/stopping policy whose observation channel conditional on the roots does not depend on \(\theta\),

\[
 D(P_+\Vert P_-)\le\sum_{i=1}^S\kappa(r_i).
\]

This includes a finite stopped transcript and, by the usual increasing-sigma-field limit, an infinite transcript. It does not require a bounded number of extraction calls. The policy's full internal random seed can be included in the transcript without changing the conclusion.

**Proof.** Conditional on \(V=(V_1,\ldots,V_S)\), policy actions, extraction outcomes, and stopping are generated through a common stochastic kernel under both hypotheses. Hence \(\theta\to V\to H\) is a Markov chain. Data processing gives \(D(P_+^H\Vert P_-^H)\le D(P_+^V\Vert P_-^V)\). Root independence makes the latter equal to the displayed sum. This is a standard data-processing consequence, not sufficient standalone novelty.

If the rule returns a bit almost surely and has error at most \(\delta<1/2\) under **both** hypotheses, data processing through the decision gives

\[
 \operatorname{kl}(1-\delta,\delta)
 \le D(P_+\Vert P_-)
 \le\sum_i\kappa(r_i).
\]

For the first inequality, let the event be “output +”; its probabilities are at least \(1-\delta\) under + and at most \(\delta\) under −. Binary KL is minimized at those boundary probabilities. Therefore arbitrary vanishing \(\delta\) is impossible with a fixed finite imperfect root pool.

There is a sharper exact decision-theoretic floor. With a uniform prior,

\[
 e_* = \frac12\sum_{v\in\{\pm1\}^S}
          \min\{P_+(V=v),P_-(V=v)\}>0.
\]

Every transcript-based rule has Bayes error at least \(e_*\). Observing roots exactly achieves it. In the symmetric model, a likelihood-ratio rule with symmetric tie randomization has equal errors under the two truths, so \(e_*\) is also the minimax floor. Repeatedly extracting every root with \(a>1/2\) consistently reconstructs its sign; consequently the infimum achievable extraction-based error approaches \(e_*\). This last statement is an infimum/limit, not a claim that finite extraction always attains the floor.

For homogeneous \(r_i=r\), it becomes the familiar majority error:

\[
 e_*=\Pr\{B<S/2\}+\tfrac12\Pr\{B=S/2\},\qquad B\sim\mathrm{Binomial}(S,r).
\]

An additional **pointwise posterior bound** is useful when discussing selective stopping. The full-root likelihood ratio lies between \(e^{-L}\) and \(e^L\), where \(L=\sum_i\log[r_i/(1-r_i)]\); the transcript likelihood ratio inherits these bounds by averaging. Under the uniform prior, its posterior error is therefore at least \((1+e^L)^{-1}\) almost surely. Abstention does not create a transcript with arbitrary posterior confidence under these assumptions. Error guarantees with abstention must nevertheless explicitly state their denominator and return probability.

Boundary qualifications: a root with \(r_i=1\), a growing root pool, side information about truth, or a truth-dependent extraction channel changes the claim. It is false to state this floor for all “Web evidence” without the latent-root assumptions.

## 3. Acquisition costs can enter the leading coefficient

Suppose an unlimited sequence of homogeneous independent roots is available, with known fixed \(r\in(1/2,1)\). Activating each fresh root costs \(c>0\); each extraction costs \(\ell>0\). Let \(N\) be the number activated. Every root has the same reliability, and the policy has no preview of its report before activation.

**Proposition 2.** For any almost-surely terminating uniformly \(\delta\)-correct policy with finite expected cost,

\[
 \mathbb E_\theta N
 \ge \frac{\operatorname{kl}(1-\delta,\delta)}{\kappa(r)},
 \qquad
 \mathbb E_\theta C
 \ge c\frac{\operatorname{kl}(1-\delta,\delta)}{\kappa(r)}.
\]

If every activation includes at least one paid extraction, replace \(c\) by \(c+\ell\) in this lower bound. This remains a lower bound, not the exact coefficient with noisy extraction.

**Proof.** Enrich the stopped transcript by revealing every activated root's latent report. Conditional extraction/action laws then cancel from its likelihood ratio, leaving the sum of root log likelihood ratios. Activation of root \(i\) is decided before seeing its fresh independent report, so the expected sum is \(\kappa(r)\mathbb E_+N\). Bounded root log likelihood increments and finite \(\mathbb E N\) justify the stopped-sum identity (or use truncation). The observed transcript has no greater KL. Apply binary decision data processing. The − hypothesis is symmetric.

Thus fixed positive **per-root** access cost contributes at order \(\log(1/\delta)\). A single once-per-problem setup charge is only \(O(1)\). These cases should not be conflated. The statement also needs qualification when reliability can approach one with \(\delta\), or one activation is shared across a growing number of facts.

## 4. A rigorous restricted block optimization, not unrestricted optimality

Consider the class of policies that choose an integer \(k\ge1\) **before observing a fresh root**, pay \(c+k\ell\), collect exactly \(k\) extractions, and permanently discard that root. They may choose the next \(k\) using completed past blocks, and stop only at completed-block boundaries.

For a block with \(s\) positive answers, define

\[
 f_k(s)=a^s(1-a)^{k-s},\quad
 g_k(s)=(1-a)^s a^{k-s},
\]
\[
 P_{+,k}(s)=\binom ks\{r f_k(s)+(1-r)g_k(s)\},
 \quad
 P_{-,k}(s)=\binom ks\{(1-r)f_k(s)+r g_k(s)\}.
\]

The count is sufficient for the block. Put

\[
 D_k=D(P_{+,k}\Vert P_{-,k}),\qquad
 I_*=\max_{k\ge1}\frac{D_k}{c+k\ell}.
\]

Here \(D_1=\kappa(\rho)\), \(D_k\) increases strictly to \(\kappa(r)\), and the maximum is attained at a finite \(k\). Monotonicity follows by adding an observation. Its strictness holds for interior \(r,a\), because each finite-history next observation still distinguishes the hypotheses. For convergence, empirical extraction means consistently recover \(V\), while full-root data processing is an upper bound. Equivalently, block likelihood ratios converge to the root likelihood ratio and are uniformly bounded between \((1-r)/r\) and \(r/(1-r)\), allowing dominated convergence. The ratio tends to zero as \(k\to\infty\) since \(\ell>0\).

For this class, conditional KL chain rules give

\[
 D(P_+\Vert P_-)=\mathbb E_+\sum_{b\le B}D_{k_b}
 \le I_*\mathbb E_+C.
\]

Therefore \(\mathbb E C\ge\operatorname{kl}(1-\delta,\delta)/I_*\). Repeating any maximizing \(k_*\) and applying a symmetric likelihood-ratio sequential test with boundaries \(\pm\log(1/\delta)\) achieves uniform error at most \(\delta\), and

\[
 \mathbb E_\theta C
 =\frac{\log(1/\delta)}{I_*}+O(1).
\]

The proof uses iid completed blocks, positive KL drift, bounded block log likelihood increments, finite expected stopping, and bounded overshoot. A standard stopped-sum argument gives the coefficient; the probability of exiting at the incorrect boundary contributes only \(O(\delta\log(1/\delta))\). This is a restricted theorem of known-channel sequential design, not a new general optimum for agents that may return to old sources or stop inside a block.

The exact comparison of a given \(k>1\) against \(k=1\) is

\[
 \frac{D_k}{c+k\ell}>\frac{D_1}{c+\ell}
 \quad\Longleftrightarrow\quad
 c(D_k-D_1)>\ell(kD_1-D_k).
\]

This algebra requires no assertion that \(D_k\le kD_1\). A signed crossover can be retained as written. Numerical checks support subadditivity/concavity in this channel, but this note does **not** supply a proof; do not promote those checks to a theorem. Adaptive stopping within a root can improve this class and is deliberately outside the result.

## 5. Exact one-step decision and a counterexample with stopping

Use a uniform initial prior, or any specified prior in the following local calculation. At a history \(H\), define

\[
 m=\mathbb E[\theta\mid H],\quad
 h_i=\mathbb E[\theta V_i\mid H],\quad
 s=2a-1,\quad t=2r-1.
\]

The current Bayes error is \(L_0=(1-|m|)/2\). If one more extraction from an existing root is followed by a Bayes terminal decision, its expected error is exactly

\[
 L_i=\frac{1-\max\{|m|,s|h_i|\}}2.
\]

A fresh independent root, activated and queried once, has

\[
 L_{\mathrm{new}}=\frac{1-\max\{|m|,st\}}2.
\]

**Proof.** Let \(d_y=\Pr(\theta=+,Y=y\mid H)-\Pr(\theta=-,Y=y\mid H)\). For an old root, \(d_y=(m+ys h_i)/2\). Terminal Bayes error is \((1-\sum_y|d_y|)/2\). The identity \((|x+y|+|x-y|)/2=\max(|x|,|y|)\) yields the formula. For a fresh root, \(\mathbb E[\theta V_{\mathrm{new}}\mid H]=t\).

Under the explicit **one-step error-plus-cost** objective, a root repeat costs \(\lambda\ell\), activation plus extraction costs \(\lambda(c+\ell)\), and stopping costs nothing extra. Hence

\[
 \text{new beats repeat}\iff
 L_i-L_{\mathrm{new}}>\lambda c.
\]

Stopping must also be compared: \(L_0\) versus the two cost-augmented errors. This is neither a fixed-confidence optimality condition nor a universal multi-step threshold.

### Same truth posterior and same query counts, different uniquely optimal action

Set \(r=4/5\), \(a=7/10\), so \(t=3/5,s=2/5\). Two roots have each been queried twice. Compare repeating root 1 against one new root and stopping. Take \(\lambda\ell=1/100\), \(\lambda c=2/100\).

| History | Root 1 | Root 2 | \(m\) | \(h_1\) | repeat error | new error |
|---|---|---|---:|---:|---:|---:|
| H1 | \((+,-)\) | \((+,-)\) | 0 | \(3/5\) | \(19/50\) | \(19/50\) |
| H2 | \((+,+)\) | \((-,-)\) | 0 | \(1323/3485\) | \(14779/34850\) | \(19/50\) |

For H1, the three total losses are repeat \(.39\), new \(.41\), stop \(.5\): repeat is uniquely optimal. For H2, they are repeat \(6051/13940\approx.4340746\), new \(.41\), stop \(.5\): new is uniquely optimal. Repeating root 2 is symmetric. The gain of new over repeat at H2 is exactly \(768/17425\approx.0440746\).

To verify the posterior, let \(u\) be the root-local evidence mean with an unbiased root prior and let \(b\) be the truth posterior mean using the other root only. Then

\[
 m=\frac{b+tu}{1+btu},\qquad h_1=\frac{t+bu}{1+btu}.
\]

H1 has \(u=b=0\). H2 has \(u=20/29\), \(b=-12/29\), giving exactly the fractions above. Both histories have positive probability. They have the same truth posterior and per-root counts, yet different provenance posterior states. Thus neither truth posterior alone nor truth posterior plus query counts is a sufficient decision state.

### Optional strengthening: free new roots weakly dominate for one step

In the **homogeneous, fixed known extraction accuracy** model, a fresh-root query weakly improves immediate terminal Bayes error at least as much as any old-root query. This result is limited to one step and free activation in the comparison.

After any finite same-accuracy history, root-local evidence has form \(u=\tanh(n\operatorname{atanh}s)\) for integer signed count \(n\). Thus \(u=0\) or \(|u|\ge s\). Write \(m,h_i\) as above for an arbitrary other-root posterior mean \(b\). If \(|h_i|\le t\), the error comparison is immediate. Otherwise change both signs so \(u\ge s\). If \(h_i>t\), then \(b>0\) and

\[
 m-sh_i=\frac{b(1-su)+t(u-s)}{1+btu}\ge0.
\]

If \(h_i<-t\), write \(b=-v\), so \(vu>t\), \(m<0\), and

\[
 |m|-s|h_i|
 =\frac{v(1-su)+t(s-u)}{1-vtu}
 \ge0,
\]

because \(v>t/u\) makes the numerator at least \(t(1/u-u)\ge0\). Thus whenever \(|h_i|>t\), the current posterior margin already dominates its possible one-step contribution. In all cases \(L_{\mathrm{new}}\le L_i\). Different extraction accuracies, uncertain channel parameters, nonhomogeneous roots, or a multi-step objective require a separate analysis.

## 6. Finite-horizon dynamic programming is available, but needs the joint state

A small exact Bayes calculation can use the joint posterior \(\pi(\theta,V_1,\ldots,V_S)\) for activated roots. For known homogeneous parameters this state, together with remaining budget, is sufficient. It is not generally enough to use \(\pi(\theta)\) alone, as the counterexample proves.

For a remaining budget \(B\), the cost-constrained terminal-risk recursion is

\[
 F_B(\pi)=\min\left\{\min_{\hat\theta}\Pr_\pi(\theta\ne\hat\theta),
 \min_{a:\,c(a)\le B}\sum_y\Pr_\pi(y\mid a)
 F_{B-c(a)}(\pi^{a,y})\right\}.
\]

An activation action first appends a root according to \(\Pr(V=\theta)=r\), then extracts once; a repeat updates an existing latent root. The corresponding error-plus-cost recursion adds \(\lambda c(a)\) and reduces the allowed horizon. These are standard belief-state dynamic programs, not evidence of a closed-form global threshold or an asymptotically optimal algorithm. Unknown shared format variables must be included in the joint state.

## 7. Interaction with unknown query formats and identifiability

Let extraction format \(m\) have accuracy \(a_m\), with \(a_m=p\) for the group's preferred format and \(q\) otherwise, \(1/2\le q<p<1\). The root reliability remains a separate parameter.

1. **No repeated provenance, no separation of root and extraction accuracies.** If every query uses a new root and root reliability is unknown, a format supplies only the effective bias \((2r-1)(2a_m-1)\). Different positive root/extraction biases with the same product give exactly the same observation law. With two formats, their two products still do not generally identify all of \(r,p,q\). The ordering may be identifiable under a common positive root bias; the underlying levels are not.

2. **Repeated provenance can identify extraction strength without factual labels.** For disjoint extraction pairs from the same root,
   \[
   Y_{m,1}Y_{m,2}=E_{m,1}E_{m,2},\qquad
   \mathbb E[Y_{m,1}Y_{m,2}]=(2a_m-1)^2.
   \]
   Root sign and truth cancel. Independent extraction errors make disjoint pair products independent even when they reuse the same latent root. If accuracies are assumed at least one half, the positive square root identifies the extraction bias. Comparing the two squared biases identifies the preferred format when they differ. This is a rigorous extraction-calibration mechanism under the model, not a claim about arbitrary LLM repeat agreement.

3. **Agreement calibrates extraction, not factual truth.** The same statistic contains no \(r\). Even perfectly learning all format variables leaves the finite-root error floor in Proposition 1. Repeated extraction can determine a wrong root report very confidently.

4. **Sharing can amortize extraction learning, not remove missing independent evidence.** Sharing a format over many facts can make its estimate precise from many pair products. With a fixed finite imperfect root pool per fact, the factual \(\delta\downarrow0\) problem nevertheless remains infeasible. Therefore the old smallest-sharing-group criterion cannot be transferred unchanged: its asymptotic target is absent in this regime. Growing-root regimes need a new information program incorporating provenance blocks, access costs, and nuisance-parameter alternatives.

5. **Conditional one-step formulas need modification for uncertain formats.** If extraction accuracy is correlated with the latent truth/root posterior, the term \(s h_i\) must be replaced by \(\mathbb E[\theta V_i(2a_m-1)\mid H]\). It cannot generally be factored into posterior means. This is one concrete reason a naive plug-in or fused-independent posterior can be incorrect.

## 8. Exact reductions and nonreductions to the existing theory

- If all roots are perfectly factual, \(r_i=1\), then \(V_i=\theta\); independent extraction errors recover the original iid response channel with extraction levels \(p,q\), provided calibration and type-question definitions also match. This is a boundary reduction, not an instance of the finite-imperfect-root proposition.
- If every answer uses a fresh homogeneous root, answers are iid conditional on truth and their levels are \(p_{\rm eff}=rp+(1-r)(1-p)\), \(q_{\rm eff}=rq+(1-r)(1-q)\). The original task-channel theorem can apply to **these effective levels** if its parameter domain and all offline/type channels match. Original calibration of extraction levels is not automatically calibration of these factual effective levels.
- If \(a=1\), a single extraction reveals its root report exactly; repeats give no additional information and fresh-root acquisition is ordinary Bernoulli sequential testing. This limit is useful as a check, not a new theorem.
- Reinterpreting \(\theta\) to mean the source's own report also gives the old extraction problem, but changes the target from factual truth to document content. That change must be explicit.
- A finite pool of imperfect roots with repeated extraction does not satisfy the original iid likelihood or stopping-martingale assumptions relative to factual truth. Its old GLR, allocation program, and smallest-group theorem do not transfer merely by substituting average accuracies.

## 9. Adversarial novelty and claim limits

The saturation bound and exact Bayes floor are routine data-processing/Bayesian testing results. The completed-block theorem is a direct specialization of sequential experimental design with known channels and costs. The one-step formula is elementary binary Bayes decision algebra; the counterexample is useful for identifying the necessary provenance state but is not by itself a claim of a novel general theory.

A potentially substantive research contribution would need to isolate and prove an interaction that is absent from these ingredients—for example, a sharp cost of jointly learning a shared extraction interface while adaptively acquiring independent provenance roots, with a matching lower bound and an implementable policy under explicitly restricted source access. A full revisit policy with unknown shared levels has not been solved here. No statement in this note proves it, and the original expected-time proof cannot be used as a substitute.

Evidence status: exact symbolic derivations above; fraction calculations checked with deterministic rational arithmetic; exploratory finite numeric checks of \(D_k\) are not theorem evidence. Literature novelty still requires the parent's focused primary-source audit.
