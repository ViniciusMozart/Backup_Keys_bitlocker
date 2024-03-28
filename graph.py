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

import requests

def get_current_user_info(access_token):
    # Endpoint para buscar informações do usuário autenticado
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Levanta uma exceção para respostas de erro
    data = response.json()
    user_info = {
        "displayName": data.get("displayName"),
        "userPrincipalName": data.get("userPrincipalName"),
        "id": data.get("id"),
        "jobTitle": data.get("jobTitle"),
    }
    # Buscar a foto do usuário autenticado
    photo_url = "https://graph.microsoft.com/v1.0/me/photo/$value"
    photo_response = requests.get(photo_url, headers=headers, stream=True)
    if photo_response.status_code == 200:
        user_info["photo"] = photo_response.content  # A foto é retornada como dados binários
    else:
        user_info["photo"] = None  # Caso não encontre a foto, retorna None
    return user_info





