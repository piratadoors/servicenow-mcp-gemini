# Troubleshooting e Soluções Aplicadas

Este documento registra os problemas encontrados e as soluções aplicadas durante o desenvolvimento e teste do `servicenow-mcp-gemini`.

## 1. Problema: `AttributeError` ou `KeyError` devido à Ordem Incorreta de Parâmetros

### Sintoma

Funções de ferramentas (ex: `create_change_request`) falham com `AttributeError` (ex: `'AuthManager' object has no attribute 'api_url'`) ou retornam `{"success": False}` inesperadamente quando os parâmetros `auth_manager` e `server_config` são passados em ordem trocada durante os testes.

### Causa Raiz

As funções de ferramentas estavam acessando diretamente os atributos de `auth_manager` e `server_config` sem uma maneira robusta de identificar qual objeto era qual, caso a ordem fosse invertida. Funções auxiliares como `_get_instance_url` e `_get_headers` tentavam mitigar isso, mas não eram uma solução completa.

### Solução Aplicada

A função `_get_auth_and_config` (originalmente em `workflow_tools.py`) foi identificada como a solução padrão para este problema. Ela inspeciona os objetos passados e retorna `auth_manager` e `server_config` na ordem correta.

**Passos para a Correção:**

1.  **Importar a função:** Em cada arquivo de `tools` afetado, importar a função:
    ```python
    from servicenow_mcp.tools.workflow_tools import _get_auth_and_config
    ```

2.  **Aplicar no início da função da ferramenta:** No início de cada função de ferramenta que recebe `auth_manager` e `server_config`, adicionar o seguinte bloco:
    ```python
    try:
        auth_manager, server_config = _get_auth_and_config(auth_manager, server_config)
    except ValueError as e:
        logger.error(f"Error getting auth and config: {e}")
        return {
            "success": False,
            "message": f"Error getting auth and config: {str(e)}",
        }
    ```

3.  **Remover chamadas antigas:** Substituir as chamadas a `_get_instance_url` e `_get_headers` pelo uso direto dos objetos `server_config.instance_url` e `auth_manager.get_headers()`.

Esta abordagem centraliza a lógica de tratamento de parâmetros e torna as ferramentas mais robustas.
