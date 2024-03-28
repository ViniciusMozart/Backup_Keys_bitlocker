# Usar uma imagem base do Python 3.8
FROM python:3.11.8

# Definir o diretório de trabalho
WORKDIR /app
#########copiando pastas#######

COPY templates/ .
COPY static/ .

# Copiar o script python para o diretório de trabalho
COPY app.py .
COPY create_users.py .
COPY db.py .
COPY graph.py .
########copiando banco usuarios
COPY db.py .
#######copiando requisitos
COPY requirements.txt .

# Instalar os pacotes necessários usando o pip
COPY users.csv .
#RUN pip install requests msal
RUN pip install -r requirements.txt
# Definir as variáveis de ambiente usando os argumentos passados na construção da imagem
ARG TENANT_ID
ARG CLIENT_ID
ARG CLIENT_SECRET
# ARG GROUP_ID
# ARG SERVICE_PRINCIPAL_ID

ENV TENANT_ID=$TENANT_ID
ENV CLIENT_ID=$CLIENT_ID
ENV CLIENT_SECRET=$CLIENT_SECRET
# ENV GROUP_ID=$GROUP_ID

# A porta pode variar dependendo de como sua aplicação está configurada
EXPOSE 5000

# Comando para executar a aplicação usando `python .\app.py`
# Note que estamos usando a notação Unix-style para o caminho do arquivo
CMD ["python", "./app.py"]