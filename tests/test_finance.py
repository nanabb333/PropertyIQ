"""Portable subset of research financial tests. Synthetic inputs only."""
import math, unittest
from dataclasses import replace, asdict
from decimal import Decimal, localcontext
from src.finance.schema import Acquisition,Rental,Sale,Tax,Loan,Refinance,Property,Assumptions,from_dict
from src.finance.calculations import *
from src.finance.engine import compare
from src.finance.taxes import tax_status,sale_tax
from src.scenarios.property_finance import apply,NAMES
def fixture():
    tax=Tax('illustrative','fictional resident','fictional jurisdiction',100000,0,70000,0,.20,.25,.25,0,1,0)
    p=Property('SYNTHETIC_TEST','37980','fictional',100000,Acquisition(100000,'2020-01-01',initial_equity=100000,original_loan_amount=0,ownership_structure='fictional individual'),Rental(1000,.10,0,.10,0,0,100),Sale(0,0),tax=tax,property_tax_annual=1000,insurance_annual=500,maintenance_annual=500)
    a=Assumptions('2026-10-28',0,0,0,0,0)
    return p,a

def strategy(result,name):return next(s for s in result['strategies'] if s['strategy']==name)

class CalculationTests(unittest.TestCase):
    def test_gross_rent(self):self.assertEqual(gross_potential_rent(1000),12000)
    def test_vacancy(self):self.assertEqual(effective_gross_income(12000,.1),10800)
    def test_invalid_vacancy(self):
        with self.assertRaises(ValueError):effective_gross_income(12000,1.1)
    def test_noi(self):self.assertEqual(noi(10800,3080),7720)
    def test_negative_noi(self):self.assertEqual(noi(100,1000),-900)
    def test_cap(self):self.assertEqual(cap_rate(7720,100000),.0772);self.assertIsNone(cap_rate(1,0))
    def test_cashflow_functions(self):self.assertEqual(cash_flow_after_financing(cash_flow_before_tax(10000,1000),4000),5000)
    def test_debt_service(self):self.assertEqual(debt_service(100,50),150)
    def test_dscr_allcash(self):self.assertIsNone(dscr(100,0));self.assertEqual(dscr(-100,50),-2)
    def test_zero_equity(self):self.assertIsNone(cash_on_cash(1000,0));self.assertIsNone(cash_on_cash(1000,-100));self.assertEqual(cash_on_cash(1000,10000),.1)
    def test_annual_costs(self):self.assertEqual(annual_holding_costs(1000,2000,3000),6000)
    def test_terminal(self):self.assertAlmostEqual(terminal_value(100000,.05,3),115762.5)
    def test_npv(self):self.assertAlmostEqual(npv([-100,60,60],.1),4.13223140495867)
    def test_npv_discount_sensitivity(self):self.assertGreater(npv([-100,0,150],.03),npv([-100,0,150],.09))
    def test_npv_invalid(self):
        with self.assertRaises(ValueError):npv([1,2],-1)
    def test_irr(self):self.assertAlmostEqual(irr([-100,110])['rate'],.1)
    def test_negative_irr(self):self.assertAlmostEqual(irr([-100,50])['rate'],-.5)
    def test_multiple_irr(self):
        r=irr([-100,230,-132]);self.assertEqual(r['status'],'AMBIGUOUS_MULTIPLE_IRR');self.assertAlmostEqual(r['roots'][0],.1);self.assertAlmostEqual(r['roots'][1],.2)
    def test_irr_undefined(self):self.assertIsNone(irr([0,0])['rate']);self.assertIsNone(irr([1,2])['rate']);self.assertIsNone(irr([-1,-2])['rate'])
    def test_cumulative(self):self.assertEqual(cumulative_cash_flows([-10,3,5]),[-10,-7,-2])
    def test_standard_payment(self):self.assertAlmostEqual(monthly_payment(100000,.06,360),599.5505251527569)
    def test_zero_rate(self):self.assertEqual(monthly_payment(60000,0,120),500)
    def test_allcash(self):self.assertEqual(monthly_payment(0,0,0),0);self.assertEqual(loan_schedule(Loan(),1)[0]['debt_service'],0)
    def test_decimal_amortization(self):
        r=loan_schedule(Loan(100000,.06,360),1)[0]
        with localcontext() as ctx:
            ctx.prec=45;b=Decimal(100000);i=Decimal('.005');payment=b*i/(1-(1+i)**-360);inter=Decimal(0)
            for _ in range(12):j=b*i;inter+=j;b-=payment-j
        self.assertAlmostEqual(r['end_balance'],float(b),places=7);self.assertAlmostEqual(r['interest'],float(inter),places=7);self.assertAlmostEqual(r['principal']+r['end_balance'],100000)
    def test_early_payoff(self):self.assertAlmostEqual(loan_schedule(Loan(1200,0,12,200),2)[-1]['end_balance'],0)
    def test_balloon(self):
        r=loan_schedule(Loan(1200,0,12,50),1)[0];self.assertEqual(r['principal'],1200);self.assertEqual(r['balloon_principal'],600)
    def test_negative_amort_rejected(self):
        with self.assertRaises(ValueError):loan_schedule(Loan(100000,.12,360,10),1)
    def test_refinance(self):
        l=Loan(60000,0,120,prepayment_cost=500,refinance=Refinance(2,0,120,1000,60000));r=loan_schedule(l,2)[1];self.assertEqual(r['refinance_payoff'],54000);self.assertEqual(r['refinance_cash_flow'],4500);self.assertEqual(r['end_balance'],54000)
    def test_reset(self):
        r=loan_schedule(Loan(60000,.04,120,rate_type='adjustable',rate_changes={2:.08}),2);self.assertEqual(r[1]['annual_rate'],.08);self.assertGreater(r[1]['debt_service'],r[0]['debt_service'])
    def test_sale(self):
        r=sale_proceeds(200000,Sale(.05,.01,2000,1000),80000,500);self.assertAlmostEqual(r['transaction_costs'],15000);self.assertAlmostEqual(r['pretax_proceeds'],104500)

