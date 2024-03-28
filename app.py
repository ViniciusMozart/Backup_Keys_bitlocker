from flask import Flask, request, redirect, render_template,url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
import requests
import webbrowser
import db
import graph
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Substitua pelos valores adequados

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = 'http://localhost:5000/callback'
scope = 'https://graph.microsoft.com/.default'
app.secret_key = client_secret  # Necessário para manter sessões seguras
tenant_id = os.getenv("TENNANT_ID")
# tenant_id = db.get_tenant_id()
print(f'Esse é o tennantid   {tenant_id}')




# URL de autenticação da Microsoft
auth_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&response_mode=query&scope={scope}&state=12345"

# Endpoint de token da Microsoft
token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
# @login_required
def home():
    tenant_id = db.get_tenant_id()
    
    if request.method == 'POST':
        new_tenant_id = request.form['tenant_id']
        if new_tenant_id:
            conn = db.get_db_connection()
            conn.execute('INSERT INTO settings (tenant_id) VALUES (?)', (new_tenant_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('autorize'))
        else:
            flash('Please provide a tenant ID.')
    
    if tenant_id:
        return redirect(url_for('autorize'))
    else:
        return redirect(url_for('config'))



@app.route('/config')
# @login_required
def config():
    # print(current_user)
    return render_template('config-tennant.html')
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Agora usamos a função `validar_credenciais` para verificar o usuário e a senha
        if db.validar_credenciais(username, password):
            # Se as credenciais são válidas, armazenamos o username na sessão
            session['username'] = username
            return redirect(url_for('home'))
        else:
            # Se a validação falhar, retornamos uma mensagem de erro
            return 'Login falhou'
    
    # Se o método for GET, simplesmente renderizamos o formulário de login
    return render_template('login.html')


@app.route('/logout')
def logout():
    # session.pop('username', None)
    # session.clear()  # Limpa a sessão
    #logout_user()
    return redirect(url_for('login'))    

@app.route('/autorize', methods=['GET', 'POST'])
def autorize():


    return redirect(auth_url)
   

@app.route('/relatorio')
def relatorio():
    # Sua lógica para mostrar o relatório
    return render_template('relatorios.html')


@app.route('/callback')
def callback():
    
    # Captura o código de autorização retornado
    code = request.args.get('code')
    if not code:
        return 'Código de autorização não encontrado na resposta.', 400
    # Retornar a página HTML que inicia o processo
    return render_template('processando.html', code=code)
    
    
    
@app.route('/processar')
def processar():
    code = request.args.get('code')
    if not code:
        return jsonify({'success': False, 'message': 'Código não fornecido'}), 400
    # Troca o código por um token de acesso
    token_data = {
        'client_id': client_id,
        'scope': scope,
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_r = requests.post(token_url, data=token_data, headers=headers)
    token_r.raise_for_status()  # Levanta um erro para respostas HTTP falhas
    token_response = token_r.json()
    

    access_token = token_response.get('access_token')
    print(f'Esse é o token:{access_token}')
    if not access_token:
        return 'Token de acesso não foi encontrado na resposta.', 400
    
    # Aqui você faria algo com o access_token, como armazená-lo de forma segura
    try:
        
        recovery_keys_url = 'https://graph.microsoft.com/v1.0/informationProtection/bitlocker/recoveryKeys'
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(recovery_keys_url, headers=headers)
        response.raise_for_status()
        
        keys = response.json().get('value', [])
        print(f"Successfully retrieved {len(keys)} keys.")
        # Salva os dados no SQLite
        
    except Exception as e:
        print(f"Error retrieving recovery keys: {e}")
    
    db.save_keys(keys, access_token)
    return jsonify({'success': True})
   
   

    

if __name__ == '__main__':
    app.run(debug=True)
