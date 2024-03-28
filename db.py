import sqlite3
import graph
import pandas as pd

from werkzeug.security import generate_password_hash, check_password_hash


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



def init_db():
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
        recoveryKey VARCHAR(255)
    );
    ''')
    conn.commit()
    conn.close()

def save_keys(keys, access_token):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    # Garante que a tabela existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_devices_bt (
        auto_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        id TEXT,  -- Removido o NOT NULL e UNIQUE aqui
        createdDateTime TEXT,
        deviceId TEXT NOT NULL,  -- Assumindo que deviceId pode servir como identificador único temporário
        deviceName TEXT,
        volumeType TEXT,
        recoveryKey VARCHAR(255)
    );
    ''')

    for key in keys:
        recovery_key_id = key.get('id')  # Pode ser None
        device_id = key['deviceId']
        recovery_key = graph.get_recovery_key(recovery_key_id, access_token) if recovery_key_id else None
        device_name = graph.get_device_name(device_id, access_token)

        # Verifica se existe um registro para o deviceId
        cursor.execute('SELECT id FROM tb_devices_bt WHERE deviceId = ?', (device_id,))
        row = cursor.fetchone()

        if row:
            # Registro existe, atualiza (se 'id' está presente, atualiza-o também)
            cursor.execute('''
            UPDATE tb_devices_bt
            SET id = COALESCE(?, id),  -- Atualiza 'id' apenas se for não NULL
                createdDateTime = ?,
                deviceName = ?,
                volumeType = ?,
                recoveryKey = COALESCE(?, recoveryKey)  -- Atualiza 'recoveryKey' apenas se for não NULL
            WHERE deviceId = ?;
            ''', (recovery_key_id, key['createdDateTime'], device_name, key['volumeType'], recovery_key, device_id))
        else:
            # Registro não existe, insere novo
            cursor.execute('''
            INSERT INTO tb_devices_bt (id, createdDateTime, deviceId, deviceName, volumeType, recoveryKey)
            VALUES (?, ?, ?, ?, ?, ?);
            ''', (recovery_key_id, key['createdDateTime'], device_id, device_name, key['volumeType'], recovery_key))

    conn.commit()
    conn.close()



# def save_keys(keys, access_token):
#     conn = sqlite3.connect('data.db')
#     cursor = conn.cursor()
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS tb_devices_bt (
#         auto_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
#         id TEXT NOT NULL,
#         createdDateTime TEXT,
#         deviceId TEXT,
#         deviceName TEXT,  -- Nova coluna para o nome do dispositivo
#         volumeType TEXT,
#         recoveryKey VARCHAR(255)
#     );
#     ''')

#     for key in keys:
#             recovery_key_id = key['id']
#             device_id = key['deviceId']
            
#             # Buscar a chave de recuperação e o nome do dispositivo
#             recovery_key = graph.get_recovery_key(recovery_key_id, access_token)
#             device_name = graph.get_device_name(device_id, access_token)
#             print(device_name)

#             # Inserir ou atualizar os dados na tabela tb_devices_bt
#             cursor.execute('''
#             INSERT INTO tb_devices_bt (id, createdDateTime, deviceId, deviceName, volumeType, recoveryKey)
#             VALUES (?, ?, ?, ?, ?, ?)
#             ON CONFLICT(auto_id) DO UPDATE SET
#                 createdDateTime = excluded.createdDateTime,
#                 deviceId = excluded.deviceId,
#                 deviceName = excluded.deviceName,
#                 volumeType = excluded.volumeType,
#                 recoveryKey = excluded.recoveryKey;
#             ''', (recovery_key_id, key['createdDateTime'], device_id, device_name, key['volumeType'], recovery_key))

#     conn.commit()
#     conn.close()
    
    
    def pegar_usuarios():
        # Conectar ao banco de dados SQLite
        conn = sqlite3.connect('data.db')

        # Execute a consulta SQL para recuperar os dados desejados
        query = "SELECT * FROM tb_users"
        
        users = pd.read_sql_query(query, conn)

    
        # Fechar a conexão com o banco de dados
        conn.close()
        return users

def create_table_tb_users():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Crie a tabela se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_users (
            upn TEXT PRIMARY KEY,
            displayName TEXT,
            password TEXT,
            token TEXT,
            tennant_id TEXT
        )
    ''')

    conn.commit()
    conn.close()


    
def insert_user(upn, displayName, hashed_password):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    # Certifique-se de que a tabela existe
    create_table_tb_users()
    try:
        cursor.execute('INSERT INTO tb_users (upn, displayName, password) VALUES (?, ?, ?)', (upn, displayName, hashed_password))
        conn.commit()
    finally:
        conn.close()
 
def fetch_all_users():
    
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Ajuste a consulta conforme necessário para obter os dados dos usuários do seu banco de dados
    query = "SELECT * FROM tb_users"
    cursor.execute(query)

    users = [{"upn": row[0], "displayName": row[1], "password": row[2]} for row in cursor.fetchall()]

    conn.close()
    return users





import sqlite3
from werkzeug.security import check_password_hash
import pandas as pd

def validar_credenciais(usuario, senha_fornecida):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row  # Facilita o acesso às colunas por nome

    # Execute a consulta SQL para recuperar o hash da senha para o usuário
    query = "SELECT password FROM tb_users WHERE upn = ?"
    
    try:
        cur = conn.cursor()
        cur.execute(query, (usuario,))
        user_row = cur.fetchone()
        
        if user_row:
            senha_hash = user_row['password']
            # Verificar se a senha fornecida corresponde ao hash armazenado
            echo = check_password_hash(senha_hash, senha_fornecida)
            print(echo)
            if check_password_hash(senha_hash, senha_fornecida):
                return True  # As credenciais são válidas
    except Exception as e:
        print(f"Erro ao validar credenciais: {e}")
    finally:
        # Fechar a conexão com o banco de dados
        conn.close()
    
    return False  # As credenciais são inválidas



@staticmethod
def get(user_id):
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tb_users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        user = (user['id'], user['username'])
        return user
    return None





    
def hash_password(password_series):
    # Assegura que a função itere sobre a série ou lista de senhas
    hashed_passwords = [generate_password_hash(password, method='pbkdf2:sha256', salt_length=8) for password in password_series]
    return hashed_passwords


