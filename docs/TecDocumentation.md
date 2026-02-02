# Documentação Técnica — Plataforma Imobidon

## 1. Visão Geral

O **Imobidon** é uma plataforma imobiliária robusta desenvolvida para a divulgação de empreendimentos, gestão de leads e integração automatizada com ecossistemas imobiliários. O sistema foi projetado sob uma arquitetura escalável, utilizando uma API REST para comunicação entre serviços e um motor de sincronização de dados externo.

## 2. Stack Tecnológica

* **Backend:** Framework Django (Python) com Django REST Framework.
* **Banco de Dados:** PostgreSQL (Relacional).
* **Infraestrutura:** Arquitetura conteinerizada com Docker e Docker Compose.
* **Segurança de Servidor:** Nginx como Proxy Reverso e gerenciamento de certificados TLS.
* **Arquivos Estáticos:** WhiteNoise e gerenciamento otimizado de assets.

## 3. Arquitetura e Módulos

O sistema é modularizado para garantir independência entre as áreas de negócio:

### 3.1. Engine de Imóveis

* Gerenciamento completo de catálogo (Empreendimentos, Unidades e Tipologias).
* Suporte a geolocalização e metadados comerciais complexos.
* Sistema dinâmico de mídias (Galeria de imagens, plantas e documentos técnicos).

### 3.2. Gestão de Leads e CRM Gateway

* Módulo especializado para captação de interessados via formulários e gatilhos de conversão.
* Endpoints dedicados para recepção de eventos (ex: cliques em WhatsApp e simulações).
* Painel de auditoria e acompanhamento de status de atendimento.

### 3.3. Módulo de Conteúdo (Blog/Marketing)

* Sistema de gerenciamento de conteúdo (CMS) para SEO e autoridade de marca.
* Gestão de banners e campanhas de propaganda interna.

## 4. Capacidade de Integração (API)

A plataforma está preparada para consumir e fornecer dados através de:

* **Consumo de APIs Externas:** Motor de sincronização customizável para importação de inventário (ex: Órulo e outros provedores).
* **API REST Própria:** Endpoints estruturados em JSON para integração com Front-ends modernos ou ferramentas de terceiros.
* **Webhooks e Notificações:** Suporte a notificações via SMTP e integração com mensageria.

## 5. Segurança e Compliance

* **Criptografia:** Tráfego 100% via HTTPS.
* **Autenticação:** Sistema de permissões por níveis de acesso (Admin/Staff/User).
* **Auditoria:** Log detalhado de alterações (Audit Log) que registra ações por IP, usuário e timestamp.
* **Proteção:** Camada de segurança contra ataques comuns (CSRF, XSS e SQL Injection) nativa do framework.

## 6. Ambiente de Execução

A plataforma opera de forma isolada via Docker, facilitando o deploy em ambientes VPS ou Cloud (AWS, Google Cloud, DigitalOcean). O gerenciamento de variáveis sensíveis é feito estritamente via arquivos de ambiente (`.env`), garantindo a integridade do código-fonte.

---