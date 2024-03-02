import PySimpleGUI as sg
import threading
import json
import requests
import pandas as pd
import os
import io
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# Cria um stream para capturar logs
log_stream = io.StringIO()
handler_stream = logging.StreamHandler(log_stream)
handler_stream.setFormatter(formatter)
logger.addHandler(handler_stream)

def log_to_window(window, msg):
    window.write_event_value('-THREAD-', msg + "\n")

def retrieve_recovery_keys(tenant_id, app_id, secret):
    keys = []
    try:
        token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        token_data = {
            'client_id': app_id,
            'scope': 'https://graph.microsoft.com/.default',
            'client_secret': secret,
            'grant_type': 'client_credentials'
        }
        token_r = requests.post(token_url, data=token_data, headers=headers)
        token_r.raise_for_status()  # Raises stored HTTPError, if one occurred.
        
        token = token_r.json().get('access_token')
        recovery_keys_url = 'https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys'
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(recovery_keys_url, headers=headers)
        response.raise_for_status()
        
        keys = response.json().get('value', [])
        logger.info(f"Successfully retrieved {len(keys)} keys.")
    except Exception as e:
        logger.error(f"Error retrieving recovery keys: {e}")
    return keys

def save_to_excel(data, folder_path):
    try:
        df = pd.DataFrame(data)
        filename = os.path.join(folder_path, "recovery_keys.xlsx")
        df.to_excel(filename, index=False)
        logger.info(f"File saved: {filename}")
    except Exception as e:
        logger.error(f"Error saving Excel file: {e}")

def process_data(values, window):
    try:
        tenant_id = values['tennant']
        app_id = values['app']
        secret = values['secret']
        folder_path = values['arquivo_save']
        
        if not all([tenant_id, app_id, secret, folder_path]):
            sg.popup("All fields must be filled!", title="Error")
            return
        
        keys = retrieve_recovery_keys(tenant_id, app_id, secret)
        if keys:
            save_to_excel(keys, folder_path)
            log_to_window(window, "Data processing completed successfully.\n")
        else:
            log_to_window(window, "No data to save. \n")
    except Exception as e:
        log_to_window(window, f"An error occurred: {e}  \n")

def janela():
    sg.theme('SystemDefault')
    main_folder = os.path.join(os.path.expanduser("~"), "Documents")
    
   # Definir o layout da primeira coluna
    coluna1 = [
        [sg.Text("Configuração do Service", font="arial 12")],
        [sg.Text("Tennant id: ", font="arial 12"),
            sg.Input(font="arial 12", key="tennant", size=(30, 20),enable_events = True)],
        [sg.Text("App id:       ", font="arial 12"),
            sg.Input(font="arial 12", key="app", size=(30, 20),enable_events = True)],
        [sg.Text("Secret:       ", font="arial 12"),
            sg.Input(password_char = "*", key="secret",font="arial 12", size=(30, 20),enable_events = True)],
        [sg.Text('Selecione a pasta para Salvar ',size=700,visible=True,key='rel')],
        [sg.InputText(key='arquivo_save',visible=True,readonly=True,enable_events=True), sg.FolderBrowse(initial_folder= main_folder,visible=True,key='browser2')],
        # [sg.Text('Andamento da Leitura')],
        # [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progress')],
        # [sg.Text('Locs lidas: 0/0 (0.00%) - Estimativa de Término: --:--:--', key='info')],
        
    ]

    # Definir o layout da segunda coluna
    coluna2 = [
        [sg.Text("Logs",font="arial 12", key="logs", size=(None, None))],
        [sg.Output(font="arial 8", 
                        key="-OUTPUT-", 
                        size=(55, 30),
                        background_color = "black",
                        text_color="lime")],
        [sg.Button('Cancelar',font="arial 12"), sg.Button('Iniciar',font="arial 12")]
    ]

      # Definir o layout da janela
    layout = [
        [sg.Text("Backup de Chaves Bitlocker ", font="arial 20 bold")],
        [sg.Column(coluna1, justification='center',size=(400,600)), 
            sg.Column(coluna2, justification='center',element_justification='Left', size=(400,600))],
    ]

    window = sg.Window("Backup de Chaves Bitlocker V1.0", layout,icon='./static/img/ico.ico',size=(800,600),button_color='black',sbar_background_color='black',titlebar_icon='./static/img/ico.ico')

    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED or event == 'Cancelar':
            break
        elif event == 'Iniciar':
            threading.Thread(target=process_data, args=(values, window), daemon=True).start()
        elif event == '-THREAD-':
            current_logs = window['-OUTPUT-'].get() + values[event] + '\n'
            window['-OUTPUT-'].update(current_logs)

    window.close()

if __name__ == '__main__':
    janela()
