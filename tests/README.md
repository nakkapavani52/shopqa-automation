# ShopQA Test Automation

A small Flask app (REST API + two web pages) and a test automation framework built around it.

## What is tested
- API tests with Pytest and requests: login, products, status codes 200, 201, 400, 401, 404 and 500
- UI tests with Selenium: login success, wrong password, add a product
- Manual test cases written in Excel and run in Postman

## Tech
Python, Flask, SQLAlchemy, Pytest, requests, Selenium, Postman, Git

## How to run
1. Create and activate a virtual environment: `python -m venv venv`, then `venv\Scripts\activate`
2. Install packages: `pip install flask sqlalchemy requests pytest pytest-html selenium`
3. Start the app in one terminal: `python app.py`
4. Run the tests in a second terminal: `pytest -v tests`
5. HTML report: `pytest -v tests --html=reports/report.html --self-contained-html`

## Author
Pavani