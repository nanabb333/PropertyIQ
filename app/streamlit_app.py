"""Synthetic-only public Streamlit application. No ingestion or auth code imported."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from src.public_demo import (MARKETS,WORKFLOWS,QUESTIONS,case,financial_rows,synthetic_markets,
                             provenance,sensitivity,scores,evidence,review_packet,fingerprint,
                             PropertyProfile,PROPERTY_TYPES,LAYOUTS,profile_financial_defaults,
                             synthetic_profile_scenario,apply_profile_suggestions,profile_case)

st.set_page_config(page_title='PropertyIQ · Synthetic edition',page_icon='◈',layout='wide')
st.markdown('''<style>
.stApp{background:#f5f7fa;color:#152d40}h1,h2,h3{color:#152d40}
section[data-testid="stSidebar"]{background:#e9eef3}
div[data-testid="stMetric"]{background:white;border:1px solid #dce4eb;border-radius:10px;padding:16px}
.block-container{max-width:1320px;padding-top:2rem}button{border-radius:8px!important}
</style>''',unsafe_allow_html=True)
st.title('PropertyIQ')
st.caption('An inspectable real estate research workspace · public synthetic edition')
st.info('All markets, indices and property inputs here are fictional. No Zillow, FRED or other source data are included.')
def invalidate_review():
    for key in ('review_packet','review_choice','review_confirm','review_input_hash'):
        st.session_state.pop(key,None)


def financial_key(field,label):
    return 'current_value_'+label if field=='current_value' else 'finance_'+field+'_'+label


def mark_user_input(label,field):
    st.session_state['financial_sources_'+label][field]='User input'
    st.session_state.get('fixture_receipts_'+label,{}).pop(field,None)


def property_profile_panel(label,tax_complete):
    index=MARKETS.index(label)
    defaults=profile_financial_defaults(index)
    remembered=st.session_state.get('financial_values_'+label,defaults)
    draft=st.session_state.get('profile_values_'+label,{
        'zip_code':('20008','19103','15213')[index],
        'property_type':'Condominium' if index==0 else 'Single-family home',
        'layout':'2 Bed / 2 Bath','bedrooms':2,'bathrooms':2.,
        'interior_sqft':(900.,1500.,1300.)[index],'parking_spaces':None,'year_built':None})
    source_key='financial_sources_'+label
    if 'fixture_receipts_'+label not in st.session_state:st.session_state['fixture_receipts_'+label]={}
    if source_key not in st.session_state:
        st.session_state[source_key]={k:'Synthetic template default' for k in defaults}
    with st.expander('Property Profile — descriptive inputs',expanded=True):
        st.caption('Editable profile inputs · fictional template defaults, not verified observations. ZIP format is checked, not postal assignment. No city/state mapping or geocoding. The fictional case/CBSA compatibility codes and index series are not mapped to your ZIP.')
        zip_code=st.text_input('ZIP Code (5 digits)',value=draft['zip_code'],key='profile_zip_'+label)
        kind=st.selectbox('Property type',PROPERTY_TYPES,index=PROPERTY_TYPES.index(draft['property_type']),key='profile_type_'+label)
        layout=st.selectbox('Unit layout',(*LAYOUTS,'Custom'),index=(*LAYOUTS,'Custom').index(draft['layout']),key='profile_layout_'+label)
        if layout=='Custom':
            beds=st.number_input('Bedrooms',min_value=0,max_value=20,value=draft['bedrooms'],key='profile_beds_'+label)
            baths=st.number_input('Bathrooms',min_value=.5,max_value=20.,value=float(draft['bathrooms']),step=.5,key='profile_baths_'+label)
        else:beds,baths=LAYOUTS[layout]
        area=st.number_input('Interior area (sq ft)',min_value=0.,max_value=1000000.,value=float(draft['interior_sqft']),key='profile_area_'+label)
        parking=None;year=None
        if st.checkbox('Supply parking spaces',value=draft['parking_spaces'] is not None,key='profile_parking_known_'+label):
            parking=st.number_input('Parking spaces',min_value=0,max_value=20,value=draft['parking_spaces'] if draft['parking_spaces'] is not None else 1,key='profile_parking_'+label)
        if st.checkbox('Supply year built',value=draft['year_built'] is not None,key='profile_year_known_'+label):
            year=st.number_input('Year built',min_value=1600,max_value=2026,value=draft['year_built'] if draft['year_built'] is not None else 2000,key='profile_year_'+label)
        profile=PropertyProfile(zip_code,kind,layout,beds,baths,area,parking,year)
        st.session_state['profile_values_'+label]=profile.__dict__.copy()
        try:profile.validate()
        except ValueError as error:
            invalidate_review()
            st.error(str(error));st.stop()
    with st.expander('Synthetic suggestions — preview before applying'):
        proposal=synthetic_profile_scenario(profile)
        st.caption(proposal['source'])
        st.caption('Fixture: '+proposal['fixture']+' · '+proposal['version'])
        pending={k:st.session_state.get(financial_key(k,label),v) for k,v in remembered.items()}
        st.table([{'Field':k,'Current':pending[k],'Suggested':v['value'],'Units':v['unit']} for k,v in proposal['suggestions'].items()])
        st.caption('Only the four shown fields may be replaced. Market value, purchase price, mortgage and basis are never suggested or changed. ZIP/layout edits alone do not apply anything.')
        approved=st.checkbox('Replace the four shown fields with these synthetic suggestions',key='approve_fixture_'+label)
        if st.button('Apply synthetic suggestions',disabled=not approved,key='apply_fixture_'+label):
            updated,_=apply_profile_suggestions(pending,profile,confirmed=True)
            for k in proposal['suggestions']:
                st.session_state[financial_key(k,label)]=updated[k]
                st.session_state[source_key][k]='Explicitly applied synthetic fixture'
                st.session_state['fixture_receipts_'+label][k]={
                    'fixture':proposal['fixture'],'version':proposal['version'],
                    'profile_sha256':proposal['profile_sha256'],'source':proposal['source'],
                    **proposal['suggestions'][k],'formula_inputs':proposal['formula_inputs']}
                # Suggestion source labels differ from the overall scenario source.
                st.session_state['fixture_receipts_'+label][k]['source']=proposal['source']
            st.success('Only the four previewed assumptions applied. Every field remains editable.')
        st.json({'formula_inputs':proposal['formula_inputs'],'limitations':proposal['limitations']})
    financial={}
    labels={
        'current_value':('Current market value (USD)',1.),
        'purchase_price':('Original purchase price (USD)',0.),
        'loan_balance':('Outstanding mortgage balance (USD)',0.),
        'monthly_rent':('Monthly rent (USD/month)',0.),
        'hoa_monthly':('HOA / condo fees (USD/month)',0.),
        'property_tax_annual':('Property taxes (USD/year)',0.),
        'insurance_annual':('Insurance (USD/year)',0.),
        'maintenance_annual':('Maintenance operating expense (USD/year)',0.),
        'loan_annual_rate':('Annual mortgage rate (decimal)',0.),
        'loan_remaining_months':('Remaining mortgage term (months)',1),
        'tax_basis':('Adjusted tax basis (USD; separate from purchase price)',0.)}
    with st.expander('Financial inputs — independent assumptions',expanded=True):
        st.caption('Fictional template defaults or user inputs; no inferred local valuations. Session memory only. Do not enter personal records.')
        for field,(title,minimum) in labels.items():
            value=remembered[field]
            maximum=600 if field=='loan_remaining_months' else 1. if field=='loan_annual_rate' else 1000000000.
            financial[field]=st.number_input(title,min_value=minimum,max_value=maximum,
                value=None if financial_key(field,label) in st.session_state or value is None else int(value) if field=='loan_remaining_months' else float(value),
                key=financial_key(field,label),disabled=field=='tax_basis' and not tax_complete,
                on_change=mark_user_input,args=(label,field))
            st.caption('Source: '+st.session_state[source_key][field])
        st.caption('Maintenance excludes separately entered HOA, property taxes and insurance. Template utilities, rental repairs, management/leasing and reserves remain explicit in the annual schedule. Purchase price is historical; it does not infer equity, closing costs or adjusted basis. A zero loan balance may use the displayed term/rate for a later explicit balance edit.')
    st.session_state['financial_values_'+label]=dict(financial)
    return profile,financial,dict(st.session_state[source_key]),dict(st.session_state['fixture_receipts_'+label])


with st.sidebar:
    st.header('Workspace')
    page=st.radio('Workflow',WORKFLOWS)
    label=st.selectbox('Fictional property',MARKETS)
    horizon=st.select_slider('Financial horizon (years)',options=[1,3,5,10],value=5)
    appreciation=st.slider('Illustrative annual appreciation (%)',-5.,8.,2.5,.5)/100
    vacancy=st.slider('Illustrative rental vacancy (%)',0.,30.,6.,1.)/100
    tax_complete=st.checkbox('Use complete fictional tax assumptions',value=False)
    profile,financial,sources,receipts=property_profile_panel(label,tax_complete)
    st.caption('Unavailable market evidence: no local comps, geocoding, appraisal or validated property forecasts. Offline workflows; no login, Keychain or inference.')
try:
    prop,assumptions,result=profile_case(profile,financial,MARKETS.index(label),horizon,appreciation,vacancy,tax_complete,sources,receipts)
except (ValueError,OverflowError):
    invalidate_review()
    st.error('Financial assumptions are unsupported or inconsistent. Check positive value/area, loan settings and depreciation basis; no stale result is displayed.')
    st.stop()
summary=result['profile_summary']
st.caption(f"Property Profile · ZIP {profile.zip_code} · {profile.property_type} · {profile.bedrooms} bed / {profile.bathrooms:g} bath · {profile.interior_sqft:,.0f} sq ft · Current value ${prop.current_value:,.0f}")
st.caption(f"Calculated output: ${summary['value_per_sqft']:,.2f}/sq ft = entered value / entered interior area. Not an independent market price estimate.")
st.caption('Assumption sources: '+', '.join(sorted(set(sources.values())))+' · Market evidence unavailable.')
with st.expander('Profile, units and assumption evidence'):
    st.json({'model_inputs':result['assumptions'],'user_profile':summary,'financial_input_sources':sources,'applied_synthetic_receipts':receipts,'synthetic_suggestions':result['profile_scenario'],
             'review':'Human review required; no strategy is automatically ranked or selected.'})
current_hash=fingerprint(result['assumptions'])
if st.session_state.get('review_input_hash')!=current_hash:
    st.session_state.pop('review_packet',None)
    st.session_state.pop('review_choice',None)
    st.session_state.pop('review_confirm',None)
    st.session_state['review_input_hash']=current_hash

if page=='Market explorer':
    st.header('Invented markets, visible assumptions')
    st.write('Compare three independently invented index paths. Each is generated from an explicit mathematical formula, not calibrated to housing data.')
    rows=pd.DataFrame(synthetic_markets())
    rows['month']=pd.to_datetime(rows['month'])
    a,b,c=st.columns(3)
    a.metric('Fictional markets','3');b.metric('Months per market','120');c.metric('External observations','0')
    st.subheader('Synthetic price indices')
    st.caption('Dimensionless index · 2015–2024 demonstration period · arbitrary baseline near 100')
    st.line_chart(rows.pivot(index='month',columns='market',values='price_index'),height=310)
    st.subheader('Synthetic rent indices')
    st.line_chart(rows.pivot(index='month',columns='market',values='rent_index'),height=260)
    with st.expander('Generator and data lineage'):
        st.json(provenance());st.dataframe(rows.head(6),hide_index=True)

elif page=='Financial comparison':
    st.header('Hold, sell or rent: compare assumptions')
    st.caption('USD · nominal annual cash flows · common-housing comparison · fixed strategy order, no recommendation')
    a,b,c=st.columns(3)
    a.metric('Fictional property value',f'${prop.current_value:,.0f}')
    b.metric('Loan balance',f'${prop.loan.balance:,.0f}')
    c.metric('Monthly asking rent',f'${prop.rental.monthly_rent:,.0f}')
    st.dataframe(pd.DataFrame(financial_rows(result)),hide_index=True,width='stretch')
    st.caption('NPV discounts the comparison cash-flow stream at the configured 6% annual rate. Terminal wealth is a different, undiscounted measure.')
    if not tax_complete:st.warning('INCOMPLETE_TAX: adjusted basis is deliberately missing. After-tax results are withheld, not filled with zero.')
    else:st.warning('Tax rates and basis are invented arithmetic assumptions, not a tax filing calculation.')
    cash=pd.DataFrame({s['strategy']:[r['household_cashflow_before_tax'] for r in s['annual_schedule']] for s in result['strategies']},index=range(1,horizon+1))
    st.subheader('Annual household cash flow before tax ($)')
    st.bar_chart(cash,height=280)
    with st.expander('Inspect annual rental schedule'):
        st.dataframe(pd.DataFrame(result['strategies'][2]['annual_schedule']),hide_index=True)

elif page=='Scenario lab':
    st.header('Sensitivity, without assigned probabilities')
    st.write('Vary appreciation while holding the selected property, vacancy and horizon constant. A scenario is an assumption, not a forecast.')
    rows=sensitivity(prop,assumptions,horizon,result)
    table=pd.DataFrame([{'Annual appreciation (%)':r['alternative_value']*100,'Strategy':r['strategy'],'Pre-tax NPV ($)':r['alternative']['npv']} for r in rows])
    st.line_chart(table.pivot(index='Annual appreciation (%)',columns='Strategy',values='Pre-tax NPV ($)'),height=340)
    st.dataframe(table,hide_index=True,width='stretch')

elif page=='Forecast lab':
    st.header('Rolling-origin mechanics on fictional indices')
    fh=st.select_slider('Forecast horizon (months)',options=[3,6,9,12],value=6)
    table=pd.DataFrame(scores(fh))
    st.caption('Expanding training windows, at least 60 months. Errors are percentage points of log growth: 100 × ln(target / origin).')
    st.dataframe(table,hide_index=True,width='stretch')
    st.bar_chart(table.pivot(index='Market',columns='Baseline',values='MAE (log-growth pp)'),height=290)
    st.warning('Synthetic experiment only: these scores do not measure real-world accuracy, point-in-time validity or investment performance. No future outcome has been validated.')
    st.json({'minimum_training_months':60,'origins_per_market_and_model':61-fh,'horizon_months':fh,'target_availability':'known generated historical suffix','real_data_used':False})

elif page=='Evidence explorer':
    st.header('Read-only evidence, computed locally')
    st.write('Six fixed queries route to deterministic code. This is an evidence explorer, not an LLM chat or the private research edition’s 16-tool agent.')
    question=st.selectbox('Evidence question',QUESTIONS)
    st.json(evidence(question,prop,assumptions,result,horizon))

elif page=='Human review':
    st.header('The reviewer owns the decision')
    st.write('Record a fictional choice only after reviewing evidence. No strategy is preselected and no engine finalizes a decision.')
    st.dataframe(pd.DataFrame(financial_rows(result)),hide_index=True)
    choice=st.selectbox('Human choice',['Hold','Sell','Rent out','Undecided'],index=None,placeholder='Choose explicitly',key='review_choice')
    confirmed=st.checkbox('I confirm this is a fictional demonstration choice',key='review_confirm')
    if st.button('Record demonstration choice',disabled=not choice or not confirmed):
        st.session_state['review_packet']=review_packet(result,choice,confirmed)
    if 'review_packet' in st.session_state:
        st.success('Human demonstration choice recorded in this browser session only.')
        st.json(st.session_state['review_packet'])
        st.download_button('Download synthetic review JSON',json.dumps(st.session_state['review_packet'],indent=2,allow_nan=False),'propertyiq-synthetic-review.json','application/json')

st.divider()
st.caption('Educational prototype. Not an appraisal, tax/legal advice or personalized investment recommendation. No automatic ranking. No external data, credentials or network APIs are used by the demo.')
