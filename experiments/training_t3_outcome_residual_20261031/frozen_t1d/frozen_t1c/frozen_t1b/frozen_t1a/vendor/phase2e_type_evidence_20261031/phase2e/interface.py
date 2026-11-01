"""Explicit Exact applicability gate; no semantic-to-iid assumption injection."""
def validate_exact(public,calibration):
    domain=public.get('rate_domain',{})
    if not isinstance(domain,dict) or not domain.get('levels_unknown') or 'eta' not in domain:
        raise ValueError('Theory-faithful bounded iid rate-domain contract required')
    s=public.get('type_accuracy')
    if not isinstance(s,(list,tuple)) or len(s)!=len(public['groups']) or any(not isinstance(v,(float,int)) or not .5<v<1 for v in s):
        raise ValueError('Known finite group type accuracies required')
    if set(calibration)!={'high','low'} or len(calibration['high'])!=len(calibration['low']):
        raise ValueError('Real equally long labelled reference streams required')
    if any(type(v) is not int or v not in (0,1) for a in calibration.values() for v in a):
        raise ValueError('Calibration must contain observed binary outcomes')
    if not 1<=public['d']<=4:raise ValueError('Certified evaluation limited to d<=4')
