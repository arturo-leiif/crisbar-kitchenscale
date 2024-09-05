import requests
import json
import time

# Define the URL of the Raspberry Pi Pico webhook receiver
url = 'http://172.16.11.216:80/'

# 'https://webhook.site/1bbf121e-f2f4-40a1-9e11-3dc4d42eb664'

# Define the JSON payload to send

payload1 = {
    'event': 'new order', 
    'number': '66',
    'items': [
        {
            'name': 'Item A',
            'weight': '30, 35',
            'quantity': 2
        },
        {
            'name': 'Item B',
            'weight': '20, 25',
            'quantity': 1
        },
        {
            'name': 'Item C',
            'weight': '50, 60',
            'quantity': 3
        }
    ]
}
payload2 = {
    'event': 'order->cooking',
    'number': '66'
}

# Send the HTTP POST request
try:
    response = requests.post(url, json=payload1)
    print("Webhook sent. Server responded with:", response.text)
    time.sleep(2)
    response = requests.post(url, json=payload2)
    print("Webhook sent. Server responded with:", response.text)


except requests.exceptions.RequestException as e:
    print("Error sending webhook:", e)