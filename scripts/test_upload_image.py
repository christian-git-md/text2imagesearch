import requests

url = "http://0.0.0.0:9091/add-image"
data = {"image_url": "https://i.pinimg.com/474x/34/18/a6/3418a655e5f5784cd2539a6d9a8dbc3a.jpg"}
response = requests.post(url, data=data)
print(response.text)
