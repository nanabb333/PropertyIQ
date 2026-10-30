"""Versioned explicit inputs. Amounts nominal USD; annual rates decimal, not percent."""
from dataclasses import dataclass,field,asdict
from datetime import date
import math

@dataclass(frozen=True)
class Acquisition:
    purchase_price:float
    acquisition_date:str
    closing_costs:float=0
    capital_improvements:float=0
    initial_equity:float|None=None
    original_loan_amount:float|None=None
    ownership_structure:str|None=None

@dataclass(frozen=True)
class Refinance:
    year:int
    annual_rate:float
    term_months:int
    closing_cost:float=0
    new_loan_amount:float|None=None
    prepayment_cost:float|None=None
    new_prepayment_cost:float=0

@dataclass(frozen=True)
class Loan:
    balance:float=0
    annual_rate:float=0
    remaining_months:int=0
    monthly_payment:float|None=None
    prepayment_cost:float=0
    rate_type:str='fixed'
    rate_changes:dict[int,float]=field(default_factory=dict)
    refinance:Refinance|None=None

@dataclass(frozen=True)
class Rental:
    monthly_rent:float
    vacancy:float=.05
    rent_growth:float=.02
    management_rate:float=0
    leasing_months_per_year:float=0
    repairs_annual:float=0
    capex_reserve_monthly:float=0
    owner_utilities_annual:float=0
    tenant_utilities_annual:float=0
    lease_up_months:int=0

@dataclass(frozen=True)
class Sale:
    brokerage_rate:float
    transfer_recordation_rate:float
    closing_fixed:float=0
    repair_staging:float=0
    explicit_terminal_prices:dict[int,float]=field(default_factory=dict)

@dataclass(frozen=True)
class Tax:
    mode:str='not_modeled'
    residency:str|None=None
    jurisdiction:str|None=None
    current_adjusted_basis:float|None=None
    prior_depreciation:float|None=None
    depreciable_basis_remaining:float|None=None
    annual_depreciation:float|None=None
    capital_gain_rate:float|None=None
    recapture_rate:float|None=None
    rental_income_rate:float|None=None
    withholding_rate:float|None=None
    deductible_sale_cost_fraction:float|None=None
    other_sale_tax_fixed:float|None=None
    settlement_delay_months:int=0

@dataclass(frozen=True)
class Property:
    property_id:str
    market:str
    property_type:str
    current_value:float
    acquisition:Acquisition
    rental:Rental
    sale:Sale
    loan:Loan=field(default_factory=Loan)
    tax:Tax=field(default_factory=Tax)
    interior_sqft:float|None=None
    parking_ownership:str='none'
    parking_value:float=0
    value_includes_parking:bool=True
    hoa_monthly:float=0
    property_tax_annual:float=0
    insurance_annual:float=0
    maintenance_annual:float=0
    owner_occupancy_utilities_annual:float=0
    special_assessments:dict[int,float]=field(default_factory=dict)
    assessment_treatment:str='capital'
    major_capex:dict[int,float]=field(default_factory=dict)
    is_synthetic:bool=True

    @property
    def total_value(self):return self.current_value+(self.parking_value if self.parking_ownership=='owned' and not self.value_includes_parking else 0)

@dataclass(frozen=True)
class Assumptions:
    valuation_date:str
    discount_rate:float
    inflation:float
    appreciation:float
    hoa_growth:float
    property_tax_growth:float
    housing_mode:str='property_only'
    alternative_housing_monthly:float|None=None
    housing_rent_growth:float=0
    avoided_rent_monthly:float|None=None
    include_avoided_rent:bool=False
    reinvest_sale_proceeds:bool=False
    alternative_return:float|None=None
    cash_accumulation_rate:float=0
    investment_return_tax_rate:float|None=None


