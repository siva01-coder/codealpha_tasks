import sys
import os
import unittest
import json

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, get_deepl_endpoint

class LinguaAITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_deepl_endpoint_resolution(self):
        # Free key ending with :fx
        self.assertEqual(get_deepl_endpoint("abcd-1234:fx"), "https://api-free.deepl.com/v2/translate")
        # Pro key without :fx
        self.assertEqual(get_deepl_endpoint("abcd-1234"), "https://api.deepl.com/v2/translate")

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LINGUA', response.data)
        self.assertIn(b'LinguaAI', response.data)

    def test_languages_endpoint(self):
        response = self.app.get('/api/languages')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['source_languages']), 10)
        self.assertGreater(len(data['target_languages']), 10)

    def test_translate_missing_key(self):
        # Default .env has placeholder YOUR_REAL_KEY_HERE
        response = self.app.post('/api/translate', 
                                json={"text": "Hello", "source_lang": "auto", "target_lang": "DE"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("authentication failed", data['error'].lower())

    def test_translate_empty_text(self):
        response = self.app.post('/api/translate', 
                                json={"text": "", "source_lang": "auto", "target_lang": "DE"})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
