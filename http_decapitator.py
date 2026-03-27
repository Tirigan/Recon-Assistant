import requests

url = input("Enter URL: ")

response = requests.get(url)

for key, value in response.headers.items():
    print(f"{key}: {value}")
