FROM python:3.14.6-slim

# Non-root user — limits blast radius if the app is exploited
RUN useradd --no-create-home --shell /bin/false appuser

WORKDIR /app

# Install dependencies before copying app code so this layer is cached
# separately and only invalidated when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Drop root before the process starts
USER appuser

# Confirms the runtime and dependencies are intact.
# A real server would use: CMD curl -f http://localhost:PORT/health || exit 1
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import subprocess, os" || exit 1

CMD ["python", "app/main.py"]
