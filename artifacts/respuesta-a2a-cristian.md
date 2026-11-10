# Evidencia A2A · Agente Cristian

Esta respuesta valida que el agente A2A de Cristian recibió un mensaje y devolvió una respuesta mediante JSON-RPC.

## Consulta enviada

```powershell
$ctx = [guid]::NewGuid().ToString()
$cuerpo = @{ jsonrpc="2.0"; id="1"; method="message/send"; params=@{ message=@{ role="user"; messageId="m1"; contextId=$ctx; parts=@(@{ kind="text"; text="¿Qué sitios puedo visitar en Lima?" }) } } } | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8004/ -ContentType "application/json" -Headers @{accept="utf-8"} -Body ([System.Text.Encoding]::UTF8.GetBytes($cuerpo)) | ConvertTo-Json -Depth 10
```

## Respuesta recibida

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "contextId": "b3afe73d-bdd8-45b1-9f8d-e009ab37b710",
    "kind": "message",
    "messageId": "68692e67-af12-41d6-a206-ef4279bdbd7e",
    "parts": [
      {
        "kind": "text",
        "text": "Puedes visitar el Centro Histórico de Lima, la Huaca Pucllana y el Malecón de Miraflores."
      }
    ],
    "role": "agent"
  }
}
```

La respuesta confirma que el servidor A2A está funcionando en `http://127.0.0.1:8004`.
