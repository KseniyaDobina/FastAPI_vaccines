import requests

BASE_URL = ""
headers = {
    "x-api-key": "free_user_3DMEU4a0PJ3NdJcxavundLhRMnP",
}
response = requests.get(
            f"https://reqres.in/api/users", headers=headers)
print(response)
print(1)
