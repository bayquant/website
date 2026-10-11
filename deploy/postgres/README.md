# postgres

One shared Postgres 16 for every app on the droplet. Each app gets its own role
and database, so apps cannot read each other's data.

| File | Purpose |
|---|---|
| `compose.yaml` | The server, a named volume (`postgres_data`), and a healthcheck |
| `init/01-roles.sh` | Creates one role and database per app on first boot |

No port is published. Other containers connect to `postgres:5432` over the
external `backend` network (`deploy.sh` creates it if missing). To reach it from
your laptop, tunnel to the container's address on that network:

```bash
ip=$(ssh deploy@bayquant.dev "docker inspect -f '{{.NetworkSettings.Networks.backend.IPAddress}}' postgres")
ssh -L 5432:$ip:5432 deploy@bayquant.dev
```

## One-time setup on the droplet

Create `/opt/secrets/postgres.env` (mode 600, owned by the deploy user). Use
hex passwords so they are safe inside connection URLs
(`openssl rand -hex 24`):

```
POSTGRES_PASSWORD=...
PREFECT_DB_PASSWORD=...
```

`PREFECT_DB_PASSWORD` must match the one in `/opt/secrets/prefect.env`.

## Deploy

```bash
deploy/deploy.sh postgres
```

Deploy this before `prefect` on a fresh droplet. Redeploying is safe: data lives
in the named volume, which the deploy step never touches. A new `postgres:16`
minor release will restart the container once.

## Adding an app

`init/` runs only when the data volume is empty, so editing it does not affect
an existing database. For a new app (say `nautilus`), run once on the droplet:

```bash
docker exec -i postgres psql -U postgres << 'SQL'
CREATE ROLE nautilus LOGIN PASSWORD 'generated-hex-password';
CREATE DATABASE nautilus OWNER nautilus;
SQL
```

Also add it to `init/01-roles.sh` and to `compose.yaml` so a rebuilt droplet
recreates it. The app's own schema is the app's job (for Nautilus, apply the SQL
in its `schema/sql` folder to that database).

## Not set up yet

- Backups. Nothing dumps this database anywhere off the droplet yet.
