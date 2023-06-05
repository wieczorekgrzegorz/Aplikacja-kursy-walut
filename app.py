# Import libraries necessary for application
from flask import Flask, render_template, request, after_this_request
import requests
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import os
from datetime import datetime, timedelta

# Set a non-reactive backend for matplotlib to avoid 
# "Tcl_AsyncDelete: async handler deleted by the wrong thread" error
matplotlib.use('Agg')

# Define database file path and create folder if it does not exist.
data_folder = "data"
db_file = os.path.join(data_folder, "currency_rates.db")
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

static_folder = 'static'
chart_file = os.path.join(static_folder, "chart.png")

app = Flask(__name__)

def fetch_available_currencies(): 
    url = "https://api.nbp.pl/api/exchangerates/tables/a"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data and len(data) > 0:
            rates = data[0].get("rates")
            
            if rates:
                available_currencies = [rate["code"] for rate in rates]
                available_currencies.sort()
                
    return available_currencies 

def is_data_already_in_cache(currency: str, start_date: str, end_date: str, db_file: str) -> bool:    
    start_date_date_format = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_date_format = datetime.strptime(end_date, '%Y-%m-%d').date()  
    days_difference = (end_date_date_format - start_date_date_format).days

    dates_to_check = []
    
    for i in range(days_difference):
        date_to_check = start_date_date_format + timedelta(days = i)
        
        # Weekends excluded as there's no exchange on weekends. 
        if date_to_check.isoweekday() < 6:
            dates_to_check.append(date_to_check.strftime('%Y-%m-%d'))
            
    conn = sqlite3.connect(db_file)
    conn.row_factory = lambda cursor, row: row[0]
    cached_list = []
     
    with conn:   
        c = conn.cursor()
        query = '''
                SELECT 
                    date,
                    rate 
                FROM 
                    rates 
                WHERE 
                    currency = ? AND date BETWEEN ? AND ?
                ORDER BY
                    date
                '''
        c.execute(query, (currency, start_date, end_date))          
    cached_list = c.fetchall()

    for date in dates_to_check:
        if date not in cached_list:
            print('Requested data not in cache, downloading from NBP API.')
            return False
    print('Requested data aready in local db.')
    return True
                    

def fetch_currency_rates(currency:str , start_date:str , end_date:str) -> tuple[str, dict]:
    url = f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/{start_date}/{end_date}"
    response = requests.get(url)
    
    error_message = None
    if response.status_code == 200:
        return error_message, response.json()
    
    elif response.status_code == 404:
        error_message = 'Error 404: No data found for selected currency and/or time frame.'
        return error_message, None
    
    else:
        error_message = f'Failure, status code: {response.status_code}.'
        return error_message, None

