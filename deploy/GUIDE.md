# Guia de Deploy no Hostinger VPS (Docker + Nginx Proxy Manager)

Este é o fluxo recomendado para este projeto, mantendo `DEBUG=False` e imagens (`/media`) funcionando em produção.

## Arquitetura final

- `proxy` (Nginx Proxy Manager): recebe tráfego público (80/443)
- `nginx` (interno): serve `/static` e `/media`, e repassa o restante para Django
- `web` (Django + Gunicorn)
- `db` (PostgreSQL)

## 1) Preparar o servidor

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
```

## 2) Subir o projeto

```bash
cd /var/www
git clone <SEU_REPO_URL> imobiliaria
cd imobiliaria
```

Crie/edite o arquivo `.env` na raiz do projeto:

```env
DEBUG=False
SECRET_KEY=gere_uma_chave_forte

DB_NAME=imobiliaria
DB_USER=imobiliaria
DB_PASSWORD=senha_forte
DB_PORT=5432

WHATSAPP_NUMERO=5548999999999

CSRF_TRUSTED_ORIGINS=https://imobidon.com.br,https://www.imobidon.com.br
```

> Observação: o projeto atualmente usa `ALLOWED_HOSTS` fixo em `settings.py`, então garanta que seu domínio está na lista.

## 3) Build e start dos containers

```bash
docker compose up -d --build
```

Verifique se tudo subiu:

```bash
docker compose ps
docker compose logs -f web
docker compose logs -f nginx
```

## 4) Configurar o Nginx Proxy Manager (Hostinger)

No painel do NPM (`http://SEU_IP:81`):

1. Crie um `Proxy Host`
2. Domain Names: `imobidon.com.br` e/ou `www.imobidon.com.br`
3. Scheme: `http`
4. Forward Hostname/IP: `nginx`
5. Forward Port: `80`
6. Ative `Websockets Support`
7. Aba SSL: solicite certificado Let's Encrypt e ative `Force SSL`

> O NPM e o `nginx` interno precisam estar na mesma rede Docker (`imobidom_net`), já configurada no `docker-compose.yml`.

## 5) Por que as imagens continuam com DEBUG=False?

- Uploads vão para volume persistente: `media_volume -> /app/backend/media`
- O `nginx` interno expõe `/media/` com `alias /app/backend/media/`
- Portanto as imagens não dependem do Django em modo debug

Arquivo usado: `deploy/nginx-docker.conf`

## 6) Comandos úteis de operação

Rebuild após alteração de código:

```bash
docker compose up -d --build
```

Executar migrações manualmente:

```bash
docker compose exec web python backend/manage.py migrate
```

Criar superusuário:

```bash
docker compose exec web python backend/manage.py createsuperuser
```

## 7) Checklist rápido de diagnóstico (se imagem não abrir)

1. URL da imagem começa com `/media/...`
2. Container `nginx` está `Up`
3. NPM aponta para `nginx:80` (não para `web:8000`)
4. `docker compose logs nginx` sem erro de `permission denied`
5. Arquivo existe no volume:

```bash
docker compose exec web ls -la /app/backend/media
```

Se os 5 itens estiverem OK, as imagens funcionam normalmente com `DEBUG=False`.
