# website

The BayQuant site (FastAPI), built from the repo's `Dockerfile`, served at
`bayquant.dev` and `www.bayquant.dev`.

| File | Purpose |
|---|---|
| `compose.yaml` | Builds the image from the repo root and publishes `127.0.0.1:8000` only |
| `website.caddy` | Caddy site block that proxies both hostnames to port 8000 |

## Deploy

```bash
deploy/deploy.sh website
```

The whole repo is shipped, since the image is built on the droplet. The deploy
waits for the container healthcheck (`/health`), which can take up to a minute
because the app fetches its notes at startup.

## Depends on

Nothing. It does not use Postgres.
