# BayQuant

A landing page for BayQuant: quantitative research and systematic strategy work,
served by FastAPI and containerized with Docker. It also serves a browsable copy
of the [bayquant/brain](https://github.com/bayquant/brain) notes vault at `/brain`.

## Run with Docker

```bash
# Build the image
docker build -t bayquant .

# Run the container
docker run -p 8000:8000 bayquant
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

To stop the container, press `Ctrl+C`.

## Run locally

Dependencies are managed with [uv](https://docs.astral.sh/uv/): declared in
`pyproject.toml` and pinned in `uv.lock`.

```bash
uv sync
uv run uvicorn website.main:app --reload
```

To add or upgrade a dependency, use `uv add <package>` (it updates both files).

## Deploying

Services run on a DigitalOcean droplet prepared by the
[digital-ocean](https://github.com/bayquant/digital-ocean) repo (Docker and Caddy
installed, no app on it). Everything about how things run lives in `deploy/`,
one folder per service, each with its own README:

```
deploy/
  deploy.sh        # deploy.sh <service> [user@host]
  website/         # this app (FastAPI, built from the Dockerfile)
  postgres/        # shared Postgres: one role and database per app
  prefect/         # Prefect server, backed by the shared Postgres
```

Commit your changes, then:

```bash
deploy/deploy.sh website                      # deploys to deploy@bayquant.dev
deploy/deploy.sh website deploy@DROPLET_IP    # use the IP right after the droplet is recreated
```

Only the committed `HEAD` is deployed. The script replaces `/opt/apps/<service>`
on the droplet, rebuilds, restarts that one service, reloads Caddy if the service
has a `.caddy` file, and waits for its healthcheck. Services are independent:
deploying one never restarts another.

Secrets live on the droplet in `/opt/secrets/<service>.env`, outside the repo and
outside the directory the deploy replaces. See each service's README for setup.
On a fresh droplet, deploy `postgres` before `prefect`.

## Routes

- `/`: the landing page
- `/health`: liveness check
- `/brain`: index of notes fetched from the vault
- `/brain/{slug}`: a single rendered note
- `/brain/assets/{name}`: an image embedded in a note

## Project layout

```
website/                Application package
  main.py               App creation, startup fetch, router wiring
  routes/
    api/                JSON endpoints
      health.py         /health
    views/              Server-rendered HTML pages
      templating.py     Shared Jinja2 templates instance
      home.py           Landing page
      brain.py          /brain, /brain/{slug} and /brain/assets/{name}
  services/
    brain_content.py    Fetches and parses the bayquant/brain vault
  templates/
    index.html          Landing page
    brain_base.html     Shared shell for note pages
    brain_index.html    Notes index
    brain_note.html     Single note
```

The repo root holds only config (`Dockerfile`, `pyproject.toml`, `uv.lock`,
`.python-version`, `README.md`) and the `deploy/` folder; all application code
lives in the `website/` package.

## Notes (`/brain`)

At startup the app downloads the [bayquant/brain](https://github.com/bayquant/brain)
vault, renders each markdown note to HTML (resolving Obsidian `[[wiki-links]]`,
`![[image]]` embeds and `$...$` math, which KaTeX draws in the browser), and
groups the index by vault folder. Notes refresh on every
container restart: no image rebuild needed. If GitHub is unreachable at startup
the site still runs; `/brain` just reports that notes are unavailable.

## Editing content

The landing page markup, styles, and copy live in `templates/index.html`.
Placeholder bio text, focus tags, and footer links (email, GitHub, LinkedIn, X)
should be swapped for real content.
