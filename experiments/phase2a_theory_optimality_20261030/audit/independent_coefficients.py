#!/usr/bin/env python3
"""Independent Phase 2a checks: nested continuous SLSQP, no parent imports.

The outer optimizer is nonlinear SLSQP with continuously minimized information
constraints.  A *single final* fixed-alternative LP provides a numerical lower
bound; it is not the outer optimization algorithm.  Convex tangent bounds on
each inner minimization supply an independently assessed feasibility residual.
This program writes no files.  Run with OPENBLAS_NUM_THREADS=1 for bounded CPU.
"""
from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq, linprog, minimize, minimize_scalar


UPPER = 0.99  # eta=.01; all fitted means in checked cases are <=p<UPPER.


def kl(r, x):
    r, x = np.asarray(r), np.asarray(x)
    return r * np.log(r / x) + (1-r) * np.log((1-r)/(1-x))


def f_k(k, p, x):
    return float(kl(p, 1-x) + (k-1)*kl(p, x))


@dataclass
class InnerResult:
    value: float
    lower: float
    levels: np.ndarray
    gradient: np.ndarray
    success: bool


def continuous_inner(weights, means, destinations, constant=0.0,
                     start=(0.8, 0.6), upper=UPPER):
    """Minimize the ORIGINAL KL sum in two continuous coordinates.

    No weighted-mean/isotonic solver is used.  SLSQP sees a triangle with
    vertices (.5,.5), (upper,.5), (upper,upper).  For any returned point x,
    convexity gives a lower bound f(x)+min_vertex grad f(x).(vertex-x).
    """
    weights, means = np.asarray(weights), np.asarray(means)
    destinations = np.asarray(destinations, dtype=int)

    def objective(levels):
        return float(weights @ kl(means, levels[destinations]) + constant)

    def derivative(levels):
        fitted = levels[destinations]
        terms = weights*(fitted-means)/(fitted*(1-fitted))
        return np.bincount(destinations, weights=terms, minlength=2)

    start = np.clip(np.asarray(start), .5, upper)
    if start[0] < start[1]:
        start[:] = np.mean(start)
    result = minimize(objective, start, method="SLSQP", jac=derivative,
                      bounds=[(.5, upper), (.5, upper)],
                      constraints=[{"type": "ineq", "fun": lambda x:x[0]-x[1],
                                    "jac": lambda x:np.array([1., -1.])}],
                      options={"ftol": 3e-13, "maxiter": 150})
    levels = result.x
    value, gradient = objective(levels), derivative(levels)
    vertices = np.array([[.5,.5],[upper,.5],[upper,upper]])
    lower = value + float(np.min((vertices-levels) @ gradient))
    return InnerResult(value, lower, levels, gradient, bool(result.success))


def oracle_coefficient(d, p, q, alpha):
    """Root search with a continuously optimized two-dimensional oracle KL."""
    def information(a):
        return continuous_inner([alpha,alpha,a,(d-1)*a],
                                [p,q,1-p,p], [0,1,0,0], start=(p,q))
    high = 1.
    while information(high).value < 1:
        high *= 2
    a = brentq(lambda a:information(a).value-1, 0, high, xtol=2e-13)
    check = information(a)
    return {"a":a, "K_or":d*a, "u":check.levels[0],
            "v":check.levels[1], "root_residual":check.value-1,
            "inner_tangent_gap":check.value-check.lower}


def gamma(k, p, q, alpha, a):
    """Independent scalar minimization, rather than substituting w_k."""
    def objective(w):
        return float(alpha*kl(q,w)+a*f_k(k,p,w))
    result = minimize_scalar(objective, bounds=(.5,UPPER), method="bounded",
                             options={"xatol":2e-14,"maxiter":200})
    candidates = [(float(result.fun),float(result.x)),
                  (objective(.5),.5),(objective(UPPER),UPPER)]
    value, w = min(candidates)
    formula_w = max(.5,(alpha*q+a*(1+(k-2)*p))/(alpha+k*a))
    return {"Gamma":value,"w":w,"formula_w_difference":w-formula_w}


