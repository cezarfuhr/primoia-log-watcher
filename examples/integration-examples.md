# 🔗 Exemplos de Integração - Serviços Primoia

Este documento contém exemplos práticos de como integrar serviços específicos do ecossistema Primoia com o Log-Watcher.

## 📋 Serviços do Ecossistema

### 1. nex-web-backend (Spring Boot/Kotlin)

#### Configuração no `application.yml`

```yaml
primoia:
  log:
    enabled: true
    api-key: ${PRIMOIA_LOG_API_KEY:nex-web-backend-key-2024}
    base-url: ${PRIMOIA_LOG_URL:http://localhost:8000}
    service-name: nex-web-backend
    service-type: nex-web-backend
    service-version: ${APP_VERSION:1.0.0}
    service-instance-id: ${HOSTNAME:web-backend-001}
```

#### Cliente de Log

```kotlin
@Component
class PrimoiaLogClient(
    @Value("\${primoia.log.api-key}") private val apiKey: String,
    @Value("\${primoia.log.base-url}") private val baseUrl: String,
    @Value("\${primoia.log.service-name}") private val serviceName: String,
    @Value("\${primoia.log.service-type}") private val serviceType: String,
    @Value("\${primoia.log.service-version}") private val serviceVersion: String,
    @Value("\${primoia.log.service-instance-id}") private val serviceInstanceId: String
) {
    private val restTemplate = RestTemplate()
    
    fun sendLog(level: String, message: String, context: Map<String, Any> = emptyMap()) {
        val logData = mapOf(
            "service_name" to serviceName,
            "service_type" to serviceType,
            "service_version" to serviceVersion,
            "service_instance_id" to serviceInstanceId,
            "level" to level,
            "message" to message,
            "environment" to (System.getenv("SPRING_PROFILES_ACTIVE") ?: "dev"),
            "timestamp" to Instant.now().toString(),
            "host" to InetAddress.getLocalHost().hostName,
            "ip_address" to InetAddress.getLocalHost().hostAddress
        ) + context
        
        val headers = HttpHeaders().apply {
            set("Authorization", "Bearer $apiKey")
            contentType = MediaType.APPLICATION_JSON
        }
        
        val request = HttpEntity(logData, headers)
        
        try {
            restTemplate.postForEntity("$baseUrl/api/v1/ingestion/logs/single", request, String::class.java)
        } catch (e: Exception) {
            // Log local em caso de falha
            println("Erro ao enviar log para Primoia: ${e.message}")
        }
    }
}
```

#### Uso em Controllers

```kotlin
@RestController
@RequestMapping("/api/v1/users")
class UserController(
    private val userService: UserService,
    private val logClient: PrimoiaLogClient
) {
    
    @PostMapping
    fun createUser(@RequestBody user: User): ResponseEntity<User> {
        val startTime = System.currentTimeMillis()
        
        try {
            val createdUser = userService.create(user)
            
            logClient.sendLog("INFO", "Usuário criado com sucesso", mapOf(
                "user_id" to createdUser.id,
                "endpoint" to "/api/v1/users",
                "http_method" to "POST",
                "status_code" to 201,
                "execution_time_ms" to (System.currentTimeMillis() - startTime)
            ))
            
            return ResponseEntity.status(201).body(createdUser)
        } catch (e: Exception) {
            logClient.sendLog("ERROR", "Erro ao criar usuário", mapOf(
                "exception_type" to e.javaClass.simpleName,
                "exception_message" to e.message,
                "endpoint" to "/api/v1/users",
                "http_method" to "POST",
                "status_code" to 500,
                "execution_time_ms" to (System.currentTimeMillis() - startTime)
            ))
            throw e
        }
    }
}
```

### 2. nex-mobile-backend (Spring Boot)

#### Interceptor para Logs Automáticos

