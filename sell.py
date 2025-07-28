# Sell all ESPP shares from EquatePlus
# Company name, login info, and an electronic payment already setup
# Currently, an EFT avoids all fees and charges

import sys
import tempfile
import time

from common import initialize_driver, initialize_wait, sign_in
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


def click_button_robustly(button_xpath, description="button"):
    """
    Click a button with robust error handling and fallback methods.

    Args:
        button_xpath (str): XPath selector for the button
        description (str): Description of the button for logging
    """
    time.sleep(2)
    print(f"Click {description}")

    # Find the button
    try:
        button = driver.find_element(By.XPATH, button_xpath)
        print(f"Button found: {button}")
    except Exception as e:
        print(f"Button not found with XPath: {button_xpath}")
        print(f"Error: {e}")

        # Try to find the button by text content
        try:
            button = driver.find_element(
                By.XPATH, f"//button[contains(text(), 'Next')]"
            )
            print(f"Found button by text: {button}")
        except:
            print("Could not find button by text either")

        # Try to find any button with the class
        try:
            buttons = driver.find_elements(By.CLASS_NAME, "PrincipalButton")
            print(f"Found {len(buttons)} buttons with PrincipalButton class")
            for i, btn in enumerate(buttons):
                print(f"Button {i}: text='{btn.text}', enabled={btn.is_enabled()}")
                # If this is the Next button, use it
                if btn.text.strip() == "Next":
                    print(f"Using button {i} as Next button")
                    button = btn
                    break
            else:
                print("Could not find Next button among PrincipalButton elements")
                raise Exception("Next button not found")
        except:
            print("Could not find any PrincipalButton elements")
            raise

    # Scroll to the button to ensure it's visible
    driver.execute_script("arguments[0].scrollIntoView(true);", button)
    print("Button scrolled into view")
    time.sleep(1)

    # Try regular click first, if it fails, use JavaScript click
    print("Clicking button")
    button.click()
    print("Button clicked")


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
        click_button_robustly('//ul[@class="TransactionTypeList"]//button[@class="TransactionButton" and text()="Sell"]', "Sell button")

        print("Click Total Quantity button")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "totalQuantityButton")
            )
        )
        driver.find_element(By.ID, "totalQuantityButton").click()

        print("Click Next button")
        click_button_robustly('//button[@class="PrincipalButton" and text()="Next"]', "Next button")

        print("Click Accept checkbox")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//label[@for="ORDER_AGREEMENT_MARKET_ACCEPT_FORM_CONDITIONS0"]')
            )
        )
        driver.find_element(By.XPATH, '//label[@for="ORDER_AGREEMENT_MARKET_ACCEPT_FORM_CONDITIONS0"]').click()

        print("Click Next button")
        click_button_robustly('//button[@class="PrincipalButton" and text()="Next"]', "Next button")

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


try:
    sell_shares()
except:
    driver.quit
