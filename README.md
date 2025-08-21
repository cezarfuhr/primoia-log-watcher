# Plano de Projeto: Log-Watcher AI SaaS

---
**[Visão Detalhada: Hub de Diagnóstico Centralizado](VISION_DIAGNOSTICS.md)**
---

## 1. Visão Geral

O Log-Watcher AI é um serviço (SaaS) projetado para ser o **hub central de observabilidade e diagnóstico** do ecossistema Primoia. Ele ingere logs de todas as aplicações, utiliza modelos de IA para analisá-los de forma inteligente, e transforma o ruído de logs brutos em insights acionáveis, ajudando a identificar problemas mais rápido e a entender a saúde da aplicação de forma proativa.

## 2. Proposta de Valor e Funções de Diagnóstico

- **Redução de Ruído:** Agrupa milhares de linhas de log repetitivas em um único evento acionável.
- **Detecção Inteligente de Anomalias:** Usa IA para identificar padrões incomuns que podem indicar um problema, mesmo antes que ele gere um erro crítico.
- **Economia de Tempo:** Desenvolvedores gastam menos tempo procurando "agulhas no palheiro" e mais tempo codificando.
- **Acessibilidade:** Oferece uma alternativa mais simples e barata às complexas e caras plataformas de observabilidade do mercado (Datadog, New Relic).

## 3. Modelo de Negócio (Freemium com Assinatura)

O objetivo é construir uma base de usuários com um tier gratuito e converter uma porcentagem para um plano pago e sustentável.

- **Tier Gratuito (Free):**
  - Até 500 MB de ingestão de logs / mês.
  - Retenção de dados de 7 dias.
  - Análise de anomalias básica.
  - Ideal para projetos pessoais e freelancers.

- **Tier Profissional (Pro):**
  - **Preço Alvo:** $15 / mês.
  - Até 10 GB de ingestão de logs / mês.
  - Retenção de dados de 30 dias.
  - Análises avançadas e sugestão de causa-raiz.
  - Alertas via Email/Webhook.

## 4. Arquitetura do MVP (Produto Mínimo Viável)

A arquitetura é desenhada para ser assíncrona, resiliente e de baixo custo inicial, utilizando o Proxmox como base.

```
                                     +-------------------------+
+----------+   Logs (HTTPS)   +------>|  API de Ingestão (API)  |
| Cliente  |------------------+       | (Kotlin/Python)         |
+----------+                         +-----------+-------------+
                                                 |
                                     +-----------v-------------+
                                     |  Fila de Mensagens      |
                                     |  (RabbitMQ / NATS)      |
                                     +-----------+-------------+
                                                 |
+--------------------------------+   +-----------v-------------+   +----------------------+
|  Banco de Dados Relacional     |<--+  Workers de Análise (IA)  +-->|  Ollama (LLM)        |
|  (PostgreSQL)                  |   |  (Python)               |   |  (Modelos de IA)     |
|  - Usuários, Chaves API        |   +-------------------------+   +----------------------+
|  - Resultados da Análise       |
+--------------------------------+

+--------------------------------+
|  Frontend Simples (Web)        |
|  - Dashboard de resultados     |
|  - Gestão de Chave API         |
|  (Conecta-se ao PostgreSQL     |
|   ou a uma API de leitura)     |
+--------------------------------+
```

- **API de Ingestão:** Um endpoint leve escrito em Kotlin (usando Ktor/Spring) ou Python (usando FastAPI) que recebe os logs, valida a chave de API e publica o trabalho em uma fila.
- **Fila de Mensagens:** RabbitMQ ou NATS rodando em um container. Desacopla a ingestão do processamento, garantindo que não se percam dados se a análise estiver lenta.
- **Workers de Análise:** Processos em Python que consomem da fila. Eles fazem o trabalho pesado:
  1. Chamam os modelos de IA no **Ollama** para resumir, agrupar ou encontrar anomalias.
  2. Estruturam o resultado.
  3. Salvam os insights no banco de dados **PostgreSQL**.
- **Banco de Dados:** PostgreSQL para armazenar dados de usuários, chaves de API e os resultados processados das análises.
- **Frontend:** Uma aplicação web mínima (pode ser feita com um framework simples como Streamlit em Python, ou um HTML/JS básico) para o usuário se cadastrar, pegar sua chave de API e ver os relatórios gerados.

## 5. Estratégia de Marketing: "Construa em Público"

O marketing será o próprio desenvolvimento do projeto.

- **Blog Técnico / Canal do YouTube:** Documentar cada decisão de arquitetura, cada desafio técnico e cada sucesso.
- **Conteúdo Alvo:** "Como escolhi entre RabbitMQ e NATS para meu SaaS", "Testando modelos do Ollama para análise de logs", "Minha jornada para os primeiros 10 clientes pagantes".
- **Comunidade:** Engajar em comunidades de desenvolvedores (Reddit, Dev.to, fóruns) compartilhando os aprendizados, não fazendo propaganda direta. O produto será uma consequência natural do conteúdo de valor.

## 6. Roadmap Fásico

- **Fase 1 (MVP - 3 a 6 meses):**
  - [ ] Configurar a infraestrutura base no Proxmox (Docker, Gitea, etc.).
  - [ ] Desenvolver a API de ingestão.
  - [ ] Criar o primeiro worker de análise com uma lógica simples (ex: agrupar por similaridade).
  - [ ] Lançar o frontend mínimo com autenticação e visualização de API Key.
  - [ ] Começar o blog e documentar os primeiros passos.

- **Fase 2 (Beta Aberto - 2 meses):**
  - [ ] Lançar o Tier Gratuito para os seguidores do blog e comunidades.
  - [ ] Coletar feedback intensamente. O que funciona? O que falta?
  - [ ] Refinar os modelos de IA e a lógica de análise com base no feedback.

- **Fase 3 (Lançamento Comercial - Contínuo):**
  - [ ] Implementar um sistema de pagamento (Stripe/Lemon Squeezy).
  - [ ] Lançar o Tier Profissional.
  - [ ] Continuar o ciclo de criar conteúdo e melhorar o produto.

- **Fase 4 (Futuro):**
  - [ ] Integração de alertas (Slack, Telegram, Discord).
  - [ ] Dashboards de visualização mais avançados no frontend.
  - [ ] Análise de logs em tempo real (streaming).

## 7. Stack Tecnológica Sugerida

- **Infraestrutura:** Proxmox, Docker
- **Backend (API):** Kotlin (Ktor) ou Python (FastAPI)
- **Backend (Workers):** Python
- **Fila de Mensagens:** RabbitMQ
- **Banco de Dados:** PostgreSQL
- **IA (Local):** Ollama
- **Controle de Versão:** Gitea (self-hosted)