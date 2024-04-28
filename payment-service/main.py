import requests
import webbrowser

# Step 1: Generate OAuth Token
oauth_url = 'https://secure.snd.payu.com/pl/standard/user/oauth/authorize'
oauth_data = {
    'grant_type': 'client_credentials',
    'client_id': '478129',
    'client_secret': 'abd35aed5fd4fee1f1045b2523ad31a4'
}
oauth_response = requests.post(oauth_url, data=oauth_data)

if oauth_response.status_code == 200:
    oauth_token = oauth_response.json().get('access_token')
    print(f"OAuth token generated successfully: {oauth_token}")
else:
    print(f"Error generating OAuth token: {oauth_response.status_code}")
    print(oauth_response.text)
    exit()

# Step 2: Create a New Order
order_url = 'https://secure.snd.payu.com/api/v2_1/orders'
order_data = {
    "customerIp": "127.0.0.1",
    "merchantPosId": "478129",
    "description": "CloneGG",
    "currencyCode": "PLN",
    "totalAmount": "1",
    "products": [
       {
          "name": "Konto premium",
          "unitPrice": "1",
          "quantity": "1"
        }
    ]
}

authorization = 'Bearer ' + oauth_token
order_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'{authorization}'
}
order_response = requests.post(order_url, json=order_data, headers=order_headers)

if order_response.status_code == 200:
    print("Order created successfully")
    if order_response.url:
        print("Redirecting user to PayU payment page...")
        webbrowser.open(order_response.url)
    else:
        print("No redirect URI found in the response.")
else:
    print(f"Error creating order: {order_response.status_code}")
    print(order_response.text)