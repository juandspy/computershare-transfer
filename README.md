# computershare-transfer
Transfer or sell all ESPP shares from Computershare to another brokerage or account.

---

### Dependencies:
* selenium
* webdriver-manager
* Chrome for the webdriver
* python-dotenv

---

### Installation/Setup:
* Optional: `uv venv && source .venv/bin/activate`
* Install dependencies using `pip install -r requirements.txt` (or `uv pip sync requirements.txt`)
* Install Chrome

#### Variables:
These are environment variables for a transfer:

* `USERNAME` : Computershare username
* `PASSWORD` : Computershare password
* `COMPANY_NAME` : Company name
* `DTC` : DTC for brokerage
* `ACCOUNT_NUMBER` : Account number for brokerage

`DTC` and `ACCOUNT_NUMBER` are not needed for selling.

You can define using whatever method works best for you (`export` in `.bash_profile`, define in Python console, or just define in the script), or you can create a .env file in the following format:
```
# .env file
USERNAME=username1
PASSWORD=password
COMPANY_NAME=company
DTC=0000
ACCOUNT_NUMBER=X12345678
```
---

### Usage

#### Check for new shares

You can check your shares by running `python get_shares.py`. If you want to
run it periodically and send you a Telegram message, you can configure crontab:

1. Open the terminal and edit the crontab:
```
crontab -e
```
2. Add the cron job to run the script from the folder where your .env file is
   located. For example, if your script is in /path/to/folder, you can add:
```
   0 8 * * * cd /path/to/folder && /usr/bin/python3 notify_new_shares.py >> logfile.log 2>&1
```
3. This would run the script every day at 8AM.

#### Transfer

In a terminal, run `python transfer.py`.
Selenium will open a headless Chrome window (aka you won't see anything) and automate the transfer of all whole shares to your chosen brokerage.

#### Sell

An electronic payment needs to be setup for a sale to avoid fees and charges.

In a terminal, run `python sell.py`.
Selenium will open a headless Chrome window (aka you won't see anything) and automate the sale of all shares to the first electronic payment option.

Multiple electronic payment options have not been tested.

# Warning

This will transfer all whole shares to your chosen brokerage or sell all shares to the first electronic payment option.

Use at your own risk.
