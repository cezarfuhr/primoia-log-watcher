#!/bin/bash

# Script de entrada para testes do Primoia Log-Watcher em Docker

echo "🚀 Iniciando testes do Primoia Log-Watcher..."

# Aguardar o serviço principal estar pronto
echo "⏳ Aguardando o serviço principal estar pronto..."
until python -c "
import requests
import time
try:
    response = requests.get('$LOG_WATCHER_URL/health', timeout=5)
    if response.status_code == 200:
        print('✅ Serviço está pronto!')
        exit(0)
    else:
        print('❌ Serviço retornou status:', response.status_code)
        exit(1)
except Exception as e:
    print('⏳ Aguardando...', e)
    exit(1)
" 2>/dev/null; do
    echo "⏳ Aguardando o serviço estar pronto..."
    sleep 5
done

echo "✅ Serviço principal está pronto!"

# Executar os testes
echo "🧪 Executando testes..."
python send_logs_example.py

echo "🎉 Testes concluídos!"
