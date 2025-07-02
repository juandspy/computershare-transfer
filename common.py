import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


# Load env variables from ".env" file in the same folder
load_dotenv(override=True)

# Your EquatePlus username
USERNAME = os.getenv("USERNAME")

# Your EquatePlus password
PASSWORD = os.getenv("PASSWORD")

# DTC number for brokerage
DTC = os.getenv("DTC")

# Account number
ACCOUNT_NUMBER = os.getenv("ACCOUNT_NUMBER")


def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    # Automatically get and cache the webdriver for Chrome
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get("http://www.na.equateplus.com/")
    return driver


def initialize_wait(driver):
    return WebDriverWait(driver, 10)


def sign_in(wait, driver):
    print("Sign in")
    wait.until(
        expected_conditions.title_contains(
            "EquatePlus | Employee Share Plan Participant Login"
        )
    )

    print("Input username")
    driver.find_element(By.ID, "eqUserId").send_keys(str(USERNAME))
    print("Click Continue button")
    driver.find_element(By.ID, "defaultButton").click()

    print("Input password")
    wait.until(expected_conditions.presence_of_element_located((By.ID, "eqPwdId")))
    driver.find_element(By.ID, "eqPwdId").send_keys(str(PASSWORD))

    print("Login")
    driver.find_element(By.ID, "defaultButton").click()

    wait.until(
        expected_conditions.presence_of_element_located(
            (By.ID, "portfolioandsharepriceandplans")
        )
    )


if __name__ == "__main__":
    driver = initialize_driver()
    wait = initialize_wait(driver)
    sign_in(wait, driver)
