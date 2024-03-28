
import pandas as pd
import db
import sqlite3
 

# Leitura do CSV usando pandas
df = pd.read_csv("users.csv", sep=',')
# Hash das senhas
hashed_passwords = db.hash_password(df['hash_password'])


for (upn, displayName, hash_password) in zip(df['upn'], df['displayName'], hashed_passwords):
    try:
        db.insert_user(upn, displayName, hash_password)
    except sqlite3.IntegrityError:
        print(f"Erro: O email {upn} já está cadastrado no sistema. Se esqueceu a senha, selecione 'Esqueci a senha' na tela de login.")
    except Exception as e:
        print(f"Erro ao inserir usuário {upn}: {e}")