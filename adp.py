import os
import shutil
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from sqlitedict import SqliteDict
from telegram import send_telegram_message
import time
from datetime import datetime


# Load env variables from ".env" file in the same folder
load_dotenv(override=True)

# ADP credentials
ADP_USERNAME = os.getenv("ADP_USERNAME")
ADP_PASSWORD = os.getenv("ADP_PASSWORD")

# Database file
DATABASE_FILE = "payslips.db"
PATH_TO_PAYSLIPS = "/Users/jdiazsua/Documents/Projects/PoCs/payslip-reader/payslips/"
PATH_TO_DOWNLOADS = "/Users/jdiazsua/Downloads/"


def initialize_driver():
    """Initialize Chrome driver for ADP website"""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    # Automatically get and cache the webdriver for Chrome
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    driver.get("https://www.adpnet.esp.adp.com/wapps2/vdlmdocs")
    return driver


def initialize_wait(driver):
    """Initialize WebDriverWait with 10 second timeout"""
    return WebDriverWait(driver, 10)


def sign_in(wait, driver):
    """Sign in to ADP website using credentials from environment variables"""
    print("Accessing ADP website...")
    
    # Wait for the page to load
    wait.until(
        expected_conditions.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    print("Page loaded successfully")
    print(f"Page title: {driver.title}")

    # Wait for the login form to be present
    wait.until(expected_conditions.presence_of_element_located((By.ID, "login-form_username")))

    # Access the shadow DOM for the username field
    login_form = driver.find_element(By.ID, "login-form_username")
    shadow = driver.execute_script('return arguments[0].shadowRoot', login_form)
    username_input = shadow.find_element(By.NAME, "sdf-input")
    username_input.clear()
    username_input.send_keys(ADP_USERNAME)

    # Click the "Next" button after entering the username
    next_btn = driver.find_element(By.ID, "verifUseridBtn")
    driver.execute_script('arguments[0].click();', next_btn)


    # Access the shadow DOM for the password field
    wait.until(expected_conditions.presence_of_element_located((By.ID, "login-form_password")))
    password_form = driver.find_element(By.ID, "login-form_password")
    shadow_pwd = driver.execute_script('return arguments[0].shadowRoot', password_form)
    password_input = shadow_pwd.find_element(By.NAME, "sdf-input")
    password_input.clear()
    password_input.send_keys(ADP_PASSWORD)

    # Click the "Sign in" button after entering the password
    sign_btn = driver.find_element(By.ID, "signBtn")
    driver.execute_script('arguments[0].click();', sign_btn)

    print("Login submitted")

    # Wait until the next page is rendered after sign in
    wait.until(lambda d: d.title == "MultiDocs")


def read_previous_payslip_date():
    """Read the previous payslip date from the SQLite dictionary."""
    with SqliteDict(DATABASE_FILE) as db:
        return db.get("last_payslip_date", "")


def write_current_payslip_date(payslip_date):
    """Write the current payslip date to the SQLite dictionary."""
    with SqliteDict(DATABASE_FILE, autocommit=True) as db:
        db["last_payslip_date"] = payslip_date


def count_items_in_db():
    """Count items in the database."""
    with SqliteDict(DATABASE_FILE) as db:
        return sum(1 for _ in db.items())

def navigate_to_payment_tile(wait, driver):
    """Navigate to the payment tile and return the tile content element."""
    # Wait for the Employee tile to be present
    wait.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, "//h1[contains(@class, 'tile-title') and text()='Employee']")
        )
    )
    employee_tile = driver.find_element(
        By.XPATH, "//h1[contains(@class, 'tile-title') and text()='Employee']"
    )
    employee_tile.click()

    wait.until(
        expected_conditions.presence_of_element_located(
            (By.XPATH, "//h1[contains(@class, 'tile-title-woimage') and text()='My last payment']")
        )
    )

    # Find the last payslip date in the tile
    tile_content = wait.until(
        expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "tile-content")
        )
    )
    return tile_content


def get_current_payslip_date(tile_content):
    """Extract the current payslip date from the tile content."""
    last_date_elem = tile_content.find_element(By.TAG_NAME, "h4")
    current_date = last_date_elem.text.strip()
    print(f"Current payslip date: {current_date}")
    return current_date


def handle_database_initialization(current_date):
    """Handle database initialization for first-time runs."""
    if count_items_in_db() == 0:
        print("Database not initialized yet (first time running)")
        write_current_payslip_date(current_date)
        return True
    return False


def send_payslip_notification(current_date):
    """Send telegram notification for new payslip."""
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id:
        message = f"New payslip available for {current_date}"
        send_telegram_message(chat_id, message)
        print("Telegram notification sent")
    else:
        print("TELEGRAM_CHAT_ID not set, skipping notification")


def get_latest_file(path):
    """Get the most recently modified file in the given path."""
    files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def download_and_move_payslip(tile_content, current_date):
    """Download the payslip and move it to the correct location."""
    # Find and click the download button for the payslip
    download_btn = tile_content.find_element(By.CSS_SELECTOR, "a.btn.btn-aceptar[onclick*=\"lastPay('down')\"]")
    download_btn.click()

    # Wait for the download to complete (assumes default download dir and browser config)
    dt = datetime.strptime(current_date, "%B %Y")
    filename = dt.strftime("%Y_%m.pdf")
    print(f"Payslip will be saved as {PATH_TO_PAYSLIPS}{filename}")

    latest_file = get_latest_file(PATH_TO_DOWNLOADS)
    print(f"Latest file in {PATH_TO_DOWNLOADS}: {latest_file}")

    if latest_file:
        dest_path = os.path.join(PATH_TO_PAYSLIPS, filename)
        print(f"Moving {latest_file} to {dest_path}")
        shutil.move(latest_file, dest_path)
    else:
        print("No file to move")


def get_last_payslip(wait, driver):
    """Main function to check for new payslips and handle the process."""
    # Read previous payslip date from database
    previous_date = read_previous_payslip_date()
    print(f"Previous payslip date: {previous_date}")
    
    # Navigate to payment tile and get content
    tile_content = navigate_to_payment_tile(wait, driver)
    
    # Get current payslip date
    current_date = get_current_payslip_date(tile_content)

    # Handle database initialization for first-time runs
    if handle_database_initialization(current_date):
        return

    # Check if we have a new payslip
    if current_date != previous_date and current_date:
        print(f"New payslip detected! Previous: {previous_date}, Current: {current_date}")
        
        # Send notification and download payslip
        send_payslip_notification(current_date)
        download_and_move_payslip(tile_content, current_date)
    else:
        print("No new payslip found")

    # Update the database with the current date
    write_current_payslip_date(current_date)

def get_driver():
    """Get a configured driver instance for interactive use"""
    if not ADP_USERNAME or not ADP_PASSWORD:
        print("Error: ADP_USERNAME and ADP_PASSWORD environment variables must be set")
        return None
    
    driver = initialize_driver()
    wait = initialize_wait(driver)
    # sign_in(wait, driver)
    return driver, wait


if __name__ == "__main__":
    if not ADP_USERNAME or not ADP_PASSWORD:
        print("Error: ADP_USERNAME and ADP_PASSWORD environment variables must be set")
        exit(1)
    
    driver = initialize_driver()
    wait = initialize_wait(driver)
    sign_in(wait, driver)
    get_last_payslip(wait, driver)
    
    # Keep the browser open for a moment to see the result
    time.sleep(5)
    driver.quit()
