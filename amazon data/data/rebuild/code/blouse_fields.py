"""Conservative seller-claim audit. All outputs reference the original field and original text."""
import re
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from audit_blouses import HIGH, norm, utterances, FIELDS, CN

LEX = {
 'neckline':{
 'high_neck':HIGH.pattern,'v_neck':r'\bv[ -]?(?:neck(?:line)?|shaped neck)\b','crew_neck':r'\bcrew[ -]?neck(?:line)?\b',
 'round_neck':r'\bround[ -]?neck(?:line)?\b','scoop_neck':r'\bscoop[ -]?neck(?:line)?\b','boat_neck':r'\b(?:boat[ -]?neck|bateau)\b',
 'mock_neck':r'\bmock[ -]?(?:neck|turtle(?:neck)?)\b','turtleneck':r'\b(?:turtle[ -]?neck|roll[ -]?neck)\b',
 'square_neck':r'\bsquare[ -]?neck(?:line)?\b','off_shoulder':r'\boff[ -](?:the[ -])?shoulders?\b',
 'one_shoulder':r'\bone[ -]shoulder\b','halter':r'\bhalter(?:neck)?\b','cowl_neck':r'\bcowl[ -]?neck\b',
 'sweetheart':r'\bsweetheart[ -]?neck(?:line)?\b','henley':r'\bhenley\b','collared_neck':r'\b(?:collared(?:[ -]neck)?|shirt collar|point collar|peter pan collar|stand(?:ing)? collar|mandarin collar)\b'},
 'sleeve':{'sleeveless':r'\b(?:sleeveless|no sleeves?)\b','short_sleeve':r'\bshort[ -]?sleeve(?:d|s)?\b',
 'long_sleeve':r'\blong[ -]?sleeve(?:d|s)?\b','three_quarter_sleeve':r'\b(?:(?:3/4|3-4|3⁄4|three[ -]quarters?)(?:[ -]length)?[ -]?sleeve(?:d|s)?)\b',
 'half_sleeve':r'\b(?:half|elbow[ -]length)[ -]sleeve(?:d|s)?\b','cap_sleeve':r'\bcap[ -]sleeve(?:d|s)?\b',
 'seven_eighths_sleeve':r'\b7/8[ -]sleeves?\b','cropped_sleeve':r'\b(?:cropped|bracelet[ -]length)[ -]sleeves?\b'},
 'pattern':{'solid':r'\b(?:solid(?:[ -]colou?red?)?|plain[ -](?:color|pattern|blouse|top|shirt))\b',
 'floral':r'\b(?:florals?|flower[ -](?:print|pattern))\b','stripes':r'\b(?:striped|stripes|stripe[ -](?:print|pattern))\b',
 'plaid':r'\b(?:plaid|tartan|gingham|checkered|checked[ -](?:pattern|print))\b','polka_dot':r'\b(?:polka[ -]dots?|swiss[ -]dots?|dotted[ -](?:pattern|print))\b',
 'animal_print':r'\b(?:leopard|zebra|animal)[ -]?(?:print|pattern|spots?)\b','paisley':r'\bpaisley\b','color_block':r'\bcolou?r[ -]?block(?:ed|ing)?\b',
 'geometric':r'\bgeometric[ -]?(?:print|pattern)?\b','tie_dye':r'\btie[ -]dy(?:e|ed)\b','camo':r'\b(?:camouflage|camo print)\b',
 'graphic_print':r'\b(?:letter|graphic|butterfly|heart|star)[ -](?:print|pattern)\b'}}
LEX={k:{v:re.compile(p,re.I) for v,p in vals.items()} for k,vals in LEX.items()}
FIBER_NAMES={'cotton':'cotton','polyester':'polyester','polyamide':'nylon','nylon':'nylon','spandex':'elastane','elastane':'elastane','lycra':'elastane',
 'rayon':'rayon','viscose':'viscose','linen':'linen','modal':'modal','acrylic':'acrylic','wool':'wool','silk':'silk','lyocell':'lyocell',
 'bamboo':'bamboo','cashmere':'cashmere','polyurethane':'polyurethane','flax':'linen','tencel':'tencel'}
