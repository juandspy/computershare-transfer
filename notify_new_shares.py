import os

from sqlitedict import SqliteDict
from common import initialize_driver, initialize_wait, sign_in
from get_shares import get_shares
from telegram import send_telegram_message
from pprint import pprint

# Database file
DATABASE_FILE = 'shares.db'

def read_previous_values():
    """Read the previous values from the SQLite dictionary."""
    out = {}
    with SqliteDict(DATABASE_FILE) as db:
        for key, item in db.items():
            out[key] = item
    return out

def write_current_values(shares):
    """Write the current values to the SQLite dictionary."""
    with SqliteDict(DATABASE_FILE, autocommit=True) as db:
        for key, value in shares.items():
            db[key] = value

def main():
    previous_values = read_previous_values()
    print("Stored shares:")
    pprint(previous_values)
    print("-"*5)

    driver = initialize_driver()
    wait = initialize_wait(driver)
    sign_in(wait, driver)

    shares = get_shares(wait, driver)
    print("Updated shares:")
    pprint(shares)
    print("-"*20)

    if count_items_in_db(previous_values) == 0:
        # The database is not initialized yet (first time running this script)
        write_current_values(shares)
        return

    # Iterate through the shares and check for increases
    for share_name, current_value in shares.items():
        previous_value = previous_values.get(share_name, 0)

        # Compare current shares with the previous value
        if current_value > previous_value:
            message = f"You have new shares for the {share_name} account"
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            send_telegram_message(chat_id, message)

    # Update the database with the current values. We do it in the end of the
    # script to make sure in case of an error sending the message, we will be
    # notified in the next run
    write_current_values(shares)

def count_items_in_db(db):
    return sum(1 for _ in db.items())

if __name__ == "__main__":
    main()
