# prefect

Prefect 3 server (API, UI and background services in one process), backed by
the shared [postgres](../postgres/README.md) service. It serves
`prefect.bayquant.dev` behind Caddy basic auth.

| File | Purpose |
|---|---|
| `compose.yaml` | The server, joined to the `backend` network, port `127.0.0.1:4200` only |
| `prefect.caddy` | Caddy site block with basic auth, proxying to port 4200 |

## One-time setup on the droplet

1. Add a DNS `A` record for `prefect.bayquant.dev` pointing at the droplet.
2. Deploy [postgres](../postgres/README.md) first.
3. Create `/opt/secrets/prefect.env` (mode 600, owned by the deploy user):

   ```
   PREFECT_DB_PASSWORD=...   # same value as in /opt/secrets/postgres.env
   ```

4. Create the Caddy auth snippet (outside the repo, so the hash stays private):

   ```bash
   sudo install -d /etc/caddy/secrets
   echo "basic_auth {
       bayquant $(caddy hash-password)
   }" | sudo tee /etc/caddy/secrets/prefect-auth.caddy
   ```

## Deploy

```bash
deploy/deploy.sh prefect
```

Each deploy pulls the newest `prefecthq/prefect:3-*` image. Pin a specific tag in
`compose.yaml` if you want upgrades to be deliberate.

## Notes

- Only the server runs here. Running flows needs a worker, which is not set up
  yet. A worker on the droplet should use `http://prefect:4200/api` over the
  `backend` network, not the public URL.
- The database is the `prefect` database in the shared Postgres. Its state is in
  Postgres, so this service is safe to wipe and redeploy.
