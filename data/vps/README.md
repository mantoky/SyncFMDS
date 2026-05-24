# VPS Payload - Conector e Rollback

## Objetivo
- Extrair dados do banco externo.
- Gerar payload unico (`vps_payload_latest.json`) para a UI.
- Manter versoes para rollback rapido.

## Estrutura
- `vps_payload_latest.json`: payload ativo consumido pela UI.
- `versions/*.json`: historico versionado por data/hora.
- `index.json`: catalogo das versoes para rollback.
- `schema_vps_payload.json`: contrato do payload.
- `template_catalog.json`: mapa fixo de template/tipo por bloco (anti-resistencia do time).
- `vps_external_query.sql`: query padrao para banco externo.

## Geracao (conector)
### Origem JSON
`python vps_connector.py --input-json caminho\\origem.json --out-dir data\\vps`

### Origem SQLite
`python vps_connector.py --sqlite-db caminho\\base.db --sqlite-query "SELECT * FROM vw_vps_payload" --out-dir data\\vps`

### Origem SQL Server (banco externo)
1. Defina a variavel de ambiente:
`setx VPS_SQLSERVER_CONN "Driver={ODBC Driver 17 for SQL Server};Server=...;Database=...;UID=...;PWD=...;TrustServerCertificate=yes;"`
2. Rode:
`python vps_connector.py --out-dir data\\vps --sqlserver-query-file data\\vps\\vps_external_query.sql`

### Sync operacional (atalho)
`powershell -ExecutionPolicy Bypass -File .\\run_vps_sync.ps1`

### Origem Firebase / Firestore (REST)
`python vps_connector.py --out-dir data\\vps --firestore-project-id syncfmds --firestore-api-key SUA_API_KEY --firestore-collection vps_payload_blocks`

Tambem funciona por variavel de ambiente:
- `VPS_FIRESTORE_PROJECT_ID`
- `VPS_FIRESTORE_API_KEY`
- `VPS_FIRESTORE_COLLECTION`

### Rollback rapido (CLI)
`python vps_connector.py --out-dir data\\vps --rollback-version vps_YYYYMMDD_HHMMSS`

## Regra de render na UI
- A guia `VPS Vale` renderiza por:
  - `order`
  - `tipo_bloco`
- `template` e metadados ficam fixos.
- `data` representa conteudo variavel.
