"""Versioned deterministic assumption alternatives, no forecasts/probabilities."""
import hashlib,json
from dataclasses import asdict,replace
from src.finance.schema import Refinance,validate

VERSION='phase4b-v1'
def canonical(x):
    def normalize(v):
        if isinstance(v,dict):
            if len({str(k) for k in v})!=len(v):raise ValueError('Ambiguous normalized dictionary keys')
            return {str(k):normalize(val) for k,val in v.items()}
        if isinstance(v,(list,tuple)):return [normalize(a) for a in v]
        return v
    return json.dumps(normalize(x),sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def fingerprint(x):return hashlib.sha256(canonical(x)).hexdigest()
VARIABLES=('appreciation','monthly_rent','vacancy','hoa_growth','property_tax_growth','maintenance_annual','brokerage_rate','closing_fixed','discount_rate','horizon',
           'insurance_annual','lease_up_months','loan_balance','sale_price')

def baseline_value(p,a,h,var):
    if var in ('appreciation','hoa_growth','property_tax_growth','discount_rate'):return getattr(a,var)
    if var in ('monthly_rent','vacancy','lease_up_months'):return getattr(p.rental,var)
    if var in ('maintenance_annual','insurance_annual'):return getattr(p,var)
    if var in ('brokerage_rate','closing_fixed'):return getattr(p.sale,var)
    if var=='horizon':return h
    if var=='loan_balance':return p.loan.balance
    if var=='sale_price':return p.sale.explicit_terminal_prices.get(h,p.total_value*(1+a.appreciation)**h)
    raise ValueError('Unsupported variable')

def change(p,a,h,var,value):
    if var not in VARIABLES:raise ValueError('Unsupported variable')
    if var in ('appreciation','hoa_growth','property_tax_growth','discount_rate'):a=replace(a,**{var:value})
    elif var in ('monthly_rent','vacancy','lease_up_months'):p=replace(p,rental=replace(p.rental,**{var:value}))
    elif var in ('maintenance_annual','insurance_annual'):p=replace(p,**{var:value})
    elif var in ('brokerage_rate','closing_fixed'):p=replace(p,sale=replace(p.sale,**{var:value}))
    elif var=='horizon':
        if type(value)!=int or value not in (1,3,5,10):raise ValueError('Unsupported horizon')
        h=value
    elif var=='loan_balance':p=replace(p,loan=replace(p.loan,balance=value))
    elif var=='sale_price':p=replace(p,sale=replace(p.sale,explicit_terminal_prices={**p.sale.explicit_terminal_prices,h:value}))
    validate(p,a);return p,a,h

def applies(p,var,strategy):
    if var in ('monthly_rent','vacancy','lease_up_months'):return strategy=='rent_out'
    if var in ('appreciation','hoa_growth','property_tax_growth','maintenance_annual','insurance_annual','sale_price'):return strategy!='sell'
    return True

CATALOG=('base','negative_appreciation','zero_appreciation','moderate_appreciation','higher_appreciation',
 'rent_decline','stable_rent','rent_growth','higher_vacancy','lease_up_delay','hoa_escalation','property_tax_escalation',
 'insurance_increase','major_maintenance','special_assessment','interest_rate_up','refinancing_costs','higher_loan_payoff',
 'exit_price_down','brokerage_up','closing_costs_up','exit_1y','exit_3y','exit_5y','exit_10y')

def _scenario(p,a,h,name):
    p0,a0,h0=p,a,h
    mapping={'negative_appreciation':('appreciation',-.03),'zero_appreciation':('appreciation',0.),'moderate_appreciation':('appreciation',.025),'higher_appreciation':('appreciation',.05),
        'higher_vacancy':('vacancy',.20),'lease_up_delay':('lease_up_months',6),'hoa_escalation':('hoa_growth',.10),'property_tax_escalation':('property_tax_growth',.08),
        'insurance_increase':('insurance_annual',p.insurance_annual*1.25),'higher_loan_payoff':('loan_balance',p.loan.balance*1.10),
        'exit_price_down':('sale_price',baseline_value(p,a,h,'sale_price')*.90),'brokerage_up':('brokerage_rate',p.sale.brokerage_rate+.01),'closing_costs_up':('closing_fixed',p.sale.closing_fixed+2000)}
    if name in mapping:p,a,h=change(p,a,h,*mapping[name])
    elif name in ('rent_decline','stable_rent','rent_growth'):p=replace(p,rental=replace(p.rental,rent_growth={'rent_decline':-.02,'stable_rent':0.,'rent_growth':.03}[name]))
    elif name=='major_maintenance':p=replace(p,major_capex={**p.major_capex,3:p.major_capex.get(3,0)+20000})
    elif name=='special_assessment':p=replace(p,special_assessments={**p.special_assessments,2:p.special_assessments.get(2,0)+15000},assessment_treatment='capital')
    elif name=='interest_rate_up':
        if p.loan.rate_type!='adjustable' or not p.loan.balance:return {'name':name,'status':'NOT_APPLICABLE','reason':'Rate shock needs adjustable outstanding debt','version':VERSION}
        p=replace(p,loan=replace(p.loan,rate_changes={**p.loan.rate_changes,2:p.loan.annual_rate+.02}))
    elif name=='refinancing_costs':
        if not p.loan.balance:return {'name':name,'status':'NOT_APPLICABLE','reason':'No existing debt to refinance','version':VERSION}
        if p.loan.refinance:return {'name':name,'status':'UNSUPPORTED','reason':'Would overwrite supplied refinancing','version':VERSION}
        p=replace(p,loan=replace(p.loan,refinance=Refinance(2,.042,240,6000)))
    elif name.startswith('exit_') and name.endswith('y'):
        h=int(name[5:-1])
        if h not in (1,3,5,10):raise ValueError('Unknown exit horizon')
    elif name!='base':raise ValueError('Unknown scenario')
    validate(p,a)
    assumptions={'property':asdict(p),'assumptions':asdict(a),'horizon':h}
    before={'property':asdict(p0),'assumptions':asdict(a0),'horizon':h0}
    version=fingerprint({'scenario_version':VERSION,'name':name,'inputs':assumptions,'baseline_inputs':before})
    return {'name':name,'version':VERSION,'scenario_hash':version,'baseline_hash':fingerprint(before),'status':'READY','assumptions':assumptions,
        'probability':None,'classification':'DETERMINISTIC_HYPOTHETICAL_NOT_A_FORECAST','pair':(p,a,h)}

def scenario(p,a,h,name):
    if name not in CATALOG:raise ValueError('Unknown scenario')
    try:return _scenario(p,a,h,name)
    except (ValueError,TypeError,OverflowError) as e:return {'name':name,'version':VERSION,'status':'UNSUPPORTED','reason':str(e),'baseline_hash':fingerprint({'property':asdict(p),'assumptions':asdict(a),'horizon':h})}
