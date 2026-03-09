FROM python:3.11-slim

LABEL maintainer="Yumo Xu <yumorepos.github.io>" \
      description="Montreal Housing Market Dashboard (Streamlit + Plotly)" \
      version="1.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY analysis.py .
COPY .streamlit/ .streamlit/

EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen(f'http://localhost:{__import__(\"os\").environ.get(\"PORT\",8501)}/_stcore/health')" || exit 1

ENTRYPOINT ["sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true"]
