import os
import requests

from pprint import pprint


TIMEOUT = 5


def get_updates():
    """
    Use this function in order to gather the chat ID for your bot consumers.
    
    You can easily call it with
        python -c "import telegram; telegram.get_updates()"
    """
    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    pprint(requests.get(url, timeout=TIMEOUT).json())


def send_telegram_message(chat_id, message):
    """
    Send a message to a given chat ID.
    
    You can easily call it with
        python -c "import telegram; telegram.send_telegram_message('$CHAT', '$MSG')"
    """
    token = os.getenv("TELEGRAM_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    print(f"Sending message '{message}' to chat '{chat_id}'")
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, json=payload, timeout=TIMEOUT)
    print(f"Status code: {response.status_code}")
    print(f"Body: {response.text}")
