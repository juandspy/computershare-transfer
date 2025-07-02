from common import initialize_driver, initialize_wait, sign_in, expected_conditions, By
from pprint import pprint


def get_shares(wait, driver):
    print("Getting available shares")
    shares = {}

    wait.until(
        expected_conditions.presence_of_element_located(
            (By.CLASS_NAME, "PlanSummaryTotal")
        )
    )

    # Wait for the N5 elements to be present (shares amounts)
    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "N5")))

    # Find all plan summary items
    plan_items = driver.find_elements(By.CLASS_NAME, "PlanSummaryTotal")
    plan_items.extend(driver.find_elements(By.CLASS_NAME, "PlanSummaryAvailable"))

    print(f"Found {len(plan_items)} plan summary items")

    for item in plan_items:
        try:
            # Get the title (Total, Available, etc.)
            title_element = item.find_element(By.TAG_NAME, "h4")
            title = title_element.text.strip()

            # Get the subtitle if it exists (for Available items)
            subtitle_element = item.find_elements(By.CLASS_NAME, "SubTitle")
            if subtitle_element:
                subtitle = subtitle_element[0].text.strip()
                title = f"{title} - {subtitle.replace(':', '').strip()}"

            # Get the shares amount - look for N5 class within this specific item
            shares_element = item.find_element(By.CLASS_NAME, "N5")
            shares_text = shares_element.text.strip()

            # Skip if shares text is empty
            if not shares_text:
                print(f"Skipping item '{title}' - no shares amount found")
                continue

            # Convert the shares text to float (remove any extra spaces and replace comma with dot)
            shares_amount = float(shares_text.replace(",", ".").strip())

            print(f"Found {title}: {shares_amount} shares")
            shares[title] = shares_amount

        except Exception as e:
            print(f"Skipping item due to error: {e}")

    return shares


if __name__ == "__main__":
    driver = initialize_driver()
    wait = initialize_wait(driver)
    sign_in(wait, driver)
    shares = get_shares(wait, driver)
    pprint(shares)
