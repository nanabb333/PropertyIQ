import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.public_demo import WORKFLOWS

class PublicUITests(unittest.TestCase):
    def test_edit_current_value_updates_financial_display(self):
        app=self.app();app.sidebar.radio[0].set_value('Financial comparison').run()
        field=app.number_input(key='current_value_Harbor')
        self.assertEqual(field.label,'Current market value (USD)')
        self.assertEqual(field.value,650000.)
        before=app.dataframe[0].value.copy()
        field.set_value(750000.).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,'$750,000')
        self.assertTrue((before['Pre-tax NPV ($)']!=app.dataframe[0].value['Pre-tax NPV ($)']).all())
        # All workflows share the edited assumption; returning does not reset it.
        app.sidebar.radio[0].set_value('Scenario lab').run()
        self.assertFalse(app.exception)
        app.sidebar.radio[0].set_value('Financial comparison').run()
        self.assertEqual(app.number_input(key='current_value_Harbor').value,750000.)

    def test_value_edit_invalidates_review_and_sessions_are_isolated(self):
        app=self.app();app.sidebar.radio[0].set_value('Human review').run()
        app.selectbox(key='review_choice').select('Hold').run()
        app.checkbox(key='review_confirm').check().run();app.button[0].click().run()
        self.assertIn('review_packet',app.session_state)
        app.number_input(key='current_value_Harbor').set_value(750000.).run()
        self.assertEqual(len(app.success),0)
        self.assertIsNone(app.selectbox(key='review_choice').value)
        self.assertEqual(self.app().number_input(key='current_value_Harbor').value,650000.)
        app.sidebar.selectbox[0].select('Cedar').run()
        self.assertEqual(app.number_input(key='current_value_Cedar').value,360000.)

    def app(self):return AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app/streamlit_app.py'),default_timeout=20).run()
    def test_all_workflows_render(self):
        app=self.app()
        for page in WORKFLOWS:
            app.sidebar.radio[0].set_value(page).run()
            with self.subTest(page=page):self.assertEqual(len(app.exception),0)
    def test_no_login_or_inference_controls(self):
        app=self.app()
        self.assertFalse(any('login' in b.label.lower() or 'inference' in b.label.lower() for b in app.button))
    def test_review_no_default_and_explicit_record(self):
        app=self.app();app.sidebar.radio[0].set_value('Human review').run()
        self.assertIsNone(app.selectbox(key='review_choice').value);self.assertTrue(app.button[0].disabled)
        app.selectbox(key='review_choice').select('Undecided').run();self.assertTrue(app.button[0].disabled)
        app.checkbox(key='review_confirm').check().run();app.button[0].click().run()
        self.assertEqual(len(app.success),1);self.assertEqual(app.session_state['review_packet']['choice'],'Undecided')
    def test_changed_inputs_invalidate_review(self):
        app=self.app();app.sidebar.radio[0].set_value('Human review').run()
        app.selectbox(key='review_choice').select('Hold').run();app.checkbox(key='review_confirm').check().run();app.button[0].click().run()
        app.sidebar.slider[0].set_value(4.).run()
        self.assertEqual(len(app.success),0);self.assertIsNone(app.selectbox(key='review_choice').value)
    def test_tax_disclosure(self):
        app=self.app();app.sidebar.radio[0].set_value('Financial comparison').run()
        self.assertTrue(any('INCOMPLETE_TAX' in w.value for w in app.warning))
        app.sidebar.checkbox[0].check().run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('invented' in w.value for w in app.warning))

    def test_profile_and_user_override_persist_across_all_workflows(self):
        app=self.app()
        app.number_input(key='finance_monthly_rent_Harbor').set_value(4444.).run()
        app.text_input(key='profile_zip_Harbor').set_value('99999').run()
        for page in WORKFLOWS:
            app.sidebar.radio[0].set_value(page).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key='profile_zip_Harbor').value,'99999')
            self.assertEqual(app.number_input(key='finance_monthly_rent_Harbor').value,4444.)
        self.assertEqual(app.session_state['financial_sources_Harbor']['monthly_rent'],'User input')

    def test_profile_change_does_not_apply_financial_suggestions(self):
        app=self.app();app.sidebar.radio[0].set_value('Financial comparison').run()
        before=app.dataframe[0].value.copy()
        app.text_input(key='profile_zip_Harbor').set_value('19103').run()
        app.selectbox(key='profile_type_Harbor').select('Multifamily').run()
        self.assertTrue(before.equals(app.dataframe[0].value))
        self.assertEqual(app.number_input(key='finance_monthly_rent_Harbor').value,3100.)
        self.assertTrue(app.button(key='apply_fixture_Harbor').disabled)

    def test_explicit_suggestions_apply_only_previewed_fields(self):
        app=self.app();app.sidebar.radio[0].set_value('Financial comparison').run()
        unchanged={key:app.number_input(key=key).value for key in ('current_value_Harbor','finance_purchase_price_Harbor','finance_loan_balance_Harbor','finance_tax_basis_Harbor')}
        app.checkbox(key='approve_fixture_Harbor').check().run()
        app.button(key='apply_fixture_Harbor').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key='finance_monthly_rent_Harbor').value,2160.)
        self.assertEqual(app.number_input(key='finance_hoa_monthly_Harbor').value,350.)
        for key,value in unchanged.items():self.assertEqual(app.number_input(key=key).value,value)
        self.assertEqual(app.session_state['fixture_receipts_Harbor']['monthly_rent']['fixture'],'ZIP_TOKEN_20008')
        app.text_input(key='profile_zip_Harbor').set_value('19103').run()
        self.assertEqual(app.number_input(key='finance_monthly_rent_Harbor').value,2160.)
        self.assertEqual(app.session_state['fixture_receipts_Harbor']['monthly_rent']['fixture'],'ZIP_TOKEN_20008')
        app.number_input(key='finance_monthly_rent_Harbor').set_value(4200.).run()
        self.assertNotIn('monthly_rent',app.session_state['fixture_receipts_Harbor'])
        self.assertEqual(app.session_state['financial_sources_Harbor']['monthly_rent'],'User input')

    def test_descriptive_profile_edit_invalidates_review(self):
        app=self.app();app.sidebar.radio[0].set_value('Human review').run()
        app.selectbox(key='review_choice').select('Undecided').run()
        app.checkbox(key='review_confirm').check().run();app.button[0].click().run()
        self.assertIn('review_packet',app.session_state)
        app.text_input(key='profile_zip_Harbor').set_value('19103').run()
        self.assertIsNone(app.selectbox(key='review_choice').value)
        self.assertNotIn('review_packet',app.session_state)

    def test_invalid_zip_and_zero_area_fail_closed(self):
        app=self.app();app.sidebar.radio[0].set_value('Financial comparison').run()
        app.text_input(key='profile_zip_Harbor').set_value('invalid').run()
        self.assertFalse(app.exception);self.assertTrue(app.error)
        self.assertEqual(len(app.dataframe),0)
        app.text_input(key='profile_zip_Harbor').set_value('20008').run()
        app.number_input(key='profile_area_Harbor').set_value(0.).run()
        self.assertFalse(app.exception);self.assertTrue(app.error)
        self.assertEqual(len(app.dataframe),0)

    def test_custom_layout_and_optional_fields(self):
        app=self.app()
        app.selectbox(key='profile_layout_Harbor').select('Custom').run()
        app.number_input(key='profile_beds_Harbor').set_value(4).run()
        app.number_input(key='profile_baths_Harbor').set_value(2.5).run()
        app.checkbox(key='profile_parking_known_Harbor').check().run()
        app.checkbox(key='profile_year_known_Harbor').check().run()
        self.assertFalse(app.exception)
        app.sidebar.radio[0].set_value('Evidence explorer').run()
        self.assertEqual(app.number_input(key='profile_beds_Harbor').value,4)
        self.assertEqual(app.number_input(key='profile_baths_Harbor').value,2.5)
        self.assertEqual(app.number_input(key='profile_year_Harbor').value,2000)

    def test_profile_sessions_do_not_share_edits(self):
        first=self.app();first.text_input(key='profile_zip_Harbor').set_value('99999').run()
        first.number_input(key='finance_purchase_price_Harbor').set_value(321000.).run()
        second=self.app()
        self.assertEqual(second.text_input(key='profile_zip_Harbor').value,'20008')
        self.assertEqual(second.number_input(key='finance_purchase_price_Harbor').value,490000.)


    def test_case_switch_restores_drafts_and_provenance(self):
        app=self.app()
        app.text_input(key='profile_zip_Harbor').set_value('99999').run()
        app.selectbox(key='profile_layout_Harbor').select('Custom').run()
        app.number_input(key='profile_beds_Harbor').set_value(4).run()
        app.number_input(key='finance_monthly_rent_Harbor').set_value(4567.).run()
        app.sidebar.selectbox[0].select('Cedar').run()
        self.assertEqual(app.number_input(key='finance_monthly_rent_Cedar').value,2200.)
        app.sidebar.selectbox[0].select('Harbor').run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key='finance_monthly_rent_Harbor').value,4567.)
        self.assertEqual(app.text_input(key='profile_zip_Harbor').value,'99999')
        self.assertEqual(app.number_input(key='profile_beds_Harbor').value,4)
        self.assertEqual(app.session_state['financial_sources_Harbor']['monthly_rent'],'User input')


    def test_invalid_draft_clears_review_even_when_reverted(self):
        app=self.app();app.sidebar.radio[0].set_value('Human review').run()
        app.selectbox(key='review_choice').select('Hold').run()
        app.checkbox(key='review_confirm').check().run();app.button[0].click().run()
        self.assertIn('review_packet',app.session_state)
        app.text_input(key='profile_zip_Harbor').set_value('invalid').run()
        self.assertNotIn('review_packet',app.session_state)
        app.text_input(key='profile_zip_Harbor').set_value('20008').run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.selectbox(key='review_choice').value)
        self.assertNotIn('review_packet',app.session_state)
