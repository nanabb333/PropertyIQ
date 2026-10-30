"""Entirely fictional property-level assumptions, independent of metro observations."""
from dataclasses import replace
from src.finance.schema import Acquisition,Loan,Rental,Sale,Tax,Property,Assumptions

def demos():
    vals=[('47900','SYNTHETIC_DC_CONDO',650000,3100,320000,600,5200,1200,2800,2019,490000,900),
          ('37980','SYNTHETIC_PHILADELPHIA_HOME',360000,2200,0,0,4400,1500,3200,2020,280000,1500),
          ('38300','SYNTHETIC_PITTSBURGH_HOME',240000,1750,135000,0,3600,1300,2800,2021,190000,1300)]
    result=[]
    for market,pid,value,rent,balance,hoa,ptax,insurance,maintenance,year,purchase,area in vals:
        acq=Acquisition(purchase,f'{year}-06-01',purchase*.025,12000,purchase*.3 if balance else purchase,purchase*.7 if balance else 0,'fictional individual sole owner')
        loan=Loan(balance,.05 if balance else 0,240 if balance else 0,rate_type='adjustable' if market=='38300' else 'fixed')
        tax=Tax(mode='illustrative',residency='FICTIONAL_US_RESIDENT',jurisdiction='ILLUSTRATIVE_ONLY_'+market,current_adjusted_basis=purchase+12000,prior_depreciation=0,
            depreciable_basis_remaining=purchase*.7,annual_depreciation=7000 if value>400000 else 5000,capital_gain_rate=.20,recapture_rate=.25,rental_income_rate=.25,withholding_rate=0,deductible_sale_cost_fraction=1,other_sale_tax_fixed=0)
        prop=Property(pid,market,'fictional condo' if hoa else 'fictional detached',value,acq,Rental(rent,.06,.025,.08,1,800,150,600,1200,2),Sale(.05,.015,2000,2500),loan,tax,area,
            parking_ownership='owned' if hoa else 'none',parking_value=25000 if hoa else 0,value_includes_parking=True,hoa_monthly=hoa,property_tax_annual=ptax,insurance_annual=insurance,maintenance_annual=maintenance,owner_occupancy_utilities_annual=2400)
        a=Assumptions('2026-10-28',.06,.025,.025,.04,.03,'common_housing',rent,.025,rent,False,False,None,0,None)
        result.append((prop,a))
    return result
