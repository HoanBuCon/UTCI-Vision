# API — bản CPU (mặc định). Docker là nơi duy nhất cố định torch (ADR-005). Cổng: UTCI_API_PORT (compose truyền vào).
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UTCI_DEVICE=cpu UTCI_API_HOST=0.0.0.0
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN pip install torch==2.14.1 torchvision==0.29.1 --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt requirements-nodeps.txt ./
RUN pip install -r requirements.txt && pip install --no-deps -r requirements-nodeps.txt
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
RUN pip install --no-deps .

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"UTCI_API_PORT\"]}/api/v1/health')"
CMD ["python", "-m", "utci_vision.api"]
