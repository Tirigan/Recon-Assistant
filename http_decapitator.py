import requests

url = input("Enter URL: ")

try:
    response = requests.get(url, timeout=5)

    print(f"\nStatus Code: {response.status_code}")
    print("\nHeaders:")

    for key, value in response.headers.items():
        print(f"{key}: {value}")

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
