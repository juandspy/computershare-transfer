import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException
import time

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

    try:
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.ID, "portfolioandsharepriceandplans")
            )
        )
    except:
        print(f"Couldn't find the homepage. Trying to ignore security enhancements proposals")
        # Ignore any security enhancements proposals
        get_started_btn = driver.find_element(By.ID, "getStarted")
        if get_started_btn:
            ignore_security_configuration(wait, driver)

    wait.until(
        expected_conditions.presence_of_element_located(
            (By.ID, "portfolioandsharepriceandplans")
        )
    )

def click_button_robustly(driver, button_xpath, description="button"):
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


def ignore_security_configuration(wait, driver):
    click_button_robustly(driver, '//button[@id="getStarted" and contains(text(), "Get started")]', "Get started button")

    print("Looking for the accept weaker security button")
    wait.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, '//a[@class="L3" and contains(text(), "I accept weaker security")]')
        )
    )
    print("Button found")
    accept_weaker_security = driver.find_element(By.XPATH, '//a[@class="L3" and contains(text(), "I accept weaker security")]')
    accept_weaker_security.click()
    print("Button clicked")

    click_button_robustly(driver, '//button[@class="PrincipalButton" and @id="Done"]', "Done button")

if __name__ == "__main__":
    driver = initialize_driver()
    wait = initialize_wait(driver)
    sign_in(wait, driver)
