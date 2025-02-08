# Transfer ESPP shares from Computershare to another brokerage
#
# DTC, company name, login info, and brokerage account number are needed
# Loading the previously mentioned info from a .env file in the same directory as this file

import sys
import tempfile
import time

from dotenv import load_dotenv
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from common import (
    initialize_driver,
    initialize_wait,
    sign_in,
    DTC,
    ACCOUNT_NUMBER,
    PASSWORD
)

# Load env variables from ".env" file in the same folder
load_dotenv()

# Automatically get and cache the webdriver for Chrome
driver = initialize_driver()
wait = initialize_wait(driver)


# Function to transfer shares to another brokerage
def transfer_shares():
    try:
        sign_in(wait, driver)

        print("Click Transact")
        wait.until(expected_conditions.presence_of_element_located((By.ID, "ctl01_primaryNavigation")))
        driver.find_element(By.XPATH, '//a[contains(@href,"Transactions")]').click()

        print("Select ESPP holding (not dividends)")
        wait.until(expected_conditions.presence_of_element_located((By.ID, "EmployeePlanId")))
        select = Select(driver.find_element(By.ID, "EmployeePlanId"))
        select.select_by_value("1")

        print("Click transfer button")
        wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "DlgLnk")))
        driver.find_element(By.XPATH, '//a[contains(@title,"Transfer to Broker")]').click()

        print("Click all available shares radio")
        wait.until(expected_conditions.presence_of_element_located((By.ID, "sharePortion0")))
        driver.find_element(By.ID, "sharePortion0").click()

        print("Select DTC")
        wait.until(expected_conditions.presence_of_element_located((By.ID, "BrokerCodeType")))
        select = Select(driver.find_element(By.ID, "BrokerCodeType"))
        select.select_by_value("D")

        print("Input broker DTC and account number")
        driver.find_element(By.ID, "BrokerCode").send_keys(str(DTC))
        driver.find_element(By.ID, "AccountNumber").send_keys(str(ACCOUNT_NUMBER))

        print("Click next button")
        driver.find_element(By.ID, "cmdNext").click()

        print("Input PIN again")
        wait.until(expected_conditions.presence_of_element_located((By.ID, "PIN")))
        driver.find_element(By.ID, "PIN").send_keys(str(PASSWORD))

        print("Click submit")
        driver.find_element(By.ID, "cmdNext").click()

        time.sleep(2)
        screenshot_path = tempfile.mktemp(prefix = "transfer_", suffix=".png")
        driver.save_screenshot(screenshot_path)
        print(f"You can find a screenshot of your transaction at {screenshot_path}")

    except:
        # Need to add more specific exception catches
        print("Error?")
        print(sys.exc_info()[0])
        pass

    driver.quit()


try:
    transfer_shares()
except:
    driver.quit
