from twilio.rest import Client
import os

from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN =os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE")


def send_sms(phone, message):

    client = Client(

        ACCOUNT_SID,

        AUTH_TOKEN

    )

    try:

        client.messages.create(

            body=message,

            from_=TWILIO_NUMBER,

            to=phone

        )

        print("✅ SMS Sent")

    except Exception as e:

        print("⚠ SMS Failed")

        print(e)