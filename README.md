# 📈 Price Tracker API – System Monitorowania Cen

## 🚀 Przegląd
Prosty, ale inteligentny system do monitorowania cen produktów z dowolnych stron eCommerce. Aplikacja przechowuje historię cen w PostgreSQL i wysyła spersonalizowane alerty e-mail, gdy cena spadnie.

---

## 🛠️ Architektura i Technologie

| Komponent | Technologia | Kluczowe Osiągnięcie |
| :--- | :--- | :--- |
| **Backend** | **Python (FastAPI)** | Wdrożenie pełnego REST API (CRUD) dla Użytkowników i Produktów. |
| **Baza Danych** | **PostgreSQL (SQLAlchemy)** | Modelowanie relacji 1:N (User:Product), kaskadowe usuwanie danych. |
| **Scraping** | **Wielopoziomowy Scraper** | Strategia 3-fazowa: **HTTPX/Regex** ➡️ **OpenAI AI** ➡️ **Selenium** |
| **Logika** | **APScheduler, SMTP** | Cykliczne sprawdzanie cen w tle i dynamiczna wysyłka alertów e-mail do właściciela produktu. |
| **Frontend** | **Vanilla JS/HTML** | Prosty interfejs do demonstracji funkcjonalności API. |

---

## ⚡ Jak Uruchomić (Quick Start)

**Wymagania:** Python 3.10+, PostgreSQL, Klucz OpenAI API, Dane SMTP.

1.  **Klonowanie i instalacja zależności:**
    ```bash
    git clone [Twój adres repo]
    pip install -r requirements.txt
    ```

2.  **Konfiguracja:** Wypełnij plik **`.env`** danymi do PostgreSQL, OpenAI API oraz serwera SMTP.

3.  **Inicjalizacja i Start:**
    ```bash
    python app/db.py
    uvicorn app.main:app --reload
    ```
    * API i Swagger: `http://localhost:8000/docs`

---

## ➡️ Następne Kroki

* [ ] **Docker:** Pełna konteneryzacja środowiska (API + PostgreSQL + Chrome/Selenium).
* [ ] **Waluty:** Implementacja konwersji walut.
* [ ] **Uwierzytelnianie (JWT):** Dodanie tokenów bezpieczeństwa dla API.