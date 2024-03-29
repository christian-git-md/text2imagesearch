import requests

url = "http://0.0.0.0:9091/"
data = {"text": "A woman in a pink dress dancing in the rain"}
response = requests.post(url, data=data)
print(response.text)