```java
@Component
public class PrimoiaLogInterceptor implements HandlerInterceptor {
    
    @Autowired
    private PrimoiaLogClient logClient;
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        request.setAttribute("startTime", System.currentTimeMillis());
        request.setAttribute("requestId", UUID.randomUUID().toString());
        
        logClient.sendLog("INFO", "Requisição iniciada", Map.of(
            "request_id", request.getAttribute("requestId"),
            "endpoint", request.getRequestURI(),
            "http_method", request.getMethod(),
            "user_agent", request.getHeader("User-Agent"),
            "ip_address", getClientIpAddress(request)
        ));
        
        return true;
    }
    
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        long startTime = (Long) request.getAttribute("startTime");
        String requestId = (String) request.getAttribute("requestId");
        long executionTime = System.currentTimeMillis() - startTime;
        
        Map<String, Object> context = Map.of(
            "request_id", requestId,
            "endpoint", request.getRequestURI(),
            "http_method", request.getMethod(),
            "status_code", response.getStatus(),
            "execution_time_ms", executionTime
        );
        
        if (ex != null) {
            context.put("exception_type", ex.getClass().getSimpleName());
            context.put("exception_message", ex.getMessage());
            logClient.sendLog("ERROR", "Erro na requisição", context);
        } else {
            logClient.sendLog("INFO", "Requisição concluída", context);
        }
    }
}
```

### 3. auth-service (Spring Boot)

#### Logs de Autenticação

```java
@Service
public class AuthenticationService {
    
    @Autowired
    private PrimoiaLogClient logClient;
    
    public AuthenticationResult authenticate(String username, String password) {
        try {
            // Lógica de autenticação...
            AuthenticationResult result = performAuthentication(username, password);
            
            logClient.sendLog("INFO", "Autenticação bem-sucedida", Map.of(
                "username", username,
                "auth_method", "password",
                "success", true,
                "session_id", result.getSessionId()
            ));
            
            return result;
        } catch (AuthenticationException e) {
            logClient.sendLog("WARNING", "Tentativa de autenticação falhou", Map.of(
                "username", username,
                "auth_method", "password",
                "success", false,
                "failure_reason", e.getMessage(),
                "ip_address", getCurrentIpAddress()
            ));
            throw e;
        }
    }
    
    public void logout(String sessionId) {
        logClient.sendLog("INFO", "Usuário fez logout", Map.of(
            "session_id", sessionId,
            "logout_method", "explicit"
        ));
    }
}
```

### 4. conductor (Python)

#### Cliente Python

```python
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class PrimoiaLogClient:
    def __init__(self):
        self.api_key = os.getenv("PRIMOIA_LOG_API_KEY", "conductor-key-2024")
        self.base_url = os.getenv("PRIMOIA_LOG_URL", "http://localhost:8000")
        self.service_name = "conductor"
        self.service_type = "conductor"
        self.service_version = os.getenv("CONDUCTOR_VERSION", "1.0.0")
        self.service_instance_id = os.getenv("HOSTNAME", "conductor-001")
        
    def send_log(self, level: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Envia um log para o Primoia Log-Watcher"""
        if context is None:
            context = {}
            
        log_data = {
            "service_name": self.service_name,
            "service_type": self.service_type,
            "service_version": self.service_version,
            "service_instance_id": self.service_instance_id,
            "level": level,
            "message": message,
            "environment": os.getenv("ENVIRONMENT", "dev"),
            "timestamp": datetime.utcnow().isoformat(),
            **context
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ingestion/logs/single",
                headers=headers,
                json=log_data,
                timeout=5
            )
            response.raise_for_status()
        except Exception as e:
            # Log local em caso de falha
            print(f"Erro ao enviar log para Primoia: {e}")

# Instância global
log_client = PrimoiaLogClient()

# Decorator para logs automáticos
def log_function_call(func):
    def wrapper(*args, **kwargs):
        try:
            log_client.send_log("INFO", f"Iniciando execução: {func.__name__}", {
                "function_name": func.__name__,
                "args_count": len(args),
                "kwargs_count": len(kwargs)
            })
            
            result = func(*args, **kwargs)
            
            log_client.send_log("INFO", f"Execução concluída: {func.__name__}", {
                "function_name": func.__name__,
                "success": True
            })
            
            return result
        except Exception as e:
            log_client.send_log("ERROR", f"Erro na execução: {func.__name__}", {
                "function_name": func.__name__,
                "exception_type": type(e).__name__,
                "exception_message": str(e)
            })
            raise
    
    return wrapper

# Uso
@log_function_call
def process_task(task_id: str):
    # Lógica do processamento...
    pass
```

