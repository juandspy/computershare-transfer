# Sell all ESPP shares from EquatePlus
# Company name, login info, and an electronic payment already setup
# Currently, an EFT avoids all fees and charges

import sys
import tempfile
import time

from common import initialize_driver, initialize_wait, sign_in, click_button_robustly
from dotenv import load_dotenv
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait

# Load env variables from ".env" file in the same folder
load_dotenv()

# Automatically get and cache the webdriver for Chrome
driver = initialize_driver()
wait = initialize_wait(driver)



# Function to sell all shares from Computershare directly
def sell_shares():
    wait = WebDriverWait(driver, 10)
    driver.get("https://www.na.equateplus.com/EquatePlusParticipant2/start?csrfpId=CivkBxvZdEKQYqZahp4QeAAE")
    try:
        sign_in(wait, driver)

        print("Click Transact")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "AllTransactions")
            )
        )
        transact_button = wait.until(
            expected_conditions.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[@class="AllTransactions"]//button[contains(@class,"PrincipalButton")]',
                )
            )
        )
        transact_button.click()

        print("Click Sell button")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "TransactionTypeList")
            )
        )
        print("Found TransactionTypeList")
        sell_button = wait.until(
            expected_conditions.element_to_be_clickable(
                (
                    By.XPATH,
                    '//ul[@class="TransactionTypeList"]//button[@class="TransactionButton" and text()="Sell"]',
                )
            )
        )
        print("Found Sell button")
        # sell_button.click()
        click_button_robustly(driver, '//ul[@class="TransactionTypeList"]//button[@class="TransactionButton" and text()="Sell"]', "Sell button")

        print("Click Total Quantity button")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "totalQuantityButton")
            )
        )
        driver.find_element(By.ID, "totalQuantityButton").click()

        print("Click Next button")
        click_button_robustly(driver, '//button[@class="PrincipalButton" and text()="Next"]', "Next button")

        print("Click Accept checkbox")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//label[@for="ORDER_AGREEMENT_MARKET_ACCEPT_FORM_CONDITIONS0"]')
            )
        )
        driver.find_element(By.XPATH, '//label[@for="ORDER_AGREEMENT_MARKET_ACCEPT_FORM_CONDITIONS0"]').click()

        print("Click Next button")
        click_button_robustly(driver, '//button[@class="PrincipalButton" and text()="Next"]', "Next button")

        print("Select cash account")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.NAME, 'cashAccountId')
            )
        )
        select = Select(driver.find_element(By.NAME, "cashAccountId"))
        select.select_by_index(1)

        print("Click Place order button")
        driver.find_element(By.XPATH, '//button[text()="Place order"]').click()
    except:
        # Need to add more specific exception catches
        screenshot_path = tempfile.mktemp(prefix="transfer_", suffix=".png")
        driver.save_screenshot(screenshot_path)
        print(f"You can find a screenshot of the issue at {screenshot_path}")
        print("Error?")
        print(sys.exc_info()[0])

    driver.quit()

if __name__ == "__main__":
    try:
        sell_shares()
    except:
        driver.quit()

