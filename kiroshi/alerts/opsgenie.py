from kiroshi.settings import settings

import requests

def opsgenie(message):
    request = requests.post(settings.opsgenie_url, headers={'Authorization': f'GenieKey {settings.opsgenie_api_key}'}, data=message)
    request.raise_for_status()
    return None