FIBERS='|'.join(FIBER_NAMES)
FIBER=re.compile(r'\b('+FIBERS+r')\b')
PCT=re.compile(r'(?<![\d.])(\d+(?:\.\d+)?)\s*%\s*(?:(?:organic|recycled|combed|pima|ring[ -]spun)\s+)?('+FIBERS+r')\b')
def is_attr_source(a,k):
    if not k.startswith('details.'):return True
    match={'neckline':'neck|collar','sleeve':'sleeve','fabric':'fabric|material','care':'care|wash','pattern':'pattern|print'}
    return bool(re.search(match[a],k,re.I))
def composition(s):
    return sorted((FIBER_NAMES[v],Decimal(p)) for p,v in PCT.findall(s))
def fmt(comp):
    return ' + '.join(f'{float(q):g}% {name}' for name,q in comp)
def whole(s):
    return bool(PCT.search(s)) and not re.sub(r'[\s,;/+&:-]|\band\b','',PCT.sub('',s))
def care_claims(s):
    result=set()
    methods={'machine':r'machine[ -]wash(?:able|ed|ing)?|wash(?:ed|ing)?\s+(?:in\s+)?(?:a |the )?(?:washing )?machine',
             'hand':r'hand[ -]wash(?:able|ing|ed)?|wash(?:ed|ing)? by hand','dry_clean':r'dry[ -]clean(?:ing|ed)?'}
    for m,rx in methods.items():
        for h in re.finditer(r'\b(?:'+rx+r')\b',s):
            before=s[max(0,h.start()-30):h.start()];after=s[h.end():h.end()+20]
            neg=bool(re.search(r"(?:do not|don't|never|avoid|not|no|cannot)\s*$",before) or re.match(r'\s+(?:is )?not (?:allowed|recommended)',after))
            only=bool(re.match(r'\s+only\b',after) or re.search(r'\bonly\s*$',before))
            result.add(('no_' if neg else 'only_' if only else 'allow_')+m)
    if re.search(r'\bmachine\s*(?:or|and|/)\s*hand[ -]wash',s):result.add('allow_machine')
    if re.search(r'\bhand\s*(?:or|and|/)\s*machine[ -]wash',s):result.add('allow_hand')
    if re.search(r'\b(?:do not|never) wash\s*(?:[.!;,]|$)',s):result.add('no_wet')
    return result

