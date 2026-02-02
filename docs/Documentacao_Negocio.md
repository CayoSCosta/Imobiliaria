# Documentação de Negócio — Plataforma Imobiliária

## 1. Sumário executivo
A plataforma centraliza a divulgação de empreendimentos, captação de leads e gestão do funil comercial, com integração a fornecedores de dados imobiliários (Órulo). O objetivo é aumentar o volume e a qualidade dos leads, reduzir esforço operacional e acelerar o ciclo de vendas.

## 2. Objetivos de negócio
- **Aumentar geração de leads qualificados**
- **Reduzir tempo de publicação de novos empreendimentos**
- **Padronizar comunicação e acompanhamento comercial**
- **Manter conteúdo institucional e marketing atualizado**

## 3. Público-alvo e personas
- **Comprador final**: busca imóvel residencial e simulações de financiamento
- **Equipe comercial**: atua no atendimento e conversão de leads
- **Gestor/Marketing**: publica conteúdo e controla campanhas

## 4. Proposta de valor
- **Experiência unificada** entre catálogo, detalhes e simuladores
- **Captação integrada** (formulários e WhatsApp)
- **Admin customizado** para operação rápida
- **Automação de conteúdo** via importação Órulo

## 5. Escopo funcional
### 5.1 Catálogo de imóveis
- Busca e visualização de imóveis
- Página de detalhe do imóvel
- Unidades vinculadas ao imóvel
- Imagens, plantas e documentos

### 5.2 Captação de leads
- Formulários de contato e simuladores
- Lead criado com origem, status e mensagem
- Exportação CSV para relatórios

### 5.3 Gestão comercial
- Listagem e filtros de leads
- Atualização de status do funil
- Acompanhamentos por lead

### 5.4 Conteúdo e institucional
- Blog com posts e propagandas
- Páginas institucionais

### 5.5 Integrações
- Órulo: importação e sincronização de imóveis
- E-mail: notificações de leads
- WhatsApp: rastreio de contato

## 6. Jornada do usuário (alto nível)
1. Usuário acessa catálogo
2. Visualiza detalhe do imóvel
3. Realiza simulação/contato
4. Lead é criado no sistema
5. Time comercial faz acompanhamento
6. Conversão em visita/proposta

## 7. Funil de vendas (status de lead)
- `novo`
- `em_atendimento`
- `visita_agendada`
- `proposta`
- `fechado`
- `perdido`

## 8. Indicadores (KPIs)
- **Leads por canal**
- **Taxa de conversão por etapa**
- **Tempo médio de atendimento**
- **Leads por empreendimento**
- **Conversão de simulações em contato**

## 9. Governança e compliance
- Auditoria de alterações administrativas
- Registro de data e usuário das mudanças
- Políticas de privacidade e termos

Referências de páginas institucionais:
- [templates/politica_de_privacidade.html](templates/politica_de_privacidade.html)
- [templates/termos_de_uso.html](templates/termos_de_uso.html)

## 10. Regras de negócio principais
- Imóveis podem ser inativados sem exclusão definitiva
- Leads sempre registram origem e status inicial
- Sincronização Órulo não remove dados locais, apenas atualiza

## 11. Operação e papéis
- **Admin Marketing:** conteúdo, blog, propagandas
- **Admin Comercial:** leads e acompanhamento
- **Admin Técnico:** integrações, manutenção e deploy

## 12. Riscos e mitigação
- **Dependência de integração externa (Órulo):** monitoramento e fallback manual
- **Qualidade de dados:** validação de campos obrigatórios
- **Picos de acesso:** escala via Docker + Gunicorn

## 13. Roadmap sugerido
- Dashboard de métricas e BI
- Automações de follow-up
- Integração com CRM externo

---

**Responsáveis de negócio:**
- Time Comercial / Marketing

**Última atualização:** 02/02/2026
