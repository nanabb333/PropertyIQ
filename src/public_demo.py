"""Public edition: deterministic synthetic evidence, never a data-source fallback."""
import hashlib
import json
import math
from dataclasses import asdict, replace
from datetime import date
from src.finance.demo import demos
from src.finance.engine import compare
from src.finance.sensitivity import one_way

GENERATOR = 'propertyiq-fictional-market-v1'
MARKETS = ('Harbor', 'Cedar', 'Summit')
WORKFLOWS = ('Market explorer', 'Financial comparison', 'Scenario lab',
             'Forecast lab', 'Evidence explorer', 'Human review')
QUESTIONS = ('Financial grounding', 'Scenario sensitivity', 'Forecast provenance',
             'Missing tax information', 'Reviewer authority', 'Data provenance')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def fingerprint(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def month(index):
    return date(2015 + index // 12, 1 + index % 12, 1).isoformat()


def synthetic_markets():
    """120 invented months, 3 invented markets. No observed inputs or fitted parameters."""
    rows = []
    for j, name in enumerate(MARKETS):
        for t in range(120):
            price = 100 * math.exp((.0015 + j*.0003)*t + .025*math.sin(t/7+j)
                                   - .06*math.exp(-((t-72-j*3)/8)**2))
            rent = 100 * math.exp((.0018+j*.0002)*t + .018*math.sin(t/6+j))
            rows.append({'month': month(t), 'market': name, 'price_index': price,
                         'rent_index': rent, 'classification': 'SYNTHETIC'})
    return rows


def provenance():
    return {'classification': 'SYNTHETIC_ONLY', 'generator': GENERATOR,
            'period': ['2015-01-01', '2024-12-01'], 'rows': 360,
            'sha256': fingerprint(synthetic_markets()),
            'external_data_used': False, 'calibrated_to_real_data': False}


def forecast(history, horizon, model):
    if horizon not in (3,6,9,12) or len(history)<60:
        raise ValueError('60 training months and a supported horizon required')
    if any(not math.isfinite(x) or x<=0 for x in history):
        raise ValueError('Positive finite synthetic index required')
    if model=='No change': return history[-1]
    if model=='12-month trend': return history[-1]*(history[-1]/history[-13])**(horizon/12)
    if model=='Seasonal naive': return history[len(history)-1+horizon-12]
    raise ValueError('Unsupported baseline')


def backtest(horizon=6):
    if horizon not in (3,6,9,12): raise ValueError('Unsupported horizon')
    records=[]
    rows=synthetic_markets()
    for name in MARKETS:
        values=[r['price_index'] for r in rows if r['market']==name]
        for origin in range(59,len(values)-horizon):
            history=values[:origin+1]  # The forecast never receives its target/future.
            actual_growth=100*math.log(values[origin+horizon]/values[origin])
            for model in ('No change','12-month trend','Seasonal naive'):
                predicted=forecast(history,horizon,model)
                growth=100*math.log(predicted/values[origin])
                records.append({'market':name,'model':model,'origin':month(origin),
                                'target':month(origin+horizon),'training_months':len(history),
                                'horizon_months':horizon,'predicted_growth_pp':growth,
                                'actual_growth_pp':actual_growth,'error_pp':growth-actual_growth,
                                'classification':'SYNTHETIC_EXPERIMENT'})
    return records


def scores(horizon=6):
    records=backtest(horizon)
    result=[]
    for market in MARKETS:
        for model in ('No change','12-month trend','Seasonal naive'):
            group=[r for r in records if r['market']==market and r['model']==model]
            errors=[r['error_pp'] for r in group]
            result.append({'Market':market,'Baseline':model,'Origins':len(errors),
                           'MAE (log-growth pp)':sum(abs(x) for x in errors)/len(errors),
                           'RMSE (log-growth pp)':math.sqrt(sum(x*x for x in errors)/len(errors))})
    return result


def case(case_index=0, horizon=5, appreciation=.025, vacancy=.06, tax_complete=False,
         current_value=None):
    if type(case_index) is not int or case_index not in (0,1,2): raise ValueError('Unknown fictional case')
    if horizon not in (1,3,5,10): raise ValueError('Unsupported financial horizon')
    if type(tax_complete) is not bool: raise ValueError('Explicit synthetic tax state required')
    prop,assumptions=demos()[case_index]
    if current_value is not None:
        if type(current_value) not in (int,float) or not math.isfinite(current_value) or current_value<=0:
            raise ValueError('Current market value must be a positive finite number')
        prop=replace(prop,current_value=current_value)
    prop=replace(prop,property_id='SYNTHETIC_'+MARKETS[case_index].upper(),
                 rental=replace(prop.rental,vacancy=vacancy))
    if not tax_complete:
        prop=replace(prop,tax=replace(prop.tax,current_adjusted_basis=None))
    assumptions=replace(assumptions,appreciation=appreciation)
    return prop,assumptions,compare(prop,assumptions,horizon)


def financial_rows(result):
    return [{'Strategy':{'hold_occupy':'Hold / occupy','sell':'Sell / hold cash','rent_out':'Rent out'}[s['strategy']],
             'Pre-tax NPV ($)':s['pretax']['npv'],
             'Terminal wealth ($)':s['terminal_wealth_before_tax'],
             'After-tax NPV ($)':s['after_tax']['npv'] if s['after_tax'] else None}
            for s in result['strategies']]


def sensitivity(prop, assumptions, horizon, context=None):
    rows=one_way(prop,assumptions,horizon,'appreciation',[-.03,0.,.025,.05])
    if context and 'property_profile' in context['assumptions']:
        for row in rows:
            row['profile_version']=context['assumptions']['profile_version']
            row['profile_sha256']=fingerprint(context['assumptions']['property_profile'])
            row['financial_input_sources']=context['assumptions']['financial_input_sources']
            row['applied_synthetic_receipts']=context['assumptions']['applied_synthetic_receipts']
            row['units']={'appreciation':'annual decimal rate','npv':'USD','terminal_wealth':'USD'}
            row['review_requirement']='Explicit human review; no ranking or recommendation.'
    return rows


def evidence(question, prop, assumptions, result, horizon):
    """Six deterministic read-only routes; no LLM, tools chosen by a provider, or IO."""
    if question not in QUESTIONS: raise ValueError('Choose a fixed evidence question')
    if question=='Financial grounding':
        return {'route':'financial_compare','rows':financial_rows(result),'assumptions_sha256':fingerprint(result['assumptions']),
                'profile':result.get('profile_summary'),'financial_input_sources':result['assumptions'].get('financial_input_sources'),
                'scenario_provenance':result.get('profile_scenario'),
                'applied_synthetic_receipts':result['assumptions'].get('applied_synthetic_receipts')}
    if question=='Scenario sensitivity':
        rows=sensitivity(prop,assumptions,horizon,result)
        return {'route':'sensitivity','scenarios':len(rows),'probabilities_assigned':False,'input_sha256':fingerprint(result['assumptions']),
                'profile_version':result['assumptions'].get('profile_version'),
                'financial_input_sources':result['assumptions'].get('financial_input_sources'),
                'applied_synthetic_receipts':result['assumptions'].get('applied_synthetic_receipts'),
                'units':{'appreciation':'annual decimal rate','npv':'USD'},
                'limitations':'Hypothetical sensitivity, no local market evidence or validated forecast; human review required.'}
    if question=='Forecast provenance':
        return {'route':'forecast_provenance','generator':provenance(),'horizons':[3,6,9,12],
                'training_minimum_months':60,'real_world_accuracy_validated':False,'future_outcomes_verified':False}
    if question=='Missing tax information':
        return {'route':'tax_status','tax_status':result['tax_status'],'missing_information':result['missing_information']}
    if question=='Reviewer authority':
        return {'route':'reviewer_control','automatic_choice':False,'can_finalize':False,
                'message':'Only an explicit human action records a local demonstration choice.'}
    return {'route':'data_provenance',**provenance()}


def review_packet(result, choice, confirmed):
    if choice not in ('Hold','Sell','Rent out','Undecided') or confirmed is not True:
        raise ValueError('Explicit human choice and confirmation required')
    return {'classification':'SYNTHETIC_REVIEW_DEMONSTRATION','choice':choice,
            'decision_authority':'HUMAN_LOCAL_DEMO_ONLY','identity_verified':False,
            'ranking_performed':False,'input_sha256':fingerprint(result['assumptions']),
            'production_record':False,'financial_result':financial_rows(result)}

# Property profile, validation and authored fixtures are separate from the engine.
# This module remains a pure adapter: no filesystem, logging or network access.
from dataclasses import dataclass
import re

PROFILE_VERSION = 'synthetic-property-profile-v1.2'
PROPERTY_TYPES = ('Condominium','Single-family home','Townhouse','Multifamily','Other')
LAYOUTS = {'Studio':(0,1.),'1 Bed / 1 Bath':(1,1.),'2 Bed / 1 Bath':(2,1.),
           '2 Bed / 2 Bath':(2,2.),'3 Bed / 2 Bath':(3,2.)}

@dataclass(frozen=True)
class PropertyProfile:
    zip_code:str='20008'
    property_type:str='Condominium'
    layout:str='2 Bed / 2 Bath'
    bedrooms:int=2
    bathrooms:float=2.
    interior_sqft:float=900.
    parking_spaces:int|None=None
    year_built:int|None=None

    def validate(self):
        if not isinstance(self.zip_code,str) or re.fullmatch(r'[0-9]{5}',self.zip_code) is None:
            raise ValueError('ZIP must contain exactly five ASCII digits; postal assignment is not verified.')
        if self.property_type not in PROPERTY_TYPES:raise ValueError('Unsupported property type.')
        if self.layout not in (*LAYOUTS,'Custom'):raise ValueError('Unsupported layout.')
        if type(self.bedrooms)!=int or not 0<=self.bedrooms<=20:raise ValueError('Bedrooms must be an integer from 0 to 20.')
        if type(self.bathrooms) not in (int,float) or not math.isfinite(self.bathrooms) or not 0<self.bathrooms<=20:
            raise ValueError('Bathrooms must be positive and no greater than 20.')
        if self.layout in LAYOUTS and (self.bedrooms,self.bathrooms)!=LAYOUTS[self.layout]:
            raise ValueError('Bedroom/bathroom counts must match the selected standard layout.')
        if type(self.interior_sqft) not in (int,float) or not math.isfinite(self.interior_sqft) or self.interior_sqft<=0:
            raise ValueError('Interior area must be positive finite square feet.')
        if self.parking_spaces is not None and (type(self.parking_spaces)!=int or not 0<=self.parking_spaces<=20):
            raise ValueError('Parking spaces must be unknown or an integer from 0 to 20.')
        if self.year_built is not None and (type(self.year_built)!=int or not 1600<=self.year_built<=2026):
            raise ValueError('Year built must be unknown or an integer from 1600 to 2026 (fixture version limit).')
        return self

# ZIP strings select authored demonstrations only. No mapping to city, geography,
# observed rent, comparable sales or fitted market parameters is claimed.
SYNTHETIC_ZIP_FIXTURES = {
    '20008':(2400.,350.,1000.,2000.),
    '19103':(1800.,250.,1200.,2300.),
    '15213':(1300.,150.,1100.,2600.),
}
GENERIC_FIXTURE = (1500.,200.,1200.,2400.)
SUGGESTION_UNITS = {'monthly_rent':'USD/month','hoa_monthly':'USD/month',
                    'insurance_annual':'USD/year','maintenance_annual':'USD/year'}
TYPE_FACTORS = {'Condominium':(1.,1.),'Single-family home':(1.1,0.),
                'Townhouse':(1.05,.5),'Multifamily':(1.6,0.),'Other':(1.,.5)}

def synthetic_profile_scenario(profile):
    profile.validate()
    supported=profile.zip_code in SYNTHETIC_ZIP_FIXTURES
    rent,hoa,insurance,maintenance=SYNTHETIC_ZIP_FIXTURES.get(profile.zip_code,GENERIC_FIXTURE)
    area_factor=min(2.,max(.5,profile.interior_sqft/1000.))
    type_factor,hoa_factor=TYPE_FACTORS[profile.property_type]
    layout_factor={'Studio':.7,'1 Bed / 1 Bath':.85,'2 Bed / 1 Bath':.95,
                   '2 Bed / 2 Bath':1.,'3 Bed / 2 Bath':1.15}.get(profile.layout,
                   .7+.15*profile.bedrooms+.05*profile.bathrooms)
    values={'monthly_rent':round(rent*area_factor*type_factor*layout_factor,2),
            'hoa_monthly':round(hoa*hoa_factor,2),'insurance_annual':insurance,
            'maintenance_annual':maintenance}
    return {'version':PROFILE_VERSION,'fixture':'ZIP_TOKEN_'+profile.zip_code if supported else 'GENERIC_FALLBACK',
            'source':'Synthetic illustrative assumptions — not observed ZIP-level data',
            'supported_synthetic_fixture':supported,'observed_market_evidence':False,
            'profile_sha256':fingerprint(asdict(profile)),
            'suggestions':{k:{'value':v,'unit':SUGGESTION_UNITS[k],'source':'Authored synthetic fixture',
                'definition':('Base rent × clipped area factor × property-type factor × layout factor' if k=='monthly_rent' else
                              'Base HOA × property-type HOA factor' if k=='hoa_monthly' else 'Fixed authored annual fixture amount')} for k,v in values.items()},
            'formula_inputs':{'base_rent':rent,'base_hoa':hoa,'area_factor':area_factor,'type_factor':type_factor,
                              'hoa_factor':hoa_factor,'layout_factor':layout_factor},
            'limitations':['ZIP format only; no postal assignment or city/state mapping verified.',
                'Illustrative assumptions, not local benchmarks, valuations or validated forecasts.',
                'No probability, ranking or investment recommendation; human review required.',
                'Parking/year built are descriptive and do not change financial assumptions.']}


def apply_profile_suggestions(financial,profile,*,confirmed=False):
    if confirmed is not True:raise ValueError('Explicit confirmation required to apply synthetic suggestions.')
    proposal=synthetic_profile_scenario(profile)
    updated=dict(financial)
    updated.update({k:v['value'] for k,v in proposal['suggestions'].items()})
    return updated,proposal


def profile_summary(profile,current_value):
    profile.validate()
    if type(current_value) not in (int,float) or not math.isfinite(current_value) or current_value<=0:
        raise ValueError('Current market value must be positive and finite.')
    unit_value=current_value/profile.interior_sqft
    if not math.isfinite(unit_value):raise ValueError('Calculated value per square foot exceeds the finite numerical range.')
    return {**asdict(profile),'current_value':current_value,'value_per_sqft':unit_value,
            'value_per_sqft_definition':'Entered current value / entered interior square feet; USD/sq ft, not an estimated market price.',
            'market_evidence':'Unavailable: no local observations, appraisal, geocoding or comparable sales.'}


def profile_financial_defaults(case_index=0):
    if type(case_index)!=int or case_index not in (0,1,2):raise ValueError('Unknown fictional case.')
    p,_=demos()[case_index]
    return {'current_value':p.current_value,'purchase_price':p.acquisition.purchase_price,
            'loan_balance':p.loan.balance,'monthly_rent':p.rental.monthly_rent,
            'hoa_monthly':p.hoa_monthly,'property_tax_annual':p.property_tax_annual,
            'insurance_annual':p.insurance_annual,'maintenance_annual':p.maintenance_annual,
            'loan_annual_rate':p.loan.annual_rate,'loan_remaining_months':p.loan.remaining_months or 240,
            'tax_basis':p.tax.current_adjusted_basis}


def profile_case(profile,financial,case_index=0,horizon=5,appreciation=.025,vacancy=.06,
                 tax_complete=False,sources=None,applied_receipts=None):
    profile.validate()
    expected=set(profile_financial_defaults(case_index))
    if set(financial)!=expected:raise ValueError('Only the closed set of financial input fields is accepted.')
    for k,v in financial.items():
        if type(v) not in (int,float) or not math.isfinite(v) or v<0:
            raise ValueError('Financial inputs must be finite nonnegative numbers.')
        if k not in ('loan_annual_rate','loan_remaining_months') and v>1000000000.:
            raise ValueError('Demonstration monetary inputs are limited to USD one billion.')
    if financial['current_value']<=0 or not 0<=financial['loan_annual_rate']<=1:
        raise ValueError('Positive market value and a decimal loan rate between 0 and 1 required.')
    if type(financial['loan_remaining_months'])!=int or not 1<=financial['loan_remaining_months']<=600:
        raise ValueError('Loan term must be an integer from 1 to 600 months.')
    p,a,_=case(case_index,horizon,appreciation,vacancy,tax_complete,financial['current_value'])
    p=replace(p,property_type=profile.property_type,interior_sqft=profile.interior_sqft,
        acquisition=replace(p.acquisition,purchase_price=financial['purchase_price']),
        loan=replace(p.loan,balance=financial['loan_balance'],annual_rate=financial['loan_annual_rate'],
                     remaining_months=financial['loan_remaining_months']),
        rental=replace(p.rental,monthly_rent=financial['monthly_rent']),
        hoa_monthly=financial['hoa_monthly'],property_tax_annual=financial['property_tax_annual'],
        insurance_annual=financial['insurance_annual'],maintenance_annual=financial['maintenance_annual'],
        tax=replace(p.tax,current_adjusted_basis=financial['tax_basis'] if tax_complete else None))
    result=compare(p,a,horizon)
    allowed_sources={'Synthetic template default','User input'}
    provenance=dict(sources) if sources is not None else {k:'Synthetic template default' if v==profile_financial_defaults(case_index)[k] else 'User input' for k,v in financial.items()}
    if set(provenance)!=expected or any(v not in allowed_sources and v!='Explicitly applied synthetic fixture' for v in provenance.values()):
        raise ValueError('Closed provenance labels required for all financial inputs.')
    receipts=dict(applied_receipts or {})
    applied={k for k,v in provenance.items() if v=='Explicitly applied synthetic fixture'}
    if set(receipts)!=applied or not applied<=set(SUGGESTION_UNITS):
        raise ValueError('Each applied synthetic field requires an explicit application receipt.')
    for field,receipt in receipts.items():
        keys={'fixture','version','profile_sha256','source','value','unit','definition','formula_inputs'}
        if not isinstance(receipt,dict) or set(receipt)!=keys:
            raise ValueError('Closed synthetic application receipt required.')
        if (receipt['version']!=PROFILE_VERSION or receipt['fixture'] not in ('GENERIC_FALLBACK',*('ZIP_TOKEN_'+z for z in SYNTHETIC_ZIP_FIXTURES))
            or receipt['source']!='Synthetic illustrative assumptions — not observed ZIP-level data'
            or receipt['unit']!=SUGGESTION_UNITS[field] or receipt['value']!=financial[field]
            or not isinstance(receipt['profile_sha256'],str) or re.fullmatch('[a-f0-9]{64}',receipt['profile_sha256']) is None):
            raise ValueError('Synthetic receipt does not match the applied field.')
    result['assumptions']['applied_synthetic_receipts']=receipts
    result['assumptions']['property_profile']=asdict(profile)
    result['assumptions']['financial_input_sources']=provenance
    result['assumptions']['profile_version']=PROFILE_VERSION
    result['profile_summary']=profile_summary(profile,p.current_value)
    result['profile_scenario']=synthetic_profile_scenario(profile)
    result['profile_scenario']['application']='Suggestions are not implicitly applied; financial_input_sources records explicit selections.'
    return p,a,result
