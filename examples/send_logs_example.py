#!/usr/bin/env python3
"""
Exemplo de como enviar logs para o Primoia Log-Watcher

Este script demonstra como os serviços do ecossistema Primoia podem
enviar logs para o hub de diagnóstico centralizado.
"""

import asyncio
import httpx
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Configurações
LOG_WATCHER_URL = "http://localhost:8000"
API_KEY = "nex-web-backend-key-2024"  # Exemplo de API key


class LogSender:
    """
    Cliente para enviar logs para o Primoia Log-Watcher
    """
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_single_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia um log individual
        
        Args:
            log_data: Dados do log no formato padronizado
            
        Returns:
            Resposta da API
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ingestion/logs/single",
                headers=self.headers,
                json=log_data
            )
            response.raise_for_status()
            return response.json()
    
    async def send_log_batch(self, batch_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envia um lote de logs
        
        Args:
            batch_data: Dados do lote no formato padronizado
            
        Returns:
            Resposta da API
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/ingestion/logs/batch",
                headers=self.headers,
                json=batch_data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do serviço
        
        Returns:
            Estatísticas do serviço
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/ingestion/stats",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()


def create_sample_log(
    service_name: str,
    level: str,
    message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Cria um log de exemplo no formato padronizado
    
    Args:
        service_name: Nome do serviço
        level: Nível do log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        message: Mensagem do log
        **kwargs: Campos adicionais do log
        
    Returns:
        Log no formato padronizado
    """
    log = {
        "service_name": service_name,
        "service_type": service_name,
        "service_version": "1.0.0",
        "service_instance_id": f"{service_name}-{uuid.uuid4().hex[:8]}",
        "timestamp": datetime.utcnow().isoformat(),
        "level": level,
        "message": message,
        "environment": "dev",
        "host": "localhost",
        "ip_address": "127.0.0.1"
    }
    
    # Adicionar campos opcionais
    log.update(kwargs)
    
    return log


async def example_single_logs():
    """
    Exemplo de envio de logs individuais
    """
    print("=== Exemplo: Envio de Logs Individuais ===")
    
    sender = LogSender(LOG_WATCHER_URL, API_KEY)
    
    # Log de informação
    info_log = create_sample_log(
        service_name="nex-web-backend",
        level="INFO",
        message="User login successful",
        logger_name="com.nex.web.controller.AuthController",
        context={
            "user_id": "12345",
            "email": "user@example.com"
        },
        tags=["auth", "login", "success"],
        request_id="req-abc-123",
        user_id="12345",
        endpoint="/api/v1/auth/login",
        http_method="POST",
        status_code=200,
        execution_time_ms=45.2
    )
    
    # Log de erro
    error_log = create_sample_log(
        service_name="nex-web-backend",
        level="ERROR",
        message="Database connection failed",
        logger_name="com.nex.web.repository.UserRepository",
        context={
            "database": "postgresql",
            "connection_pool": "main"
        },
        tags=["database", "connection", "error"],
        exception_type="ConnectionException",
        exception_message="Connection timeout after 30 seconds",
        stack_trace="java.sql.SQLException: Connection timeout...",
        request_id="req-def-456",
        endpoint="/api/v1/users",
        http_method="GET",
        status_code=500,
        execution_time_ms=30000.0
    )
    
    # Log de warning
    warning_log = create_sample_log(
        service_name="nex-web-backend",
        level="WARNING",
        message="High memory usage detected",
        logger_name="com.nex.web.monitoring.MemoryMonitor",
        context={
            "memory_usage_percent": 85.5,
            "heap_size_mb": 2048,
            "free_memory_mb": 300
        },
        tags=["monitoring", "memory", "warning"],
        memory_usage_mb=1748.0
    )
    
    # Enviar logs
    logs_to_send = [info_log, error_log, warning_log]
    
    for i, log in enumerate(logs_to_send, 1):
        try:
            result = await sender.send_single_log(log)
            print(f"Log {i} enviado com sucesso: {result['log_id']}")
        except Exception as e:
            print(f"Erro ao enviar log {i}: {e}")


async def example_batch_logs():
    """
    Exemplo de envio de lote de logs
    """
    print("\n=== Exemplo: Envio de Lote de Logs ===")
    
    sender = LogSender(LOG_WATCHER_URL, API_KEY)
    
    # Criar múltiplos logs para o lote
    batch_logs = []
    
    for i in range(5):
        log = create_sample_log(
            service_name="nex-web-backend",
            level="INFO",
            message=f"Processing request {i+1}",
            logger_name="com.nex.web.controller.RequestController",
            context={
                "request_number": i+1,
                "batch_id": "batch-001"
            },
            tags=["request", "processing"],
            request_id=f"req-{i+1:03d}",
            endpoint="/api/v1/process",
            http_method="POST",
            status_code=200,
            execution_time_ms=float(i * 10 + 50)
        )
        batch_logs.append(log)
    
    # Criar lote
    batch_data = {
        "batch_id": f"batch-{uuid.uuid4().hex[:8]}",
        "service_name": "nex-web-backend",
        "service_type": "nex-web-backend",
        "service_version": "1.0.0",
        "service_instance_id": "web-backend-001",
        "logs": batch_logs,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        result = await sender.send_log_batch(batch_data)
        print(f"Lote enviado com sucesso: {result['batch_id']}")
        print(f"Total de logs no lote: {result['total_logs']}")
        print(f"IDs dos logs: {result['log_ids']}")
    except Exception as e:
        print(f"Erro ao enviar lote: {e}")


async def example_get_stats():
    """
    Exemplo de obtenção de estatísticas
    """
    print("\n=== Exemplo: Obtenção de Estatísticas ===")
    
    sender = LogSender(LOG_WATCHER_URL, API_KEY)
    
    try:
        stats = await sender.get_stats()
        print("Estatísticas do serviço:")
        print(json.dumps(stats, indent=2, default=str))
    except Exception as e:
        print(f"Erro ao obter estatísticas: {e}")


async def example_simulate_service_activity():
    """
    Simula atividade de um serviço enviando logs em intervalos
    """
    print("\n=== Exemplo: Simulação de Atividade de Serviço ===")
    
    sender = LogSender(LOG_WATCHER_URL, API_KEY)
    
    # Simular diferentes tipos de logs que um serviço real enviaria
    log_templates = [
        {
            "level": "INFO",
            "message": "Request processed successfully",
            "tags": ["request", "success"]
        },
        {
            "level": "DEBUG",
            "message": "Database query executed",
            "tags": ["database", "query"]
        },
        {
            "level": "WARNING",
            "message": "Cache miss - fetching from database",
            "tags": ["cache", "performance"]
        },
        {
            "level": "ERROR",
            "message": "External API call failed",
            "tags": ["api", "external", "error"]
        }
    ]
    
    for i in range(3):  # Simular 3 ciclos de logs
        print(f"\nCiclo {i+1}:")
        
        for template in log_templates:
            log = create_sample_log(
                service_name="nex-web-backend",
                level=template["level"],
                message=f"{template['message']} (cycle {i+1})",
                logger_name="com.nex.web.service.SimulationService",
                context={
                    "cycle": i+1,
                    "template": template["message"]
                },
                tags=template["tags"] + [f"cycle-{i+1}"],
                request_id=f"sim-req-{i+1}-{template['level'].lower()}",
                execution_time_ms=float(i * 5 + 20)
            )
            
            try:
                result = await sender.send_single_log(log)
                print(f"  ✓ {template['level']}: {result['log_id']}")
            except Exception as e:
                print(f"  ✗ {template['level']}: {e}")
            
            # Pequena pausa entre logs
            await asyncio.sleep(0.5)


async def main():
    """
    Função principal que executa todos os exemplos
    """
    print("🚀 Iniciando exemplos do Primoia Log-Watcher")
    print(f"📡 Conectando em: {LOG_WATCHER_URL}")
    print(f"🔑 Usando API Key: {API_KEY}")
    
    try:
        # Verificar se o serviço está rodando
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{LOG_WATCHER_URL}/health")
            if response.status_code == 200:
                print("✅ Serviço está rodando!")
            else:
                print("❌ Serviço não está respondendo corretamente")
                return
    except Exception as e:
        print(f"❌ Não foi possível conectar ao serviço: {e}")
        print("Certifique-se de que o Primoia Log-Watcher está rodando em http://localhost:8000")
        return
    
    # Executar exemplos
    await example_single_logs()
    await example_batch_logs()
    await example_get_stats()
    await example_simulate_service_activity()
    
    print("\n🎉 Exemplos concluídos!")
    print("📊 Acesse http://localhost:8000/docs para ver a documentação da API")
    print("📈 Acesse http://localhost:8000/api/v1/stats/global para ver estatísticas globais")


if __name__ == "__main__":
    asyncio.run(main())
