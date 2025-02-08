from common import initialize_driver, initialize_wait, sign_in, expected_conditions, By
from pprint import pprint


def get_shares(wait, driver):
    print("Getting available shares")
    shares = {}

    wait.until(
        expected_conditions.presence_of_all_elements_located(
            (
                By.XPATH,
                "//tbody/tr[contains(@class, 'altRwTre') or contains(@class, 'altRwFlse')]",
            )
        )
    )

    rows = driver.find_elements(
        By.XPATH,
        "//tbody/tr[contains(@class, 'altRwTre') or contains(@class, 'altRwFlse')]",
    )
    print(f"Table is rendered. Found {len(rows)} rows")

    for row in rows:
        try:
            name = row.find_element(By.XPATH, "./td[1]").text.strip()

            balance_element = row.find_elements(
                By.XPATH, "./td[5]"
            )  # `find_elements` avoids NoSuchElementException
            balance = balance_element[0].text.strip() if balance_element else "0.0"

            shares[name] = float(balance) if balance else 0.0

        except Exception as e:
            print(f"Skipping row due to error: {e}")
    return shares


if __name__ == "__main__":
    driver = initialize_driver()
    wait = initialize_wait(driver)
    sign_in(wait, driver)
    shares = get_shares(wait, driver)
    pprint(shares)
