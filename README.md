# BayQuant

A landing page for BayQuant — quantitative research and systematic strategy work,
served by FastAPI and containerized with Docker.

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
uvicorn main:app --reload
```

## Editing content

All markup, styles, and copy live in `static/index.html`. Placeholder bio text,
focus tags, and footer links (email, GitHub, LinkedIn, X) should be swapped for
real content.