class IndependentProgram:
    """Per-coordinate grouped counts; all type patterns; one flip per group."""
    def __init__(self, sizes, p, q, alpha, type_accuracy=None):
        self.sizes = tuple(sizes)
        self.p, self.q, self.alpha = p,q,alpha
        self.groups = np.repeat(np.arange(len(sizes)),sizes)
        self.G, self.d = len(sizes),sum(sizes)
        self.type_accuracy = type_accuracy
        self.kappas = (None if type_accuracy is None else
                       np.full(self.G,float(kl(type_accuracy,1-type_accuracy))))
        self.nvars = 2*self.G+(0 if self.kappas is None else self.G)
        self.cost = np.r_[sizes,sizes, [] if self.kappas is None else np.ones(self.G)]
        self.alternatives = [(mask,(self.groups == h).nonzero()[0][0])
                             for mask in range(2**self.G) for h in range(self.G)]
        self._cache = None

    def terms(self, allocation, type_mask, flip_mask):
        a,b = allocation[:self.G],allocation[self.G:2*self.G]
        weights,means,destinations = [self.alpha,self.alpha],[self.p,self.q],[0,1]
        for j,g in enumerate(self.groups):
            swap = (type_mask >> int(g))&1
            flipped = (flip_mask >> j)&1
            weights += [a[g],b[g]]
            means += [1-self.p if flipped else self.p,
                      1-self.q if flipped else self.q]
            destinations += [swap,1-swap]
        constant = (0. if self.kappas is None else
                    sum(self.kappas[g]*allocation[2*self.G+g]
                        for g in range(self.G) if (type_mask >> g)&1))
        return weights,means,destinations,constant

    def evaluate(self, allocation, type_mask, flip_mask):
        terms = self.terms(allocation,type_mask,flip_mask)
        return continuous_inner(*terms,start=(self.p,self.q))

    def row(self, type_mask, flip_mask, levels):
        """Affine online information at a fixed alternative, independently built."""
        row = np.zeros(self.nvars)
        for j,g in enumerate(self.groups):
            swap, flipped = (type_mask >> int(g))&1,(flip_mask >> j)&1
            row[g] += kl(1-self.p if flipped else self.p,levels[swap])
            row[self.G+g] += kl(1-self.q if flipped else self.q,levels[1-swap])
        if self.kappas is not None:
            for g in range(self.G):
                row[2*self.G+g] = self.kappas[g]*((type_mask>>g)&1)
        return row

    def all_constraints(self, allocation):
        if self._cache is not None and np.array_equal(allocation,self._cache[0]):
            return self._cache[1:]
        values,gradients,inner = [],[],[]
        for mask,j in self.alternatives:
            result = self.evaluate(allocation,mask,1<<j)
            values.append(result.value-1)
            gradients.append(self.row(mask,1<<j,result.levels))
            inner.append(result)
        self._cache = (allocation.copy(),np.array(values),np.array(gradients),inner)
        return self._cache[1:]

    def solve(self):
        start = np.full(self.nvars,2.)
        result = minimize(lambda x:float(self.cost@x),start,jac=lambda x:self.cost,
                          method="SLSQP",bounds=[(0,None)]*self.nvars,
                          constraints=[{"type":"ineq",
                                        "fun":lambda x:self.all_constraints(x)[0],
                                        "jac":lambda x:self.all_constraints(x)[1]}],
                          options={"ftol":2e-11,"maxiter":150})
        x = np.maximum(result.x,0)
        _,rows,inners = self.all_constraints(x)
        # Fixed alternatives yield necessary constraints and a numerical lower bound.
        rhs = np.array([1-self.alpha*(kl(self.p,z.levels[0])+kl(self.q,z.levels[1]))
                        for z in inners])
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore",message="Unrecognized options detected")
            lp = linprog(self.cost,A_ub=-rows,b_ub=-rhs,bounds=(0,None),method="highs",
                         options={"threads":1,"primal_feasibility_tolerance":1e-9,
                                  "dual_feasibility_tolerance":1e-9})
        min_online = min(x[h]*kl(self.p,.5)+x[self.G+h]*kl(self.q,.5)
                         for h in range(self.G))
        min_lower = min(z.lower for z in inners)
        # Scaling only the online counts adds >=(factor-1)*min_online to every
        # alternative, even when the offline contribution is substantial.
        factor = 1+max(0.,1-min_lower+2e-10)/min_online
        x_upper = x*factor
        _,_,upper_inners = self.all_constraints(x_upper)
        return {"sizes":list(self.sizes),"p":self.p,"q":self.q,"alpha":self.alpha,
                "type_accuracy":self.type_accuracy,"K":float(self.cost@x),
                "K_numerical_lower":float(lp.fun),
                "K_feasible_upper":float(self.cost@x_upper),
                "bound_width":float(self.cost@x_upper-lp.fun),
                "allocation":x.tolist(),"outer_success":bool(result.success),
                "outer_message":str(result.message),"iterations":int(result.nit),
                "min_inner_value":min(z.value for z in inners),
                "max_inner_tangent_gap":max(z.value-z.lower for z in inners),
                "upper_min_inner_tangent_lower":min(z.lower for z in upper_inners),
                "all_inner_success":all(z.success for z in inners+upper_inners),
                "lp_success":bool(lp.success)}


