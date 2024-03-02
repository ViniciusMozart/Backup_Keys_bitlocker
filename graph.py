import requests
def get_recovery_key(recovery_key_id, access_token):
    url = f"https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys/{recovery_key_id}?$select=key"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Isso lançará uma exceção para respostas HTTP não bem-sucedidas
    data = response.json()
    return data.get("key")


def get_device_name(device_id, access_token):
    # url = f"https://graph.microsoft.com/v1.0/devices/{device_id}"
    url = f"https://graph.microsoft.com/v1.0/devices?$filter=deviceId eq '{device_id}'&$count=true"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    if 'value' in data and len(data['value']) > 0:
        # Acessa o primeiro dispositivo na lista
        device_name = data['value'][0].get('displayName')
        return device_name
    else:
        return None




# def get_device_name(device_id, access_token):
#     url = f"https://graph.microsoft.com/v1.0/devices?$filter=deviceId eq '{device_id}'&$count=true"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     print(data)
#     return data.get("displayName")