def save_currency_rates_to_db(currency:str, currency_rates:dict, db_file:str) -> None:
    conn = sqlite3.connect(db_file)
    with conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS rates(
                        date     TIMESTAMP,
                        currency TEXT,
                        rate     REAL)
                        ''')

        rows_to_insert = []
        
        for item in currency_rates['rates']:
            date = item['effectiveDate']                      
            rate = item['mid']
            currency = currency
            rows_to_insert.append((date, currency, rate))
        
        c.executemany("INSERT INTO rates VALUES (?, ?, ?)", rows_to_insert)
        
        # remove duplicated rows
        c.execute('''
                    DELETE 
                    FROM rates AS r1 
                    WHERE EXISTS (
                        SELECT * 
                        FROM rates AS r2 
                        WHERE r1.date = r2.date 
                            AND r1.currency = r2.currency 
                            AND r1.rowid > r2.rowid
                            )
                        ''')

def get_data_from_local_db(currency:str, start_date:str, end_date:str, db_file:str) -> list[tuple]:    
    conn = sqlite3.connect(db_file)
     
    with conn:   
        c = conn.cursor()
        query = '''
            SELECT 
                date, 
                rate 
            FROM 
                rates 
            WHERE 
                currency = ? 
                AND date BETWEEN ? AND ?
            ORDER BY
                date
        '''
        c.execute(query, (currency, start_date, end_date))
                
        return c.fetchall()

def generate_chart(currency_table:list[tuple], selected_currency:str) -> None:
    dates = [row[0] for row in currency_table]
    rates = [row[1] for row in currency_table]
    
    fig, ax = plt.subplots()
    axes_color = '#1f77b4'
    grid_color = '#e7f6f8'
    bg_color = '#fcfcfc'
    fig.set_facecolor(bg_color)
    ax.patch.set_facecolor(bg_color)

    ax.plot(dates, rates, linewidth = 2, marker = '.', markersize = 7)

    ax.set_ylabel(f'Exchange rates', fontdict = {'weight': 'bold'})
    ax.yaxis.label.set_color(axes_color)
    
    major_locator_x = mdates.AutoDateLocator(interval_multiples = True)        
    ax.xaxis.set_major_locator(major_locator_x)
    minor_locator_x = ticker.MultipleLocator(1)
    ax.xaxis.set_minor_locator(minor_locator_x)
    ax.xaxis.label.set_color(axes_color)
    
    ax.tick_params(axis='x', colors=axes_color)
    ax.tick_params(axis='y', colors=axes_color)
    plt.xticks(rotation = 45, ha = 'right')
        
    ax.set_title(f'{selected_currency}/PLN Exchange Rates', fontdict = {'weight': 'bold'})
    ax.title.set_color(axes_color)
    
    ax.grid(visible = True, axis = 'y', color = grid_color, linestyle = ':')
    ax.grid(visible = True, axis = 'x', color = grid_color, linestyle = ':')
    
    ax.spines['bottom'].set_color(axes_color)
    ax.spines['top'].set_color(axes_color) 
    ax.spines['right'].set_color(axes_color)
    ax.spines['left'].set_color(axes_color)
    
    plt.tight_layout()
    plt.savefig(chart_file)  
    plt.close()

def validate_user_input(start_date, end_date):
    error_message = None
    start_date_date_format = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_date_format = datetime.strptime(end_date, '%Y-%m-%d').date()   
    
    try:
        assert start_date_date_format <= end_date_date_format, "'Start Date' cannot be after 'End Date'."                
        max_range = timedelta(days = 93)
        assert end_date_date_format - start_date_date_format <= max_range, "Maximum date range is 93 calendar days."

    except Exception as e:
        error_message = str(e)
        return False, error_message
        
    return True, error_message
    
# Main route '/'
@app.route('/', methods = ['GET', 'POST'])
def index():
    available_currencies = fetch_available_currencies()
    
    error_message = None
    today = datetime.now().date()
    yesterday = today - timedelta(days = 1)
    
    if request.method == 'POST':
        
        selected_currency = request.form.get('currency')        
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        input_dates_valid, error_message = validate_user_input(start_date, end_date)
        
        if input_dates_valid == False:
            return render_template('index.html', 
                                error_message = input_dates_valid, 
                                chart_available = False, 
                                available_currencies = available_currencies, 
                                yesterday = yesterday
                                )

        data_already_in_cache = is_data_already_in_cache(selected_currency, start_date, end_date, db_file)
        
        if data_already_in_cache == False:
            error_message, currency_rates = fetch_currency_rates(selected_currency, start_date, end_date)
            save_currency_rates_to_db(selected_currency, currency_rates, db_file)
                    
        currency_table = get_data_from_local_db(selected_currency, start_date, end_date, db_file)

        @after_this_request
        def send_chart(response):
            generate_chart(currency_table, selected_currency)
            return response
        
        return render_template('index.html', 
                                error_message = error_message, 
                                chart_available = True, 
                                available_currencies = available_currencies, 
                                selected_currency = selected_currency,
                                yesterday = yesterday, 
                                start_date = start_date, 
                                end_date = end_date,
                                currency_data = currency_table
                                )
        
    return render_template('index.html', 
                           error_message = error_message, 
                           chart_available = False, 
                           available_currencies = available_currencies, 
                           yesterday = yesterday
                           )

if __name__ == '__main__':
    app.run(debug = False, port = 8000)