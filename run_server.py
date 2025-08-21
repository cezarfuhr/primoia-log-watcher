#!/usr/bin/env python3
"""
Script para executar o servidor do Primoia Log-Watcher

Este script inicia o servidor FastAPI do hub de diagnóstico centralizado.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Adicionar o diretório src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Função principal para executar o servidor"""
    
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print("🚀 Iniciando Primoia Log-Watcher...")
    print(f"📡 Servidor: {host}:{port}")
    print(f"🔄 Reload: {reload}")
    print(f"📝 Log Level: {log_level}")
    print("=" * 50)
    
    # Executar o servidor
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True
    )

if __name__ == "__main__":
    main()
