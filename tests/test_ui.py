import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture
def driver():
    driver = webdriver.Edge()  # use webdriver.Chrome() if you prefer Chrome
    driver.maximize_window()
    yield driver
    driver.quit()


def login(driver, username, password):
    driver.get(f"{BASE_URL}/ui/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()


def test_ui_login_success(driver):
    login(driver, "admin", "admin123")
    WebDriverWait(driver, 10).until(EC.url_contains("/ui/products"))
    assert "/ui/products" in driver.current_url


def test_ui_login_wrong_password(driver):
    login(driver, "admin", "wrong")
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.ID, "message"), "Login failed")
    )
    assert "Invalid credentials" in driver.find_element(By.ID, "message").text


def test_ui_add_product(driver):
    login(driver, "admin", "admin123")
    WebDriverWait(driver, 10).until(EC.url_contains("/ui/products"))
    driver.find_element(By.ID, "product-name").send_keys("Mouse")
    driver.find_element(By.ID, "product-price").send_keys("500")
    driver.find_element(By.ID, "add-btn").click()
    new_row = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//table[@id='product-table']//td[text()='Mouse']"))
    )
    assert new_row.text == "Mouse"