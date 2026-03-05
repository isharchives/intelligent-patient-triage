import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.getenv("TWILIO_PHONE")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(phone, message):

    try:
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE,
            to=phone
        )
        print(f"SMS sent to {phone}")
        return True
    except Exception as e:
        print("SMS Error:", e)
        return False