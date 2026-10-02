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

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn website.main:app --reload
```

## Routes

- `/`: the landing page
- `/health`: liveness check
- `/brain`: index of notes fetched from the vault
- `/brain/{slug}`: a single rendered note

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
      brain.py          /brain and /brain/{slug}
  services/
    brain_content.py    Fetches and parses the bayquant/brain vault
  templates/
    index.html          Landing page
    brain_base.html     Shared shell for note pages
    brain_index.html    Notes index
    brain_note.html     Single note
```

The repo root holds only config (`Dockerfile`, `requirements.txt`, `README.md`);
all application code lives in the `website/` package.

## Notes (`/brain`)

At startup the app downloads the [bayquant/brain](https://github.com/bayquant/brain)
vault, renders each markdown note to HTML (resolving Obsidian `[[wiki-links]]`),
and serves them styled with the vault's own `brain.css`. Notes refresh on every
container restart: no image rebuild needed. If GitHub is unreachable at startup
the site still runs; `/brain` just reports that notes are unavailable.

## Editing content

The landing page markup, styles, and copy live in `templates/index.html`.
Placeholder bio text, focus tags, and footer links (email, GitHub, LinkedIn, X)
should be swapped for real content.
