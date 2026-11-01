# A nondegenerate region where every optimal allocation mixes reading depths

Date: 2026-11-01. This is a computer-assisted theorem with analytic region bounds, extending the sealed [point certificate](../web_oracle_structure_20261031/DEPTH_MIXING_THEOREM.md). Its finite interval calculations are checked by [certify_region.py](certify_region.py). No empirical model responses or parameter-search outcomes enter the proof.

## 1. Model and exact claim

Retain the [fixed unknown-extraction model](../web_unknown_calibration_20261031/MODEL_AND_SCOPE.md). There is one binary truth. Each fresh source has one persistent report, correct with probability r. The source accuracy r is **known within each instance**; letting r vary below compares different instances and does not make it an unknown nuisance parameter. Conditional on the report, independent extractions have unknown accuracies p and q, with the better format known to the oracle. All 27 completed blocks (a,b), with 1 <= a+b <= 6, are available. A block costs c+ell(a+b). Fix eta=1/40; alternative rates range over 1/2 <= v <= u <= 39/40. The oracle does not know the truth, p, or q.

The two labelled reference streams each have M_delta samples, with

\[
M_\delta/\log(1/\delta)\longrightarrow\alpha.
\]

They calibrate extraction of known reports. They are not truthful copies of the current fact. The objective is expected **online** cost. Their common, already-acquired cost is excluded.

Write K_or for the full-menu information-program coefficient and K_L for the coefficient restricted to actions with a+b=L. Crucially, K_L allows **every format composition and arbitrary allocations among them** at that depth. Normalize ell=1 for the proof. Let

\[
U(c)=16c+18.
\]

**Theorem A (explicit calibration/access-cost rectangle).** At

\[
(r,p,q)=(3/5,19/20,3/5),\qquad
\alpha\in[19/20,6/5],\quad c\in[1/2,3/2],
\]

the following bounds hold simultaneously:

\[
K_{\rm or}\le U(c),\qquad
\min_{1\le L\le6}K_L\ge U(c)+\frac94.
\tag{1}
\]

Every full-menu optimal allocation therefore uses at least two distinct depths. Relative to every fixed depth, the optimal online-cost coefficient is smaller by at least 3/59 (approximately 5.08%).

**Theorem B (explicit full-dimensional region).** Set epsilon=1/40000. For every

\[
\begin{aligned}
|r-3/5|&\le\epsilon,& |p-19/20|&\le\epsilon,& |q-3/5|&\le\epsilon,\\
\alpha&\in[19/20,6/5],&c&\in[1/2,3/2],
\end{aligned}
\tag{2}
\]

we have

\[
\boxed{K_{\rm or}\le U(c),\qquad
\min_{1\le L\le6}K_L\ge U(c)+\frac{15}{7}.}
\tag{3}
\]

The relative saving is at least 5/103 (approximately 4.85%). This box has nonempty interior in all five continuous parameters (r,p,q,alpha,c). In decimals its rate intervals are

\[
r,q\in[0.599975,0.600025],\qquad
p\in[0.949975,0.950025].
\]

The radius is conservative: it is an explicit certified neighborhood, not an estimated maximal radius or phase boundary. The calibration and cost intervals have widths 0.25 and 1 respectively.

For arbitrary ell>0 replace the cost interval by **c/ell in [1/2,3/2]**, replace U by 16c+18ell, and multiply the additive gaps by ell. Relative savings are unchanged.

## 2. Information program and strict certificate

For a block (a,b), let P^+_{r,p,q;a,b} denote the joint positive-count distribution under the positive truth:

\[
P^+(s,t)=\binom as\binom bt
\left[r p^s(1-p)^{a-s}q^t(1-q)^{b-t}
 +(1-r)(1-p)^s p^{a-s}(1-q)^tq^{b-t}\right].
\]

P^- swaps r with 1-r. All probabilities are positive on the compact domains used here. Define

\[
D_{a,b}(r,p,q;u,v)=D(P^+_{r,p,q;a,b}\Vert P^-_{r,u,v;a,b}),\qquad
C(p,q;u,v)=\operatorname{kl}(p,u)+\operatorname{kl}(q,v).
\]

The oracle program is

\[
\min_{x\ge0}\sum_{a,b}(c+a+b)x_{a,b}
\quad\text{s.t.}\quad
\alpha C(p,q;u,v)+\sum_{a,b}x_{a,b}D_{a,b}(r,p,q;u,v)\ge1
\quad\forall\ 1/2\le v\le u\le39/40.
\tag{4}
\]

Its expected-cost interpretation comes from the preceding stage's matching theorem. The current proof concerns this exact program; no nuisance grid replaces its constraints.

Choose the same witness at every point of (2):

\[
x_{1,0}=14,\qquad x_{2,0}=2,\qquad x_{a,b}=0\text{ otherwise}.
\tag{5}
\]

Pure-good online observations do not depend on v. Thus the minimizing v is min(q,u), and feasibility reduces exactly to

