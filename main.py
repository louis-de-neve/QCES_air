import requests
AUTH_TOKEN = "f2aec323-a779-4ee1-b63f-d147612982fb"
token_url = f"?token={AUTH_TOKEN}"
source_url = "https://api.airgradient.com/public/api/v1/"

def constructed_url(endpoint):
    return(source_url + endpoint + token_url)

endpoint = "locations/80172/measures/current"
response = requests.get(constructed_url(endpoint))
print(response.json())
