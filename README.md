# SyncFMDS

Repositorio oficial do front-end FMDS com conector VPS versionado.

## Escopo versionado
- `fmds_v5_completo.html`
- `index.html`
- configuracao Firebase Hosting (`firebase.json`, `.firebaserc`)
- configuracao Netlify (`netlify.toml`)
- runtime config (`firebase.runtime-config.js`)
- conector e automacao (`vps_connector.py`, `run_vps_sync.ps1`, `inmet_proxy.py`)
- payload VPS (`data/vps/**`)

## Deploy

Firebase Hosting:
`firebase deploy --only hosting --project syncfmds`

Netlify:
Site: `syncfmds` (`d44d77bd-ae7e-43a6-b3d8-ca850b513267`)
URL: `https://syncfmds.netlify.app`

Publicacao manual enxuta:
```powershell
New-Item -ItemType Directory -Force -Path .\netlify_publish | Out-Null
Copy-Item -Force .\fmds_v5_completo.html .\netlify_publish\index.html
Copy-Item -Force .\fmds_v5_completo.html .\netlify_publish\fmds_v5_completo.html
Copy-Item -Force .\firebase.runtime-config.js .\netlify_publish\firebase.runtime-config.js
netlify deploy --prod --dir netlify_publish --site d44d77bd-ae7e-43a6-b3d8-ca850b513267
```
