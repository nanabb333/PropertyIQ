"""Deterministic, unweighted alternatives; none is asserted most likely."""
from dataclasses import replace
from src.finance.schema import Refinance

NAMES=('base','bear_value','bull_value','rent_decline','stable_rent','moderate_rent_growth','high_vacancy','hoa_increase','property_tax_increase','major_maintenance','special_assessment','arm_rate_up','explicit_refinance')

def apply(prop,assumptions,name):
    p,a=prop,assumptions
    if name=='base':pass
    elif name=='bear_value':a=replace(a,appreciation=-.03)
    elif name=='bull_value':a=replace(a,appreciation=.05)
    elif name=='rent_decline':p=replace(p,rental=replace(p.rental,rent_growth=-.02))
    elif name=='stable_rent':p=replace(p,rental=replace(p.rental,rent_growth=0))
    elif name=='moderate_rent_growth':p=replace(p,rental=replace(p.rental,rent_growth=.03))
    elif name=='high_vacancy':p=replace(p,rental=replace(p.rental,vacancy=.20))
    elif name=='hoa_increase':a=replace(a,hoa_growth=.10)
    elif name=='property_tax_increase':a=replace(a,property_tax_growth=.08)
    elif name=='major_maintenance':p=replace(p,major_capex={**p.major_capex,3:p.major_capex.get(3,0)+20000})
    elif name=='special_assessment':p=replace(p,special_assessments={**p.special_assessments,2:p.special_assessments.get(2,0)+15000},assessment_treatment='capital')
    elif name=='arm_rate_up':
        if p.loan.rate_type!='adjustable' or not p.loan.balance:return None
        p=replace(p,loan=replace(p.loan,rate_changes={**p.loan.rate_changes,2:p.loan.annual_rate+.02}))
    elif name=='explicit_refinance':
        if not p.loan.balance:return None
        if p.loan.refinance:raise ValueError('Scenario would overwrite explicit refinancing')
        p=replace(p,loan=replace(p.loan,refinance=Refinance(2,.042,240,3500)))
    else:raise ValueError('Unknown scenario')
    return p,a
