import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


# Load env variables from ".env" file in the same folder
load_dotenv()

# Your Computershare username
USERNAME = os.getenv("USERNAME")

# Your Computershare password
PASSWORD = os.getenv("PASSWORD")

# Your company name
COMPANY_NAME = os.getenv("COMPANY_NAME")

# DTC number for brokerage
DTC = os.getenv("DTC")

# Account number
ACCOUNT_NUMBER = os.getenv("ACCOUNT_NUMBER")


def initialize_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless=new")
    # Automatically get and cache the webdriver for Chrome
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get("https://www-us.computershare.com/employee/login/selectcompany.aspx")
    return driver

def initialize_wait(driver):
    return WebDriverWait(driver, 10)


def sign_in(wait, driver):
    print("Sign in")
    wait.until(expected_conditions.title_contains("Employee - Plans"))
    driver.find_element(By.ID, "SearchName").send_keys(str(COMPANY_NAME))
    driver.find_element(By.NAME, "submitform").click()

    print("Select Employee login")
    wait.until(expected_conditions.presence_of_element_located((By.XPATH, '//a[contains(@href,"Employee/Login")]')))
    driver.find_element(By.XPATH, '//a[contains(@href,"Employee/Login")]').click()
    wait.until(expected_conditions.presence_of_element_located((By.ID, "loginIDType")))

    print("Choose Username login option")
    select = Select(driver.find_element(By.ID, "loginIDType"))
    select.select_by_visible_text("Username")

    print("Input credentials")
    driver.find_element(By.ID, "tempLoginID").send_keys(str(USERNAME))
    driver.find_element(By.ID, "employeePIN").send_keys(str(PASSWORD))
    print("Login")
    driver.find_element(By.NAME, "sbmtBtn").click()
