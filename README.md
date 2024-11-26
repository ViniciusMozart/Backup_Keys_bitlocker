Aplicação Django com Docker e Docker Compose
Este repositório contém uma aplicação Django encapsulada em um container Docker, pronta para ser implantada usando o Docker Compose. A aplicação utiliza um banco de dados MySQL e está configurada para um ambiente de desenvolvimento eficiente.

Sumário
Pré-requisitos
Estrutura do Projeto
Configuração Inicial
Como Executar
Variáveis de Ambiente
Comandos Úteis
Considerações
Licença
Pré-requisitos
Certifique-se de ter os seguintes softwares instalados em sua máquina:

Docker
Docker Compose
Estrutura do Projeto
bash
Copiar código
seu_projeto/
├── manage.py
├── seu_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                # Arquivo de variáveis de ambiente
├── README.md
manage.py: Script de gerenciamento do Django.
seu_app/: Diretório do seu projeto Django.
Dockerfile: Instruções para construir a imagem Docker da aplicação.
docker-compose.yml: Configurações para orquestrar os containers.
requirements.txt: Lista de dependências Python da sua aplicação.
.env: Arquivo contendo variáveis de ambiente (não deve ser versionado).
Configuração Inicial
Antes de executar a aplicação, siga os passos abaixo para configurar o ambiente:

Clonar o Repositório

bash
Copiar código
git clone https://github.com/seu_usuario/seu_projeto.git
cd seu_projeto
Criar o Arquivo .env

Crie um arquivo .env na raiz do projeto com o seguinte conteúdo:

env
Copiar código
# Variáveis de ambiente para o Django
DATABASE_NAME=nome_do_banco
DATABASE_USER=root
DATABASE_PASSWORD=senha_do_banco
DATABASE_HOST=db
DATABASE_PORT=3306
Nota: Substitua nome_do_banco e senha_do_banco pelas credenciais desejadas.

Atualizar o requirements.txt

Certifique-se de que o arquivo requirements.txt contém todas as dependências necessárias:

txt
Copiar código
Django>=3.2,<4.0
mysqlclient>=2.0
Como Executar
Siga os passos abaixo para construir e executar a aplicação usando o Docker Compose:

Construir e Iniciar os Containers

bash
Copiar código
docker-compose up --build
Aplicar Migrações e Criar Superusuário

Em outro terminal, execute:

bash
Copiar código
# Aplicar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser
Acessar a Aplicação

Abra seu navegador e acesse:

arduino
Copiar código
http://localhost:8000/
Variáveis de Ambiente
As variáveis de ambiente são definidas no arquivo .env. Este arquivo não deve ser versionado (adicione ao .gitignore), pois pode conter informações sensíveis.

Exemplo de .env:

env
Copiar código
DATABASE_NAME=nome_do_banco
DATABASE_USER=root
DATABASE_PASSWORD=senha_do_banco
DATABASE_HOST=db
DATABASE_PORT=3306
Comandos Úteis
Parar os Containers

bash
Copiar código
docker-compose down
Visualizar Logs

bash
Copiar código
docker-compose logs -f
Acessar o Shell do Container Web

bash
Copiar código
docker-compose exec web bash
Executar Testes

bash
Copiar código
docker-compose exec web python manage.py test
Considerações
Persistência de Dados: Os dados do banco de dados são persistidos no volume db_data, garantindo que não sejam perdidos ao reiniciar os containers.

Desenvolvimento vs. Produção: As configurações atuais são adequadas para um ambiente de desenvolvimento. Para produção, considere utilizar um servidor WSGI como Gunicorn e um servidor web como Nginx.

Segurança: Nunca exponha informações sensíveis em arquivos versionados. Utilize variáveis de ambiente para gerenciar credenciais e outros dados confidenciais.

Licença
Este projeto está licenciado sob a licença MIT.

Detalhes Técnicos
Dockerfile
dockerfile
Copiar código
# Use a imagem oficial do Python como base
FROM python:3.9-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos
COPY requirements.txt /app/

# Instala as dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copia todo o conteúdo do projeto para o diretório de trabalho
COPY . /app/

# Expõe a porta que o Django usará
EXPOSE 8000

# Comando para executar a aplicação
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
docker-compose.yml
yaml
Copiar código
version: '3.9'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - DATABASE_HOST=${DATABASE_HOST}
      - DATABASE_PORT=${DATABASE_PORT}
    networks:
      - network_app

  db:
    image: mysql:5.7
    command: --default-authentication-plugin=mysql_native_password
    environment:
      MYSQL_DATABASE: ${DATABASE_NAME}
      MYSQL_ROOT_PASSWORD: ${DATABASE_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - network_app

volumes:
  db_data:

networks:
  network_app:
    name: minha_rede_compartilhada
Nota: As variáveis de ambiente são referenciadas usando ${VARIAVEL} para serem carregadas a partir do arquivo .env.

Configuração do settings.py
python
Copiar código
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DATABASE_NAME', 'nome_do_banco'),
        'USER': os.environ.get('DATABASE_USER', 'root'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', 'senha_do_banco'),
        'HOST': os.environ.get('DATABASE_HOST', 'db'),
        'PORT': os.environ.get('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
Como Conectar a Outros Serviços na Mesma Rede
Para adicionar outro serviço (por exemplo, um container Redis) e conectá-lo à mesma rede:

Adicionar o Serviço ao docker-compose.yml

yaml
Copiar código
redis:
  image: redis:latest
  ports:
    - "6379:6379"
  networks:
    - network_app
Referenciar o Serviço no Código

No seu código Django, você pode se conectar ao Redis usando o hostname redis, que é resolvido automaticamente pelo Docker devido à configuração de rede compartilhada.

Exemplo de Uso da Rede Externa em Outro Projeto
Se você deseja que outro projeto utilize a mesma rede:

No Outro docker-compose.yml

yaml
Copiar código
version: '3.9'

services:
  outro_servico:
    image: alguma_imagem
    networks:
      - network_app

networks:
  network_app:
    external: true
    name: minha_rede_compartilhada
Criar a Rede Externa (se ainda não existir)

bash
Copiar código
docker network create minha_rede_compartilhada