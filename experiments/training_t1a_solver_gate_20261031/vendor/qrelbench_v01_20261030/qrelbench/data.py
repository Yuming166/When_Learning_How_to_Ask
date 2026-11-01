"""Evaluator-only fictional catalog generator and deterministic record predicates."""
from dataclasses import dataclass
from copy import deepcopy
from .randomness import derive,bit,integer,opaque

KINDS=['stock','price','shipping','returns']
SOURCE_REFS={
 'stock':['https://schema.org/Offer','https://schema.org/availability'],
 'price':['https://schema.org/Offer','https://schema.org/price','https://schema.org/priceCurrency'],
 'shipping':['https://schema.org/OfferShippingDetails','https://schema.org/shippingRate'],
 'returns':['https://schema.org/MerchantReturnPolicy','https://schema.org/merchantReturnDays']}


@dataclass
class PrivateEpisode:
    public: dict
    records: list
    truth: list
    types: list
    key: bytes
    provenance: dict


def evaluate(record,proposition):
    offer=record['offers'];kind=proposition['predicate'];t=proposition.get('threshold')
    if kind=='stock':return int(offer['availability']=='https://schema.org/InStock')
    if kind=='price':return int(offer['price']<=t)
    if kind=='shipping':return int(offer['shippingDetails']['shippingRate']['value']==0)
    if kind=='returns':return int(offer['hasMerchantReturnPolicy']['merchantReturnDays']>=t)
    raise ValueError('Unknown predicate')


def render(proposition,fmt):
    item=proposition['product_id'];kind=proposition['predicate'];t=proposition.get('threshold')
    clauses={'stock':f'item {item} is currently in stock',
             'price':f'the offered price of item {item} is at most USD {t}',
             'shipping':f'the shipping charge for item {item} is zero',
             'returns':f'the return window for item {item} is at least {t} days'}
    claim=clauses[kind]
    if fmt=='A':return f'Is it true that {claim}? Answer 1 for true and 0 for false.'
    if fmt=='B':return f'Choose the truth status of this statement: {claim}. Answer 1 if it holds and 0 if it does not.'
    raise ValueError('Unknown format')


def make_episode(master_seed,split,index,partition):
    if split not in {'train','development','test'}:raise ValueError('Unknown split')
    if not partition or any(type(k) is not int or k<1 for k in partition):raise ValueError('Invalid partition')
    # Partition is deliberately excluded: same independent catalog across grouping comparisons.
    key=derive(str(master_seed).encode(),'qrelbench-v0.1',split,index)
    d=sum(partition);targets=[];records=[];truth=[];groups=[];membership=[]
    for g,k in enumerate(partition):
        gid=opaque(key,'group',g);groups.append({'id':gid,'targets':list(range(len(membership),len(membership)+k))})
        membership.extend([g]*k)
    for j in range(d):
        theta=bit(key,'truth',j);kind=KINDS[integer(key,0,3,'public_kind',j)]
        pid=opaque(key,'public_product_id',j);offer={'@type':'Offer','priceCurrency':'USD'}
        prop={'predicate':kind,'product_id':pid}
        if kind=='stock':offer['availability']='https://schema.org/InStock' if theta else 'https://schema.org/OutOfStock'
        elif kind=='price':
            threshold=integer(key,50,150,'public_price_threshold',j);prop['threshold']=threshold
            distance=integer(key,1,30,'private_price_distance',j)
            offer['price']=threshold-distance if theta else threshold+distance
        elif kind=='shipping':
            fee=0 if theta else integer(key,1,30,'private_shipping_charge',j)
            offer['shippingDetails']={'@type':'OfferShippingDetails','shippingRate':{'@type':'MonetaryAmount','currency':'USD','value':fee}}
        else:
            threshold=[14,30,60][integer(key,0,2,'public_return_threshold',j)];prop['threshold']=threshold
            days=threshold+integer(key,0,30,'private_return_extra',j) if theta else integer(key,0,threshold-1,'private_return_short',j)
            offer['hasMerchantReturnPolicy']={'@type':'MerchantReturnPolicy',
                'returnPolicyCategory':'https://schema.org/MerchantReturnFiniteReturnWindow','merchantReturnDays':days}
        record={'@context':'https://schema.org','@type':'Product','productID':pid,'name':f'Fictional item {pid}','offers':offer}
        assert evaluate(record,prop)==theta
        targets.append({'j':j,'id':opaque(key,'public_target_id',j),'group':membership[j],
                        'proposition':prop,'queries':{m:render(prop,m) for m in ['A','B']}})
        records.append(record);truth.append(theta)
    types=[bit(key,'group_type',g) for g in range(len(partition))]
    public={'benchmark':'QRelBench','version':'0.1.0','episode_id':opaque(key,'public_episode_id'),
            'd':d,'groups':groups,'targets':targets,'formats':['A','B'],
            'source_type':'fictional_procedural_catalog','schema_reference':'https://schema.org/Product',
            'truth_prior':'independent Bernoulli(0.5); no forced balance'}
    provenance={'generator':'qrelbench-v0.1','split':split,'episode_index':index,'master_seed':master_seed,
                'source_type':'fictional_procedural_catalog','schema_references':SOURCE_REFS,
                'grouping':'synthetic source ownership; no shared database records',
                'semantic_validation':'same canonical proposition for A/B; deterministic evaluator matches every sampled bit',
                'private_seed_scope':'evaluator only; public view excludes reconstruction seeds'}
    return PrivateEpisode(public,records,truth,types,key,provenance)


def public_view(episode):return deepcopy(episode.public)
