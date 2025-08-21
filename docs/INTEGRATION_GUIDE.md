# 📋 Guia de Integração: Primoia Log-Watcher

Este guia explica como integrar qualquer serviço do ecossistema Primoia com o **Hub de Diagnóstico Centralizado**.

## 🎯 Visão Geral

O **Primoia Log-Watcher** é o sistema centralizado de logs para todo o ecossistema Primoia. Ele coleta, processa e analisa logs de todos os serviços, fornecendo insights inteligentes e diagnóstico proativo.

### Benefícios da Integração:
- ✅ **Observabilidade Centralizada** - Todos os logs em um só lugar
- ✅ **Análise Inteligente** - IA para detectar problemas antes que afetem usuários
- ✅ **Redução de Ruído** - Agrupamento automático de logs similares
- ✅ **Diagnóstico Proativo** - Alertas e sugestões de causa-raiz
- ✅ **Métricas Unificadas** - Visão consolidada da saúde do ecossistema

## 🚀 Integração Rápida

### 1. Obter API Key

Cada serviço precisa de uma API key única. Solicite sua chave através do endpoint administrativo:

```bash
# Adicionar novo serviço (requer acesso administrativo)
curl -X POST "http://localhost:8000/api/v1/admin/services" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "meu-servico",
    "service_type": "meu-servico",
    "api_key": "minha-api-key-2024",
    "rate_limit": 100
  }'
```

### 2. Enviar Primeiro Log

```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/logs/single" \
  -H "Authorization: Bearer minha-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "meu-servico",
    "service_type": "meu-servico",
    "service_version": "1.0.0",
    "service_instance_id": "instancia-001",
    "level": "INFO",
    "message": "Serviço iniciado com sucesso",
    "environment": "dev",
    "host": "meu-host",
    "ip_address": "192.168.1.100"
  }'
```

### 3. Verificar Integração

```bash
# Verificar estatísticas do serviço
curl -H "Authorization: Bearer minha-api-key-2024" \
  "http://localhost:8000/api/v1/ingestion/stats"
```

## 📝 Formato de Log Padronizado

Todos os serviços devem enviar logs no seguinte formato:

### Campos Obrigatórios

```json
{
  "service_name": "string",           // Nome do serviço (ex: "nex-web-backend")
  "service_type": "string",           // Tipo do serviço (ex: "nex-web-backend")
  "service_version": "string",        // Versão do serviço (ex: "1.2.3")
  "service_instance_id": "string",    // ID único da instância
  "level": "string",                  // DEBUG, INFO, WARNING, ERROR, CRITICAL
  "message": "string",                // Mensagem principal do log
  "environment": "string"             // dev, staging, prod
}
```

### Campos Opcionais

```json
{
  "logger_name": "string",            // Nome do logger (ex: "com.nex.web.controller")
  "thread_name": "string",            // Nome da thread
  "context": {},                      // Contexto adicional (objeto)
  "tags": ["string"],                 // Tags para categorização
  "exception_type": "string",         // Tipo da exceção
  "exception_message": "string",      // Mensagem da exceção
  "stack_trace": "string",            // Stack trace completo
  "execution_time_ms": 0.0,           // Tempo de execução em ms
  "memory_usage_mb": 0.0,             // Uso de memória em MB
  "request_id": "string",             // ID único da requisição
  "user_id": "string",                // ID do usuário
  "endpoint": "string",               // Endpoint da API
  "http_method": "string",            // Método HTTP
  "status_code": 0,                   // Código de status HTTP
  "host": "string",                   // Hostname da máquina
  "ip_address": "string"              // Endereço IP
}
```

## 🔧 Implementação por Linguagem

### Python

```python
import requests
import json
from datetime import datetime

class PrimoiaLogClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def send_log(self, level: str, message: str, **kwargs):
        """Envia um log para o Primoia Log-Watcher"""
        log_data = {
            "service_name": "meu-servico",
            "service_type": "meu-servico",
            "service_version": "1.0.0",
            "service_instance_id": "instancia-001",
            "level": level,
            "message": message,
            "environment": "dev",
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/ingestion/logs/single",
            headers=self.headers,
            json=log_data
        )
        response.raise_for_status()
        return response.json()

# Uso
client = PrimoiaLogClient("minha-api-key-2024")
client.send_log("INFO", "Usuário logado com sucesso", user_id="12345")
client.send_log("ERROR", "Falha na conexão com banco", exception_type="ConnectionError")
```

