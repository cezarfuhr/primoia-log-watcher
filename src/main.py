"""
Aplicação Principal do Primoia Log-Watcher

Hub de Diagnóstico Centralizado para o ecossistema Primoia.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.ingestion import router as ingestion_router
from .services.auth_service import AuthService
from .services.queue_service import QueueService
from .services.metrics_service import MetricsService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Serviços globais
auth_service = AuthService()
queue_service = QueueService()
metrics_service = MetricsService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    logger.info("Starting Primoia Log-Watcher...")
    
    # Verificar se os serviços estão funcionando
    try:
        auth_status = await auth_service.get_status()
        queue_status = await queue_service.get_status()
        
        logger.info(f"Auth service status: {auth_status['status']}")
        logger.info(f"Queue service status: {queue_status['status']}")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    
    logger.info("Primoia Log-Watcher started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Primoia Log-Watcher...")


# Criar aplicação FastAPI
app = FastAPI(
    title="Primoia Log-Watcher",
    description="Hub de Diagnóstico Centralizado para o ecossistema Primoia",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(ingestion_router)


@app.get("/", response_model=Dict[str, Any])
async def root():
    """
    Endpoint raiz com informações sobre o serviço
    """
    return {
        "service": "Primoia Log-Watcher",
        "version": "1.0.0",
        "description": "Hub de Diagnóstico Centralizado para o ecossistema Primoia",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "ingestion": "/api/v1/ingestion"
        }
    }


@app.get("/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check geral da aplicação
    """
    try:
        # Verificar status dos serviços
        auth_status = await auth_service.get_status()
        queue_status = await queue_service.get_status()
        
        # Verificar se todos os serviços estão saudáveis
        all_healthy = (
            auth_status.get("status") == "healthy" and
            queue_status.get("status") == "healthy"
        )
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": auth_status.get("timestamp"),
            "services": {
                "auth": auth_status,
                "queue": queue_status
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/api/v1/stats/global", response_model=Dict[str, Any])
async def get_global_stats():
    """
    Endpoint para obter estatísticas globais do sistema
    """
    try:
        stats = await metrics_service.get_global_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting global stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


@app.get("/api/v1/stats/top-services", response_model=Dict[str, Any])
async def get_top_services(limit: int = 10):
    """
    Endpoint para obter os serviços mais ativos
    """
    try:
        if limit < 1 or limit > 100:
            raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
        
        top_services = await metrics_service.get_top_services(limit)
        
        return {
            "top_services": top_services,
            "limit": limit,
            "total_services": len(top_services)
        }
        
    except Exception as e:
        logger.error(f"Error getting top services: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving top services")


@app.get("/api/v1/admin/services", response_model=Dict[str, Any])
async def list_services():
    """
    Endpoint administrativo para listar todos os serviços registrados
    """
    try:
        services = auth_service.list_services()
        
        return {
            "services": services,
            "total_services": len(services),
            "active_services": len([s for s in services if s["is_active"]])
        }
        
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        raise HTTPException(status_code=500, detail="Error listing services")


@app.post("/api/v1/admin/services", response_model=Dict[str, Any])
async def add_service(
    service_name: str,
    service_type: str,
    api_key: str,
    rate_limit: int = 100
):
    """
    Endpoint administrativo para adicionar um novo serviço
    """
    try:
        success = auth_service.add_service(
            service_name=service_name,
            service_type=service_type,
            api_key=api_key,
            rate_limit=rate_limit
        )
        
        if success:
            return {
                "status": "success",
                "message": f"Service {service_name} added successfully",
                "service_name": service_name,
                "api_key": api_key
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to add service")
            
    except Exception as e:
        logger.error(f"Error adding service: {e}")
        raise HTTPException(status_code=500, detail="Error adding service")


@app.delete("/api/v1/admin/services/{service_name}", response_model=Dict[str, Any])
async def remove_service(service_name: str):
    """
    Endpoint administrativo para remover um serviço
    """
    try:
        success = auth_service.remove_service(service_name)
        
        if success:
            return {
                "status": "success",
                "message": f"Service {service_name} removed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Service not found")
            
    except Exception as e:
        logger.error(f"Error removing service: {e}")
        raise HTTPException(status_code=500, detail="Error removing service")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para exceções não tratadas
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
