import requests

BASE_URL = "http://127.0.0.1:5000"
HEADERS = {"Authorization": "Bearer secret-token-123"}


def test_login_success():  # TC01
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_wrong_password():  # TC02
    response = requests.post(
        f"{BASE_URL}/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


def test_get_products():  # TC03
    response = requests.get(f"{BASE_URL}/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_product():  # TC04
    payload = {"name": "Laptop", "price": 55000}
    response = requests.post(f"{BASE_URL}/products", json=payload, headers=HEADERS)
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Laptop"
    assert body["price"] == 55000


def test_create_product_without_token():  # TC05
    response = requests.post(f"{BASE_URL}/products", json={"name": "Phone", "price": 20000})
    assert response.status_code == 401


def test_create_product_invalid_data():  # TC06
    response = requests.post(f"{BASE_URL}/products", json={"name": "", "price": 1000}, headers=HEADERS)
    assert response.status_code == 400


def test_get_product_not_found():  # TC07
    response = requests.get(f"{BASE_URL}/products/99999")
    assert response.status_code == 404


def test_server_error():  # TC08
    response = requests.get(f"{BASE_URL}/crash")
    assert response.status_code == 500