def check_record(raw,info):
    facts={a:[] for a in FIELDS}; concerns={a:set() for a in FIELDS}; conflict={a:set() for a in FIELDS}
    def ev(a,k,s,l):facts[a].append(dict(source=k,claim=l,text=s))
    listings=list(utterances(raw))
    for k,s in listings:
        t=norm(s)
        for a in ['neckline','sleeve','pattern']:
            if not is_attr_source(a,k):continue
            for val,pat in LEX[a].items():
                if pat.search(t):
                    ev(a,k,s,val)
                    if re.search(r'\b(?:available in|choose from|other (?:styles|patterns)|various (?:styles|patterns)|depending on (?:the )?colou?r|different (?:prints|patterns))\b',t):
                        concerns[a].add('可能描述多种款式或变体')
            if k.startswith('details.') and not any(x['source']==k for x in facts[a]):
                concerns[a].add('结构化字段存在未归类取值');ev(a,k,s,'unmapped')
        if is_attr_source('care',k):
            cs=care_claims(t)
            for x in sorted(cs):ev('care',k,s,x)
            if not cs and k.startswith('details.'):concerns['care'].add('结构化洗护值需复核');ev('care',k,s,'unmapped')
        if is_attr_source('fabric',k):
            comp=composition(t)
            if comp:
                ev('fabric',k,s,fmt(comp))
                if re.search(r'\b(?:lining|contrast fabric|shell fabric|sleeves? only|depending on|varies by|different colou?rs?)\b',t):
                    concerns['fabric'].add('成分可能依部位或变体变化')
            if '%' in t and re.search(r'\d\s*%\s*[a-z]',t) and len(re.findall(r'\d\s*%',t))>len(comp):
                if not re.search(r'100%\s*(?:satisfaction|brand new|guarantee)',t):concerns['fabric'].add('含未解析百分比');ev('fabric',k,s,'unparsed')
    values={a:'' for a in FIELDS}
    for a in ['neckline','sleeve','pattern']:
        terms={x['claim'] for x in facts[a]}-{'unmapped'}
        if a=='neckline' and {'round_neck','crew_neck'}<=terms:terms.remove('round_neck')
        if a=='neckline' and 'high_neck' in terms and terms&{'mock_neck','turtleneck'}:terms.remove('high_neck')
        if len(terms)>1:
            if a=='pattern' or (a=='neckline' and terms&{'high_neck','collared_neck','henley'}):concerns[a].add('多种描述，无法确定单一标签')
            else:conflict[a].add('同一属性出现不同取值')
        elif len(terms)==1:values[a]=next(iter(terms))
    comps=set(); extra=[]; primary=set()
    for k,s in listings:
        if not is_attr_source('fabric',k):continue
        t=norm(s); comp=composition(t)
        if comp:
            if sum(q for _,q in comp)==100 and len({v for v,_ in comp})==len(comp):
                comps.add(tuple(comp))
                if whole(t) or k.lower()=='details.fabric type':primary.add(tuple(comp))
            else:extra.extend(comp)
    if len(comps)>1:conflict['fabric'].add('完整成分比例互相冲突')
    elif len(comps)==1 and primary:
        base=next(iter(comps));values['fabric']=fmt(base)
        if any(x not in base for x in extra):conflict['fabric'].add('其他成分或比例与完整声明不符')
        for k,s in listings:
            if not is_attr_source('fabric',k):continue
            t=norm(s)
            if k=='title' or k.startswith('details.') or re.search(r'\b(?:made (?:of|from|with)|fabric|material|blend)\b',t):
                for fib in set(FIBER.findall(t)):
                    if FIBER_NAMES[fib] not in dict(base):
                        concerns['fabric'].add('其他面料名称与成分表需核对');ev('fabric',k,s,'other_'+fib)
            if len(base)==1 and re.search(r'\b'+base[0][0]+r'\s+blend\b',t):
                concerns['fabric'].add('纯成分与混纺措辞并存');ev('fabric',k,s,'blend')
    terms={x['claim'] for x in facts['care']}
    if ('only_hand' in terms and terms&{'allow_machine','only_machine','no_hand','only_dry_clean','no_wet'}) or ('only_dry_clean' in terms and terms&{'allow_hand','allow_machine','only_hand','only_machine'}) or ('no_machine' in terms and terms&{'allow_machine','only_machine'}) or ('no_hand' in terms and terms&{'allow_hand','only_hand'}) or ('no_wet' in terms and terms&{'allow_machine','allow_hand','only_machine','only_hand'}) or ('only_machine' in terms and terms&{'allow_hand','only_hand'}):
        conflict['care'].add('洗护许可、禁止或仅限指令冲突')
    elif 'only_hand' in terms:values['care']='hand_wash_only'
    elif terms&{'allow_machine','only_machine'}:values['care']='machine_wash_permitted'
    if raw['price'] is not None:ev('price','price',str(raw['price']),str(raw['price']))
    try:
        n=Decimal(str(raw['price']))
        if n.is_finite() and n>0:
            if n==Decimal(str(info['price'])):values['price']=float(n)
            else:conflict['price'].add('原始价格与清洗后价格不一致')
    except InvalidOperation:pass
    for k,s in listings:
        if k.startswith('details.') and 'price' in k.lower():
            ev('price',k,s,'alternate_price');concerns['price'].add('另有价格字段，须判定口径')
    # A multi-pack, outfit or explicit alternative style is not a single experimental blouse.
    scope=''
    if re.search(r'\b(?:[2-9]\s*(?:pack|pcs|pieces?)|pack of [2-9]|two[ -]piece|outfit set|matching set)\b',norm(raw['title'])):
        scope='标题指向套组或多件装'
    rows=[];bad=[]
    for a in FIELDS:
        status='冲突' if conflict[a] else '待复核' if concerns[a] else '缺失' if values[a]=='' else '通过'
        reason='；'.join(sorted(conflict[a]|concerns[a])) or ('缺少可唯一编码的卖家证据' if status=='缺失' else '')
        rows.append((a,status,reason,facts[a]))
        if status!='通过':bad.append(CN[a]+'：'+status+' '+reason)
    if scope:bad.append(scope)
    card={'parent_asin':raw['parent_asin'],'cohort':info['cohort'],'source_row':raw['row'],'title':raw['title'],'store':raw.get('store'),
          **values,'explicit_high_neck':True if any(x['claim']=='high_neck' for x in facts['neckline']) else None}
    return card,bad,rows

