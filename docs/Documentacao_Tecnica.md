# Documentação Técnica — Plataforma Imobiliária

## 1. Visão geral
Plataforma web para divulgação de imóveis, captação e gestão de leads, com integração à API Órulo para importação e atualização de empreendimentos. O sistema possui frontend público, API REST e painel administrativo customizado.

**Código-fonte e configurações principais:**
- [backend/config/settings.py](backend/config/settings.py)
- [backend/config/urls.py](backend/config/urls.py)
- [backend/imoveis/urls.py](backend/imoveis/urls.py)
- [backend/leads/urls.py](backend/leads/urls.py)
- [backend/blog/urls.py](backend/blog/urls.py)

## 2. Stack tecnológica
- **Backend:** Django 5.2 + Django REST Framework
- **Banco de dados:** PostgreSQL
- **Servidor de aplicação:** Gunicorn
- **Serviço de arquivos estáticos:** WhiteNoise
- **Proxy / TLS:** Nginx (ambiente VPS) ou Nginx Proxy Manager (Docker)
- **Containerização:** Docker + Docker Compose

**Dependências:**
- Raiz: [requirements.txt](requirements.txt)
- Backend: [backend/requirements.txt](backend/requirements.txt)

## 3. Arquitetura (alto nível)
**Camadas principais:**
1. **Frontend público (templates + assets estáticos)**
   - Templates em [templates/](templates/)
   - Assets em [frontend/static/](frontend/static/)
2. **API REST**
   - Endpoints JSON para imóveis e leads
3. **Admin customizado**
   - Rotas sob `custom-admin/`
4. **Persistência**
   - PostgreSQL com modelos Django
5. **Integrações externas**
   - Órulo API
   - SMTP para notificações de leads

## 4. Apps Django e responsabilidades
### 4.1 imoveis
- Catálogo de imóveis, unidades, imagens, instalações e arquivos
- Importação/sync com Órulo
- Páginas institucionais e simuladores

**Modelos-chave:**
- `Imovel`, `Unidade`, `ImagemImovel`, `ImagemUnidade`, `Instalacao`, `ArquivoImovel`
- Implementação em [backend/imoveis/models.py](backend/imoveis/models.py)

**Rotas principais:**
- Público: `/`, `/imovel/<slug>/`, `/simulacao/*`, `/fale-conosco/`
- API: `/api/imoveis/`, `/api/imoveis/<id>/`
- Admin: `/custom-admin/*`

**Definições de rotas:** [backend/imoveis/urls.py](backend/imoveis/urls.py)

### 4.2 leads
- Captação e gestão de leads
- Acompanhamento e exportação CSV

**Modelos:**
- `Lead`, `Acompanhamento`
- Definição em [backend/leads/models.py](backend/leads/models.py)

**Rotas:**
- API: `/api/leads/`, `/api/whatsapp-click/`
- Admin: `/custom-admin/leads/*`

**Definições de rotas:** [backend/leads/urls.py](backend/leads/urls.py)

### 4.3 blog
- Posts e propagandas
- Admin para criação/edição

**Modelos:**
- `Post`, `Propaganda`
- Definição em [backend/blog/models.py](backend/blog/models.py)

**Rotas:** [backend/blog/urls.py](backend/blog/urls.py)

### 4.4 audit
- Auditoria de alterações (criação/edição/exclusão)
- Registro de usuário, IP, user-agent e URL

**Modelo:**
- `AuditLog` em [backend/audit/models.py](backend/audit/models.py)

## 5. Integração Órulo
- Importação de imóveis, unidades, imagens e plantas
- Sincronização e atualização de dados

**Serviço:** [backend/imoveis/orulo_service.py](backend/imoveis/orulo_service.py)

**Configuração requerida (.env):**
- `ORULO_CLIENT_ID`
- `ORULO_CLIENT_SECRET`
- `ORULO_BASE_URL`

Exemplo em [\.env.example](.env.example)

## 6. Configuração de ambiente
**Variáveis principais:**
- Django: `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`
- PostgreSQL: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- SMTP: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`
- Leads: `LEAD_NOTIFICATION_EMAILS`
- WhatsApp: `WHATSAPP_NUMERO`

Arquivo de exemplo: [\.env.example](.env.example)

## 7. Execução local (sem Docker)
1. Criar `.env` conforme [\.env.example](.env.example)
2. Instalar dependências (arquivo de backend)
3. Executar migrações e coletar estáticos

> Referência de deploy e operação: [deploy/GUIDE.md](deploy/GUIDE.md)

## 8. Execução via Docker
- `web`: Django + Gunicorn
- `db`: PostgreSQL
- `proxy`: Nginx Proxy Manager

Configuração em [docker-compose.yml](docker-compose.yml)

## 9. Modelagem de dados (resumo)
### Imóvel
- Informações comerciais: título, descrição, tipo, status, destaque
- Endereço e geolocalização
- Preços e taxas
- Integração Órulo

### Unidade
- Tipologia: área, quartos, banheiros, suítes, vagas

### Lead
- Dados do interessado e preferências
- Status de atendimento

### Post
- Conteúdo institucional e marketing

## 10. Segurança e compliance
- Proteção de rotas administrativas via autenticação Django
- Logs de auditoria para rastreio de alterações
- CSRF habilitado no Django

## 11. Observabilidade e manutenção
- Logs padrão do Django + integração de auditoria
- Scripts de diagnóstico em [backend/scripts/](backend/scripts/)

## 12. Padrões e convenções
- Organização por apps Django
- Templates e assets segregados por responsabilidade
- Imagens e arquivos com upload path por slug de imóvel

---

**Responsáveis técnicos:**
- Time de Engenharia / TI

**Última atualização:** 02/02/2026
