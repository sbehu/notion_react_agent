FROM python:3.12-slim

WORKDIR /app

# Install system utilities
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Pull the official high-performance uv binary straight into your container execution layer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Copy your dependency configurations
COPY requirements.txt .

# EXHAUSTIVE FORCE-FEED: Hardcoding the internet packages right here forces uv to download them 
# and completely overrides any old or missing text file versions!

RUN uv pip install --system --no-cache langchain-community duckduckgo-search ddgs -r requirements.txt

COPY . .
EXPOSE 8000

# Run uvicorn cleanly through the system layer
CMD ["uv", "run", "python", "main.py"]