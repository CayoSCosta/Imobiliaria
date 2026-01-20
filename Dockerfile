FROM python:3.11-slim

# Evita que o Python grave arquivos pyc no disco (PYTHONDONTWRITEBYTECODE)
# Evita que o Python bufferize stdout e stderr (PYTHONUNBUFFERED)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para compilar pacotes Python e conectar ao Postgres
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos
COPY backend/requirements.txt /app/requirements.txt

# Instala as dependências Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copia o restante do código do projeto
COPY . /app/

# Executa o collectstatic para reunir arquivos estáticos (opcional aqui, pode ser no entrypoint)
# RUN python backend/manage.py collectstatic --noinput

# Comando padrão (pode ser sobrescrito pelo docker-compose)
CMD ["gunicorn", "--chdir", "backend", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
