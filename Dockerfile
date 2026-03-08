# Montreal Housing Dashboard — Dockerfile
# ----------------------------------------
# Multi-stage-friendly single image using Python 3.11-slim.
# Build:  docker build -t montreal-housing .
# Run:    docker run -p 8501:8501 montreal-housing

FROM python:3.11-slim

# Metadata
LABEL maintainer="Yumo Xu <yumorepos.github.io>" \
      description="Montreal Housing Market Dashboard (Streamlit + Plotly)" \
      version="1.0"

# Prevent .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies (minimal set for pandas/numpy)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py .
COPY analysis.py .
COPY .streamlit/ .streamlit/

# Expose Streamlit default port
EXPOSE 8501

# Health check — Streamlit exposes a /_stcore/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

# Run the dashboard
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", \
            "--server.address=0.0.0.0"]