### Java (Spring Boot)

```java
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.Map;
import java.util.HashMap;

@Component
public class PrimoiaLogClient {
    private final String apiKey;
    private final String baseUrl;
    private final RestTemplate restTemplate;
    
    public PrimoiaLogClient(@Value("${primoia.log.api-key}") String apiKey,
                           @Value("${primoia.log.base-url:http://localhost:8000}") String baseUrl) {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.restTemplate = new RestTemplate();
    }
    
    public void sendLog(String level, String message, Map<String, Object> context) {
        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "Bearer " + apiKey);
        headers.setContentType(MediaType.APPLICATION_JSON);
        
        Map<String, Object> logData = new HashMap<>();
        logData.put("service_name", "meu-servico");
        logData.put("service_type", "meu-servico");
        logData.put("service_version", "1.0.0");
        logData.put("service_instance_id", "instancia-001");
        logData.put("level", level);
        logData.put("message", message);
        logData.put("environment", "dev");
        logData.putAll(context);
        
        HttpEntity<Map<String, Object>> request = new HttpEntity<>(logData, headers);
        
        restTemplate.postForEntity(
            baseUrl + "/api/v1/ingestion/logs/single",
            request,
            String.class
        );
    }
}

// Uso
@Autowired
private PrimoiaLogClient logClient;

public void exemplo() {
    Map<String, Object> context = new HashMap<>();
    context.put("user_id", "12345");
    context.put("endpoint", "/api/v1/users");
    
    logClient.sendLog("INFO", "Usuário criado com sucesso", context);
}
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

class PrimoiaLogClient {
    constructor(apiKey, baseUrl = 'http://localhost:8000') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async sendLog(level, message, context = {}) {
        const logData = {
            service_name: 'meu-servico',
            service_type: 'meu-servico',
            service_version: '1.0.0',
            service_instance_id: 'instancia-001',
            level,
            message,
            environment: 'dev',
            timestamp: new Date().toISOString(),
            ...context
        };
        
        try {
            const response = await axios.post(
                `${this.baseUrl}/api/v1/ingestion/logs/single`,
                logData,
                { headers: this.headers }
            );
            return response.data;
        } catch (error) {
            console.error('Erro ao enviar log:', error.message);
            throw error;
        }
    }
}

// Uso
const logClient = new PrimoiaLogClient('minha-api-key-2024');
logClient.sendLog('INFO', 'Serviço iniciado', { port: 3000 });
```

## 📦 Envio em Lote

Para otimizar performance, envie múltiplos logs de uma vez:

```bash
curl -X POST "http://localhost:8000/api/v1/ingestion/logs/batch" \
  -H "Authorization: Bearer minha-api-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "batch-001",
    "service_name": "meu-servico",
    "service_type": "meu-servico",
    "service_version": "1.0.0",
    "service_instance_id": "instancia-001",
    "logs": [
      {
        "level": "INFO",
        "message": "Log 1",
        "environment": "dev"
      },
      {
        "level": "WARNING",
        "message": "Log 2",
        "environment": "dev"
      }
    ]
  }'
```

## 🔍 Monitoramento e Estatísticas

### Verificar Estatísticas do Serviço

```bash
curl -H "Authorization: Bearer minha-api-key-2024" \
  "http://localhost:8000/api/v1/ingestion/stats"
```

### Verificar Estatísticas Globais

```bash
curl "http://localhost:8000/api/v1/stats/global"
```

### Verificar Top Serviços

```bash
curl "http://localhost:8000/api/v1/stats/top-services?limit=10"
```

## 🛠️ Configuração por Ambiente

### Desenvolvimento

```bash
# URL do Log-Watcher
PRIMOIA_LOG_URL=http://localhost:8000
PRIMOIA_LOG_API_KEY=minha-api-key-dev
```

### Produção

```bash
# URL do Log-Watcher
PRIMOIA_LOG_URL=https://logs.primoia.com
PRIMOIA_LOG_API_KEY=minha-api-key-prod
```

