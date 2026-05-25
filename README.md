# Snake Game

A browser-based Snake game served by FastAPI, containerized with Docker.

## Run with Docker

```bash
# Build the image
docker build -t snake-game .

# Run the container
docker run -p 8000:8000 snake-game
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

To stop the container, press `Ctrl+C`.

## Run locally

```bash
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn main:app --reload
```

## Controls

- **Arrow keys** or **WASD** — move
- **P** — pause