class EngineTests(unittest.TestCase):
    def setUp(self):self.p,self.a=fixture()
    def result(self,p=None,a=None,h=1):return compare(p or self.p,a or self.a,h)
    def test_rental_reference_case(self):
        s=strategy(self.result(),'rent_out');r=s['annual_schedule'][0];self.assertEqual(r['noi'],7720);self.assertEqual(r['property_cashflow_after_financing_before_tax'],6520);self.assertEqual(s['terminal_reserve_release'],1200);self.assertEqual(s['pretax']['npv'],7720);self.assertEqual(s['after_tax']['npv'],5790)
    def test_occupancy_not_income(self):
        s=strategy(self.result(),'hold_occupy');r=s['annual_schedule'][0];self.assertEqual(r['effective_gross_income'],0);self.assertIsNone(r['noi']);self.assertEqual(s['pretax']['npv'],-2000)
    def test_optional_avoided_rent(self):
        a=replace(self.a,avoided_rent_monthly=1000,include_avoided_rent=True);s=strategy(self.result(a=a),'hold_occupy');self.assertEqual(s['pretax']['npv'],-2000);self.assertEqual(s['economic_npv_including_optional_non_cash'],10000)
    def test_common_housing(self):
        a=replace(self.a,housing_mode='common_housing',alternative_housing_monthly=1000);r=self.result(a=a);self.assertEqual(strategy(r,'rent_out')['pretax']['npv'],-4280);self.assertEqual(strategy(r,'sell')['pretax']['npv'],-12000)
    def test_avoided_rent_double_count_rejected(self):
        a=replace(self.a,housing_mode='common_housing',alternative_housing_monthly=1000,avoided_rent_monthly=1000,include_avoided_rent=True)
        with self.assertRaises(ValueError):self.result(a=a)
    def test_reserve_and_capex_no_double_count(self):
        p=replace(self.p,major_capex={1:2000});s=strategy(self.result(p=p),'rent_out');r=s['annual_schedule'][0];self.assertEqual(r['reserve_withdrawal'],1200);self.assertEqual(r['reserve_end'],0);self.assertEqual(r['property_cashflow_after_financing_before_tax'],5720);self.assertEqual(s['pretax']['npv'],5720)
    def test_principal_not_noi_or_double_payoff(self):
        p=replace(self.p,loan=Loan(60000,0,120));s=strategy(self.result(p=p),'rent_out');r=s['annual_schedule'][0];self.assertEqual(r['noi'],7720);self.assertEqual(r['principal'],6000);self.assertEqual(s['sale']['loan_payoff'],54000);self.assertEqual(s['pretax']['npv'],7720)
    def test_no_sunk_acquisition_double_count(self):
        changed=replace(self.p,acquisition=replace(self.p.acquisition,closing_costs=9000,capital_improvements=10000,initial_equity=1));self.assertEqual(strategy(self.result(),'hold_occupy')['pretax'],strategy(self.result(p=changed),'hold_occupy')['pretax'])
    def test_tax_missing(self):
        p=replace(self.p,tax=Tax());r=self.result(p=p);self.assertEqual(r['tax_status']['status'],'INCOMPLETE_TAX');self.assertTrue(all(s['after_tax'] is None for s in r['strategies']))
    def test_missing_ownership(self):
        p=replace(self.p,acquisition=replace(self.p.acquisition,ownership_structure=None));self.assertIn('ownership_structure',self.result(p=p)['missing_information'])
    def test_no_exclusion_assumed(self):
        p=replace(self.p,current_value=200000);s=strategy(self.result(p=p),'sell');self.assertEqual(s['sale_tax']['positive_gain'],100000);self.assertEqual(s['sale_tax']['estimated_final_liability'],20000)
    def test_withholding_not_additional_tax(self):
        sale=sale_proceeds(200000,Sale(.05,.01,2000,1000),80000,500);tax=replace(self.p.tax,current_adjusted_basis=120000,prior_depreciation=10000,withholding_rate=.15);r=sale_tax(sale,tax);self.assertEqual(r['estimated_final_liability'],13500);self.assertEqual(r['withholding'],30000);self.assertEqual(r['closing_cash_after_withholding'],74500);self.assertEqual(r['after_tax_economic_proceeds'],91000);self.assertEqual(r['after_tax_economic_proceeds'],sale_tax(sale,replace(tax,withholding_rate=0))['after_tax_economic_proceeds'])
    def test_depreciation_reduces_basis_once(self):
        p=replace(self.p,tax=replace(self.p.tax,current_adjusted_basis=90000,prior_depreciation=10000,annual_depreciation=1000));r=strategy(self.result(p=p),'rent_out')['sale_tax'];self.assertEqual(r['adjusted_basis'],89000);self.assertEqual(r['recapture_base'],11000)
    def test_no_negative_tax_refund(self):
        p=replace(self.p,rental=replace(self.p.rental,monthly_rent=0));r=strategy(self.result(p=p),'rent_out')['annual_schedule'][0];self.assertLess(r['noi'],0);self.assertEqual(r['rental_tax_estimate'],0)
    def test_no_automatic_reinvestment(self):self.assertEqual(strategy(self.result(h=3),'sell')['terminal_asset_after_liquidation_before_tax'],100000)
    def test_explicit_reinvestment(self):
        a=replace(self.a,reinvest_sale_proceeds=True,alternative_return=.1,investment_return_tax_rate=.2);s=strategy(self.result(a=a,h=3),'sell');self.assertAlmostEqual(s['terminal_asset_after_liquidation_before_tax'],133100);self.assertAlmostEqual(s['terminal_asset_after_tax'],125971.2)
    def test_missing_investment_tax_withholds_all_aftertax(self):
        a=replace(self.a,reinvest_sale_proceeds=True,alternative_return=.1);r=self.result(a=a);self.assertTrue(all(s['after_tax'] is None for s in r['strategies']))
    def test_investment_loss_has_no_automatic_tax_credit(self):
        a=replace(self.a,reinvest_sale_proceeds=True,alternative_return=-.10,investment_return_tax_rate=.25);s=strategy(self.result(a=a),'sell');self.assertEqual(s['terminal_asset_after_tax'],90000)
    def test_refinance_cashout_not_operating_cash_on_cash(self):
        p=replace(self.p,loan=Loan(60000,0,120,refinance=Refinance(2,0,120,0,60000)));s=strategy(self.result(p=p,h=3),'rent_out');r=s['annual_schedule'][1];self.assertEqual(r['refinance_cash_flow'],6000);self.assertAlmostEqual(r['cash_on_cash'],(r['property_cashflow_after_financing_before_tax']-6000)/40000)
    def test_withholding_changes_liquidity_not_normalized_return(self):
        p=replace(self.p,tax=replace(self.p.tax,withholding_rate=.15));a=self.result(h=3);b=self.result(p=p,h=3)
        for s,t in zip(a['strategies'],b['strategies']):self.assertAlmostEqual(s['after_tax']['npv'],t['after_tax']['npv'])
        self.assertNotEqual(a['current_sale_tax']['closing_cash_after_withholding'],b['current_sale_tax']['closing_cash_after_withholding'])
    def test_each_critical_tax_input_missing_is_explicit(self):
        for name in ('residency','jurisdiction','current_adjusted_basis','prior_depreciation','annual_depreciation'):
            p=replace(self.p,tax=replace(self.p.tax,**{name:None}));r=self.result(p=p);self.assertEqual(r['tax_status']['status'],'INCOMPLETE_TAX');self.assertTrue(all(s['after_tax'] is None for s in r['strategies']))
    def test_annual_periods_are_anniversaries(self):
        self.assertEqual(strategy(self.result(h=3),'hold_occupy')['annual_schedule'][-1]['period_end'],'2029-10-28')
    def test_leap_anniversary(self):
        self.assertEqual(strategy(self.result(a=replace(self.a,valuation_date='2028-02-29')),'hold_occupy')['annual_schedule'][0]['period_end'],'2029-02-28')
    def test_depreciation_basis_cannot_exceed_total_basis(self):
        with self.assertRaises(ValueError):self.result(p=replace(self.p,tax=replace(self.p.tax,depreciable_basis_remaining=100001)))
    def test_zero_or_negative_equity(self):
        p=replace(self.p,loan=Loan(100000,0,360));r=self.result(p=p);self.assertTrue(all(s['pretax']['irr']['rate'] is None for s in r['strategies']));self.assertIsNone(strategy(r,'rent_out')['annual_schedule'][0]['cash_on_cash'])
        p=replace(p,loan=Loan(110000,0,360));s=strategy(self.result(p=p),'sell');self.assertEqual(s['immediate_external_funding_required'],10000)
    def test_parking_not_double_counted(self):
        p=replace(self.p,parking_ownership='owned',parking_value=10000);self.assertEqual(p.total_value,100000);self.assertEqual(replace(p,value_includes_parking=False).total_value,110000)
    def test_lease_up_separate_from_vacancy(self):
        p=replace(self.p,rental=replace(self.p.rental,lease_up_months=3));r=strategy(self.result(p=p),'rent_out')['annual_schedule'][0];self.assertEqual(r['gross_potential_rent'],12000);self.assertEqual(r['lease_up_loss'],3000);self.assertEqual(r['vacancy_loss'],900);self.assertEqual(r['effective_gross_income'],8100)
    def test_special_assessment_classification(self):
        p=replace(self.p,special_assessments={1:5000});r=strategy(self.result(p=p),'rent_out')['annual_schedule'][0];self.assertEqual(r['noi'],7720);self.assertEqual(r['capital_spending'],5000)
        p=replace(p,assessment_treatment='operating');r=strategy(self.result(p=p),'rent_out')['annual_schedule'][0];self.assertEqual(r['noi'],2720);self.assertEqual(r['capital_spending'],0)
    def test_horizon_validation(self):
        with self.assertRaises(ValueError):self.result(h=2)
    def test_fixed_rate_reset_rejected(self):
        with self.assertRaises(ValueError):self.result(p=replace(self.p,loan=Loan(10000,.05,120,rate_changes={2:.08})))
    def test_nominal_costs_and_value(self):
        a=replace(self.a,inflation=.10,appreciation=.05);r=strategy(self.result(a=a,h=3),'hold_occupy')['annual_schedule'];self.assertEqual(r[1]['operating_expenses'],2100);self.assertAlmostEqual(r[-1]['year_end_nominal_value'],115762.5)
    def test_no_ranking(self):self.assertFalse(self.result()['ranking_performed']);self.assertEqual([s['strategy'] for s in self.result()['strategies']],['hold_occupy','sell','rent_out'])
    def test_schema_roundtrip(self):
        x=from_dict({'property':asdict(self.p),'assumptions':asdict(self.a)});self.assertEqual(compare(*x,3),self.result(h=3))
    def test_scenario_appreciation(self):
        p,a=apply(self.p,self.a,'bear_value');self.assertEqual(a.appreciation,-.03);self.assertLess(strategy(compare(p,a,3),'hold_occupy')['terminal_property_value'],100000)
    def test_scenario_assessment(self):
        p,a=apply(self.p,self.a,'special_assessment');self.assertEqual(p.special_assessments[2],15000)
    def test_financing_scenario_not_for_allcash(self):self.assertIsNone(apply(self.p,self.a,'explicit_refinance'));self.assertIsNone(apply(self.p,self.a,'arm_rate_up'))