def finite(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def nonnegative(v,name):
    if not finite(v) or v<0:raise ValueError('Nonnegative finite '+name+' required')
def rate(v,name,negative=False):
    if not finite(v) or v<=-1 or (not negative and not 0<=v<=1):raise ValueError('Invalid decimal '+name)

def validate(p,a):
    date.fromisoformat(a.valuation_date);date.fromisoformat(p.acquisition.acquisition_date)
    if p.acquisition.acquisition_date>a.valuation_date:raise ValueError('Future acquisition')
    if not p.property_id or p.market not in ('47900','37980','38300'):raise ValueError('Missing/unsupported property market')
    if p.current_value<=0 or not finite(p.current_value):raise ValueError('Positive current value required')
    for name in ('hoa_monthly','property_tax_annual','insurance_annual','maintenance_annual','owner_occupancy_utilities_annual','parking_value'):nonnegative(getattr(p,name),name)
    if p.interior_sqft is not None and (not finite(p.interior_sqft) or p.interior_sqft<=0):raise ValueError('Invalid area')
    if p.parking_ownership not in ('none','owned','leased','unknown') or (p.parking_ownership!='owned' and p.parking_value):raise ValueError('Unsupported/nonowned parking valuation')
    if p.assessment_treatment not in ('capital','operating'):raise ValueError('Assessment classification required')
    for d in (p.special_assessments,p.major_capex,p.sale.explicit_terminal_prices):
        for year,v in d.items():
            if type(year)!=int or not 1<=year<=10:raise ValueError('Event year outside1..10')
            nonnegative(v,'event amount')
    for name in ('purchase_price','closing_costs','capital_improvements') :nonnegative(getattr(p.acquisition,name),name)
    for name in ('initial_equity','original_loan_amount'):
        if getattr(p.acquisition,name) is not None:nonnegative(getattr(p.acquisition,name),name)
    r=p.rental
    for name in ('monthly_rent','leasing_months_per_year','repairs_annual','capex_reserve_monthly','owner_utilities_annual','tenant_utilities_annual'):nonnegative(getattr(r,name),name)
    for name in ('vacancy','management_rate'):rate(getattr(r,name),name)
    rate(r.rent_growth,'rent_growth',True)
    if type(r.lease_up_months)!=int or not 0<=r.lease_up_months<=120:raise ValueError('Invalid lease-up period')
    for name in ('brokerage_rate','transfer_recordation_rate'):rate(getattr(p.sale,name),name)
    if p.sale.brokerage_rate+p.sale.transfer_recordation_rate>1:raise ValueError('Sale percentage costs exceed price')
    for name in ('closing_fixed','repair_staging'):nonnegative(getattr(p.sale,name),name)
    l=p.loan
    for name in ('balance','prepayment_cost'):nonnegative(getattr(l,name),name)
    rate(l.annual_rate,'loan annual rate')
    if type(l.remaining_months)!=int or l.remaining_months<0 or (l.balance and l.remaining_months==0):raise ValueError('Loan requires remaining amortization months')
    if l.monthly_payment is not None:nonnegative(l.monthly_payment,'monthly_payment')
    if l.rate_type not in ('fixed','adjustable') or (l.rate_changes and l.rate_type!='adjustable'):raise ValueError('Fixed loan cannot reset its rate')
    for year,v in l.rate_changes.items():
        if type(year)!=int or not 1<=year<=10:raise ValueError('Invalid rate-reset year')
        rate(v,'reset rate')
    if l.refinance:
        ref=l.refinance
        if type(ref.year)!=int or not 1<=ref.year<=10 or type(ref.term_months)!=int or ref.term_months<=0:raise ValueError('Invalid refinancing term/year')
        rate(ref.annual_rate,'refinance rate');nonnegative(ref.closing_cost,'refinance closing');nonnegative(ref.new_prepayment_cost,'new prepayment fee')
        for name in ('new_loan_amount','prepayment_cost'):
            if getattr(ref,name) is not None:nonnegative(getattr(ref,name),name)
        if ref.year in l.rate_changes:raise ValueError('Refinance and reset collide in same year')
    if p.tax.mode not in ('not_modeled','illustrative'):raise ValueError('Tax mode must be explicit')
    for name in ('current_adjusted_basis','prior_depreciation','depreciable_basis_remaining','annual_depreciation','other_sale_tax_fixed'):
        if getattr(p.tax,name) is not None:nonnegative(getattr(p.tax,name),name)
    for name in ('capital_gain_rate','recapture_rate','rental_income_rate','withholding_rate','deductible_sale_cost_fraction'):
        if getattr(p.tax,name) is not None:rate(getattr(p.tax,name),name)
    if p.tax.settlement_delay_months!=0:raise ValueError('Only explicit same-period tax settlement supported')
    if p.tax.depreciable_basis_remaining is not None and p.tax.current_adjusted_basis is not None and p.tax.depreciable_basis_remaining>p.tax.current_adjusted_basis:raise ValueError('Depreciable remaining basis exceeds total adjusted basis')
    for name in ('discount_rate','inflation','appreciation','hoa_growth','property_tax_growth','housing_rent_growth','cash_accumulation_rate'):rate(getattr(a,name),name,True)
    if a.housing_mode not in ('property_only','common_housing'):raise ValueError('Invalid housing comparison mode')
    if a.housing_mode=='common_housing' and a.alternative_housing_monthly is None:raise ValueError('Common housing requires alternative rent')
    if a.include_avoided_rent and (a.avoided_rent_monthly is None or a.housing_mode=='common_housing'):raise ValueError('Avoided rent missing or double counted')
    for name in ('alternative_housing_monthly','avoided_rent_monthly'):
        if getattr(a,name) is not None:nonnegative(getattr(a,name),name)
    if a.reinvest_sale_proceeds and a.alternative_return is None:raise ValueError('Reinvestment return must be explicit')
    if not a.reinvest_sale_proceeds and a.alternative_return is not None:raise ValueError('Return supplied without explicit reinvestment')
    if a.alternative_return is not None:rate(a.alternative_return,'alternative return',True)
    if a.investment_return_tax_rate is not None:rate(a.investment_return_tax_rate,'investment tax')

def from_dict(d):
    x=dict(d['property']);x['acquisition']=Acquisition(**x['acquisition']);x['rental']=Rental(**x['rental']);sale=dict(x['sale']);sale['explicit_terminal_prices']={int(k):v for k,v in sale.get('explicit_terminal_prices',{}).items()};x['sale']=Sale(**sale)
    loan=dict(x.get('loan',{}));loan['rate_changes']={int(k):v for k,v in loan.get('rate_changes',{}).items()}
    if loan.get('refinance'):loan['refinance']=Refinance(**loan['refinance'])
    x['loan']=Loan(**loan);x['tax']=Tax(**x.get('tax',{}))
    for k in ('special_assessments','major_capex'):x[k]={int(y):v for y,v in x.get(k,{}).items()}
    return Property(**x),Assumptions(**d['assumptions'])