\[
f_\alpha(r,p,q;u)=\alpha C_*(p,q;u)
 +14D_{1,0}(r,p,q;u,u)+2D_{2,0}(r,p,q;u,u)\ge1,
\tag{6}
\]

where C_*(p,q;u)=kl(p,u)+kl(q,min(q,u)).

At the central rates and alpha=1, the rechecked continuous certificate gives

\[
\inf_{1/2\le u\le39/40}f_1(r_0,p_0,q_0;u)>1+\frac1{35}.
\tag{7}
\]

Specifically, 950 intervals of width 1/2000 cover the full domain. Exact rational probabilities and rigorous logarithm intervals bound f at each midpoint. Its derivative is evaluated exactly. A global Lipschitz constant 44800 for f' gives, for radius h=1/4000,

\[
f(u)\ge f(u_i)-|f'(u_i)|h-44800h^2/2.
\]

The smallest certified surplus is greater than 0.0285716211137, which exceeds 1/35. The profiled calibration is C1 at u=q, so the same bound crosses that join. The script independently recomputes these 950 inequalities; the old JSON decimal is not used as proof input.

## 3. Widening calibration and access cost: proof of Theorem A

For the central p_0,q_0, C_*(u) is convex: both pieces have positive second derivative, and their first derivatives agree at u=q_0. Its maximum on the compact interval is at an endpoint. Exact log bounds check

\[
C_*(39/40)<C_*(1/2)=C_0<103/200.
\tag{8}
\]

If alpha>=1, calibration only increases (6). If 19/20<=alpha<=1, (7)-(8) give

\[
f_\alpha-1>\frac1{35}-\frac1{20}\frac{103}{200}
=\frac{79}{28000}>0.
\tag{9}
\]

Thus (5) is feasible throughout the claimed calibration interval and costs U(c).

A single alternative (u,v) and multiplier y>=0 give a fixed-depth lower bound whenever

\[
yD_{a,L-a}(r,p,q;u,v)\le c+L\quad(0\le a\le L):
\qquad K_L\ge y[1-\alpha C(p,q;u,v)].
\tag{10}
\]

For L=1 use (u,v)=(1/2,1/2). The exact certificate at c=1 checks 100 D_{a,1-a}<2 for both compositions. Rescale y to 50(c+1). Then

\[
K_1\ge50(c+1)(1-\alpha C_0)
\ge50(c+1)(1-\alpha\cdot103/200).
\tag{11}
\]

The tied-rate alternative is legitimate by continuity from strict ordered alternatives. For L>=2 use (u,v)=(p_0,q_0), whose calibration KL is zero. The exact certificate verifies

\[
(413/10)D_{a,L-a}(r_0,p_0,q_0;p_0,q_0)<1+L
\]

for all 25 compositions at depths two through six. Rescaling y gives

\[
K_L\ge\frac{413}{10}\frac{c+L}{L+1}\qquad(2\le L\le6).
\tag{12}
\]

The bound in (11) minus U(c) is minimized at alpha=6/5,c=1/2 and equals 53/20, greater than 9/4. For (12), the difference from U(c) decreases with c, so it is minimized at c=3/2. There it decreases with L and reaches 9/4 at L=6. This proves (1).

## 4. Rate perturbations: proof of Theorem B

We establish derivative bounds on the larger auxiliary box

\[
r,q\in[.59,.61],\qquad p\in[.94,.96].
\tag{13}
\]

All line segments from the center to (2) stay inside (13). All nuisance rates retain the **entire** original domain, including values far from p and q.

### 4.1 Uniform feasibility survives

For distributions P(t),Q(t), differentiation of KL gives

\[
\partial_tD(P\Vert Q)
=\sum_sP'_s\log(P_s/Q_s)-\sum_sP_sQ'_s/Q_s.
\tag{14}
\]

For pure depth one, every probability in P and Q lies in [.3955,.6045], so |log(P/Q)|<1/2. Also ||partial_r P||_1<=2, |partial_r log Q|<=100/39<3 and ||partial_p P||_1<=.44. Consequently

\[
|\partial_rD_{1,0}|<4,\qquad |\partial_pD_{1,0}|<1/4.
\tag{15}
\]

For pure depth two, the middle-count probabilities are 2p(1-p) in [.0768,.1128] and 2u(1-u) in [.04875,.5]. True endpoint probabilities are at least .39(.94)^2. Alternative endpoint probabilities are at least r(1-r)>=.59(.39), since

\[
Q_2=(u-r)^2+r(1-r),\qquad
Q_0=(u-(1-r))^2+r(1-r).
\]

Thus both P_s/Q_s and Q_s/P_s, at every count s, are at most 625/96, whose log is less than 2. The law derivative norms are ||partial_r P||_1<=2 and ||partial_p P||_1<=4. The latter follows by differentiating the product law before applying the count map; each Bernoulli factor contributes L1 norm at most 2. Mixtures and count maps cannot increase this bound. Therefore

\[
|\partial_rD_{2,0}|<7,\qquad |\partial_pD_{2,0}|<8.
\tag{16}
\]

