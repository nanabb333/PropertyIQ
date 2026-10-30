"""Unrounded calculations. Positive receipts, negative cash expenditures in streams."""
import math
import numpy as np

def gross_potential_rent(monthly_rent,months=12):return monthly_rent*months
def effective_gross_income(gross,vacancy):
    if gross<0 or not 0<=vacancy<=1:raise ValueError('Invalid rent/vacancy')
    return gross*(1-vacancy)
def noi(effective_income,operating_expenses):return effective_income-operating_expenses
def cap_rate(net_operating_income,value):return net_operating_income/value if value>0 else None
def debt_service(principal,interest):return principal+interest
def cash_flow_before_tax(net_operating_income,capital_spending=0):return net_operating_income-capital_spending
def cash_flow_after_financing(before_tax,debt_payment):return before_tax-debt_payment
def dscr(net_operating_income,debt_payment):return net_operating_income/debt_payment if debt_payment>0 else None
def cash_on_cash(cash_flow,equity):return cash_flow/equity if equity>0 else None
def annual_holding_costs(operating,debt=0,capital=0):return operating+debt+capital
def terminal_value(value,appreciation,years):return value*(1+appreciation)**years
def npv(cashflows,discount_rate):
    if not cashflows or not math.isfinite(discount_rate) or discount_rate<=-1 or not all(math.isfinite(v) for v in cashflows):raise ValueError('Invalid NPV inputs')
    return math.fsum(v/(1+discount_rate)**t for t,v in enumerate(cashflows))
def cumulative_cash_flows(cashflows):
    return [math.fsum(cashflows[:i+1]) for i in range(len(cashflows))]
def irr(cashflows):
    if not cashflows or not all(math.isfinite(v) for v in cashflows):raise ValueError('Invalid IRR inputs')
    if not any(cashflows):return {'status':'UNDEFINED_ALL_ZERO','rate':None,'roots':[]}
    if not (min(cashflows)<0<max(cashflows)):return {'status':'UNDEFINED_NO_SIGN_CHANGE','rate':None,'roots':[]}
    # Positive real roots in discount factor x=1/(1+r); no arbitrary single-root guess.
    roots=np.polynomial.polynomial.polyroots(cashflows);rates=[]
    for x in roots:
        if abs(x.imag)<1e-8 and x.real>1e-12:
            r=float(1/x.real-1)
            if math.isfinite(r) and r>-1 and abs(npv(cashflows,r))<=1e-6*max(1,sum(map(abs,cashflows))) and not any(abs(r-old)<1e-7 for old in rates):rates.append(r)
    rates.sort()
    return {'status':'OK' if len(rates)==1 else ('AMBIGUOUS_MULTIPLE_IRR' if rates else 'UNDEFINED_NO_ADMISSIBLE_ROOT'),'rate':rates[0] if len(rates)==1 else None,'roots':rates}

def monthly_payment(balance,annual_rate,months):
    if balance<0 or annual_rate<0 or months<0:raise ValueError('Invalid loan')
    if balance==0:return 0.
    if months<=0:raise ValueError('Positive balance needs amortization')
    r=annual_rate/12
    return balance/months if r==0 else balance*r/(-math.expm1(-months*math.log1p(r)))

def loan_schedule(loan,years):
    balance=loan.balance;rate=loan.annual_rate;months=loan.remaining_months;penalty=loan.prepayment_cost
    payment=loan.monthly_payment if loan.monthly_payment is not None else monthly_payment(balance,rate,months);rows=[]
    for y in range(1,years+1):
        start=balance;new_debt=old_payoff=refi_cost=prepay=0.
        if loan.refinance and loan.refinance.year==y:
            ref=loan.refinance;old_payoff=balance;new_debt=balance if ref.new_loan_amount is None else ref.new_loan_amount
            if old_payoff:prepay=penalty if ref.prepayment_cost is None else ref.prepayment_cost
            refi_cost=ref.closing_cost;balance=new_debt;rate=ref.annual_rate;months=ref.term_months;penalty=ref.new_prepayment_cost;payment=monthly_payment(balance,rate,months)
        elif y in loan.rate_changes and balance:
            rate=loan.rate_changes[y];payment=monthly_payment(balance,rate,months)
        principal=interest=balloon=0.
        for _ in range(12):
            if balance<=1e-9:balance=0.;continue
            i=balance*rate/12
            if payment<i-1e-9:raise ValueError('Negative amortization unsupported')
            q=min(balance,max(0.,payment-i))
            if months==1:balloon+=balance-q;q=balance
            balance-=q;principal+=q;interest+=i;months-=1
        rows.append({'year':y,'start_balance':start,'interest':interest,'principal':principal,'debt_service':principal+interest,'end_balance':balance,'balloon_principal':balloon,
            'new_borrowing':new_debt,'refinance_payoff':old_payoff,'refinance_closing_cost':refi_cost,'refinance_prepaid_penalty':prepay,
            'refinance_cash_flow':new_debt-old_payoff-refi_cost-prepay,'exit_prepayment_cost':penalty if balance else 0.,'annual_rate':rate})
    return rows

def remaining_loan_payoff(schedule,year):return schedule[year-1]['end_balance']
def sale_proceeds(price,sale,balance=0,prepayment_cost=0,cost_factor=1):
    costs=price*(sale.brokerage_rate+sale.transfer_recordation_rate)+(sale.closing_fixed+sale.repair_staging)*cost_factor
    return {'gross_price':price,'brokerage':price*sale.brokerage_rate,'transfer_recordation':price*sale.transfer_recordation_rate,'closing_fixed':sale.closing_fixed*cost_factor,'repair_staging':sale.repair_staging*cost_factor,
        'transaction_costs':costs,'loan_payoff':balance,'prepayment_cost':prepayment_cost,'pretax_proceeds':price-costs-balance-prepayment_cost}
