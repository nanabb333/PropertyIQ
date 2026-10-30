"""Signed annual cash contributions reconciled to immutable Phase4A streams."""
import math

def decompose(comparison):
    p=comparison['assumptions']['property'];a=comparison['assumptions']['comparison'];h=comparison['horizon_years'];out=[]
    for s in comparison['strategies']:
        parts={};economic={};name=s['strategy']
        def add(key,t,value):parts.setdefault(key,[0.]*(h+1))[t]+=value
        add('initial_opportunity_capital_NOT_new_purchase',0,-comparison['normalized_initial_capital_before_tax'])
        for r in s['annual_schedule']:
            y=r['year'];inf=(1+a['inflation'])**(y-1)
            if name!='sell':
                if name=='rent_out':
                    add('gross_potential_rent',y,r['gross_potential_rent']);add('lease_up_losses',y,-r['lease_up_loss']);add('vacancy_losses',y,-r['vacancy_loss'])
                add('HOA',y,-12*p['hoa_monthly']*(1+a['hoa_growth'])**(y-1));add('property_taxes',y,-p['property_tax_annual']*(1+a['property_tax_growth'])**(y-1))
                add('insurance',y,-p['insurance_annual']*inf);add('maintenance',y,-p['maintenance_annual']*inf);add('operating_assessments',y,-r['operating_assessment'])
                if name=='rent_out':
                    rent=p['rental']['monthly_rent']*(1+p['rental']['rent_growth'])**(y-1);active=max(0,12-min(12,max(0,p['rental']['lease_up_months']-12*(y-1))))
                    add('incremental_rental_repairs',y,-p['rental']['repairs_annual']*inf);add('owner_paid_rental_utilities',y,-p['rental']['owner_utilities_annual']*inf)
                    add('management',y,-r['effective_gross_income']*p['rental']['management_rate']);add('leasing',y,-rent*p['rental']['leasing_months_per_year']*active/12)
                else:add('occupancy_utilities',y,-p['owner_occupancy_utilities_annual']*inf)
                add('capital_expenditure',y,-r['capital_spending']);add('reserve_net_transfer_NOT_expense',y,-(r['reserve_end']-r['reserve_start']))
                for key,field in (('loan_interest','interest'),('loan_principal','principal'),('refinance_old_loan_payoff','refinance_payoff'),('refinance_fees','refinance_closing_cost'),('refinance_penalty','refinance_prepaid_penalty')):add(key,y,-r[field])
                add('refinance_new_borrowing_NOT_income',y,r['new_borrowing'])
            add('alternative_housing',y,-r['alternative_housing_cash_cost'])
            economic.setdefault('avoided_rent_non_cash_NOT_in_cash_NPV',[0.]*(h+1))[y]=r['avoided_rent_non_cash']
        if name=='sell':
            capital=comparison['normalized_initial_capital_before_tax'];add('released_capital_retained_at_terminal',h,capital)
            add('reinvestment_or_funding_growth',h,s['terminal_asset_after_liquidation_before_tax']-capital)
        else:
            sale=s['sale'];add('terminal_gross_sale',h,sale['gross_price'])
            for key,field in (('terminal_brokerage','brokerage'),('terminal_transfer_recordation','transfer_recordation'),('terminal_closing_costs','closing_fixed'),('terminal_staging','repair_staging'),('terminal_loan_payoff','loan_payoff'),('terminal_prepayment_cost','prepayment_cost')):add(key,h,-sale[field])
            add('terminal_reserve_release',h,s['terminal_reserve_release'])
        target=s['pretax']['normalized_cashflows'];summed=[math.fsum(v[t] for v in parts.values()) for t in range(h+1)]
        if any(not math.isclose(x,y,abs_tol=1e-7,rel_tol=1e-11) for x,y in zip(summed,target)):raise ValueError('Pretax contribution mismatch')
        pv={k:math.fsum(v[t]/(1+a['discount_rate'])**t for t in range(h+1)) for k,v in parts.items()}
        if not math.isclose(sum(pv.values()),s['pretax']['npv'],abs_tol=1e-7,rel_tol=1e-11):raise ValueError('NPV contribution mismatch')
        taxparts=None;afterpv=None
        if s['after_tax']:
            taxparts={};initial_tax=comparison['current_sale_tax']['estimated_final_liability']
            def taxadd(key,t,v):taxparts.setdefault(key,[0.]*(h+1))[t]+=v
            taxadd('aftertax_opportunity_basis_adjustment_NOT_actual_refund',0,initial_tax)
            for r in s['annual_schedule']:taxadd('rental_tax_estimate',r['year'],-r['rental_tax_estimate'])
            if name!='sell':taxadd('terminal_estimated_sale_liability',h,-s['sale_tax']['estimated_final_liability'])
            else:
                taxadd('sale_tax_reduces_terminal_allocated_principal',h,-initial_tax)
                taxadd('aftertax_growth_difference',h,s['terminal_asset_after_tax']-s['terminal_asset_after_liquidation_before_tax']+initial_tax)
            after=[summed[t]+math.fsum(v[t] for v in taxparts.values()) for t in range(h+1)]
            if any(not math.isclose(x,y,abs_tol=1e-7,rel_tol=1e-11) for x,y in zip(after,s['after_tax']['normalized_cashflows'])):raise ValueError('Aftertax contribution mismatch')
            afterpv=s['pretax']['npv']+math.fsum(v[t]/(1+a['discount_rate'])**t for v in taxparts.values() for t in range(h+1))
            if not math.isclose(afterpv,s['after_tax']['npv'],abs_tol=1e-7,rel_tol=1e-11):raise ValueError('Aftertax NPV mismatch')
        out.append({'strategy':name,'pretax_cashflow_components':parts,'pretax_npv_components':pv,'reconciled_pretax_npv':sum(pv.values()),
            'tax_adjustment_components':taxparts,'reconciled_aftertax_npv':afterpv,'non_cash_occupancy_display':economic,
            'actual_initial_property_cash_released':s['initial_property_cash_released'],'liquidity_withholding_details':s['sale_tax'],
            'notes':['Initial opportunity capital is not an actual new acquisition payment.','Principal repayment and exit loan payoff are separate once-only components.','Reserves are cash transfers, not NOI expenses.','Creditable withholding is liquidity-only and is not deducted again.','Economic occupancy benefit is separately reported by Phase4A and never added to this financial cash NPV.']})
    return out
