# Guia de Deploy no Hostinger VPS (Ubuntu)

Este guia assume que você tem acesso SSH ao seu VPS.

## 1. Preparação do Servidor

Atualize o sistema e instale os pacotes necessários:

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git -y
```

## 2. Configuração do Projeto

Clone seu repositório (ou copie os arquivos) para `/var/www/imobiliaria`.

```bash
cd /var/www
git clone <SEU_REPO_URL> imobiliaria
cd imobiliaria
```

Crie o ambiente virtual e instale as dependências:

```bash
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
```

## 3. Configuração de Ambiente (.env)

Crie o arquivo `.env` na raiz do projeto (`/var/www/imobiliaria/.env`) com suas configurações de produção:

```bash
DEBUG=False
SECRET_KEY=sua_chave_secreta_super_segura_gerada_aleatoriamente
ALLOWED_HOSTS=seu_dominio.com,www.seu_dominio.com,seu_ip_vps
# Adicione outras chaves como banco de dados se usar PostgreSQL
```

## 4. Finalizando Django

Colete os arquivos estáticos e aplique migrações:

```bash
# Estando em /var/www/imobiliaria/backend com venv ativado
python manage.py collectstatic
python manage.py migrate
```

## 5. Configurar Gunicorn (Application Server)

Copie e habilite o serviço do Gunicorn:

```bash
sudo cp ../deploy/gunicorn.service /etc/systemd/system/
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

Verifique se está rodando: `sudo systemctl status gunicorn`

## 6. Configurar Nginx (Web Server)

Edite o arquivo `deploy/nginx.conf` e troque `SEU_DOMINIO_AQUI` pelo seu domínio real ou IP.

Copie para a pasta do Nginx:

```bash
sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/imobiliaria
sudo ln -s /etc/nginx/sites-available/imobiliaria /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 7. Firewall (UFW)

Se tiver firewall ativado:

```bash
sudo ufw allow 'Nginx Full'
```

## 8. HTTPS (SSL) - Opcional mas recomendado

Instale o Certbot:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d seu_dominio.com
```

---
Agora seu site deve estar no ar!