## 🔐 Segurança

### Rate Limiting

Cada serviço tem um limite de logs por minuto configurado na API key. Exemplo:
- `nex-web-backend`: 1000 logs/min
- `nex-mobile-backend`: 500 logs/min
- `auth-service`: 200 logs/min

### Autenticação

- Use sempre HTTPS em produção
- Mantenha as API keys seguras
- Rotacione as chaves periodicamente
- Use variáveis de ambiente para armazenar as chaves

## 🐛 Troubleshooting

### Erro 403 - Not Authenticated
```bash
# Verificar se a API key está correta
curl -H "Authorization: Bearer minha-api-key-2024" \
  "http://localhost:8000/api/v1/ingestion/stats"
```

### Erro 400 - Invalid Log Format
```bash
# Verificar se todos os campos obrigatórios estão presentes
# Verificar se o formato JSON está correto
```

### Erro 429 - Rate Limit Exceeded
```bash
# Reduzir frequência de envio de logs
# Implementar retry com backoff exponencial
```

### Logs não aparecem
```bash
# Verificar conectividade com o Log-Watcher
curl http://localhost:8000/health

# Verificar logs do serviço
docker logs primoia-log-watcher
```

## 📊 Exemplos de Uso por Tipo de Serviço

### API REST (Spring Boot/Kotlin)

```java
@RestController
public class UserController {
    
    @PostMapping("/api/v1/users")
    public ResponseEntity<User> createUser(@RequestBody User user) {
        try {
            User created = userService.create(user);
            logClient.sendLog("INFO", "Usuário criado", Map.of(
                "user_id", created.getId(),
                "endpoint", "/api/v1/users",
                "http_method", "POST",
                "status_code", 201
            ));
            return ResponseEntity.status(201).body(created);
        } catch (Exception e) {
            logClient.sendLog("ERROR", "Erro ao criar usuário", Map.of(
                "exception_type", e.getClass().getSimpleName(),
                "exception_message", e.getMessage(),
                "endpoint", "/api/v1/users",
                "http_method", "POST",
                "status_code", 500
            ));
            throw e;
        }
    }
}
```

### Frontend (React/Vue)

```javascript
// Interceptor para logs de requisições
axios.interceptors.request.use(config => {
    logClient.sendLog('INFO', 'Requisição iniciada', {
        endpoint: config.url,
        method: config.method,
        request_id: generateRequestId()
    });
    return config;
});

axios.interceptors.response.use(
    response => {
        logClient.sendLog('INFO', 'Requisição bem-sucedida', {
            endpoint: response.config.url,
            method: response.config.method,
            status_code: response.status,
            response_time_ms: response.headers['x-response-time']
        });
        return response;
    },
    error => {
        logClient.sendLog('ERROR', 'Erro na requisição', {
            endpoint: error.config?.url,
            method: error.config?.method,
            status_code: error.response?.status,
            error_message: error.message
        });
        throw error;
    }
);
```

### Background Jobs (Celery/Quartz)

```python
@celery.task
def process_user_data(user_id):
    try:
        log_client.send_log("INFO", "Iniciando processamento de dados", {
            "user_id": user_id,
            "job_type": "user_data_processing"
        })
        
        # Processamento...
        result = process_data(user_id)
        
        log_client.send_log("INFO", "Processamento concluído", {
            "user_id": user_id,
            "job_type": "user_data_processing",
            "execution_time_ms": get_execution_time()
        })
        
        return result
    except Exception as e:
        log_client.send_log("ERROR", "Erro no processamento", {
            "user_id": user_id,
            "job_type": "user_data_processing",
            "exception_type": type(e).__name__,
            "exception_message": str(e)
        })
        raise
```

## 🎯 Próximos Passos

1. **Implementar cliente** no seu serviço usando um dos exemplos acima
2. **Configurar variáveis de ambiente** com a API key
3. **Testar integração** enviando logs de teste
4. **Monitorar estatísticas** para verificar se os logs estão chegando
5. **Implementar logs estruturados** com contexto relevante

## 📞 Suporte

- **Documentação da API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Issues**: Abra uma issue no repositório do projeto

---

**Status**: ✅ **Pronto para Integração** - Seu serviço pode começar a enviar logs agora!
