import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
from src.public_demo import WORKFLOWS

class PublicUITests(unittest.TestCase):
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
