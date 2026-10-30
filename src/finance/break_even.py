"""Bounded scan + bisection with honest conditional root diagnostics.
Finite scanning cannot certify all roots of an arbitrary black-box function.
"""
import math
from src.finance.engine import compare
from src.finance.calculations import sale_proceeds
from src.scenarios.intelligence import change,baseline_value,fingerprint


def solve_bounded(fn,target,lower,upper,*,samples=129,x_tolerance=1e-8,value_tolerance=.01,max_iterations=100,monotonic_contract=None,slope_floor=1e-8):
    result={'target':target,'bounds':[lower,upper],'samples':samples,'x_tolerance':x_tolerance,'value_tolerance':value_tolerance,'max_iterations':max_iterations,
        'monotonic_contract':monotonic_contract,'value':None,'roots':[],'sampled_non_monotonic':False,'unstable':False,
        'limitation':'Finite scan may miss narrow/tangent/discontinuous roots. Unique/no-solution claims are conditional on the stated structural monotonicity contract, not certified for arbitrary functions.'}
    finite=lambda x:type(x) in (float,int) and math.isfinite(x)
    if not all(finite(x) for x in (target,lower,upper,x_tolerance,value_tolerance,slope_floor)) or lower>=upper or x_tolerance<=0 or value_tolerance<=0 or slope_floor<0 or type(samples)!=int or not 3<=samples<=4097 or type(max_iterations)!=int or max_iterations<=0 or monotonic_contract not in (None,'increasing','decreasing','constant'):
        return {'status':'INVALID_INPUT','value':None,'roots':[],'error':'Finite ordered bounds/target and valid positive tolerances, sample count and iteration limit required'}
    xs=[lower+(upper-lower)*i/(samples-1) for i in range(samples)];ys=[];evaluations=0
    def val(x):
        nonlocal evaluations
        y=fn(x);evaluations+=1
        if not finite(y):raise ValueError('Nonfinite function output')
        return y-target
    try:ys=[val(x) for x in xs]
    except (ValueError,TypeError,OverflowError,ZeroDivisionError) as e:return {**result,'status':'INVALID_FUNCTION_OR_DOMAIN','error':str(e),'evaluations':evaluations}
    differences=[b-a for a,b in zip(ys,ys[1:])];noise=max(value_tolerance*1e-6,1e-12)
    positive=any(d>noise for d in differences);negative=any(d< -noise for d in differences)
    result['sampled_non_monotonic']=positive and negative
    if (monotonic_contract=='increasing' and negative) or (monotonic_contract=='decreasing' and positive) or (monotonic_contract=='constant' and (positive or negative)):
        return {**result,'status':'MONOTONIC_CONTRACT_VIOLATION','evaluations':evaluations}
    near=[i for i,y in enumerate(ys) if abs(y)<=value_tolerance];plateaus=[]
    for i in near:
        if plateaus and i==plateaus[-1][-1]+1:plateaus[-1].append(i)
        else:plateaus.append([i])
    flat=[g for g in plateaus if len(g)>1]
    # Several near-zero samples cannot establish a unique point at the requested resolution.
    if flat:
        result['status']='MULTIPLE_OR_FLAT_WITHIN_TOLERANCE';result['near_zero_intervals']=[[xs[g[0]],xs[g[-1]]] for g in flat];result['evaluations']=evaluations
        result['unstable']=True;return result
    candidates=[{'value':xs[i],'residual':ys[i],'iterations':0,'bracket':[xs[i],xs[i]],'converged':True} for i in near]
    failed=[]
    for i,(yl,yr) in enumerate(zip(ys,ys[1:])):
        if yl*yr>=0 or i in near or i+1 in near:continue
        lo,hi=xs[i],xs[i+1];fl=yl;best=None
        for iteration in range(1,max_iterations+1):
            mid=(lo+hi)/2
            try:fm=val(mid)
            except (ValueError,TypeError,OverflowError,ZeroDivisionError) as e:return {**result,'status':'INVALID_FUNCTION_OR_DOMAIN','error':str(e),'evaluations':evaluations}
            best={'value':mid,'residual':fm,'iterations':iteration,'bracket':[lo,hi],'converged':abs(fm)<=value_tolerance and hi-lo<=x_tolerance}
            if best['converged']:break
            if fm==0:lo=hi=mid
            elif fl*fm<0:hi=mid
            else:lo=mid;fl=fm
        if best['converged']:candidates.append(best)
        else:failed.append(best)
    candidates.sort(key=lambda r:r['value']);roots=[]
    for root in candidates:
        if roots and abs(root['value']-roots[-1]['value'])<=x_tolerance*2:continue
        x=root['value'];step=max(x_tolerance*10,(upper-lower)*1e-6);l=max(lower,x-step);r=min(upper,x+step)
        try:slope=(val(r)-val(l))/(r-l)
        except (ValueError,TypeError,OverflowError,ZeroDivisionError):slope=None
        root['local_slope']=slope;root['unstable']=slope is None or abs(slope)<slope_floor;roots.append(root)
    result.update(roots=roots,failed_brackets=failed,evaluations=evaluations,unstable=any(r['unstable'] for r in roots))
    if failed:result['status']='NONCONVERGED_OR_DISCONTINUOUS'
    elif len(roots)>1:result['status']='MULTIPLE_SOLUTIONS_FOUND'
    elif not roots:result['status']='NO_SOLUTION_WITHIN_BOUNDS_CONDITIONAL' if monotonic_contract else 'NO_BRACKET_FOUND_UNRESOLVED'
    elif result['unstable']:result['status']='UNSTABLE_ROOT_CANDIDATE'
    elif result['sampled_non_monotonic']:result['status']='NON_MONOTONIC_ROOT_CANDIDATE'
    elif monotonic_contract=='constant':result['status']='MULTIPLE_OR_FLAT_WITHIN_TOLERANCE'
    elif monotonic_contract:result['status']='CONDITIONAL_UNIQUE_ROOT';result['value']=roots[0]['value']
    else:result['status']='ROOT_CANDIDATE_UNIQUENESS_UNVERIFIED'
    return result


