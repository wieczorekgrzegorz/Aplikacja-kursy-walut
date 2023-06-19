import unittest
import os
import tempfile
import sqlite3

from app import (
    fetch_available_currencies,
    is_data_already_in_cache,
    fetch_currency_rates,
    save_currency_rates_to_db,
    get_data_from_local_db,
    validate_user_input,
)


class TestCurrencyApp(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.db_file = os.path.join("data", "currency_rates.db")
        self.temp_db_file = os.path.join("data", tempfile.NamedTemporaryFile().name)

    def test_fetch_available_currencies(self):
        # Test case for successful API call
        print("Test 1: Test case for successful API call.")
        available_currencies = fetch_available_currencies()
        self.assertIsNotNone(available_currencies)
        self.assertGreater(len(available_currencies), 0)

    def test_is_data_already_in_cache(self):
        # Create temporary database file
        db_file = self.temp_db_file

        # Create a connection to the temporary database file
        conn = sqlite3.connect(db_file)
        with conn:
            c = conn.cursor()

            # Create a table to simulate cached data
            c.execute("CREATE TABLE rates (date TIMESTAMP, currency TEXT, rate REAL)")

            # Insert test data into the table
            c.execute("INSERT INTO rates VALUES ('2022-01-01', 'USD', 1.0)")
            c.execute("INSERT INTO rates VALUES ('2022-01-02', 'USD', 1.1)")
            c.execute("INSERT INTO rates VALUES ('2022-01-03', 'USD', 1.2)")
            conn.commit()

            # Test case when data is already in cache
            print("Test 2a: Test case when data is already in cache.")
            currency = "USD"
            start_date = "2022-01-01"
            end_date = "2022-01-03"
            result = is_data_already_in_cache(currency, start_date, end_date, db_file)
            self.assertTrue(result)

            # Test case when data is not in cache
            print("Test 2b: Test case when data is not in cache.")
            currency = "EUR"
            start_date = "2022-01-01"
            end_date = "2022-01-07"
            result = is_data_already_in_cache(currency, start_date, end_date, db_file)
            self.assertFalse(result)

    def test_fetch_currency_rates(self):
        # Test case for successful API call
        print("Test 3a: Test case for successful API call.")
        currency = "USD"
        start_date = "2022-01-01"
        end_date = "2022-01-07"
        error_message, response = fetch_currency_rates(currency, start_date, end_date)
        self.assertIsNone(error_message)
        self.assertIsNotNone(response)

        # Test case for non-existent currency
        print("Test 3b: Test case for non-existent currency.")
        currency = "XYZ"
        error_message, response = fetch_currency_rates(currency, start_date, end_date)
        self.assertIsNotNone(error_message)
        self.assertIsNone(response)

    def test_save_currency_rates_to_db(self):
        # Test case for saving currency rates to the database
        print("Test 4: Test case for saving currency rates to the database.")

        currency = "USD"
        currency_rates = {
            "rates": [
                {"no": "001/A/NBP/2022", "effectiveDate": "2022-01-01", "mid": 3.75},
                {"no": "001/A/NBP/2022", "effectiveDate": "2022-01-02", "mid": 3.80},
                {"no": "001/A/NBP/2022", "effectiveDate": "2022-01-03", "mid": 3.85},
            ]
        }
        save_currency_rates_to_db(currency, currency_rates, self.db_file)

        # Verify if the data is saved correctly in the database and can be retrieved
        currency_data = get_data_from_local_db(
            currency, "2022-01-01", "2022-01-03", self.db_file
        )
        self.assertEqual(
            currency_data,
            [("2022-01-01", 3.75), ("2022-01-02", 3.80), ("2022-01-03", 3.85)],
        )

    def test_validate_user_input(self):
        # Test case for valid input
        print("Test 5a: Test case for valid input.")
        start_date = "2022-01-01"
        end_date = "2022-01-07"
        valid, error_message = validate_user_input(start_date, end_date)
        self.assertTrue(valid)
        self.assertIsNone(error_message)

        # Test case for invalid input (end date before start date)
        print("Test 5b: Test case for invalid input (end date before start date).")
        start_date = "2022-01-07"
        end_date = "2022-01-01"
        valid, error_message = validate_user_input(start_date, end_date)
        self.assertFalse(valid)
        self.assertEqual(error_message, "'Start Date' cannot be after 'End Date'.")

        # Test case for invalid input (date range exceeds maximum)
        print("Test 5c: Test case for invalid input (date range exceeds maximum).")
        start_date = "2022-01-01"
        end_date = "2022-04-15"
        valid, error_message = validate_user_input(start_date, end_date)
        self.assertFalse(valid)
        self.assertEqual(error_message, "Maximum date range is 93 calendar days.")


if __name__ == "__main__":
    unittest.main()
