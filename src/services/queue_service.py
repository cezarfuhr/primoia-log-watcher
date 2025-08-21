"""
Serviço de Fila para o Primoia Log-Watcher

Gerencia o processamento assíncrono dos logs através de filas de mensagens.
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class QueueMessage:
    """Estrutura de uma mensagem na fila"""
    message_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3


class QueueService:
    """
    Serviço de fila para processamento assíncrono dos logs
    
    Em produção, isso seria implementado com Redis, RabbitMQ ou NATS.
    Por enquanto, usamos uma implementação em memória para demonstração.
    """
    
    def __init__(self):
        # Filas em memória (em produção seriam Redis/RabbitMQ)
        self._log_processing_queue: List[QueueMessage] = []
        self._batch_processing_queue: List[QueueMessage] = []
        self._failed_messages: List[QueueMessage] = []
        
        # Contadores para métricas
        self._total_messages_processed = 0
        self._total_messages_failed = 0
        self._queue_sizes = {
            "log_processing": 0,
            "batch_processing": 0,
            "failed": 0
        }
        
        logger.info("Queue service initialized")
    
    async def enqueue_log_processing(self, processing_data: Dict[str, Any]) -> bool:
        """
        Adiciona um log individual à fila de processamento
        
        Args:
            processing_data: Dados do log para processamento
            
        Returns:
            True se a mensagem foi adicionada com sucesso
        """
        try:
            message = QueueMessage(
                message_id=f"log_{processing_data['log_id']}",
                message_type="log_processing",
                payload=processing_data,
                timestamp=datetime.utcnow()
            )
            
            self._log_processing_queue.append(message)
            self._queue_sizes["log_processing"] = len(self._log_processing_queue)
            
            logger.debug(f"Enqueued log for processing: {processing_data['log_id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error enqueueing log: {e}")
            return False
    
    async def enqueue_batch_processing(self, processing_data_list: List[Dict[str, Any]]) -> bool:
        """
        Adiciona um lote de logs à fila de processamento
        
        Args:
            processing_data_list: Lista de dados dos logs para processamento
            
        Returns:
            True se o lote foi adicionado com sucesso
        """
        try:
            message = QueueMessage(
                message_id=f"batch_{datetime.utcnow().timestamp()}",
                message_type="batch_processing",
                payload={
                    "batch_data": processing_data_list,
                    "batch_size": len(processing_data_list)
                },
                timestamp=datetime.utcnow()
            )
            
            self._batch_processing_queue.append(message)
            self._queue_sizes["batch_processing"] = len(self._batch_processing_queue)
            
            logger.debug(f"Enqueued batch for processing: {len(processing_data_list)} logs")
            return True
            
        except Exception as e:
            logger.error(f"Error enqueueing batch: {e}")
            return False
    
    async def dequeue_log_processing(self) -> Optional[QueueMessage]:
        """
        Remove e retorna a próxima mensagem da fila de processamento de logs
        
        Returns:
            Próxima mensagem ou None se a fila estiver vazia
        """
        if not self._log_processing_queue:
            return None
        
        message = self._log_processing_queue.pop(0)
        self._queue_sizes["log_processing"] = len(self._log_processing_queue)
        
        logger.debug(f"Dequeued log message: {message.message_id}")
        return message
    
    async def dequeue_batch_processing(self) -> Optional[QueueMessage]:
        """
        Remove e retorna a próxima mensagem da fila de processamento de lotes
        
        Returns:
            Próxima mensagem ou None se a fila estiver vazia
        """
        if not self._batch_processing_queue:
            return None
        
        message = self._batch_processing_queue.pop(0)
        self._queue_sizes["batch_processing"] = len(self._batch_processing_queue)
        
        logger.debug(f"Dequeued batch message: {message.message_id}")
        return message
    
    async def mark_message_processed(self, message: QueueMessage) -> None:
        """
        Marca uma mensagem como processada com sucesso
        
        Args:
            message: A mensagem que foi processada
        """
        self._total_messages_processed += 1
        logger.debug(f"Marked message as processed: {message.message_id}")
    
    async def mark_message_failed(self, message: QueueMessage, error: str) -> None:
        """
        Marca uma mensagem como falhada e a move para a fila de falhas
        
        Args:
            message: A mensagem que falhou
            error: Descrição do erro
        """
        message.retry_count += 1
        
        if message.retry_count >= message.max_retries:
            # Máximo de tentativas atingido, mover para fila de falhas
            message.payload["final_error"] = error
            self._failed_messages.append(message)
            self._queue_sizes["failed"] = len(self._failed_messages)
            self._total_messages_failed += 1
            
            logger.error(f"Message failed permanently: {message.message_id}, error: {error}")
        else:
            # Recolocar na fila para nova tentativa
            if message.message_type == "log_processing":
                self._log_processing_queue.append(message)
                self._queue_sizes["log_processing"] = len(self._log_processing_queue)
            else:
                self._batch_processing_queue.append(message)
                self._queue_sizes["batch_processing"] = len(self._batch_processing_queue)
            
            logger.warning(f"Message retry {message.retry_count}/{message.max_retries}: {message.message_id}")
    
    async def get_queue_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das filas
        
        Returns:
            Dict com estatísticas das filas
        """
        return {
            "log_processing_queue_size": len(self._log_processing_queue),
            "batch_processing_queue_size": len(self._batch_processing_queue),
            "failed_messages_size": len(self._failed_messages),
            "total_messages_processed": self._total_messages_processed,
            "total_messages_failed": self._total_messages_failed,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status do serviço de fila
        
        Returns:
            Dict com status do serviço
        """
        stats = await self.get_queue_stats()
        
        return {
            "status": "healthy",
            "queues": {
                "log_processing": {
                    "size": stats["log_processing_queue_size"],
                    "status": "active"
                },
                "batch_processing": {
                    "size": stats["batch_processing_queue_size"],
                    "status": "active"
                },
                "failed": {
                    "size": stats["failed_messages_size"],
                    "status": "active"
                }
            },
            "metrics": {
                "total_processed": stats["total_messages_processed"],
                "total_failed": stats["total_messages_failed"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def clear_failed_messages(self) -> int:
        """
        Limpa a fila de mensagens falhadas
        
        Returns:
            Número de mensagens removidas
        """
        count = len(self._failed_messages)
        self._failed_messages.clear()
        self._queue_sizes["failed"] = 0
        
        logger.info(f"Cleared {count} failed messages")
        return count
    
    async def retry_failed_messages(self) -> int:
        """
        Tenta reprocessar mensagens falhadas
        
        Returns:
            Número de mensagens reprocessadas
        """
        retried_count = 0
        
        for message in self._failed_messages[:]:  # Cópia da lista para iteração segura
            # Reset retry count
            message.retry_count = 0
            
            # Mover de volta para a fila apropriada
            if message.message_type == "log_processing":
                self._log_processing_queue.append(message)
                self._queue_sizes["log_processing"] = len(self._log_processing_queue)
            else:
                self._batch_processing_queue.append(message)
                self._queue_sizes["batch_processing"] = len(self._batch_processing_queue)
            
            # Remover da fila de falhas
            self._failed_messages.remove(message)
            retried_count += 1
        
        self._queue_sizes["failed"] = len(self._failed_messages)
        
        logger.info(f"Retried {retried_count} failed messages")
        return retried_count
    
    def get_queue_size(self, queue_name: str) -> int:
        """
        Retorna o tamanho de uma fila específica
        
        Args:
            queue_name: Nome da fila
            
        Returns:
            Tamanho da fila
        """
        if queue_name == "log_processing":
            return len(self._log_processing_queue)
        elif queue_name == "batch_processing":
            return len(self._batch_processing_queue)
        elif queue_name == "failed":
            return len(self._failed_messages)
        else:
            return 0
