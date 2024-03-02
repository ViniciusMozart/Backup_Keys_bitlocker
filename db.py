import sqlite3
import graph


def get_db_connection():
    DATABASE = 'data.db'
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_tenant_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        tenant_id TEXT
    );               
    ''')
    result = conn.execute('SELECT tenant_id FROM settings LIMIT 1').fetchone()
    conn.close()
    if result:  # Verifica se o resultado não é None
        return result[0]  # Retorna o primeiro elemento da tupla, que é o tenant_id
    return None
# def get_tenant_id():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS settings (
#     tenant_id TEXT
#     );               
#     ''')
#     tenant_id = conn.execute('SELECT tenant_id FROM settings LIMIT 1').fetchone()
#     conn.close()
#     return tenant_id

def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_devices_bt (
        auto_id INTEGER PRIMARY KEY AUTOINCREMENT,
        id TEXT,
        deviceName TEXT,
        createdDateTime TEXT,
        deviceId TEXT,
        volumeType TEXT
    );
    ''')
    conn.commit()
    conn.close()


def save_keys(keys, access_token):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_devices_bt (
        auto_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        id TEXT NOT NULL,
        createdDateTime TEXT,
        deviceId TEXT,
        deviceName TEXT,  -- Nova coluna para o nome do dispositivo
        volumeType TEXT,
        recoveryKey TEXT   -- Nova coluna para a chave de recuperação
    );
    ''')

    for key in keys:
            recovery_key_id = key['id']
            device_id = key['deviceId']
            
            # Buscar a chave de recuperação e o nome do dispositivo
            recovery_key = graph.get_recovery_key(recovery_key_id, access_token)
            device_name = graph.get_device_name(device_id, access_token)
            print(device_name)

            # Inserir ou atualizar os dados na tabela tb_devices_bt
            cursor.execute('''
            INSERT INTO tb_devices_bt (id, createdDateTime, deviceId, deviceName, volumeType, recoveryKey)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(auto_id) DO UPDATE SET
                createdDateTime = excluded.createdDateTime,
                deviceId = excluded.deviceId,
                deviceName = excluded.deviceName,
                volumeType = excluded.volumeType,
                recoveryKey = excluded.recoveryKey;
            ''', (recovery_key_id, key['createdDateTime'], device_id, device_name, key['volumeType'], recovery_key))

    conn.commit()
    conn.close()
