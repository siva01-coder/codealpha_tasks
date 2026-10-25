import unittest
import json
from app import app

class FAQBotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_api_chat_test1_admission(self):
        res = self.app.post('/api/chat', json={"message": "How can I apply for admission?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["category"], "Admissions")
        self.assertGreaterEqual(data["confidence"], 25)

    def test_api_chat_test2_join_college(self):
        res = self.app.post('/api/chat', json={"message": "How do I join the college?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["category"], "Admissions")

    def test_api_chat_test3_attendance(self):
        res = self.app.post('/api/chat', json={"message": "What happens if my attendance is low?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Attendance")

    def test_api_chat_test4_exams(self):
        res = self.app.post('/api/chat', json={"message": "When are semester exams conducted?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Examinations")

    def test_api_chat_test5_scholarship(self):
        res = self.app.post('/api/chat', json={"message": "How can I get a scholarship?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Scholarships")

    def test_api_chat_test6_internship(self):
        res = self.app.post('/api/chat', json={"message": "Does the college provide internships?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Internships")

    def test_api_chat_test7_library(self):
        res = self.app.post('/api/chat', json={"message": "How can I use the library?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Library")

    def test_api_chat_test8_hostel(self):
        res = self.app.post('/api/chat', json={"message": "What is the hostel facility?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Hostel")

    def test_api_chat_test9_out_of_domain(self):
        res = self.app.post('/api/chat', json={"message": "Who is the president of the United States?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(data["category"])
        self.assertIn("college-related FAQs", data["answer"])

    def test_api_chat_test10_empty_input(self):
        res = self.app.post('/api/chat', json={"message": ""})
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], "Please enter a question.")

    def test_api_chat_test11_very_long_input(self):
        long_msg = "admission " * 300
        res = self.app.post('/api/chat', json={"message": long_msg})
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("2000 characters", data["error"])

    def test_api_chat_test12_misspelled_input(self):
        res = self.app.post('/api/chat', json={"message": "How can I aply for admision?"})
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["category"], "Admissions")

    def test_get_faqs(self):
        res = self.app.get('/api/faqs')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(data["count"], 40)

    def test_get_categories(self):
        res = self.app.get('/api/categories')
        data = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(len(data["categories"]), 15)

if __name__ == '__main__':
    unittest.main()
