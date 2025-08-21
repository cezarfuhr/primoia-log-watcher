"""
API de Ingestão para o Primoia Log-Watcher

Este módulo implementa os endpoints para receber logs de todos os serviços
do ecossistema Primoia, validar o formato e enviar para processamento.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError

from ..models.log_contract import LogEntry, LogBatch, LogLevel, ServiceType
from ..services.auth_service import AuthService
from ..services.queue_service import QueueService
from ..services.metrics_service import MetricsService

# Configuração de logging
logger = logging.getLogger(__name__)

# Router para endpoints de ingestão
router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])

# Dependências
security = HTTPBearer()
auth_service = AuthService()
queue_service = QueueService()
metrics_service = MetricsService()


@router.post("/logs/single", response_model=Dict[str, Any])
async def ingest_single_log(
    log_entry: LogEntry,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint para ingestão de um único log
    
    Recebe um log individual de qualquer serviço do ecossistema Primoia,
    valida o formato e envia para processamento.
    """
    try:
        # Validar autenticação
        api_key = credentials.credentials
        service_info = await auth_service.validate_api_key(api_key)
        
        # Validar que o serviço está autorizado a enviar logs
        if not auth_service.is_service_authorized(service_info["service_name"]):
            raise HTTPException(
                status_code=403,
                detail="Service not authorized to send logs"
            )
        
        # Validar consistência dos dados do serviço
        if log_entry.service_name != service_info["service_name"]:
            raise HTTPException(
                status_code=400,
                detail="Service name mismatch with API key"
            )
        
        # Gerar ID único para o log
        log_id = str(uuid.uuid4())
        
        # Preparar dados para processamento
        processing_data = {
            "log_id": log_id,
            "log_entry": log_entry.dict(),
            "service_info": service_info,
            "received_at": datetime.utcnow().isoformat()
        }
        
        # Enviar para processamento em background
        background_tasks.add_task(
            queue_service.enqueue_log_processing,
            processing_data
        )
        
        # Registrar métricas
        background_tasks.add_task(
            metrics_service.record_log_ingestion,
            service_name=log_entry.service_name,
            service_type=log_entry.service_type,
            log_level=log_entry.level,
            log_size=len(str(log_entry.dict()))
        )
        
        logger.info(f"Log ingested successfully: {log_id} from {log_entry.service_name}")
        
        return {
            "status": "success",
            "log_id": log_id,
            "message": "Log ingested and queued for processing",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid log format: {str(e)}")
    except Exception as e:
        logger.error(f"Error ingesting log: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/logs/batch", response_model=Dict[str, Any])
async def ingest_log_batch(
    log_batch: LogBatch,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint para ingestão de lote de logs
    
    Recebe múltiplos logs de uma vez para otimizar a performance
    da API de ingestão.
    """
    try:
        # Validar autenticação
        api_key = credentials.credentials
        service_info = await auth_service.validate_api_key(api_key)
        
        # Validar que o serviço está autorizado
        if not auth_service.is_service_authorized(service_info["service_name"]):
            raise HTTPException(
                status_code=403,
                detail="Service not authorized to send logs"
            )
        
        # Validar consistência dos dados do serviço
        if log_batch.service_name != service_info["service_name"]:
            raise HTTPException(
                status_code=400,
                detail="Service name mismatch with API key"
            )
        
        # Validar que todos os logs no lote são do mesmo serviço
        for log_entry in log_batch.logs:
            if log_entry.service_name != log_batch.service_name:
                raise HTTPException(
                    status_code=400,
                    detail="All logs in batch must be from the same service"
                )
        
        # Gerar IDs únicos para cada log
        log_ids = []
        processing_data_list = []
        
        for log_entry in log_batch.logs:
            log_id = str(uuid.uuid4())
            log_ids.append(log_id)
            
            processing_data = {
                "log_id": log_id,
                "log_entry": log_entry.dict(),
                "service_info": service_info,
                "batch_id": log_batch.batch_id,
                "received_at": datetime.utcnow().isoformat()
            }
            processing_data_list.append(processing_data)
        
        # Enviar todos os logs para processamento em background
        background_tasks.add_task(
            queue_service.enqueue_batch_processing,
            processing_data_list
        )
        
        # Registrar métricas do lote
        background_tasks.add_task(
            metrics_service.record_batch_ingestion,
            service_name=log_batch.service_name,
            service_type=log_batch.service_type,
            batch_size=len(log_batch.logs),
            batch_id=log_batch.batch_id
        )
        
        logger.info(f"Batch ingested successfully: {log_batch.batch_id} with {len(log_ids)} logs from {log_batch.service_name}")
        
        return {
            "status": "success",
            "batch_id": log_batch.batch_id,
            "log_ids": log_ids,
            "total_logs": len(log_ids),
            "message": "Log batch ingested and queued for processing",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid batch format: {str(e)}")
    except Exception as e:
        logger.error(f"Error ingesting batch: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Endpoint de health check para a API de ingestão
    """
    try:
        # Verificar conectividade com serviços dependentes
        queue_status = await queue_service.get_status()
        auth_status = await auth_service.get_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "queue": queue_status,
                "auth": auth_status
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/stats", response_model=Dict[str, Any])
async def get_ingestion_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Endpoint para obter estatísticas de ingestão do serviço
    """
    try:
        # Validar autenticação
        api_key = credentials.credentials
        service_info = await auth_service.validate_api_key(api_key)
        
        # Obter estatísticas do serviço
        stats = await metrics_service.get_service_stats(service_info["service_name"])
        
        return {
            "service_name": service_info["service_name"],
            "stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
