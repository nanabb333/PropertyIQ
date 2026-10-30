"""Synthetic-only public Streamlit application. No ingestion or auth code imported."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
import streamlit as st
from src.public_demo import (MARKETS,WORKFLOWS,QUESTIONS,case,financial_rows,synthetic_markets,
                             provenance,sensitivity,scores,evidence,review_packet,fingerprint)

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
with st.sidebar:
    st.header('Workspace')
    page=st.radio('Workflow',WORKFLOWS)
    label=st.selectbox('Fictional property',MARKETS)
    horizon=st.select_slider('Financial horizon (years)',options=[1,3,5,10],value=5)
    appreciation=st.slider('Illustrative annual appreciation (%)',-5.,8.,2.5,.5)/100
    vacancy=st.slider('Illustrative rental vacancy (%)',0.,30.,6.,1.)/100
    tax_complete=st.checkbox('Use complete fictional tax assumptions',value=False)
    st.caption('Offline workflows. No login, Keychain, provider access or inference.')
prop,assumptions,result=case(MARKETS.index(label),horizon,appreciation,vacancy,tax_complete)
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
    rows=sensitivity(prop,assumptions,horizon)
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