### 5. nex-web (React/TypeScript)

#### Cliente JavaScript

```typescript
class PrimoiaLogClient {
    private apiKey: string;
    private baseUrl: string;
    private serviceName: string;
    
    constructor() {
        this.apiKey = process.env.REACT_APP_PRIMOIA_LOG_API_KEY || 'nex-web-key-2024';
        this.baseUrl = process.env.REACT_APP_PRIMOIA_LOG_URL || 'http://localhost:8000';
        this.serviceName = 'nex-web';
    }
    
    async sendLog(level: string, message: string, context: Record<string, any> = {}) {
        const logData = {
            service_name: this.serviceName,
            service_type: this.serviceName,
            service_version: process.env.REACT_APP_VERSION || '1.0.0',
            service_instance_id: 'web-client',
            level,
            message,
            environment: process.env.NODE_ENV || 'development',
            timestamp: new Date().toISOString(),
            ...context
        };
        
        try {
            await fetch(`${this.baseUrl}/api/v1/ingestion/logs/single`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(logData)
            });
        } catch (error) {
            console.error('Erro ao enviar log:', error);
        }
    }
}

// Instância global
const logClient = new PrimoiaLogClient();

// Interceptor para requisições HTTP
axios.interceptors.request.use(config => {
    logClient.sendLog('INFO', 'Requisição iniciada', {
        url: config.url,
        method: config.method,
        request_id: generateRequestId()
    });
    return config;
});

axios.interceptors.response.use(
    response => {
        logClient.sendLog('INFO', 'Requisição bem-sucedida', {
            url: response.config.url,
            method: response.config.method,
            status: response.status,
            response_time_ms: response.headers['x-response-time']
        });
        return response;
    },
    error => {
        logClient.sendLog('ERROR', 'Erro na requisição', {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            error_message: error.message
        });
        throw error;
    }
);

// Logs de eventos do usuário
export const logUserAction = (action: string, context: Record<string, any> = {}) => {
    logClient.sendLog('INFO', `Ação do usuário: ${action}`, {
        user_action: action,
        user_id: getCurrentUserId(),
        ...context
    });
};
```

## 🔧 Configuração de Ambiente

### Variáveis de Ambiente Comuns

```bash
# Configuração do Log-Watcher
PRIMOIA_LOG_URL=http://localhost:8000
PRIMOIA_LOG_API_KEY=minha-api-key-2024

# Configuração do serviço
SERVICE_NAME=meu-servico
SERVICE_VERSION=1.0.0
SERVICE_INSTANCE_ID=instancia-001
ENVIRONMENT=dev
```

### Docker Compose com Log-Watcher

```yaml
version: '3.8'
services:
  primoia-log-watcher:
    image: primoia-log-watcher:latest
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
  
  meu-servico:
    build: .
    environment:
      - PRIMOIA_LOG_URL=http://primoia-log-watcher:8000
      - PRIMOIA_LOG_API_KEY=minha-api-key-2024
    depends_on:
      - primoia-log-watcher
```

## 📊 Monitoramento

### Verificar Integração

```bash
# Verificar se o serviço está enviando logs
curl -H "Authorization: Bearer minha-api-key-2024" \
  "http://localhost:8000/api/v1/ingestion/stats"

# Verificar logs em tempo real
docker logs -f primoia-log-watcher

# Verificar estatísticas globais
curl "http://localhost:8000/api/v1/stats/global"
```

### Alertas e Dashboards

- **Logs de Erro**: Monitorar logs com nível ERROR
- **Performance**: Acompanhar `execution_time_ms`
- **Taxa de Erro**: Calcular % de logs ERROR vs total
- **Endpoints Problemáticos**: Identificar endpoints com mais erros

## 🎯 Próximos Passos

1. **Implementar cliente** no seu serviço usando um dos exemplos acima
2. **Configurar variáveis de ambiente** com a API key correta
3. **Testar integração** enviando logs de teste
4. **Monitorar métricas** para verificar se os logs estão chegando
5. **Implementar logs estruturados** com contexto relevante para seu serviço

---

**Status**: ✅ **Exemplos Práticos** - Prontos para implementação nos serviços do ecossistema!
