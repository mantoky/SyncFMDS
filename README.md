# SyncFMDS

Repositorio oficial do front-end FMDS com conector VPS versionado.

## Escopo versionado
- `fmds_v5_completo.html`
- `index.html`
- configuracao Firebase Hosting (`firebase.json`, `.firebaserc`)
- runtime config (`firebase.runtime-config.js`)
- conector e automacao (`vps_connector.py`, `run_vps_sync.ps1`, `inmet_proxy.py`)
- payload VPS (`data/vps/**`)

## Deploy
`firebase deploy --only hosting --project syncfmds`
