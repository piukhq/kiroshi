from kiroshi.settings import settings

import requests
import json


def opsgenie(message):
    data = json.dumps({"message": message})
    headers = {"Authorization": f"GenieKey {settings.opsgenie_api_key}", "Content-Type": "application/json"}
    request = requests.post(settings.opsgenie_url, headers=headers, data=data)
    request.raise_for_status()
    print(request.text)
    return None
