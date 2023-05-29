import unittest
import os
from app import fetch_currency_rates, save_currency_rates_to_db, get_currency_data

class TestCurrencyApp(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.db_file = os.path.join("data", "currency_rates.db")
    
    def test_fetch_currency_rates(self):
        # Test case for successful API call
        print('Test 1a: Test case for successful API call.')
        currency = 'USD'
        start_date = '2022-01-01'
        end_date = '2022-01-07'
        error_message, response = fetch_currency_rates(currency, start_date, end_date)
        self.assertIsNone(error_message)
        self.assertIsNotNone(response)

        # Test case for non-existent currency
        print('Test 1b: Test case for non-existent currency.')
        currency = 'XYZ'
        error_message, response = fetch_currency_rates(currency, start_date, end_date)
        self.assertIsNotNone(error_message)
        self.assertIsNone(response)
        
    def test_save_currency_rates_to_db(self):
        # Test case for saving currency rates to the database
        print('Test 2: Test case for saving currency rates to the database.')
        
        currency = 'USD'
        currency_rates = {
            'rates': [
                {'no': '001/A/NBP/2022', 'effectiveDate': '2022-01-01', 'mid': 3.75},
                {'no': '001/A/NBP/2022', 'effectiveDate': '2022-01-02', 'mid': 3.80},
                {'no': '001/A/NBP/2022', 'effectiveDate': '2022-01-03', 'mid': 3.85}
            ]
        }
        save_currency_rates_to_db(currency, currency_rates, self.db_file)

        # Verify if the data is saved correctly in the database and can be retrieved
        currency_data = get_currency_data(currency, '2022-01-01', '2022-01-03', self.db_file)
        self.assertEqual(currency_data, [
            ('2022-01-01', 3.75),
            ('2022-01-02', 3.80),
            ('2022-01-03', 3.85)
        ])
        
if __name__ == '__main__':
    unittest.main()