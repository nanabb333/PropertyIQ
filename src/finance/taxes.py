"""Configurable illustrative arithmetic, never a jurisdictional tax determination."""

def tax_status(prop):
    t=prop.tax;missing=[]
    if not prop.acquisition.ownership_structure:missing.append('ownership_structure')
    for name in ('residency','jurisdiction','current_adjusted_basis','prior_depreciation','depreciable_basis_remaining','annual_depreciation','capital_gain_rate','recapture_rate','rental_income_rate','withholding_rate','deductible_sale_cost_fraction','other_sale_tax_fixed'):
        if getattr(t,name) is None or getattr(t,name)=='':missing.append(name)
    return {'status':'INCOMPLETE_TAX' if missing else ('ILLUSTRATIVE_ASSUMPTIONS_ONLY' if t.mode=='illustrative' else 'NOT_MODELED'),'missing':missing,'authoritative':False}

def rental_tax(noi,interest,depreciation,tax):return max(0.,noi-interest-depreciation)*tax.rental_income_rate

def sale_tax(proceeds,tax,capital_additions=0,new_depreciation=0):
    basis=tax.current_adjusted_basis+capital_additions-new_depreciation
    amount_realized=proceeds['gross_price']-proceeds['transaction_costs']*tax.deductible_sale_cost_fraction
    gain=max(0.,amount_realized-basis);recapture=min(gain,tax.prior_depreciation+new_depreciation)
    liability=(gain-recapture)*tax.capital_gain_rate+recapture*tax.recapture_rate+tax.other_sale_tax_fixed
    withheld=proceeds['gross_price']*tax.withholding_rate
    closing_cash=proceeds['pretax_proceeds']-withheld;settlement=withheld-liability
    return {'status':'ILLUSTRATIVE_ASSUMPTIONS_ONLY','adjusted_basis':basis,'amount_realized':amount_realized,'positive_gain':gain,'recapture_base':recapture,'estimated_final_liability':liability,
        'withholding':withheld,'closing_cash_after_withholding':closing_cash,'settlement_receivable_or_payable':settlement,
        'after_tax_economic_proceeds':closing_cash+settlement,'settlement_timing':'Same modeled period; no delayed-refund return assumption','first_principle':'Creditable withholding is not a second tax expense'}
