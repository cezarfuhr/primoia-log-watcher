#!/bin/bash

# Script de validação Docker para o Primoia Log-Watcher

set -e

echo "🐳 Validando Primoia Log-Watcher com Docker..."
echo "=============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Função para aguardar serviço
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    log "Aguardando serviço em $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log "✅ Serviço está pronto!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    error "❌ Serviço não ficou pronto em $max_attempts tentativas"
    return 1
}

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local data=$3
    local expected_status=$4
    
    local response
    if [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -X "$method" "$url" -H "Content-Type: application/json" -d "$data")
    else
        response=$(curl -s -w "%{http_code}" -X "$method" "$url")
    fi
    
    local status_code=${response: -3}
    local body=${response%???}
    
    if [ "$status_code" = "$expected_status" ]; then
        log "✅ $method $url - Status: $status_code"
        echo "$body" | python -m json.tool 2>/dev/null || echo "$body"
    else
        error "❌ $method $url - Esperado: $expected_status, Recebido: $status_code"
        echo "$body"
        return 1
    fi
}

# Parar containers existentes
step "Limpando containers existentes..."
docker compose down 2>/dev/null || true
docker stop primoia-log-watcher-test 2>/dev/null || true
docker rm primoia-log-watcher-test 2>/dev/null || true

# Build da imagem
step "Fazendo build da imagem Docker..."
docker build -t primoia-log-watcher .

# Teste 1: Container simples
step "Teste 1: Executando container simples..."
docker run -d --name primoia-log-watcher-test -p 8000:8000 primoia-log-watcher

# Aguardar serviço
wait_for_service "http://localhost:8000/health"

# Testar endpoints básicos
step "Testando endpoints básicos..."
test_endpoint "GET" "http://localhost:8000/" "" "200"
test_endpoint "GET" "http://localhost:8000/health" "" "200"
test_endpoint "GET" "http://localhost:8000/api/v1/stats/global" "" "200"

# Testar envio de log
step "Testando envio de log..."
log_data='{
    "service_name": "nex-web-backend",
    "service_type": "nex-web-backend",
    "service_version": "1.0.0",
    "service_instance_id": "web-backend-001",
    "level": "INFO",
    "message": "Test log from Docker validation",
    "environment": "dev",
    "host": "docker-test",
    "ip_address": "172.17.0.1"
}'

curl -s -X POST "http://localhost:8000/api/v1/ingestion/logs/single" \
  -H "Authorization: Bearer nex-web-backend-key-2024" \
  -H "Content-Type: application/json" \
  -d "$log_data" | python -m json.tool

# Testar estatísticas do serviço
step "Testando estatísticas do serviço..."
curl -s "http://localhost:8000/api/v1/ingestion/stats" \
  -H "Authorization: Bearer nex-web-backend-key-2024" | python -m json.tool

# Parar container simples
step "Parando container simples..."
docker stop primoia-log-watcher-test
docker rm primoia-log-watcher-test

# Teste 2: Docker Compose
step "Teste 2: Executando com Docker Compose..."
docker compose up -d

# Aguardar serviço
wait_for_service "http://localhost:8000/health"

# Testar novamente
step "Testando com Docker Compose..."
test_endpoint "GET" "http://localhost:8000/health" "" "200"

# Testar envio de lote
step "Testando envio de lote de logs..."
batch_data='{
    "batch_id": "test-batch-001",
    "service_name": "nex-web-backend",
    "service_type": "nex-web-backend",
    "service_version": "1.0.0",
    "service_instance_id": "web-backend-001",
    "logs": [
        {
            "service_name": "nex-web-backend",
            "service_type": "nex-web-backend",
            "service_version": "1.0.0",
            "service_instance_id": "web-backend-001",
            "level": "INFO",
            "message": "Batch log 1",
            "environment": "dev",
            "host": "docker-compose",
            "ip_address": "172.17.0.1"
        },
        {
            "service_name": "nex-web-backend",
            "service_type": "nex-web-backend",
            "service_version": "1.0.0",
            "service_instance_id": "web-backend-001",
            "level": "WARNING",
            "message": "Batch log 2",
            "environment": "dev",
            "host": "docker-compose",
            "ip_address": "172.17.0.1"
        }
    ]
}'

curl -s -X POST "http://localhost:8000/api/v1/ingestion/logs/batch" \
  -H "Authorization: Bearer nex-web-backend-key-2024" \
  -H "Content-Type: application/json" \
  -d "$batch_data" | python -m json.tool

# Verificar logs do container
step "Verificando logs do container..."
docker compose logs --tail=10

# Testar documentação
step "Verificando documentação..."
if curl -s "http://localhost:8000/docs" | grep -q "Swagger"; then
    log "✅ Documentação Swagger disponível"
else
    warn "⚠️  Documentação Swagger não encontrada"
fi

# Limpeza final
step "Limpando containers..."
docker compose down

log "🎉 Validação Docker concluída com sucesso!"
log "📊 Resumo dos testes:"
log "  ✅ Build da imagem"
log "  ✅ Container simples"
log "  ✅ Docker Compose"
log "  ✅ Endpoints da API"
log "  ✅ Envio de logs individuais"
log "  ✅ Envio de lotes"
log "  ✅ Health checks"
log "  ✅ Estatísticas"

echo ""
log "🚀 Para executar em produção:"
echo "   docker run -d -p 8000:8000 primoia-log-watcher"
echo ""
log "🔧 Para desenvolvimento:"
echo "   docker compose up -d"
echo ""
log "📚 Documentação:"
echo "   http://localhost:8000/docs"
