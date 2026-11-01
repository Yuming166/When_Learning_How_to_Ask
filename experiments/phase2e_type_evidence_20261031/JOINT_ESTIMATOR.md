# Joint evidence estimator

## Material Passport

Implementation: phase2e/exact.py and phase2e/estimator.py. Development model
and priors: METHOD_DESIGN.md. New-source tests precede the acquisition freeze.

For each candidate (theta,z), form nonnegative integer exponents a,b,c,d for
p successes/failures and q successes/failures. Its unnormalized posterior mass
is its noisy-type likelihood times

\[
J(a,b,c,d)=\int_{1/2}^{1-\eta}p^a(1-p)^b
             \int_{1/2}^{p}q^c(1-q)^d\,dq\,dp.
\]

Expand the two failure powers by the binomial theorem. Each summand is

\[
\frac{(-1)^{i+j}\binom bi\binom dj}{c+j+1}
\left[\int_{1/2}^{1-\eta}p^{a+i+c+j+1}dp
 -2^{-(c+j+1)}\int_{1/2}^{1-\eta}p^{a+i}dp\right].
\]

With rational eta and s_g every operation is exact Fraction arithmetic.
Normalize all 2^(d+G) masses; replace a by a+1 or c by c+1 to obtain the p/q
first moments. This is exact continuous posterior inference for the stated
prior. The implementation deliberately bounds d<=4 and at most 24 task/reference
observations; alternating polynomial sums become expensive, so it is a reference,
not the production estimator. Noisy reports remain likelihood factors: with no
other evidence and one report of type 1 at accuracy 4/5, P(z=1|report)=4/5,
not 1. The exact prior means at eta=1/20 are E[p]=4/5, E[q]=13/20.

The practical estimator maps u,v in [0,1]^2 to
p=.5+(.5-eta)u and q=.5+(.5-eta)uv. The normalized triangle prior contributes
Jacobian weight 2u. A fixed 32x32 Gauss-Legendre rule integrates the likelihood
for every sign/type state in log space. It returns posterior means p,q and
marginal probabilities for each theta_j,z_g. The action solver uses marginal
MAP bits, with deterministic ties at zero; they need not be a joint-MAP state.
The information policy keeps the full approximate joint distribution.

The discrete marginalization is exhaustive. Continuous integration is a
numerical approximation, with no outward rounding or global integration-error
certificate. 32-versus-64 results diagnose sensitivity on the same development
observations; agreement is evidence at those points, not a general accuracy
proof. Fixed quadrature nodes also prevent importing an infinite-horizon
continuous-parameter consistency theorem.

The explicitly labeled plug-in alternative fits all discrete states and their
ordered continuous MLEs, chooses the global maximizing state's rates, then
marginalizes all theta,z conditional on those fixed rates. It fuses observations
but removes posterior uncertainty in p,q. It can be overconfident. Its accuracy
is assessed on the same tape rather than by silently substituting it into an
arm and changing the experiment.

For the genuine posterior, conditioning on additional observed evidence cannot
increase prior-averaged Bayes squared-error risk: the law of total variance gives
E Var(X|D,C)<=E Var(X|D). This statement applies under the stated joint prior;
it is not pointwise frequentist dominance at fixed p=.85,q=.60, and it does not
certify the quadrature approximation. Type reports and group pooling can change
rate estimates indirectly through their posterior correlations with theta,z.

Tests cover 20 small random count/reference/report configurations over four
partition structures against exact rational integration, complement symmetry,
noisy-report uncertainty and plug-in labeling. Fixed-tape diagnostics compare
forced-only, joint, no-type, no-reference and plug-in estimates at shared
landmarks; empirical values and the full denominators appear in
FAIR_ABLATION_REPORT.md and artifacts/analysis/diagnostics.json.

Masked-evidence replay is a likelihood-component sensitivity analysis on a fixed
realized tape. Because the original adaptive actions may depend on the masked
reports or references, it is not exact Bayesian inference under a filtration
that hides that evidence while retaining the action history. No data-processing
or Bayes-risk guarantee is claimed for these masked replay scores. The actual
joint estimator uses every observation and has no such omitted-evidence issue.

Observed numerical sensitivity: the common Aligned-Full tape's largest 32/64
marginal discrepancy is0.0018835 at a long terminal point; at fixed64/256
prefixes it is about1.5e-5. A post-hoc check of all92 stored Fused-Info
64/256/terminal prefixes gives maximum0.0015480; recomputed next-action argmax
agrees92/92 at orders32/64. At the five largest marginal discrepancies,
orders64/128 differ by at most5.4e-8. These were stored-data checks only, with
zero additional observations and no policy changes. They do not cover every
executed planning update or certify a quadrature error bound. See
artifacts/analysis/quadrature_sensitivity.json and FINAL_RESEARCH_DECISION.md.
