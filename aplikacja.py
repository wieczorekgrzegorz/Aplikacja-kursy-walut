# Import necessary libraries
from flask import Flask, render_template, request, after_this_request
import requests
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime, timedelta

# Set a non-reactive backend for matplotlib to avoid 
# "Tcl_AsyncDelete: async handler deleted by the wrong thread" error
matplotlib.use('Agg')  

# Define constants for data and static folders and database file path.
data_folder = "data"
db_file = os.path.join(data_folder, "currency_rates.db")
static_folder = 'static'
chart_file = os.path.join(static_folder, "chart.png")

# Create a list of available currencies by fetching the data from NBP API.
available_currencies = []
url = "https://api.nbp.pl/api/exchangerates/tables/a"
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    if data and len(data) > 0:
        rates = data[0].get("rates")
        if rates:
            available_currencies = [rate["code"] for rate in rates]
            available_currencies.sort()

# initiate Flask app
app = Flask(__name__)

def fetch_currency_rates(currency:str , start_date:str , end_date:str ) -> dict:
    '''
    Fetches currency exchange rate from NBP API.

    Parameters:
        currency (str): Currency code (e.g. USD).
        start_date (str): Start date in format YYYY-MM-DD.
        end_date (str): End date in format YYYY-MM-DD.

    Returns:
        dict: JSON response containing exchange rate information or None if unsuccessful.
    '''

    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    
    else:
        return None


def save_currency_rates_to_db(currency:str , currency_rates:dict) -> None:
    '''
    Saves fetched exchange rate information to SQLite database.

    Parameters:
        currency (str): Currency code (e.g. USD).
        currency_rates (dict): JSON response containing exchange rate information.

    Returns:
        None
    '''

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    conn = sqlite3.connect(db_file)
        
    with conn:   
        c = conn.cursor()
        c.execute('''DROP TABLE IF EXISTS rates''')
        c.execute('''CREATE TABLE IF NOT EXISTS rates(date text,currency text,rate real)''')

        rows_to_insert = []
        
        for item in currency_rates['rates']:
            date = item['effectiveDate']
            rate = item['mid']
            rows_to_insert.append((date, currency, rate))
        
        c.executemany("INSERT INTO rates VALUES (?, ?, ?)", rows_to_insert)

# Function to get currency data from SQLite database.
def get_currency_data(currency:str, start_date:str, end_date:str) -> list[tuple]:
    '''
    Retrieves currency data from SQLite database.

    Parameters:
        currency (str): Currency code (e.g. USD).
        start_date (str): Start date in format YYYY-MM-DD.
        end_date (str): End date in format YYYY-MM-DD.

    Returns:
        list[tuple]: List of tuples containing date and exchange rate.
    '''
    
    conn = sqlite3.connect(db_file)
     
    with conn:   
        c = conn.cursor()
        c.execute("SELECT date, rate FROM rates WHERE currency=? AND date BETWEEN ? AND ?", 
                (currency, start_date, end_date))
                
        return c.fetchall()

# Function to generate a chart for the selected currency.
def generate_chart(currency:str, start_date:str, end_date:str):
    '''
    Generates a chart for the selected currency.

    Parameters:
        currency (str): Currency code (e.g. USD).
        start_date (str): Start date in format YYYY-MM-DD.
        end_date (str): End date in format YYYY-MM-DD.

    Returns:
        None
    '''
    
    if not os.path.exists(static_folder):
        os.makedirs(static_folder) 
        
    conn = sqlite3.connect(db_file)

    with conn:   
        c = conn.cursor()

        c.execute("SELECT date, rate FROM rates WHERE currency=? AND date BETWEEN ? AND ?", 
                  (currency, start_date, end_date))
        rows = c.fetchall()

        dates = [row[0] for row in rows]
        rates = [row[1] for row in rows]

        # Create figure and axis objects
        fig, ax = plt.subplots()

        # Format the dates on the x-axis
        locator = mdates.AutoDateLocator()
        ax.xaxis.set_major_locator(locator)

        # Plot the chart
        ax.plot(dates, rates)

        # Edit the axes
        ax.set_xlabel('Date')
        ax.set_ylabel('Exchange Rate')
        ax.set_title(f'{currency}/PLN Exchange Rates')
        ax.grid(visible = True, axis = 'y', color = 'gray', linestyle = ':')
        ax.grid(visible = True, axis = 'x', color = 'gray', linestyle = ':')
        
        plt.xticks(rotation = 45, ha = 'right')

        # Adjust the margins
        plt.tight_layout()

        # Save the chart to a file
        plt.savefig(chart_file)  
        
        plt.close()

# Main route '/'
@app.route('/', methods = ['GET', 'POST'])
def index():
    '''
    Renders the index page and handles form submission.

    Returns:
        rendered template: index.html template.
    '''
   
    if request.method == 'POST':
        
        currency = request.form.get('currency')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        # Date validation
        error_message = ''
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            today = datetime.now().date()
            yesterday = today - timedelta(days = 1)

            assert start_date <= end_date, "Error: 'Start Date' cannot be later than 'End Date'"
                
            assert end_date <= yesterday, "Error: Neither date can be later than yesterday"
                
            max_range = timedelta(days = 93)
                
            assert end_date - start_date <= max_range, "Error: Maximum date range is 93 calendar days"

        except Exception as e:
            error_message = str(e)
            return render_template('index.html', error_message = error_message, chart_available = False, 
                                   available_currencies = available_currencies, 
                                   yesterday = datetime.now().date() - timedelta(days = 1))

        currency_rates = fetch_currency_rates(currency, start_date, end_date)
        
        if currency_rates:
            save_currency_rates_to_db(currency, currency_rates)
                
            @after_this_request
            def send_chart(response):
                generate_chart(currency, start_date, end_date)
                return response

            return render_template('index.html', chart_available = True, available_currencies = available_currencies, 
                                   currency_data = get_currency_data(currency, start_date, end_date), 
                                   yesterday = datetime.now().date() - timedelta(days = 1),
                                   start_date = start_date, end_date = end_date)

    return render_template('index.html', chart_available = False, available_currencies = available_currencies, 
                           yesterday = datetime.now().date() - timedelta(days = 1))

if __name__ == '__main__':
    app.run(debug = True, port = 8000)