def verify_alternative_reduction():
    rng = np.random.default_rng(20261030)
    records,pointwise_violations = [],0
    total_full,all_inner_success,worst_gap = 0,True,0.
    for sizes in [(1,),(2,),(1,2),(2,2),(2,3)]:
        for case in range(3):
            program = IndependentProgram(sizes,.85,.60,[0.,1.,3.][case],
                                         None if case<2 else .8)
            allocation = rng.uniform(.1,2.,program.nvars)
            full_values,one_values = [],[]
            for mask in range(2**program.G):
                for flips in range(1,2**program.d):
                    result = program.evaluate(allocation,mask,flips)
                    total_full += 1
                    all_inner_success &= result.success
                    worst_gap = max(worst_gap,result.value-result.lower)
                    full_values.append(result.value)
                    if flips&(flips-1)==0:
                        one_values.append(result.value)
                    # For EACH alternative and EACH deleted flip: same levels,
                    # and therefore exact nonnegative KL increment identity.
                    if flips&(flips-1):
                        single = flips&(-flips)
                        for u,v in [(.5,.5),(.85,.6),(.75,.7),(.95,.55)]:
                            w,m,t,c = program.terms(allocation,mask,flips)
                            w1,m1,t1,c1 = program.terms(allocation,mask,single)
                            diff = np.array(w)@kl(m,np.array([u,v])[t])+c-(
                                np.array(w1)@kl(m1,np.array([u,v])[t1])+c1)
                            pointwise_violations += int(diff < -1e-12)
            # Group reduction: representative one-flip in every group.
            reduced = [program.evaluate(allocation,mask,1<<j).value
                       for mask,j in program.alternatives]
            records.append({"sizes":list(sizes),"case":case,
                            "full_min":min(full_values),
                            "oneflip_difference":min(one_values)-min(full_values),
                            "group_difference":min(reduced)-min(full_values)})
    return {"cases":len(records),"full_alternatives":total_full,
            "max_full_vs_reduced_error":max(abs(r["group_difference"]) for r in records),
            "pointwise_violations":pointwise_violations,
            "all_inner_success":bool(all_inner_success),
            "max_inner_tangent_gap":worst_gap,"records":records}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--section",choices=["all","grid","tiny","enumeration"],default="all")
    args = parser.parse_args()
    output = {"method":"independent nested continuous SLSQP; no parent imports",
              "domain_upper":UPPER}
    if args.section in ("all","grid"):
        grid = []
        for alpha in [0.,1.,2.,3.,5.,10.]:
            oracle = oracle_coefficient(16,.85,.60,alpha)
            grid.append({"alpha":alpha,**oracle,
                         "gamma":{str(k):gamma(k,.85,.60,alpha,oracle["a"])
                                  for k in [1,2,4,8,16]}})
        def critical_objective(alpha):
            a = oracle_coefficient(16,.85,.60,alpha)["a"]
            return gamma(8,.85,.60,alpha,a)["Gamma"]-1
        critical = brentq(critical_objective,1.,3.,xtol=3e-12)
        output.update(grid=grid,alpha_critical=critical,
                      critical_residual=critical_objective(critical))
    if args.section in ("all","tiny"):
        output["tiny"] = [IndependentProgram(sizes,p,q,alpha,s).solve()
                          for sizes,p,q,alpha,s in [
                              ((1,),.75,.60,0.,None),
                              ((1,),.75,.60,5.,None),
                              ((2,),.85,.60,1.,None),
                              ((1,2),.85,.60,0.,None),
                              ((2,2),.85,.60,3.,None),
                              ((1,2),.85,.60,1.,.8),
                              ((2,2),.85,.60,3.,.8)]]
    if args.section in ("all","enumeration"):
        output["enumeration"] = verify_alternative_reduction()
    failures = []
    for row in output.get("tiny",[]):
        if not all(row[key] for key in ["outer_success","all_inner_success","lp_success"]):
            failures.append("optimizer did not converge")
        if row["upper_min_inner_tangent_lower"] < 1-1e-8:
            failures.append("repaired upper allocation is not numerically feasible")
        if not -1e-8 <= row["bound_width"] <= 1e-5:
            failures.append("coefficient numerical envelope exceeds tolerance")
    enum = output.get("enumeration")
    if enum and (not enum["all_inner_success"] or enum["pointwise_violations"] or
                 enum["max_full_vs_reduced_error"] > 1e-8):
        failures.append("full-alternative reduction check failed")
    output["checks_passed"] = not failures
    print(json.dumps(output,indent=2,allow_nan=False))
    if failures:
        raise SystemExit("; ".join(failures))


if __name__ == "__main__":
    main()
