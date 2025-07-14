# Transfer ESPP shares from EquatePlus to another brokerage
#
# The brokerage account should be already setup.
# Loading the previously mentioned info from a .env file in the same directory as this file

import sys
import tempfile
import time

from dotenv import load_dotenv
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from common import initialize_driver, initialize_wait, sign_in

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


# Function to transfer shares to another brokerage
def transfer_shares():
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

        print("Click Transfer button")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "TransactionTypeList")
            )
        )
        transfer_button = wait.until(
            expected_conditions.element_to_be_clickable(
                (
                    By.XPATH,
                    '//ul[@class="TransactionTypeList"]//button[@class="TransactionButton" and text()="Transfer"]',
                )
            )
        )
        transfer_button.click()

        # get total number of shares
        print("Get total number of shares")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "ActionableQuantityValue")
            )
        )
        total_shares_element = driver.find_element(
            By.CLASS_NAME, "ActionableQuantityValue"
        )
        total_shares = total_shares_element.text
        print(f"Total shares available: {total_shares}")
        total_shares = total_shares.replace(",", ".")
        print(f"Total shares available (dot instead of comma): {total_shares}")
        total_shares_int = int(float(total_shares))
        print(f"Transferring {total_shares_int} shares (integer part only)")

        # Input the integer number of shares to transfer
        shares_input = driver.find_element(By.ID, "totalQuantity")
        shares_input.clear()
        shares_input.send_keys(str(total_shares_int))

        click_button_robustly(
            '//button[@class="PrincipalButton" and text()="Next"]', "Next button"
        )

        print("Wait for terms and conditions checkbox")
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "ORDER_AGREEMENT_TRANSFER_ACCEPT_FORM_CONDITIONS0")
            )
        )

        print("Click terms and conditions checkbox")
        # Click the label instead of the checkbox since the checkbox has tabindex="-1"
        terms_label = driver.find_element(
            By.XPATH, '//label[@for="ORDER_AGREEMENT_TRANSFER_ACCEPT_FORM_CONDITIONS0"]'
        )
        terms_label.click()

        # Wait a bit for the checkbox to be processed
        time.sleep(2)

        click_button_robustly(
            '//button[@class="PrincipalButton Next" and text()="Next"]', "Next button"
        )

        print("Click Place order button")
        time.sleep(0.5)
        click_button_robustly(
            '//button[@class="PrincipalButton twoFaMessage" and text()="Place order"]',
            "Place order button",
        )

        time.sleep(2)
        screenshot_path = tempfile.mktemp(prefix="transfer_", suffix=".png")
        driver.save_screenshot(screenshot_path)
        print(f"You can find a screenshot of your transaction at {screenshot_path}")

    except:
        # Need to add more specific exception catches
        screenshot_path = tempfile.mktemp(prefix="transfer_", suffix=".png")
        driver.save_screenshot(screenshot_path)
        print(f"You can find a screenshot of the issue at {screenshot_path}")
        print("Error?")
        print(sys.exc_info()[0])

    driver.quit()


try:
    transfer_shares()
except:
    driver.quit
