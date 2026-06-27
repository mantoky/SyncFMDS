# Deploy VPS Operacional

Restore point before VPS deploy prep:

- Branch: `main`
- Commit: `84454cc`
- Existing Netlify publish directory: `netlify_publish`
- Existing Firebase project: `syncfmds`
- Existing root `index.html` redirects to `fmds_v5_completo.html`

This VPS deploy is isolated in `vps_publish/` so it does not replace the existing FMDS app unless you explicitly point a host to this folder.

Production URL:

```text
https://vps-fmds-editor.netlify.app/
```

The internal icon bank lives in:

```text
vps_publish/icons/
```

Keep this folder with the deploy package. Runtime uploads made by users are stored in the browser as local app data; the folder is for the app's built-in reusable icon set.

## PWA behavior

- User edits, logos, background, icons and model text are stored only in that user's browser local storage.
- Updating the hosted package does not overwrite user edits.
- When a new service worker is available, the app shows an update prompt. The new package is applied only after the user chooses to update.
- Desktop and Android install through the browser install prompt.
- iOS installs through Safari: Share > Add to Home Screen.
- A local pendrive/folder install must be served through localhost, not `file://`.

For pendrive or downloaded folder usage, open:

```text
vps_publish/iniciar-vps-local.cmd
```

Then install from:

```text
http://127.0.0.1:8766/
```

## Local validation

```powershell
python -m http.server 8766 --bind 127.0.0.1 --directory vps_publish
```

Open:

```text
http://127.0.0.1:8766/
```

Validate:

- page loads on desktop
- Admin password works: `VPS@Admin`
- Salvar works
- Notas opens
- D-1 can be hidden and re-shown
- PNG exports
- PDF exports
- PWA manifest is available at `/manifest.webmanifest`
- service worker is available at `/sw.js`
- install button appears when the browser exposes the PWA install prompt
- update prompt appears after a new package is deployed

## Netlify draft deploy

Run these commands from the project root:

```powershell
cd "C:\Users\robso\OneDrive\Documentos\New project"
```

Use this when you want a preview URL first:

```powershell
netlify deploy --dir vps_publish --config netlify.vps.toml
```

Production deploy:

```powershell
netlify deploy --prod --dir vps_publish --config netlify.vps.toml
```

If your terminal is already inside `vps_publish`, use the current folder as the deploy directory:

```powershell
netlify deploy --dir . --config ..\netlify.vps.toml
netlify deploy --prod --dir . --config ..\netlify.vps.toml
```

Rollback pattern:

```powershell
netlify api restoreSiteDeploy --data '{"site_id":"SITE_ID","deploy_id":"DEPLOY_ID"}'
```

Record the Netlify site id and deploy id after the first successful draft or production deploy.

## Firebase deploy

Use the existing default project only if this VPS app should deploy to `syncfmds`.

Preview the target first:

```powershell
firebase projects:list
firebase use
```

Deploy using the isolated config:

```powershell
firebase deploy --only hosting --config firebase.vps.json
```

If you create a separate Firebase project, run:

```powershell
firebase use --add
firebase deploy --only hosting --config firebase.vps.json
```

Rollback pattern:

```powershell
firebase hosting:clone SOURCE_SITE:SOURCE_VERSION TARGET_SITE
```

Record Firebase project, site, and release/version after deploy.

## Repository

Stage only the VPS package/config files:

```powershell
git add .gitignore vps_publish netlify.vps.toml firebase.vps.json DEPLOY_VPS.md
git commit -m "Prepare VPS operacional PWA deploy package"
```
