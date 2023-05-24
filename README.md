[ENG]
This is a Python Flask application designed for Python developers. It fetches currency exchange rates from the NBP API, saves them to an SQLite database, and generates a chart for a selected currency. It provides a practical example of integrating APIs, working with databases, and generating visualizations.

Here's an explanation of the application's components:

- Import necessary libraries: The required libraries, including Flask for web development, are imported.
- Define constants: Constants are defined for the data and static folders and the database file path.
- Create a list of available currencies: The application fetches currency data from the NBP API and creates a sorted list of available currencies.
- Define functions:
    - fetch_currency_rates(): Fetches currency exchange rates from the NBP API for a specified currency and date range.
    - save_currency_rates_to_db(): Saves the fetched exchange rate information to an SQLite database.
    - get_currency_data(): Retrieves currency data from the SQLite database based on the selected currency and date range.
    - generate_chart(): Generates a chart using matplotlib for the selected currency and date range.
- Define the main route: The main route '/' is defined using Flask's @app.route decorator. It handles both GET and POST requests.
    GET request: Renders the index.html template without a chart but with available currencies.
    POST request: Validates the input dates (max period 93 days as per API NBP, 'end date' can't be earlier than 'start date', 
    neither date can be later than yesterday), fetches the currency rates, saves them to the database, generates a chart, 
    and renders the index.html template with the chart and available currencies.

To run this application locally, you need to install Flask and other required libraries. Use "pip install -r requirements.txt" to install the dependencies listed in the requirements.txt file. Then, run the "python app.py" command in your terminal or command prompt from the project directory to start the server. Finally, open your web browser and go to http://localhost:8000/ to access the application.

[PL]
Jest to aplikacja Python Flask przeznaczona dla deweloperów Pythona. Pobiera ona kursy wymiany walut z API NBP, zapisuje je w bazie danych SQLite i generuje wykres dla wybranej waluty.

Oto wyjaśnienie poszczególnych sekcji kodu:

- Import necessary libraries: Importowanie niezbędnych bibliotek.
- Define constants: Definiowanie stałych dla folderów z danymi i statycznymi oraz ścieżki pliku bazy danych.
- Create a list of available currencies: Tworzenie listy dostępnych walut poprzez pobranie danych z API NBP.
- Define functions:
    - fetch_currency_rates(): Definiowanie funkcji do pobierania kursów walut z API NBP.
    - save_currency_rates_to_db(): Definiowanie funkcji do zapisywania kursów walut w bazie danych SQLite.
    - get_currency_data(): Definiowanie funkcji do pobierania danych waluty z bazy danych SQLite.
    - generate_chart(): Definiowanie funkcji do generowania wykresu dla wybranej waluty.
- Definiowanie głównego adresu '/' za pomocą dekoratora @app.route w Flasku.
    Obsługuje żądania GET i POST. Jeśli otrzymuje żądanie POST, waliduje wprowadzone daty (max zakres 93 dni zgodnie z ograniczeniami API NBP, 
    'end date' nie może być przed 'start date', żadna z dat nie może być późniejszą niż wczorajsza),
    pobiera kursy walut, zapisuje je w bazie danych, generuje wykres dla wybranej waluty
    i renderuje szablon index.html z wykresem i dostępnymi walutami.
    Jeśli otrzymuje żądanie GET, renderuje szablon index.html bez wykresu, ale z dostępnymi walutami.

Aby uruchomić tę aplikację lokalnie na swoim komputerze, musisz zainstalować Flask i inne wymagane biblioteki.
Możesz to zrobić, uruchamiając komendę "pip install -r requirements.txt" w terminalu lub wierszu polecenia, będąc w katalogu projektu.
Następnie możesz uruchomić serwer, wpisując "python app.py" w terminalu lub wierszu polecenia, będąc w katalogu projektu.
Wreszcie, otwórz przeglądarkę internetową i przejdź pod adres http://localhost:8000/, aby uzyskać dostęp do aplikacji.