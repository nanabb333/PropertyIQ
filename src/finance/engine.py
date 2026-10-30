"""Forward decision-date accounting: actual property cash vs normalized resources."""
from dataclasses import asdict
from datetime import date
import calendar
from src.finance.schema import validate
from src.finance.calculations import (gross_potential_rent,effective_gross_income,noi,cap_rate,dscr,cash_on_cash,
    terminal_value,npv,irr,loan_schedule,sale_proceeds,cumulative_cash_flows)
from src.finance.taxes import tax_status,rental_tax,sale_tax

STRATEGIES=('hold_occupy','sell','rent_out')
LIMITATIONS=['Assumption-driven analysis, no automatic ranking or personalized recommendation.',
 'Nominal annual end-period cash flows; monthly amortization; no transaction-date day count.',
 'Sale at end of every horizon. Independent horizon experiments, not sequential disposals.',
 'Current-sale net proceeds normalize all strategies; historical acquisition cash is sunk and not deducted again.',
 'Reserves are restricted cash assets, not NOI expenses or automatic tax deductions.',
 'Negative cash flows require external funding; terminal-wealth accumulation is explicit, not a self-financing guarantee.',
 'Tax estimates are illustrative; no loss offsets, exclusions, NIIT, brackets or legal eligibility automatically inferred.']

def return_metrics(capital,cashflows,rate):
    return {'normalized_cashflows':cashflows,'npv':npv(cashflows,rate),
        'irr':irr(cashflows) if capital>0 else {'status':'UNDEFINED_NONPOSITIVE_INITIAL_CAPITAL','rate':None,'roots':[]},
        'cumulative_cashflows':cumulative_cash_flows(cashflows)}

