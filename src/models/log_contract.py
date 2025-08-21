"""
Contrato de Log Padronizado para o Ecossistema Primoia

Este módulo define o formato padronizado para envio de logs de todos os serviços
do ecossistema Primoia para o primoia-log-watcher.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class LogLevel(str, Enum):
    """Níveis de log padronizados"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ServiceType(str, Enum):
    """Tipos de serviços do ecossistema Primoia"""
    AUTH_SERVICE = "auth-service"
    NEX_MOBILE_BACKEND = "nex-mobile-backend"
    NEX_WEB_BACKEND = "nex-web-backend"
    NEX_WEB = "nex-web"
    CLOUD_MANAGER = "cloud-manager"
    CONDUCTOR = "conductor"
    BROWSE_USE = "browse-use"
    EMAIL_SERVICE = "email-service"
    EVENT_SERVICE = "event-service"
    MIGRATION_CONTROLLER = "migration-controller"
    ALERTS = "alerts"
    ECOMMERCE = "ecommerce"
    OTHER = "other"


class LogEntry(BaseModel):
    """
    Entrada de log padronizada para o ecossistema Primoia
    
    Todos os serviços devem enviar logs neste formato para garantir
    consistência e facilitar a análise automatizada.
    """
    
    # Identificação do serviço
    service_name: str = Field(..., description="Nome do serviço que está enviando o log")
    service_type: ServiceType = Field(..., description="Tipo do serviço no ecossistema")
    service_version: str = Field(..., description="Versão do serviço")
    service_instance_id: str = Field(..., description="ID único da instância do serviço")
    
    # Informações do log
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp UTC do log")
    level: LogLevel = Field(..., description="Nível de severidade do log")
    message: str = Field(..., description="Mensagem principal do log")
    
    # Contexto adicional
    logger_name: Optional[str] = Field(None, description="Nome do logger (ex: 'com.nex.web.controller')")
    thread_name: Optional[str] = Field(None, description="Nome da thread que gerou o log")
    
    # Dados estruturados
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto adicional do log")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags para categorização")
    
    # Informações de erro (quando aplicável)
    exception_type: Optional[str] = Field(None, description="Tipo da exceção (se houver)")
    exception_message: Optional[str] = Field(None, description="Mensagem da exceção")
    stack_trace: Optional[str] = Field(None, description="Stack trace completo")
    
    # Metadados de performance
    execution_time_ms: Optional[float] = Field(None, description="Tempo de execução em milissegundos")
    memory_usage_mb: Optional[float] = Field(None, description="Uso de memória em MB")
    
    # Informações de requisição (para logs de API)
    request_id: Optional[str] = Field(None, description="ID único da requisição")
    user_id: Optional[str] = Field(None, description="ID do usuário (quando aplicável)")
    endpoint: Optional[str] = Field(None, description="Endpoint da API (ex: '/api/v1/users')")
    http_method: Optional[str] = Field(None, description="Método HTTP (GET, POST, etc.)")
    status_code: Optional[int] = Field(None, description="Código de status HTTP")
    
    # Informações de ambiente
    environment: str = Field(..., description="Ambiente (dev, staging, prod)")
    host: Optional[str] = Field(None, description="Hostname da máquina")
    ip_address: Optional[str] = Field(None, description="Endereço IP da máquina")
    
    @validator('timestamp', pre=True)
    def ensure_utc_timestamp(cls, v):
        """Garante que o timestamp seja UTC"""
        if isinstance(v, str):
            # Se for string, assume que já está em UTC
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        elif isinstance(v, datetime):
            # Se for datetime, assume que já está em UTC
            return v
        return v
    
    @validator('context')
    def validate_context(cls, v):
        """Valida que o contexto não seja muito grande"""
        if v and len(str(v)) > 10000:  # 10KB limite
            raise ValueError("Context too large (max 10KB)")
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para serialização"""
        return self.dict()
    
    def get_summary(self) -> str:
        """Retorna um resumo do log para análise rápida"""
        return f"[{self.level}] {self.service_name}: {self.message}"


class LogBatch(BaseModel):
    """
    Lote de logs para envio em massa
    
    Permite que serviços enviem múltiplos logs de uma vez para otimizar
    a performance da API de ingestão.
    """
    
    batch_id: str = Field(..., description="ID único do lote")
    service_name: str = Field(..., description="Nome do serviço que está enviando o lote")
    service_type: ServiceType = Field(..., description="Tipo do serviço")
    service_version: str = Field(..., description="Versão do serviço")
    service_instance_id: str = Field(..., description="ID único da instância do serviço")
    
    logs: List[LogEntry] = Field(..., description="Lista de logs no lote")
    
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de criação do lote")
    
    @validator('logs')
    def validate_logs(cls, v):
        """Valida que o lote não seja muito grande"""
        if len(v) > 1000:  # Máximo 1000 logs por lote
            raise ValueError("Batch too large (max 1000 logs)")
        return v
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna um resumo do lote"""
        level_counts = {}
        for log in self.logs:
            level_counts[log.level] = level_counts.get(log.level, 0) + 1
        
        return {
            "batch_id": self.batch_id,
            "service_name": self.service_name,
            "total_logs": len(self.logs),
            "level_distribution": level_counts,
            "timestamp": self.timestamp.isoformat()
        }


# Exemplos de uso
EXAMPLE_LOG_ENTRY = LogEntry(
    service_name="nex-web-backend",
    service_type=ServiceType.NEX_WEB_BACKEND,
    service_version="1.2.3",
    service_instance_id="web-backend-001",
    level=LogLevel.ERROR,
    message="Failed to process user request",
    logger_name="com.nex.web.controller.UserController",
    context={
        "user_id": "12345",
        "request_data": {"email": "user@example.com"}
    },
    tags=["api", "user", "error"],
    exception_type="ValidationException",
    exception_message="Invalid email format",
    request_id="req-abc-123",
    user_id="12345",
    endpoint="/api/v1/users",
    http_method="POST",
    status_code=400,
    environment="dev",
    host="web-backend-001",
    ip_address="192.168.1.100"
)

EXAMPLE_LOG_BATCH = LogBatch(
    batch_id="batch-xyz-789",
    service_name="nex-web-backend",
    service_type=ServiceType.NEX_WEB_BACKEND,
    service_version="1.2.3",
    service_instance_id="web-backend-001",
    logs=[EXAMPLE_LOG_ENTRY]
)
