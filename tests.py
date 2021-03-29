import requests
import json
from main import HOST, PORT

BASE = "http://{}:{}/".format(HOST, str(PORT))

response = requests.post(BASE + "couriers", json.dumps({"data": [
        {
            "courier_id": 1,
            "courier_type": "foot",
            "regions": [1, 12, 22],
            "working_hours": ["11:35-14:05", "09:00-11:00"]
        },
        {
            "courier_id": 2,
            "courier_type": "bike",
            "regions": [22],
            "working_hours": ["09:00-18:00"]
        },
        {
            "courier_id": 3,
            "courier_type": "car",
            "regions": [12, 22, 23, 33],
            "working_hours": ["00:00-12:00"]
        }
    ]
}))
print(response.text)


response = requests.get(BASE + "couriers/1")
print(response.text)


response = requests.patch(BASE + "couriers/2", json.dumps({"regions": [11, 33, 2]}))
print(response.text)


response = requests.post(BASE + "orders/", json.dumps({"data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
    ]
}))
print(response.text)