def break_even(p,a,h,kind,target,bounds,*,strategy='rent_out'):
    if type(h)!=int or h not in (1,3,5,10) or not isinstance(bounds,(list,tuple)) or len(bounds)!=2:return {'status':'INVALID_INPUT','value':None,'error':'Valid horizon and two explicit finite bounds required'}
    if strategy not in ('hold_occupy','sell','rent_out'):return {'status':'INVALID_INPUT','value':None,'error':'Unsupported strategy'}
    def select(q,b,j):return next(s for s in compare(q,b,j)['strategies'] if s['strategy']==strategy)
    try:base=select(p,a,h)
    except (ValueError,TypeError,OverflowError) as e:return {'status':'INVALID_INPUT','value':None,'error':str(e)}
    metadata={'kind':kind,'strategy':strategy,'horizon_years':h,'target':target,'units':'USD except appreciation/vacancy decimal rates',
        'baseline_assumptions_hash':fingerprint({'property':__import__('dataclasses').asdict(p),'assumptions':__import__('dataclasses').asdict(a),'horizon':h}),
        'tax_scope':'Pretax only; no hidden missing-tax substitution','classification':'HYPOTHETICAL_BREAK_EVEN_NOT_A_FORECAST'}
    if kind=='rent_for_year1_property_cash':
        if strategy!='rent_out':return {**metadata,'status':'NOT_APPLICABLE','value':None}
        active=max(0,12-min(12,p.rental.lease_up_months));slope=active*((1-p.rental.vacancy)*(1-p.rental.management_rate)-p.rental.leasing_months_per_year/12)
        contract='increasing' if slope>0 else ('decreasing' if slope<0 else 'constant')
        fn=lambda x:select(*change(p,a,h,'monthly_rent',x))['annual_schedule'][0]['property_cashflow_after_financing_before_tax']
        baseline=base['annual_schedule'][0]['property_cashflow_after_financing_before_tax']
    elif kind=='vacancy_for_year1_noi':
        if strategy!='rent_out':return {**metadata,'status':'NOT_APPLICABLE','value':None}
        slope=-p.rental.monthly_rent*max(0,12-min(12,p.rental.lease_up_months))*(1-p.rental.management_rate);contract='decreasing' if slope<0 else 'constant'
        fn=lambda x:select(*change(p,a,h,'vacancy',x))['annual_schedule'][0]['noi'];baseline=base['annual_schedule'][0]['noi']
    elif kind=='exit_price_for_net_proceeds':
        if strategy=='sell':return {**metadata,'status':'NOT_APPLICABLE','value':None,'error':'This wrapper targets a future retained-property exit, not an immediate current-value change'}
        contract='increasing' if p.sale.brokerage_rate+p.sale.transfer_recordation_rate<1 else 'constant'
        fn=lambda x:select(*change(p,a,h,'sale_price',x))['sale']['pretax_proceeds'];baseline=base['sale']['pretax_proceeds']
    elif kind=='appreciation_for_npv':
        if strategy=='sell' or h in p.sale.explicit_terminal_prices:return {**metadata,'status':'NOT_APPLICABLE','value':None,'error':'Immediate sale or explicit exit price makes appreciation irrelevant to target NPV'}
        contract='increasing' if p.sale.brokerage_rate+p.sale.transfer_recordation_rate<1 else 'constant'
        fn=lambda x:select(*change(p,a,h,'appreciation',x))['pretax']['npv'];baseline=base['pretax']['npv']
    else:return {**metadata,'status':'INVALID_INPUT','value':None,'error':'Unknown break-even kind'}
    limits={'rent_for_year1_property_cash':(0,float('inf')),'vacancy_for_year1_noi':(0,1),'exit_price_for_net_proceeds':(0,float('inf')),'appreciation_for_npv':(-1,float('inf'))}
    lo,hi=limits[kind]
    if len(bounds)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in bounds) or bounds[0]<lo or bounds[1]>hi or (kind=='appreciation_for_npv' and bounds[0]<=-1):return {**metadata,'status':'INVALID_INPUT','value':None,'error':'Bounds outside supported financial domain'}
    solved=solve_bounded(fn,target,*bounds,monotonic_contract=contract,x_tolerance=1e-8 if kind in ('vacancy_for_year1_noi','appreciation_for_npv') else 1e-5,value_tolerance=.001)
    return {**metadata,'baseline_outcome':baseline,**solved}