def compare(prop,a,horizon):
    validate(prop,a)
    if horizon not in (1,3,5,10):raise ValueError('Supported horizons:1,3,5,10 years')
    tstatus=tax_status(prop);taxok=tstatus['status']=='ILLUSTRATIVE_ASSUMPTIONS_ONLY'
    afterok=taxok and (not a.reinvest_sale_proceeds or a.investment_return_tax_rate is not None)
    current_sale=sale_proceeds(prop.total_value,prop.sale,prop.loan.balance,prop.loan.prepayment_cost if prop.loan.balance else 0)
    current_tax=sale_tax(current_sale,prop.tax) if taxok else None
    capital=current_sale['pretax_proceeds'];aftercapital=current_tax['after_tax_economic_proceeds'] if taxok else None
    plan=loan_schedule(prop.loan,horizon);outputs=[]
    for strategy in STRATEGIES:
        schedule=[];reserve=0.;capital_added=depreciation=0.;last_tax=None
        for year in range(1,horizon+1):
            start_date=date.fromisoformat(a.valuation_date);end_year=start_date.year+year
            period_end=start_date.replace(year=end_year,day=min(start_date.day,calendar.monthrange(end_year,start_date.month)[1])).isoformat()
            inf=(1+a.inflation)**(year-1);debt=plan[year-1]
            rent=prop.rental.monthly_rent*(1+prop.rental.rent_growth)**(year-1)
            lease_remaining=max(0,prop.rental.lease_up_months-12*(year-1));active=max(0,12-min(12,lease_remaining))
            gpr=gross_potential_rent(rent);leaseup_loss=rent*(12-active);vacancy_loss=rent*active*prop.rental.vacancy
            egi=effective_gross_income(rent*active,prop.rental.vacancy)
            hoa=12*prop.hoa_monthly*(1+a.hoa_growth)**(year-1);ptax=prop.property_tax_annual*(1+a.property_tax_growth)**(year-1)
            assessment=prop.special_assessments.get(year,0.)
            op_assess=assessment if prop.assessment_treatment=='operating' else 0.;cap_assess=assessment-op_assess
            capex=prop.major_capex.get(year,0.)+cap_assess
            common_opex=hoa+ptax+(prop.insurance_annual+prop.maintenance_annual)*inf+op_assess
            housing=12*a.alternative_housing_monthly*(1+a.housing_rent_growth)**(year-1) if a.housing_mode=='common_housing' and strategy!='hold_occupy' else 0.
            avoided=12*a.avoided_rent_monthly*(1+a.housing_rent_growth)**(year-1) if a.avoided_rent_monthly is not None and strategy=='hold_occupy' else 0.
            value=prop.sale.explicit_terminal_prices.get(year,terminal_value(prop.total_value,a.appreciation,year))
            start_reserve=reserve;contribution=withdrawal=dep=renttax=0.
            if strategy=='sell':
                operating=net_operating=0.;property_cf=0.;interest=principal=service=refi_cf=0.;balance=0.;capex=0.;op_assess=0.
            else:
                interest=debt['interest'];principal=debt['principal'];service=debt['debt_service'];refi_cf=debt['refinance_cash_flow'];balance=debt['end_balance'];capital_added+=capex
                if strategy=='rent_out':
                    management=egi*prop.rental.management_rate;leasing=rent*prop.rental.leasing_months_per_year*active/12
                    operating=common_opex+(prop.rental.repairs_annual+prop.rental.owner_utilities_annual)*inf+management+leasing
                    net_operating=noi(egi,operating)
                    contribution=12*prop.rental.capex_reserve_monthly*inf;withdrawal=min(reserve+contribution,capex);reserve+=contribution-withdrawal
                    property_cf=net_operating-service-contribution-(capex-withdrawal)+refi_cf
                    if taxok:
                        dep=min(prop.tax.annual_depreciation,max(0.,prop.tax.depreciable_basis_remaining+capital_added-depreciation));depreciation+=dep
                        renttax=rental_tax(net_operating,interest,dep,prop.tax)
                else:
                    operating=common_opex+prop.owner_occupancy_utilities_annual*inf;net_operating=-operating
                    property_cf=-operating-service-capex+refi_cf
            household_cf=property_cf-housing
            economic_non_cash=avoided if a.include_avoided_rent else 0.
            after_cf=household_cf-renttax if taxok else None
            row={'year':year,'period_end':period_end,'year_end_nominal_value':0. if strategy=='sell' else value,'gross_potential_rent':gpr if strategy=='rent_out' else 0.,'lease_up_loss':leaseup_loss if strategy=='rent_out' else 0.,'vacancy_loss':vacancy_loss if strategy=='rent_out' else 0.,'effective_gross_income':egi if strategy=='rent_out' else 0.,
                'operating_expenses':operating,'noi':net_operating if strategy=='rent_out' else None,'cap_rate':cap_rate(net_operating,prop.total_value*(1+a.appreciation)**(year-1)) if strategy=='rent_out' else None,
                'interest':interest,'principal':principal,'debt_service':service,'loan_balance':balance,'gross_property_equity':0. if strategy=='sell' else value-balance,
                'refinance_cash_flow':refi_cf,'new_borrowing':debt['new_borrowing'] if strategy!='sell' else 0.,'refinance_payoff':debt['refinance_payoff'] if strategy!='sell' else 0.,
                'refinance_closing_cost':debt['refinance_closing_cost'] if strategy!='sell' else 0.,'refinance_prepaid_penalty':debt['refinance_prepaid_penalty'] if strategy!='sell' else 0.,
                'capital_spending':capex,'operating_assessment':op_assess,'reserve_start':start_reserve,'reserve_contribution':contribution,'reserve_withdrawal':withdrawal,'reserve_end':reserve,
                'property_cashflow_before_financing':(net_operating-capex) if strategy=='rent_out' else (-operating-capex if strategy=='hold_occupy' else 0.),
                'property_cashflow_after_financing_before_tax':property_cf,'annual_holding_costs':operating+service+capex,
                'dscr':dscr(net_operating,service) if strategy=='rent_out' else None,'cash_on_cash':cash_on_cash(property_cf-refi_cf,capital) if strategy=='rent_out' else None,
                'alternative_housing_cash_cost':housing,'avoided_rent_non_cash':avoided,'avoided_rent_included_in_comparison':economic_non_cash,
                'household_cashflow_before_tax':household_cf,'annual_depreciation':dep if taxok and strategy=='rent_out' else None,
                'rental_tax_estimate':renttax if taxok else None,'household_cashflow_after_tax':after_cf}
            schedule.append(row)
        if strategy=='sell':
            exit_sale=current_sale;exit_tax=current_tax
            pretax_return=a.alternative_return if a.reinvest_sale_proceeds else 0.
            # Negative sale equity requires external funding, not a negative investment purchase.
            asset=capital*(1+(pretax_return if capital>0 else a.cash_accumulation_rate))**horizon
            if afterok:
                ar=(pretax_return-max(0.,pretax_return)*a.investment_return_tax_rate) if a.reinvest_sale_proceeds else 0.
                afterasset=aftercapital*(1+(ar if aftercapital>0 else a.cash_accumulation_rate))**horizon
            else:afterasset=None
            terminal_property=0.;terminal_reserve=0.
        else:
            terminal_property=schedule[-1]['year_end_nominal_value'];exit_sale=sale_proceeds(terminal_property,prop.sale,plan[-1]['end_balance'],plan[-1]['exit_prepayment_cost'],(1+a.inflation)**horizon)
            exit_tax=sale_tax(exit_sale,prop.tax,capital_added,depreciation) if taxok else None
            terminal_reserve=reserve;asset=exit_sale['pretax_proceeds']+reserve;afterasset=exit_tax['after_tax_economic_proceeds']+reserve if taxok else None
        before=[-capital]+[r['household_cashflow_before_tax'] for r in schedule];before[-1]+=asset
        normalized=return_metrics(capital,before,a.discount_rate)
        economic_cf=[before[0]]+[before[i]+schedule[i-1]['avoided_rent_included_in_comparison'] for i in range(1,horizon+1)]
        after_stream=[-aftercapital]+[r['household_cashflow_after_tax'] for r in schedule] if afterok else None
        if after_stream is not None:after_stream[-1]+=afterasset
        actual_property_stream=[current_sale['pretax_proceeds'] if strategy=='sell' else 0.]+[r['property_cashflow_after_financing_before_tax'] for r in schedule]
        if strategy!='sell':actual_property_stream[-1]+=asset
        wealth=asset+sum(r['household_cashflow_before_tax']*(1+a.cash_accumulation_rate)**(horizon-r['year']) for r in schedule)
        afterwealth=afterasset+sum(r['household_cashflow_after_tax']*(1+a.cash_accumulation_rate)**(horizon-r['year']) for r in schedule) if afterok else None
        outputs.append({'strategy':strategy,'annual_schedule':schedule,'terminal_property_value':terminal_property,'terminal_reserve_release':terminal_reserve,'sale':exit_sale,'sale_tax':exit_tax,
            'initial_property_cash_released':current_sale['pretax_proceeds'] if strategy=='sell' else 0.,'initial_retained_opportunity_capital':capital if strategy!='sell' else 0.,
            'allocated_cash_or_investment_principal':capital if strategy=='sell' else 0.,'immediate_external_funding_required':max(0.,-capital) if strategy=='sell' else 0.,
            'terminal_asset_after_liquidation_before_tax':asset,'terminal_asset_after_tax':afterasset,'pretax':normalized,'after_tax':return_metrics(aftercapital,after_stream,a.discount_rate) if afterok else None,
            'economic_npv_including_optional_non_cash':npv(economic_cf,a.discount_rate),'actual_property_cashflows_before_tax':actual_property_stream,
            'actual_property_cashflow_npv_before_tax':npv(actual_property_stream,a.discount_rate),'terminal_wealth_before_tax':wealth,'terminal_wealth_after_tax':afterwealth})
    missing=list(tstatus['missing'])
    if a.housing_mode=='property_only':missing.append('Alternative housing excluded: property-only comparison is not a full household decision')
    if a.reinvest_sale_proceeds and a.investment_return_tax_rate is None:missing.append('investment_return_tax_rate: after-tax comparison withheld for all strategies')
    if prop.interior_sqft is None:missing.append('interior_sqft (descriptive only)')
    if prop.parking_ownership=='unknown':missing.append('parking ownership/valuation')
    if capital<=0:missing.append('Nonpositive net sale equity: cash-on-cash/IRR undefined; funding may be required')
    return {'schema_version':'phase4a-v1','input_classification':'SYNTHETIC_FICTIONAL_PROPERTY' if prop.is_synthetic else 'USER_SUPPLIED_UNVERIFIED','property_id':prop.property_id,'market':prop.market,'valuation_date':a.valuation_date,'horizon_years':horizon,
        'assumptions':{'property':asdict(prop),'comparison':asdict(a)},'tax_status':tstatus,'normalized_initial_capital_before_tax':capital,'normalized_initial_capital_after_tax':aftercapital,
        'current_sale':current_sale,'current_sale_tax':current_tax,'strategies':outputs,'missing_information':missing,'limitations':LIMITATIONS,
        'ranking_performed':False,'decision_status':'REVIEWER_CHOICE_REQUIRED','forecast_values_automatically_applied':False}
