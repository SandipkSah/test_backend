import unittest
from quart import json
from app import app

class QuartTestCase(unittest.TestCase):

    def setUp(self):
        # Sets up the test client before each test
        self.app = app.test_client()
        self.app.testing = True

    def test_index(self):
        # Test the index route
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), "Hello from index")

    def test_search_stocks(self):
        # Test the stock search route
        response = self.app.get('/api/search_stocks/apple')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_get_ticker(self):
        # Test the get ticker route with a valid ISIN
        valid_isin = 'US0378331005'  # Example ISIN for Apple
        response = self.app.get(f'/api/get_ticker/{valid_isin}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('ticker', data)

        # Test the get ticker route with an invalid ISIN
        invalid_isin = 'INVALIDISIN'
        response = self.app.get(f'/api/get_ticker/{invalid_isin}')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_current_price(self):
        # Test the current price route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/current_price/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('summary', data)

    def test_recent_news(self):
        # Test the recent news route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/recent_news/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('summary', data)

    def test_financial_statements(self):
        # Test the financial statements route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/financial_statements/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('summary', data)

    def test_analyst_sentiments(self):
        # Test the analyst sentiments route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/analyst_sentiments/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('summary', data)

    def test_business_model(self):
        # Test the business model route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/business_model/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)
        self.assertIn('summary', data)

    def test_time_series(self):
        # Test the time series route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/time_series/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)

    def test_swot_analysis(self):
        # Test the SWOT analysis route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/swot_analysis/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('swot_analysis', data)

    def test_total_revenue(self):
        # Test the total revenue route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/total_revenue/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    def test_ebitda(self):
        # Test the EBITDA route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/ebitda/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    def test_balance_sheet(self):
        # Test the balance sheet route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/balance_sheet/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)

    def test_gpt_analysis(self):
        # Test the GPT analysis route
        ticker = 'AAPL'  # Example ticker for Apple
        response = self.app.get(f'/api/gpt_analysis/{ticker}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('data', data)

if __name__ == '__main__':
    unittest.main()
