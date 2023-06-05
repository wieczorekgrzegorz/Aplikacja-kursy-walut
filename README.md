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
    - GET request: Renders the index.html template without a chart but with available currencies.
    - POST request: Validates the input dates (max period 93 days as per API NBP, 'end date' can't be earlier than 'start date', neither date can be later than yesterday), fetches the currency rates, saves them to the database, generates a chart, and renders the index.html template with the chart and available currencies.

To run this application locally, you need to install Flask and other required libraries. Use "pip install -r requirements.txt" to install the dependencies listed in the requirements.txt file. Then, run the "python app.py" command in your terminal or command prompt from the project directory to start the server. Finally, open your web browser and go to http://localhost:8000/ to access the application.

-----------------------------------------------

[PL]
To jest aplikacja Python Flask przeznaczona dla programistów Pythona. Pobiera ona kursy wymiany walut z API NBP, zapisuje je w bazie danych SQLite i generuje wykres dla wybranej waluty. Przedstawia praktyczny przykład integracji interfejsów API, pracy z bazami danych oraz generowania wizualizacji.

Oto wyjaśnienie poszczególnych komponentów aplikacji:

- Importowanie niezbędnych bibliotek: Wczytywane są wymagane biblioteki, w tym Flask do tworzenia aplikacji webowych.
- Definiowanie stałych: Zdefiniowane są stałe dla folderów z danymi i statycznymi plikami oraz ścieżka do pliku bazy danych.
- Tworzenie listy dostępnych walut: Aplikacja pobiera dane o walutach z API NBP i tworzy posortowaną listę dostępnych walut.
- Definiowanie funkcji:
    - fetch_available_currencies(): Pobiera dostępne waluty z API NBP.
    - is_data_already_in_cache(): Sprawdza, czy żądane dane są już dostępne w lokalnej bazie danych.
    - fetch_currency_rates(): Pobiera kursy wymiany walut z API NBP dla określonej waluty i zakresu dat.
    - save_currency_rates_to_db(): Zapisuje pobrane informacje o kursach wymiany do bazy danych SQLite.
    - get_data_from_local_db(): Pobiera dane o walucie z bazy danych SQLite na podstawie wybranej waluty i zakresu dat.
    - generate_chart(): Generuje wykres za pomocą biblioteki matplotlib dla wybranej waluty i zakresu dat.
    - validate_user_input(): Sprawdza poprawność wprowadzonych przez użytkownika daty początkowej i końcowej.
- Definiowanie głównej ścieżki: Główna ścieżka '/' jest definiowana przy użyciu dekoratora @app.route w Flasku. Obsługuje zarówno żądania GET, jak i POST.
    - Żądanie GET: Renderuje szablon index.html bez wykresu, ale z dostępnymi walutami.
    - Żądanie POST: Sprawdza poprawność wprowadzonych dat, sprawdza, czy dane są już w pamięci podręcznej, pobiera kursy walut w razie potrzeby, zapisuje je w bazie danych, generuje wykres, a następnie renderuje szablon index.html z wykresem i dostępnymi walutami.

Aby uruchomić tę aplikację lokalnie, należy zainstalować Flask i inne wymagane biblioteki. Użyj polecenia pip install -r requirements.txt, aby zainstalować zależności wymienione w pliku requirements.txt. Następnie, uruchom polecenie python app.py w terminalu lub wierszu polecenia z folderu projektu, aby uruchomić serwer. Wreszcie, otwórz przeglądarkę internetową i przejdź pod adres http://localhost:8000/, aby uzyskać dostęp do aplikacji.