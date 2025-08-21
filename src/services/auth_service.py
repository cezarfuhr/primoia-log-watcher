"""
Serviço de Autenticação para o Primoia Log-Watcher

Gerencia a autenticação e autorização dos serviços que enviam logs
para o sistema.
"""

import logging
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ServiceInfo:
    """Informações de um serviço autorizado"""
    service_name: str
    service_type: str
    api_key_hash: str
    created_at: datetime
    is_active: bool
    permissions: List[str]
    rate_limit: int  # logs por minuto


class AuthService:
    """
    Serviço de autenticação para validar API keys dos serviços
    do ecossistema Primoia.
    """
    
    def __init__(self):
        # Em produção, isso viria de um banco de dados
        # Por enquanto, usamos um dicionário em memória
        self._authorized_services: Dict[str, ServiceInfo] = {}
        self._api_key_to_service: Dict[str, str] = {}
        
        # Inicializar com alguns serviços de exemplo
        self._initialize_default_services()
    
    def _initialize_default_services(self):
        """Inicializa com serviços padrão do ecossistema Primoia"""
        default_services = [
            {
                "service_name": "nex-web-backend",
                "service_type": "nex-web-backend",
                "api_key": "nex-web-backend-key-2024",
                "permissions": ["send_logs", "read_stats"],
                "rate_limit": 1000
            },
            {
                "service_name": "nex-mobile-backend", 
                "service_type": "nex-mobile-backend",
                "api_key": "nex-mobile-backend-key-2024",
                "permissions": ["send_logs", "read_stats"],
                "rate_limit": 500
            },
            {
                "service_name": "auth-service",
                "service_type": "auth-service", 
                "api_key": "auth-service-key-2024",
                "permissions": ["send_logs", "read_stats"],
                "rate_limit": 200
            },
            {
                "service_name": "conductor",
                "service_type": "conductor",
                "api_key": "conductor-key-2024", 
                "permissions": ["send_logs", "read_stats"],
                "rate_limit": 300
            }
        ]
        
        for service_data in default_services:
            self._register_service(
                service_name=service_data["service_name"],
                service_type=service_data["service_type"],
                api_key=service_data["api_key"],
                permissions=service_data["permissions"],
                rate_limit=service_data["rate_limit"]
            )
    
    def _register_service(self, service_name: str, service_type: str, 
                         api_key: str, permissions: List[str], rate_limit: int):
        """Registra um novo serviço no sistema"""
        api_key_hash = self._hash_api_key(api_key)
        
        service_info = ServiceInfo(
            service_name=service_name,
            service_type=service_type,
            api_key_hash=api_key_hash,
            created_at=datetime.utcnow(),
            is_active=True,
            permissions=permissions,
            rate_limit=rate_limit
        )
        
        self._authorized_services[service_name] = service_info
        self._api_key_to_service[api_key] = service_name
        
        logger.info(f"Registered service: {service_name}")
    
    def _hash_api_key(self, api_key: str) -> str:
        """Gera hash da API key para armazenamento seguro"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    async def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Valida uma API key e retorna informações do serviço
        
        Args:
            api_key: A API key fornecida pelo serviço
            
        Returns:
            Dict com informações do serviço se a key for válida
            
        Raises:
            ValueError: Se a API key for inválida
        """
        if not api_key:
            raise ValueError("API key is required")
        
        # Verificar se a API key existe
        service_name = self._api_key_to_service.get(api_key)
        if not service_name:
            raise ValueError("Invalid API key")
        
        # Obter informações do serviço
        service_info = self._authorized_services.get(service_name)
        if not service_info:
            raise ValueError("Service not found")
        
        # Verificar se o serviço está ativo
        if not service_info.is_active:
            raise ValueError("Service is inactive")
        
        # Verificar rate limit (implementação básica)
        if not self._check_rate_limit(service_name):
            raise ValueError("Rate limit exceeded")
        
        logger.debug(f"Validated API key for service: {service_name}")
        
        return {
            "service_name": service_info.service_name,
            "service_type": service_info.service_type,
            "permissions": service_info.permissions,
            "rate_limit": service_info.rate_limit,
            "created_at": service_info.created_at.isoformat()
        }
    
    def is_service_authorized(self, service_name: str) -> bool:
        """
        Verifica se um serviço está autorizado a enviar logs
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            True se o serviço estiver autorizado
        """
        service_info = self._authorized_services.get(service_name)
        return service_info is not None and service_info.is_active
    
    def _check_rate_limit(self, service_name: str) -> bool:
        """
        Verifica se o serviço não excedeu o rate limit
        
        Implementação básica - em produção seria mais sofisticada
        com Redis ou similar para tracking em tempo real.
        """
        # Por enquanto, sempre retorna True
        # TODO: Implementar rate limiting real
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Retorna o status do serviço de autenticação"""
        return {
            "status": "healthy",
            "total_services": len(self._authorized_services),
            "active_services": len([s for s in self._authorized_services.values() if s.is_active]),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def add_service(self, service_name: str, service_type: str, 
                   api_key: str, permissions: List[str] = None, 
                   rate_limit: int = 100) -> bool:
        """
        Adiciona um novo serviço ao sistema
        
        Args:
            service_name: Nome do serviço
            service_type: Tipo do serviço
            api_key: API key para o serviço
            permissions: Lista de permissões
            rate_limit: Limite de logs por minuto
            
        Returns:
            True se o serviço foi adicionado com sucesso
        """
        try:
            if permissions is None:
                permissions = ["send_logs", "read_stats"]
            
            self._register_service(
                service_name=service_name,
                service_type=service_type,
                api_key=api_key,
                permissions=permissions,
                rate_limit=rate_limit
            )
            
            logger.info(f"Added new service: {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding service {service_name}: {e}")
            return False
    
    def remove_service(self, service_name: str) -> bool:
        """
        Remove um serviço do sistema
        
        Args:
            service_name: Nome do serviço a ser removido
            
        Returns:
            True se o serviço foi removido com sucesso
        """
        try:
            if service_name in self._authorized_services:
                service_info = self._authorized_services[service_name]
                
                # Remover da lista de serviços autorizados
                del self._authorized_services[service_name]
                
                # Remover da lista de API keys
                for api_key, name in list(self._api_key_to_service.items()):
                    if name == service_name:
                        del self._api_key_to_service[api_key]
                
                logger.info(f"Removed service: {service_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error removing service {service_name}: {e}")
            return False
    
    def list_services(self) -> List[Dict[str, Any]]:
        """
        Lista todos os serviços registrados
        
        Returns:
            Lista com informações de todos os serviços
        """
        services = []
        for service_name, service_info in self._authorized_services.items():
            services.append({
                "service_name": service_name,
                "service_type": service_info.service_type,
                "is_active": service_info.is_active,
                "permissions": service_info.permissions,
                "rate_limit": service_info.rate_limit,
                "created_at": service_info.created_at.isoformat()
            })
        
        return services
