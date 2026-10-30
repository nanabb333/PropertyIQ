"""Matched assumption differences, not causal inference or strategy rankings."""
from src.finance.engine import compare
from src.scenarios.intelligence import change,baseline_value,applies,fingerprint,VERSION

def summary(result):
    return {s['strategy']:{'npv':s['pretax']['npv'],'cumulative_cash_flow':sum(s['pretax']['normalized_cashflows']),
        'terminal_wealth':s['terminal_wealth_before_tax'],'after_tax_npv':s['after_tax']['npv'] if s['after_tax'] else None} for s in result['strategies']}

def deltas(base,alternative):
    return {k:None if base[k] is None or alternative[k] is None else alternative[k]-base[k] for k in base}

def comparison_row(p,base,alt,baseline_horizon,horizon,var,base_value,value,strategy):
    d=deltas(base,alt);threshold=max(1000.,.01*abs(base['npv']))
    return {'variable':var,'baseline_value':base_value,'alternative_value':value,'strategy':strategy,'applicable':applies(p,var,strategy),
        'baseline_horizon':baseline_horizon,'alternative_horizon':horizon,'baseline':base,'alternative':alt,'change':d,
        'material_npv_change':abs(d['npv'])>=threshold,'materiality_threshold':threshold,'materiality_rule':'max(USD1000,1% absolute baseline NPV)',
        'interpretation':'Conditional assumption sensitivity, not a causal estimate; strategy not ranked','cashflow_basis':'Sum of normalized pretax flows including common initial opportunity capital and one terminal asset',
        'timing_caveat':'Different holding horizons deliberately change timing/terminal date; deltas are not a same-date wealth comparison' if baseline_horizon!=horizon else None}

def one_way(p,a,h,var,values):
    base=summary(compare(p,a,h));bv=baseline_value(p,a,h,var);rows=[]
    for value in values:
        q,b,j=change(p,a,h,var,value);out=compare(q,b,j);new=summary(out)
        for strategy in base:
            row=comparison_row(p,base[strategy],new[strategy],h,j,var,bv,value,strategy)
            row['assumptions_hash']=fingerprint(out['assumptions']);row['scenario_version']=VERSION;rows.append(row)
    return rows

def two_way(p,a,h,var_x,values_x,var_y,values_y):
    if var_x==var_y:raise ValueError('Two-way axes must be distinct')
    if 'sale_price' in (var_x,var_y) and 'horizon' in (var_x,var_y):raise ValueError('Sale-price override and changing exit year need an explicit price schedule, not axis-order dependence')
    base=summary(compare(p,a,h));rows=[]
    for x in values_x:
        for y in values_y:
            q,b,j=change(p,a,h,var_x,x);q,b,j=change(q,b,j,var_y,y);out=compare(q,b,j);new=summary(out)
            for strategy in base:
                rows.append({'variable_x':var_x,'baseline_x':baseline_value(p,a,h,var_x),'alternative_x':x,'variable_y':var_y,
                    'baseline_y':baseline_value(p,a,h,var_y),'alternative_y':y,'strategy':strategy,'baseline_horizon':h,'alternative_horizon':j,
                    'baseline':base[strategy],'alternative':new[strategy],'change':deltas(base[strategy],new[strategy]),'assumptions_hash':fingerprint(out['assumptions']),
                    'scenario_version':VERSION,'interpretation':'Joint hypothetical input grid; no probabilities or strategy rankings'})
    return rows

def default_grid(p,a):
    return {'appreciation':[-.03,0.,.025,.05],'monthly_rent':[p.rental.monthly_rent*.9,p.rental.monthly_rent,p.rental.monthly_rent*1.1],
        'vacancy':[0.,p.rental.vacancy,.20],'hoa_growth':[0.,a.hoa_growth,.10],'property_tax_growth':[0.,a.property_tax_growth,.08],
        'maintenance_annual':[p.maintenance_annual*.75,p.maintenance_annual,p.maintenance_annual*1.5],
        'brokerage_rate':[max(0,p.sale.brokerage_rate-.01),p.sale.brokerage_rate,min(1-p.sale.transfer_recordation_rate,p.sale.brokerage_rate+.01)],
        'closing_fixed':[p.sale.closing_fixed,p.sale.closing_fixed+2000], 'discount_rate':[.03,.06,.09], 'horizon':[1,3,5,10]}
