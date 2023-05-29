# Import libraries necessary for application
import csv
from flask import Flask, render_template, request, after_this_request, send_file
import requests
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import MO
import matplotlib.ticker as ticker
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


print('app log: Launching app, downloading list of currencies available on NBP API... ', end = '') # console info
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
            
print('Success! ') # console info

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

    print('app log: Downloading data from NBP API... ', end = '') # console info

    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}"
    
    response = requests.get(url)
    
    error_message = None
    if response.status_code == 200:
        print('Success!') # console info
        return error_message, response.json()
    
    elif response.status_code == 404:
        error_message = 'Error 404: No data found for selected time frame.'
        print(f'{error_message}') # console info
        return error_message, None
    
    else:
        error_message = f'Failure, status code: {response.status_code}.'
        print(f'{error_message}') # console info
        return error_message, None


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
        major_locator_x = mdates.AutoDateLocator(interval_multiples = True)        
        ax.xaxis.set_major_locator(major_locator_x)
        minor_locator_x = ticker.MultipleLocator(1)
        ax.xaxis.set_minor_locator(minor_locator_x)

        # Plot the chart
        ax.plot(dates, rates, linewidth = 2, marker = '.', markersize = 7)

        ax.set_ylabel('Exchange Rate [PLN]', fontdict = {'weight': 'bold'})
        ax.set_title(f'{currency}/PLN Exchange Rates', fontdict = {'weight': 'bold'})
        
        # set fig & style
        axes_color = '#1f77b4'
        grid_color = '#e7f6f8'
        bg_color = '#fcfcfc'
        
        fig.set_facecolor(bg_color)
        ax.patch.set_facecolor(bg_color)
        
        ax.grid(visible = True, axis = 'y', color = grid_color, linestyle = ':')
        ax.grid(visible = True, axis = 'x', color = grid_color, linestyle = ':')
        
        ax.spines['bottom'].set_color(axes_color)
        ax.spines['top'].set_color(axes_color) 
        ax.spines['right'].set_color(axes_color)
        ax.spines['left'].set_color(axes_color)
        
        ax.tick_params(axis='x', colors=axes_color)
        ax.tick_params(axis='y', colors=axes_color)
        
        ax.yaxis.label.set_color(axes_color)
        ax.xaxis.label.set_color(axes_color)
        
        ax.title.set_color(axes_color)
        
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
    
    error_message = ''
    today = datetime.now().date()
    yesterday = today - timedelta(days = 1)
    
    if request.method == 'POST':
        
        print('app log: Getting user\'s input on data selection... ', end = '') # console info
        selected_currency = request.form.get('currency')
        
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        # Date validation
        error_message = None
    
        try:
            assert start_date <= end_date, "'Start Date' cannot be after 'End Date'."
                                
            max_range = timedelta(days = 93)
                
            assert end_date - start_date <= max_range, "Maximum date range is 93 calendar days."

        except Exception as e:
            error_message = str(e)
            print(f'Failure: {error_message}') # console info
            return render_template('index.html', error_message = error_message, chart_available = False, 
                                   available_currencies = available_currencies, yesterday = yesterday)
        
        print('Success!') # console info

        error_message, currency_rates = fetch_currency_rates(selected_currency, start_date, end_date)
        
        if currency_rates:
            save_currency_rates_to_db(selected_currency, currency_rates)
            
            print('app log: Generating chart... ', end = '') # console info

            @after_this_request
            def send_chart(response):
                generate_chart(selected_currency, start_date, end_date)
                return response
            
            print('Success, all set!') # console info

            return render_template('index.html', error_message = error_message, chart_available = True, 
                                   available_currencies = available_currencies, selected_currency = selected_currency,
                                   yesterday = yesterday, start_date = start_date, end_date = end_date,
                                   currency_data = get_currency_data(selected_currency, start_date, end_date))
        
    return render_template('index.html', error_message = error_message, chart_available = False, 
                           available_currencies = available_currencies, yesterday = yesterday)

if __name__ == '__main__':
    app.run(debug = False, port = 8000)
