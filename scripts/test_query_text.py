import requests

url = "http://0.0.0.0:9091/"
data = {"text": "A black cat"}
response = requests.post(url, data=data)
print(response.text)
