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


def case(case_index=0, horizon=5, appreciation=.025, vacancy=.06, tax_complete=False):
    if type(case_index) is not int or case_index not in (0,1,2): raise ValueError('Unknown fictional case')
    if horizon not in (1,3,5,10): raise ValueError('Unsupported financial horizon')
    if type(tax_complete) is not bool: raise ValueError('Explicit synthetic tax state required')
    prop,assumptions=demos()[case_index]
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


def sensitivity(prop, assumptions, horizon):
    return one_way(prop,assumptions,horizon,'appreciation',[-.03,0.,.025,.05])


def evidence(question, prop, assumptions, result, horizon):
    """Six deterministic read-only routes; no LLM, tools chosen by a provider, or IO."""
    if question not in QUESTIONS: raise ValueError('Choose a fixed evidence question')
    if question=='Financial grounding':
        return {'route':'financial_compare','rows':financial_rows(result),'assumptions_sha256':fingerprint(result['assumptions'])}
    if question=='Scenario sensitivity':
        rows=sensitivity(prop,assumptions,horizon)
        return {'route':'sensitivity','scenarios':len(rows),'probabilities_assigned':False,'input_sha256':fingerprint(result['assumptions'])}
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
