# Scope of the confidence certificate

A separate same-family Codex reviewer independently checked this mathematical argument against Theory_Note §§1,4,6. No external expert or cross-model theorem verification is claimed.

For a fixed true state and target j, write X=2Y-1. Under theta_j=0 and any predictable selection of target/format, E[X | past, selected j,m]<=0 because correctness is >=1/2. Conditional Hoeffding gives E[exp(lambda X)|past,selected j,m]<=exp(lambda²/2) for lambda>=0. Thus in global time

Z_t=exp(lambda S_j(t)-lambda² N_j(t)/2)

is a nonnegative supermartingale. Apply optional stopping to the target's nth observation time, truncated at finite horizons, and then Fatou. Even if that nth observation never occurs,

P(T_{j,n}<infinity, S_{j,n}>b_n) <= exp(-b_n²/(2n)).

For theta_j=1 apply the same proof to -S. Use b_n=sqrt(2n log(2*d*n*(n+1)/delta)); a true fixed sign has only one wrong tail. Union over j,n and sum_n 1/[n(n+1)]=1 gives at most delta/2, hence the stated conservative delta bound. This does not require a random prior on theta or independent target truths; it requires the conditional mean property of each selected response. Certified predictions must be frozen.

Correctness and termination differ. At q=.5 a permanently wrong-format strategy may never certify; report censoring. The pooled boundary also need not eventually cross merely because good-format counts diverge, if uninformative draws overwhelmingly dilute the drift. Base pilot q=.6 avoids that boundary but is capped anyway.

A persistent error can retain marginal accuracy r while violating the conditional mean condition: on a wrong first draw all repetitions are wrong, eventually crossing the wrong boundary with probability at least 1-r. Label-asymmetric control has a below-chance channel for theta0 and also falls outside the argument.

This is not the continuous-rate joint GLR or asymptotically optimal allocation in Theory_Note. It is a conservative technical certificate for the benchmark baselines. It does not independently verify the original Theorem 1–3 or their optimization coefficients.
