# Dockerfile using linuxserver/ffmpeg as base 
FROM lscr.io/linuxserver/ffmpeg:latest

# Install curl for uv installation
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set workdir
WORKDIR /app

# Copy uv files first for better caching
COPY pyproject.toml uv.lock ./

# Install Python 3.12 and dependencies
RUN uv python install 3.12
RUN uv sync --locked

# Copy the rest of the code
COPY . .

# Expose the port
EXPOSE 8000

# Run using uv
ENTRYPOINT []
CMD ["uv", "run", "server.py"]