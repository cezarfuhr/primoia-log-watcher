# Visão: Primoia Log-Watcher como Hub de Diagnóstico Centralizado

Este documento detalha a visão expandida para o projeto `primoia-log-watcher`, transformando-o no centro de observabilidade e diagnóstico proativo de todo o ecossistema Primoia.

## 1. Propósito e Valor

O `primoia-log-watcher` transcende sua função inicial de simples monitor de logs para se tornar o **cérebro operacional** do ecossistema. Ele coletará logs de todos os serviços, aplicando inteligência artificial para:

*   **Reduzir Ruído:** Agrupar eventos similares e eliminar redundâncias.
*   **Detectar Anomalias:** Identificar padrões incomuns que sinalizam problemas emergentes.
*   **Sugerir Diagnósticos:** Usar IA para analisar o contexto dos logs e propor causas-raiz para falhas.
*   **Monitoramento Proativo:** Alertar sobre problemas antes que afetem os usuários ou a performance.

## 2. Fluxo de Dados e Integração no Ecossistema

Todos os componentes do ecossistema Primoia (aplicativos mobile, frontends web, backends, serviços do `primoia-browse-use`, e o próprio `conductor`) serão configurados para enviar seus logs para o `primoia-log-watcher`.

```
+-------------------+     Logs/Eventos     +-------------------------+
|  Serviço Primoia  | -------------------> |  API de Ingestão        |
| (Mobile, Web, BE, |                      |  (primoia-log-watcher)  |
|  Conductor, etc.) | <------------------- |                         |
+-------------------+   Insights/Alertas   +-------------------------+
                                                    |
                                                    v
                                          +-------------------------+
                                          |  Fila de Mensagens      |
                                          +-------------------------+
                                                    |
                                                    v
                                          +-------------------------+
                                          |  Workers de Análise (IA)|
                                          +-------------------------+
                                                    |
                                                    v
                                          +-------------------------+
                                          |  Banco de Dados         |
                                          +-------------------------+
                                                    |
                                                    v
                                          +-------------------------+
                                          |  Frontend de Diagnóstico|
                                          +-------------------------+
```

## 3. Próximos Passos para Implementação

Se este for o próximo foco de desenvolvimento, os passos iniciais seriam:

1.  **Definir o Contrato de Log:** Padronizar o formato e o protocolo para o envio de logs de todos os serviços para o `primoia-log-watcher`.
2.  **Implementar a API de Ingestão:** Desenvolver o endpoint que receberá os logs dos demais serviços.
3.  **Integrar um Serviço Piloto:** Escolher um serviço existente (ex: `conductor_gateway` ou um dos serviços do `primoia-browse-use`) para configurar o envio de seus logs para o `primoia-log-watcher`.
4.  **Desenvolver o Módulo de IA Inicial:** Começar com a lógica de IA para agrupamento de logs e detecção de anomalias básicas.

Esta visão transforma o `primoia-log-watcher` em um componente ativo e vital para a saúde e a manutenibilidade de todo o ecossistema Primoia.
