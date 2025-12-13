# Price Tracker – system monitorowania cen

## Opis projektu
Price Tracker to aplikacja webowa do śledzenia cen produktów z wybranych stron internetowych.  
Użytkownik może dodać produkt, ustawić cenę docelową i sprawdzać, jak cena zmienia się w czasie.  
System zapisuje historię cen w bazie danych oraz wysyła powiadomienia e-mail, gdy cena spadnie poniżej ustalonego progu.

Projekt składa się z backendu w Pythonie oraz prostego frontendu w HTML, CSS i JavaScript.

---

## Architektura i technologie

| Komponent | Technologia | Funkcja |
| :--- | :--- | :--- |
| **Backend** | **Python (FastAPI)** | REST API obsługujące użytkowników, produkty oraz historię cen (CRUD). |
| **Baza danych** | **PostgreSQL + SQLAlchemy** | Relacyjny model danych (User → Product), przechowywanie cen i alertów. |
| **Scraping cen** | **HTTPX / Regex / Selenium** | Pobieranie aktualnych cen produktów, także ze stron dynamicznych. |
| **Logika aplikacji** | **APScheduler** | Okresowe sprawdzanie cen produktów w tle. |
| **Powiadomienia** | **SMTP (e-mail)** | Wysyłanie e-maili, gdy cena osiągnie ustawiony próg. |
| **Bezpieczeństwo** | **bcrypt** | Hashowanie haseł użytkowników przed zapisem w bazie. |
| **Frontend** | **HTML / CSS / JavaScript** | Prosty interfejs użytkownika komunikujący się z API przez Fetch API. |


