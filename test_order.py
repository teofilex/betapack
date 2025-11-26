import requests
import json

# Test order data
order_data = {
    "customer_name": "Marko Petrović",
    "customer_phone": "0612345678",
    "customer_email": "marko.petrovic@example.com",
    "delivery_address": "Bulevar Kralja Aleksandra 123, Beograd",
    "notes": "Molim hitnu dostavu do 15h",
    "items": [
        {
            "product_id": 1,
            "quantity": 2
        },
        {
            "product_id": 2,
            "variant_id": None,
            "quantity": 1
        }
    ]
}

# API endpoint
url = "http://localhost:8000/api/orders/"

# Send POST request
try:
    response = requests.post(url, json=order_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 201:
        print("\n✅ Order successfully created!")
        order = response.json()
        print(f"Order ID: {order.get('id')}")
        print(f"Total Amount: {order.get('total_amount')} RSD")
    else:
        print(f"\n❌ Error: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Error: Cannot connect to server. Make sure Django server is running on http://localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")



