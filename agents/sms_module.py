from twilio.rest import Client

ACCOUNT_SID = ""

AUTH_TOKEN = ""

TWILIO_NUMBER = "+19714620983"


def send_sms(phone, message):

    client = Client(

        ACCOUNT_SID,

        AUTH_TOKEN

    )

    client.messages.create(

        body=message,

        from_=TWILIO_NUMBER,

        to=phone

    )