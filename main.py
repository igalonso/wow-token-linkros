import os
from dotenv import load_dotenv
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64


load_dotenv()

zone = "eu"
realm = "cthun"
character_name = "test"
sender ="test@test.com"
to_email ="test2@test.com"

def authenticate_to_blizzard():
    client_id = os.getenv('BLIZZARD_CLIENT_ID')
    client_secret = os.getenv('BLIZZARD_CLIENT_SECRET')
    data = {
        'grant_type': 'client_credentials'
    }
    response = requests.post(
        f'https://{zone}.battle.net/oauth/token',
        data=data,
        auth=(client_id, client_secret)
    )
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None
    
def get_character_profile(access_token, character_name):
    print(f'https://{zone}.api.blizzard.com/profile/wow/character/{realm}/{character_name}/appearance?namespace=profile-{zone}&locale=en_US')
    response = requests.get(
        f'https://{zone}.api.blizzard.com/profile/wow/character/{realm}/{character_name}/appearance?namespace=profile-{zone}&locale=en_US',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    print(response.status_code)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_wow_token_price(access_token):
    response = requests.get(
        f'https://{zone}.api.blizzard.com/data/wow/token/index?namespace=dynamic-{zone}&locale=en_US',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    if response.status_code == 200:
        return response.json()['price']/10000
    else:
        return None
    
def send_email(email_info):
    msg = MIMEMultipart()
    msg['From'] = email_info['from']
    msg['To'] = email_info['to']
    msg['Subject'] = 'WoW Token Price Alert'
    body = 'The price of the WoW token has exceeded your threshold.'
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(email_info['from'], email_info['password'])
    text = msg.as_string()
    server.sendmail(email_info['from'], email_info['to'], text)
    server.quit()
def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(message_text, 'plain'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    return {
        'raw': raw_message
    }

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)

def send_email_with_gmail_api(email_info):
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('gmail', 'v1', credentials=creds)

    sender = email_info['from']
    to = email_info['to']
    subject = 'WoW Token Price Alert'
    message_text = 'The price of the WoW token has exceeded your threshold.'
    message = create_message(sender, to, subject, message_text)

    send_message(service, 'me', message)


email_info = {
    'from': sender,
    'to': to_email
}
access_token = authenticate_to_blizzard()
subject = "compra token"
message_text = "tu token mola"


def check_and_send_email_if_price_above_threshold(access_token, threshold=400000):
    price = get_wow_token_price(access_token)
    if price is not None and price > threshold:

       send_email_with_gmail_api(email_info)

check_and_send_email_if_price_above_threshold(access_token )

# write a functions that sends an email when the wow token price is over a certain threshold

#print(authenticate_to_blizzard())

#print(get_character_profile(authenticate_to_blizzard(), character_name)) # Korvax is a character on the realm C'Thun

print(get_wow_token_price(authenticate_to_blizzard()))