For the calibration term, |partial_p C_*|<4 and |partial_q C_*|<1. The latter derivative is zero when q<=u and equals logit(q)-logit(u) otherwise; it is continuous at the join. Combining (15)-(16), uniformly for alpha in [19/20,6/5],

\[
|\partial_r f_\alpha|\le70,\quad
|\partial_p f_\alpha|<25,\quad
|\partial_q f_\alpha|<2.
\]

The sum is less than 100. Moving each of r,p,q by at most epsilon therefore reduces (6) by at most 100epsilon. From (9),

\[
\boxed{f_\alpha(r,p,q;u)-1>
\frac{79}{28000}-100\frac1{40000}=\frac9{28000}>0}
\tag{17}
\]

uniformly over the whole alternative domain. The witness remains feasible.

### 4.2 All fixed depths retain a strict lower bound

For a same-rate, opposite-truth pair P,Q at depth L, write its two conditional component laws as F,G. Then

\[
P=rF+(1-r)G,\qquad Q=(1-r)F+rG.
\]

Throughout (13), P/Q lies in [39/61,61/39], so |log(P/Q)|<1/2 and |P/Q-1|<=22/39. Because sum Q'=0, the second term in (14) can use P/Q-1 in place of P/Q. Both law derivative norms are bounded by 2 for r, by 2a for p, and by 2b for q. Hence

\[
|\partial_rD|\le83/39,\quad
|\partial_pD|\le83a/39,\quad
|\partial_qD|\le83b/39.
\]

In particular,

\[
D(r,p,q;p,q)\le D(r_0,p_0,q_0;p_0,q_0)
+\frac{83(L+1)}{39}\epsilon.
\tag{18}
\]

Use the slightly smaller multiplier 206/5 in place of 413/10. For every composition at L=2,...,6, exact interval arithmetic verifies

\[
\frac{206}{5}\left[D(r_0,p_0,q_0;p_0,q_0)
+\frac{83(L+1)}{39}\epsilon\right]<L+1.
\tag{19}
\]

The tightest robust slack occurs at depth two and still exceeds 0.00356. Thus

\[
K_L\ge\frac{206}{5}\frac{c+L}{L+1},\qquad L=2,\ldots,6.
\tag{20}
\]

For L=1 and the fair alternative (1/2,1/2), Q is constant and the total derivative bound is 2. The certificate verifies 100[D_0+2epsilon]<2 for both compositions. Moreover

\[
C_0(p,q)=\operatorname{kl}(p,1/2)+\operatorname{kl}(q,1/2)
\le103/200+4\epsilon=5151/10000,
\]

since logit(p)<16/5 and logit(q)<1/2 on (13). Therefore

\[
K_1\ge50(c+1)\left(1-\alpha\frac{5151}{10000}\right).
\tag{21}
\]

The bound (21) minus U is minimized at alpha=6/5,c=1/2 and equals 2641/1000, greater than 15/7. Among (20), the worst difference is attained at c=3/2,L=6 and equals

\[
\frac{206}{5}\frac{15}{14}-42=\frac{15}{7}.
\]

This proves (3).

## 5. Necessity of mixing and relative saving

The full program attains its optimum: it has a finite feasible witness, finitely many actions of strictly positive cost, and closed continuous constraints. Its bounded-cost sublevels are compact. Every allocation supported on one depth belongs to a fixed-depth restriction and costs strictly more than U. Thus no full optimum can have single-depth support.

For either theorem let g be its uniform additive gap. Since U(c)<=42 and K_L>=U(c)+g,

\[
1-\frac{K_{\rm or}}{K_L}
\ge1-\frac{U(c)}{U(c)+g}
\ge\frac{g}{42+g}.
\]

This equals 3/59 for g=9/4 and 5/103 for g=15/7. The statement concerns asymptotic allocation support and cost coefficients; it does not assert that every finite realized trajectory of an optimal adaptive policy must contain both depths.

## 6. Interpretation and limits

The Web mechanism is acquisition of independent sources versus repeated extraction from one persistent source. Two same-format reads agree with probability p^2+(1-p)^2, independent of the truth and r; thus deeper reads can help learn the extraction channel. Fresh sources supply independent reports. The theorem proves a strict allocation tradeoff in a parameter region, rather than merely suggesting this explanation from the agreement identity.

- Calibration is finite on the log(1/delta) scale. The result is not an alpha-to-infinity statement.
- The same witness and all 27 fixed-depth composition checks are retained throughout the region. No favorable profiles or test observations are selected.
- The sufficient region is not maximal. The source-rate radius is deliberately conservative.
- The claim is pointwise in each fixed admissible instance. A uniform finite-delta remainder over the whole box is not proved here.
- No pure-good optimality theorem or exactly-two-depth support theorem is assumed or proved. The witness is pure-good, but the compared full optimum allows every composition.
- If paid calibration is added to both comparators, the additive online-cost separation persists, but the displayed relative savings for **total** cost need not hold.
- This is a controlled-model, computer-assisted structural theorem. Real Web/LLM validity and novelty relative to all prior work remain separate evidence questions.
