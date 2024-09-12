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

payload3 = {
    "data": {
        "id": "E11C4FA3348B600C",
        "order_items": [
            {
                "id": "1",
                "plu_id": "chick-bk",
                "sku": "100, 130",
                "item_name": "Chicken Bowl Korean",
                "item_price_numeric": 43000,
                "eater_notes": "Telur matang",
                "quantity": 2
            },
            {
                "id": "2",
                "plu_id": "prk-bk",
                "sku": "200, 220",
                "item_name": "Pork Belly Bowl",
                "item_price_numeric": 60000.0,
                "eater_notes": "",
                "quantity": 1
            }
        ]
    },
    "time": "2023-07-21T05:01:32.327Z",
    "type": "order",
    "event": "in_progress"
}

# Send the HTTP POST request
try:
    response = requests.post(url, json=payload3)
    print("Webhook sent. Server responded with:", response.text)



except requests.exceptions.RequestException as e:
    print("Error sending webhook:", e)