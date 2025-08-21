"""
Serviço de Métricas para o Primoia Log-Watcher

Coleta e gerencia métricas de ingestão e processamento de logs.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Serviço de métricas para coletar estatísticas de ingestão e processamento
    
    Em produção, isso seria integrado com Prometheus, Grafana ou similar.
    Por enquanto, usamos uma implementação em memória para demonstração.
    """
    
    def __init__(self):
        # Métricas de ingestão por serviço
        self._service_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_logs": 0,
            "logs_by_level": Counter(),
            "logs_by_hour": defaultdict(int),
            "total_size_bytes": 0,
            "last_ingestion": None,
            "first_ingestion": None
        })
        
        # Métricas de processamento
        self._processing_metrics = {
            "total_processed": 0,
            "total_failed": 0,
            "processing_times": [],
            "errors_by_type": Counter()
        }
        
        # Métricas de performance
        self._performance_metrics = {
            "avg_processing_time_ms": 0,
            "max_processing_time_ms": 0,
            "min_processing_time_ms": float('inf'),
            "total_processing_time_ms": 0
        }
        
        logger.info("Metrics service initialized")
    
    async def record_log_ingestion(self, service_name: str, service_type: str, 
                                 log_level: str, log_size: int) -> None:
        """
        Registra a ingestão de um log individual
        
        Args:
            service_name: Nome do serviço
            service_type: Tipo do serviço
            log_level: Nível do log
            log_size: Tamanho do log em bytes
        """
        try:
            now = datetime.utcnow()
            hour_key = now.strftime("%Y-%m-%d %H:00")
            
            # Atualizar métricas do serviço
            service_metrics = self._service_metrics[service_name]
            service_metrics["total_logs"] += 1
            service_metrics["logs_by_level"][log_level] += 1
            service_metrics["logs_by_hour"][hour_key] += 1
            service_metrics["total_size_bytes"] += log_size
            service_metrics["last_ingestion"] = now.isoformat()
            
            if service_metrics["first_ingestion"] is None:
                service_metrics["first_ingestion"] = now.isoformat()
            
            logger.debug(f"Recorded log ingestion: {service_name} - {log_level}")
            
        except Exception as e:
            logger.error(f"Error recording log ingestion: {e}")
    
    async def record_batch_ingestion(self, service_name: str, service_type: str,
                                   batch_size: int, batch_id: str) -> None:
        """
        Registra a ingestão de um lote de logs
        
        Args:
            service_name: Nome do serviço
            service_type: Tipo do serviço
            batch_size: Tamanho do lote
            batch_id: ID do lote
        """
        try:
            now = datetime.utcnow()
            hour_key = now.strftime("%Y-%m-%d %H:00")
            
            # Atualizar métricas do serviço
            service_metrics = self._service_metrics[service_name]
            service_metrics["total_logs"] += batch_size
            service_metrics["logs_by_hour"][hour_key] += batch_size
            service_metrics["last_ingestion"] = now.isoformat()
            
            if service_metrics["first_ingestion"] is None:
                service_metrics["first_ingestion"] = now.isoformat()
            
            logger.debug(f"Recorded batch ingestion: {service_name} - {batch_size} logs")
            
        except Exception as e:
            logger.error(f"Error recording batch ingestion: {e}")
    
    async def record_processing_success(self, processing_time_ms: float) -> None:
        """
        Registra o processamento bem-sucedido de um log
        
        Args:
            processing_time_ms: Tempo de processamento em milissegundos
        """
        try:
            self._processing_metrics["total_processed"] += 1
            self._processing_metrics["processing_times"].append(processing_time_ms)
            
            # Atualizar métricas de performance
            perf_metrics = self._performance_metrics
            perf_metrics["total_processing_time_ms"] += processing_time_ms
            perf_metrics["max_processing_time_ms"] = max(
                perf_metrics["max_processing_time_ms"], 
                processing_time_ms
            )
            perf_metrics["min_processing_time_ms"] = min(
                perf_metrics["min_processing_time_ms"], 
                processing_time_ms
            )
            
            # Calcular média
            total_processed = self._processing_metrics["total_processed"]
            if total_processed > 0:
                perf_metrics["avg_processing_time_ms"] = (
                    perf_metrics["total_processing_time_ms"] / total_processed
                )
            
            logger.debug(f"Recorded processing success: {processing_time_ms}ms")
            
        except Exception as e:
            logger.error(f"Error recording processing success: {e}")
    
    async def record_processing_error(self, error_type: str, error_message: str) -> None:
        """
        Registra um erro de processamento
        
        Args:
            error_type: Tipo do erro
            error_message: Mensagem do erro
        """
        try:
            self._processing_metrics["total_failed"] += 1
            self._processing_metrics["errors_by_type"][error_type] += 1
            
            logger.debug(f"Recorded processing error: {error_type}")
            
        except Exception as e:
            logger.error(f"Error recording processing error: {e}")
    
    async def get_service_stats(self, service_name: str) -> Dict[str, Any]:
        """
        Retorna estatísticas de um serviço específico
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Dict com estatísticas do serviço
        """
        try:
            service_metrics = self._service_metrics.get(service_name, {})
            
            if not service_metrics:
                return {
                    "service_name": service_name,
                    "total_logs": 0,
                    "message": "No data available for this service"
                }
            
            # Calcular estatísticas por nível
            level_stats = dict(service_metrics["logs_by_level"])
            
            # Calcular estatísticas por hora (últimas 24 horas)
            now = datetime.utcnow()
            hourly_stats = {}
            for i in range(24):
                hour = now - timedelta(hours=i)
                hour_key = hour.strftime("%Y-%m-%d %H:00")
                hourly_stats[hour_key] = service_metrics["logs_by_hour"].get(hour_key, 0)
            
            # Calcular taxa de ingestão (logs por hora)
            total_logs = service_metrics["total_logs"]
            if service_metrics["first_ingestion"]:
                first_ingestion = datetime.fromisoformat(service_metrics["first_ingestion"])
                hours_since_first = (now - first_ingestion).total_seconds() / 3600
                ingestion_rate = total_logs / max(hours_since_first, 1)
            else:
                ingestion_rate = 0
            
            return {
                "service_name": service_name,
                "total_logs": total_logs,
                "total_size_bytes": service_metrics["total_size_bytes"],
                "logs_by_level": level_stats,
                "hourly_distribution": dict(hourly_stats),
                "ingestion_rate_logs_per_hour": round(ingestion_rate, 2),
                "first_ingestion": service_metrics["first_ingestion"],
                "last_ingestion": service_metrics["last_ingestion"],
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {
                "service_name": service_name,
                "error": str(e)
            }
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas globais do sistema
        
        Returns:
            Dict com estatísticas globais
        """
        try:
            now = datetime.utcnow()
            
            # Calcular totais
            total_services = len(self._service_metrics)
            total_logs = sum(metrics["total_logs"] for metrics in self._service_metrics.values())
            total_size = sum(metrics["total_size_bytes"] for metrics in self._service_metrics.values())
            
            # Calcular distribuição por nível
            global_level_stats = Counter()
            for service_metrics in self._service_metrics.values():
                global_level_stats.update(service_metrics["logs_by_level"])
            
            # Calcular distribuição por serviço
            service_distribution = {
                service_name: metrics["total_logs"]
                for service_name, metrics in self._service_metrics.items()
            }
            
            # Calcular métricas de processamento
            processing_success_rate = 0
            if self._processing_metrics["total_processed"] + self._processing_metrics["total_failed"] > 0:
                processing_success_rate = (
                    self._processing_metrics["total_processed"] /
                    (self._processing_metrics["total_processed"] + self._processing_metrics["total_failed"])
                ) * 100
            
            return {
                "total_services": total_services,
                "total_logs": total_logs,
                "total_size_bytes": total_size,
                "logs_by_level": dict(global_level_stats),
                "service_distribution": service_distribution,
                "processing": {
                    "total_processed": self._processing_metrics["total_processed"],
                    "total_failed": self._processing_metrics["total_failed"],
                    "success_rate_percent": round(processing_success_rate, 2),
                    "errors_by_type": dict(self._processing_metrics["errors_by_type"])
                },
                "performance": {
                    "avg_processing_time_ms": round(self._performance_metrics["avg_processing_time_ms"], 2),
                    "max_processing_time_ms": self._performance_metrics["max_processing_time_ms"],
                    "min_processing_time_ms": (
                        self._performance_metrics["min_processing_time_ms"] 
                        if self._performance_metrics["min_processing_time_ms"] != float('inf') 
                        else 0
                    )
                },
                "timestamp": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting global stats: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_top_services(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna os serviços com mais logs
        
        Args:
            limit: Número máximo de serviços a retornar
            
        Returns:
            Lista dos serviços mais ativos
        """
        try:
            # Ordenar serviços por número de logs
            sorted_services = sorted(
                self._service_metrics.items(),
                key=lambda x: x[1]["total_logs"],
                reverse=True
            )
            
            top_services = []
            for service_name, metrics in sorted_services[:limit]:
                top_services.append({
                    "service_name": service_name,
                    "total_logs": metrics["total_logs"],
                    "total_size_bytes": metrics["total_size_bytes"],
                    "last_ingestion": metrics["last_ingestion"]
                })
            
            return top_services
            
        except Exception as e:
            logger.error(f"Error getting top services: {e}")
            return []
    
    async def clear_old_metrics(self, days_to_keep: int = 30) -> int:
        """
        Limpa métricas antigas para economizar memória
        
        Args:
            days_to_keep: Número de dias de métricas para manter
            
        Returns:
            Número de entradas removidas
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            cutoff_hour = cutoff_date.strftime("%Y-%m-%d %H:00")
            
            removed_count = 0
            
            for service_metrics in self._service_metrics.values():
                # Remover entradas antigas por hora
                old_hours = [
                    hour for hour in service_metrics["logs_by_hour"].keys()
                    if hour < cutoff_hour
                ]
                
                for hour in old_hours:
                    del service_metrics["logs_by_hour"][hour]
                    removed_count += 1
            
            logger.info(f"Cleared {removed_count} old metric entries")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error clearing old metrics: {e}")
            return 0
