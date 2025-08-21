# 🏗️ Primoia Log-Watcher - Hub de Diagnóstico Centralizado

> **Hub central de observabilidade e diagnóstico para o ecossistema Primoia**

O **Primoia Log-Watcher** é o sistema centralizado que coleta, processa e analisa logs de todos os serviços do ecossistema Primoia, fornecendo insights inteligentes e diagnóstico proativo através de IA.

## 🎯 O que é?

O Primoia Log-Watcher é o **cérebro operacional** do ecossistema Primoia. Ele:

- ✅ **Centraliza todos os logs** de todos os serviços em um só lugar
- ✅ **Reduz ruído** agrupando logs similares automaticamente
- ✅ **Detecta anomalias** usando IA antes que afetem usuários
- ✅ **Sugere diagnósticos** propondo causas-raiz para problemas
- ✅ **Monitora proativamente** a saúde de todo o ecossistema

## 🚀 Integração Rápida

### Para Desenvolvedores de Serviços

Se você está desenvolvendo um serviço no ecossistema Primoia, veja o **[Guia de Integração](INTEGRATION_GUIDE.md)** para começar em 5 minutos.

### Para Administradores

Se você está configurando o sistema, veja o **[Guia Docker](DOCKER_README.md)** para deploy.

## 📊 Status Atual

- ✅ **MVP Funcional** - API de ingestão operacional
- ✅ **Docker Validado** - Containerização completa
- ✅ **Autenticação** - Sistema de API keys funcionando
- ✅ **Métricas** - Coleta e visualização de estatísticas
- ✅ **Documentação** - Guias completos de integração

## 🔧 Como Usar

### Opção 1: Docker (Recomendado)

```bash
# Executar com Docker Compose
docker compose up -d

# Ou container simples
docker build -t primoia-log-watcher .
docker run -d --name primoia-log-watcher -p 8000:8000 primoia-log-watcher
```

### Opção 2: Local

```bash
pip install -r requirements.txt
python run_server.py
```

### Validação

```bash
# Testar se está funcionando
curl http://localhost:8000/health

# Executar validação completa
./validate-docker.sh
```

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| **[Guia de Integração](INTEGRATION_GUIDE.md)** | Como integrar seu serviço |
| **[Guia Docker](DOCKER_README.md)** | Deploy e configuração Docker |
| **[Status da Implementação](IMPLEMENTATION_STATUS.md)** | Progresso do desenvolvimento |
| **[Visão Detalhada](VISION_DIAGNOSTICS.md)** | Visão estratégica do projeto |

## 🔑 API Keys para Teste

| Serviço | API Key | Rate Limit |
|---------|---------|------------|
| nex-web-backend | `nex-web-backend-key-2024` | 1000 logs/min |
| nex-mobile-backend | `nex-mobile-backend-key-2024` | 500 logs/min |
| auth-service | `auth-service-key-2024` | 200 logs/min |
| conductor | `conductor-key-2024` | 300 logs/min |

## 🌐 Endpoints Principais

- **Health Check**: `GET /health`
- **Documentação**: `GET /docs` (Swagger)
- **Ingestão Individual**: `POST /api/v1/ingestion/logs/single`
- **Ingestão em Lote**: `POST /api/v1/ingestion/logs/batch`
- **Estatísticas**: `GET /api/v1/stats/global`

## 📈 Exemplo de Uso

```bash
# Enviar um log de teste
curl -X POST "http://localhost:8000/api/v1/ingestion/logs/single" \
  -H "Authorization: Bearer nex-web-backend-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "nex-web-backend",
    "service_type": "nex-web-backend",
    "service_version": "1.0.0",
    "service_instance_id": "web-backend-001",
    "level": "INFO",
    "message": "Teste de integração",
    "environment": "dev"
  }'
```

## 🏗️ Arquitetura

```
┌─────────────────┐    Logs    ┌─────────────────────┐
│  Serviços       │ ──────────► │  API de Ingestão    │
│  Primoia        │            │  (FastAPI)          │
└─────────────────┘            └─────────┬───────────┘
                                         │
                                ┌────────▼─────────┐
                                │  Fila de         │
                                │  Processamento   │
                                └────────┬─────────┘
                                         │
                                ┌────────▼─────────┐
                                │  Análise IA      │
                                │  (Futuro)        │
                                └────────┬─────────┘
                                         │
                                ┌────────▼─────────┐
                                │  Dashboard       │
                                │  & Métricas      │
                                └──────────────────┘
```

## 🎯 Próximos Passos

### Para Desenvolvedores
1. **Integrar seu serviço** - Veja o [Guia de Integração](INTEGRATION_GUIDE.md)
2. **Implementar logs estruturados** - Use o formato padronizado
3. **Monitorar métricas** - Acompanhe a saúde do seu serviço

### Para o Projeto
1. **Implementar IA** - Análise inteligente de logs
2. **Adicionar persistência** - Banco de dados PostgreSQL
3. **Criar dashboard** - Interface web para visualização
4. **Alertas** - Notificações proativas

## 🤝 Contribuindo

1. **Teste a integração** do seu serviço
2. **Reporte problemas** abrindo issues
3. **Sugira melhorias** para o formato de logs
4. **Compartilhe casos de uso** específicos

## 📞 Suporte

- **Documentação da API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Issues**: Abra uma issue no repositório

---

**Status**: ✅ **MVP Funcional** - Pronto para integração com serviços reais do ecossistema Primoia!

> 💡 **Dica**: Comece pelo [Guia de Integração](INTEGRATION_GUIDE.md) se você quer integrar seu serviço rapidamente.