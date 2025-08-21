# 🐳 Primoia Log-Watcher - Docker

Este documento contém instruções completas para executar o Primoia Log-Watcher usando Docker.

## 📋 Pré-requisitos

- Docker instalado e funcionando
- Docker Compose (opcional, mas recomendado)
- Porta 8000 disponível

## 🚀 Execução Rápida

### Opção 1: Container Simples
```bash
# Build da imagem
docker build -t primoia-log-watcher .

# Executar container
docker run -d --name primoia-log-watcher -p 8000:8000 primoia-log-watcher
```

### Opção 2: Docker Compose (Recomendado)
```bash
# Executar com docker-compose
docker compose up -d

# Ver logs
docker compose logs -f

# Parar
docker compose down
```

## 🧪 Validação Automática

Execute o script de validação para testar todos os componentes:

```bash
# Tornar executável (se necessário)
chmod +x validate-docker.sh

# Executar validação completa
./validate-docker.sh
```

Este script irá:
- ✅ Fazer build da imagem
- ✅ Testar container simples
- ✅ Testar Docker Compose
- ✅ Validar todos os endpoints da API
- ✅ Testar envio de logs individuais e lotes
- ✅ Verificar health checks
- ✅ Validar documentação

## 📊 Verificação Manual

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Endpoint Raiz
```bash
curl http://localhost:8000/
```

### 3. Enviar Log de Teste
```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/logs/single" \
  -H "Authorization: Bearer nex-web-backend-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "nex-web-backend",
    "service_type": "nex-web-backend",
    "service_version": "1.0.0",
    "service_instance_id": "web-backend-001",
    "level": "INFO",
    "message": "Test log from Docker",
    "environment": "dev",
    "host": "docker-test",
    "ip_address": "172.17.0.1"
  }'
```

### 4. Verificar Estatísticas
```bash
curl "http://localhost:8000/api/v1/stats/global"
```

## 🔧 Configuração

### Variáveis de Ambiente

O container suporta as seguintes variáveis de ambiente:

```bash
HOST=0.0.0.0          # Host do servidor (padrão)
PORT=8000             # Porta do servidor (padrão)
LOG_LEVEL=info        # Nível de log (padrão)
```

### Exemplo com Variáveis Customizadas
```bash
docker run -d \
  --name primoia-log-watcher \
  -p 8000:8000 \
  -e LOG_LEVEL=debug \
  primoia-log-watcher
```

## 📚 Documentação da API

Após iniciar o container, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔑 API Keys Pré-configuradas

Para testes, os seguintes serviços já estão configurados:

| Serviço | API Key | Rate Limit |
|---------|---------|------------|
| nex-web-backend | `nex-web-backend-key-2024` | 1000 logs/min |
| nex-mobile-backend | `nex-mobile-backend-key-2024` | 500 logs/min |
| auth-service | `auth-service-key-2024` | 200 logs/min |
| conductor | `conductor-key-2024` | 300 logs/min |

## 🐛 Troubleshooting

### Container não inicia
```bash
# Verificar logs
docker logs primoia-log-watcher

# Verificar se a porta está em uso
netstat -tulpn | grep 8000
```

### API não responde
```bash
# Verificar se o container está rodando
docker ps

# Verificar health check
curl http://localhost:8000/health

# Verificar logs em tempo real
docker logs -f primoia-log-watcher
```

### Erro de autenticação
```bash
# Verificar se está usando a API key correta
curl -H "Authorization: Bearer nex-web-backend-key-2024" \
  http://localhost:8000/api/v1/ingestion/stats
```

## 🔄 Desenvolvimento

### Modo Desenvolvimento com Volume
```bash
docker run -d \
  --name primoia-log-watcher-dev \
  -p 8000:8000 \
  -v $(pwd)/src:/app/src:ro \
  primoia-log-watcher
```

### Rebuild após mudanças
```bash
# Parar container
docker stop primoia-log-watcher

# Rebuild
docker build -t primoia-log-watcher .

# Executar novamente
docker run -d --name primoia-log-watcher -p 8000:8000 primoia-log-watcher
```

## 📦 Estrutura dos Arquivos Docker

```
primoia-log-watcher/
├── Dockerfile                 # Imagem principal
├── Dockerfile.test           # Imagem para testes
├── docker-compose.yml        # Orquestração
├── .dockerignore            # Arquivos ignorados no build
├── docker-test-entrypoint.sh # Script de entrada para testes
└── validate-docker.sh       # Script de validação
```

## 🚀 Produção

### Execução em Produção
```bash
# Build otimizado
docker build -t primoia-log-watcher:latest .

# Executar com restart automático
docker run -d \
  --name primoia-log-watcher \
  --restart unless-stopped \
  -p 8000:8000 \
  primoia-log-watcher:latest
```

### Docker Compose para Produção
```yaml
version: '3.8'
services:
  primoia-log-watcher:
    image: primoia-log-watcher:latest
    container_name: primoia-log-watcher
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 🎯 Próximos Passos

1. **Integrar com serviço real** - Conectar um serviço do ecossistema Primoia
2. **Adicionar persistência** - Migrar para PostgreSQL
3. **Implementar IA** - Adicionar análise inteligente de logs
4. **Monitoramento** - Integrar com Prometheus/Grafana
5. **Backup** - Implementar backup automático dos dados

---

**Status**: ✅ **Docker Validado e Funcionando**
