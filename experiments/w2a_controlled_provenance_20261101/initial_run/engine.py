"""Known-channel controlled provenance experiment; CPU and no model clients.

All calculations concern stipulated synthetic channels, not measured extraction.
Policies receive r,a,c and observed root counts only, never theta or realized V.
"""
import itertools
import math


def majority_success(n,p):
    if n==0: return 0.5
    return sum(math.comb(n,k)*p**k*(1-p)**(n-k)*(1 if 2*k>n else 0.5 if 2*k==n else 0)
               for k in range(n+1))


def repeat_risk(n,r,a):
    if n==0:return 0.5
    return r-(2*r-1)*majority_success(n,a)


def fresh_risk(n,r,a):
    t=r*a+(1-r)*(1-a)
    return 1-majority_success(n,t)


def root_count_law(k,r,a):
    plus=[];minus=[]
    for s in range(k+1):
        f=a**s*(1-a)**(k-s);g=(1-a)**s*a**(k-s)
        plus.append(math.comb(k,s)*(r*f+(1-r)*g))
        minus.append(math.comb(k,s)*((1-r)*f+r*g))
    return tuple(plus),tuple(minus)


def fixed_depth_risk(m,k,r,a):
    if m==0 or k==0:return 0.5
    pp,pm=root_count_law(k,r,a)
    total=0.0
    for counts in itertools.product(range(k+1),repeat=m):
        lp=math.prod(pp[s] for s in counts);lm=math.prod(pm[s] for s in counts)
        total+=0.5*min(lp,lm)
    return total


def root_information(n,r,a):
    pp,pm=root_count_law(n,r,a)
    value=0.0
    for p,q in zip(pp,pm):
        if p==0:continue
        if q==0:return math.inf
        value+=p*math.log(p/q)
    return value


class BudgetSolver:
    """Exhaustive Bayes Bellman recursion; integer read/root costs, free stopping.

    Root exchangeability permits sorting count pairs, preserving sufficient
    statistics. No within-root-discard restriction: any visited root can be read
    again. Optimality applies only to this finite stipulated decision problem.
    """
    def __init__(self,r,a,c):
        assert 0.5<=r<=1 and 0.5<=a<=1 and isinstance(c,int) and c>=0
        self.r,self.a,self.c=r,a,c
        self._values={};self._actions={};self._weights={}

    @staticmethod
    def canonical(state):return tuple(sorted(state))

    def weights(self,state):
        state=self.canonical(state)
        if state in self._weights:return self._weights[state]
        wp=wm=1.0
        for s,f in state:
            vplus=self.a**s*(1-self.a)**f
            vminus=(1-self.a)**s*self.a**f
            wp*=self.r*vplus+(1-self.r)*vminus
            wm*=(1-self.r)*vplus+self.r*vminus
        self._weights[state]=(wp,wm)
        return wp,wm

    def stop_risk(self,state):
        wp,wm=self.weights(state)
        assert wp+wm>0,'Impossible states are not evaluated'
        return min(wp,wm)/(wp+wm)

    def transition(self,state,action,positive):
        state=list(self.canonical(state))
        if action=='new':state.append((int(positive),int(not positive)))
        else:
            s,f=state[action];state[action]=(s+int(positive),f+int(not positive))
        return self.canonical(tuple(state))

    def action_value(self,state,budget,action):
        cost=self.c+1 if action=='new' else 1
        assert cost<=budget
        denom=sum(self.weights(state));value=0.0;mass=0.0
        for positive in (False,True):
            nxt=self.transition(state,action,positive)
            probability=sum(self.weights(nxt))/denom
            mass+=probability
            if probability>0:value+=probability*self.value(nxt,budget-cost)
        assert abs(mass-1)<2e-12,(state,action,mass)
        return value

    def value(self,state,remaining):
        state=self.canonical(state);key=(state,remaining)
        if key in self._values:return self._values[key]
        best=self.stop_risk(state);chosen='stop'
        if remaining>=1:
            # Unique existing count pairs give identical action values.
            previous=None
            for i,pair in enumerate(state):
                if pair==previous:continue
                previous=pair
                val=self.action_value(state,remaining,i)
                if val<best-1e-14:best,chosen=val,('repeat',i)
        if remaining>=self.c+1:
            val=self.action_value(state,remaining,'new')
            if val<best-1e-14:best,chosen=val,('new',)
        self._values[key]=best;self._actions[key]=chosen
        return best

    def initial(self,budget):
        value=self.value((),budget)
        return {'risk':value,'first_action':self._actions[((),budget)],
                'states':len(self._values),'belief_states':len(self._weights)}


def confidence_diagnostic(n,r,a,delta=0.05):
    """Wrong URL-iid posterior is a diagnostic, not an accuracy comparator."""
    pp,pm=root_count_law(n,r,a);t=r*a+(1-r)*(1-a)
    coverage=error_mass=posterior_sum=0.0
    for s in range(n+1):
        evidence=0.5*(pp[s]+pm[s])
        wrongp=t**s*(1-t)**(n-s);wrongm=(1-t)**s*t**(n-s)
        wrong=max(wrongp,wrongm)/(wrongp+wrongm)
        correct=max(pp[s],pm[s])/(pp[s]+pm[s])
        if wrong>=1-delta-1e-14:
            coverage+=evidence
            error_mass+=0.5*(pm[s] if wrongp>=wrongm else pp[s])
            posterior_sum+=evidence*wrong
        assert correct<=r+1e-12
    f=a**n;g=(1-a)**n
    return {'reads':n,'r':r,'a':a,'delta':delta,
            'naive_acceptance_probability':coverage,
            'actual_selective_error':error_mass/coverage if coverage else None,
            'mean_naive_confidence_when_accepted':posterior_sum/coverage if coverage else None,
            'correct_all_positive_confidence':(r*f+(1-r)*g)/(f+g),
            'naive_all_positive_confidence':t**n/(t**n+(1-t)**n),
            'both_unanimous_probability':f+g,
            'source_aware_acceptance_possible':r>=1-delta}
