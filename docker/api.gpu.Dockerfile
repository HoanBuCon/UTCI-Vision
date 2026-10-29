# API — bản GPU (profile `gpu`). CUDA nằm trong image; máy thật chỉ cần NVIDIA driver + Docker Desktop (WSL2).
FROM pytorch/pytorch:2.14.1-cuda12.6-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 UTCI_DEVICE=0 UTCI_API_HOST=0.0.0.0
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements-nodeps.txt ./
RUN pip install -r requirements.txt && pip install --no-deps -r requirements-nodeps.txt
COPY pyproject.toml README.md ./
COPY src ./src
COPY configs ./configs
RUN pip install --no-deps .
# Cài non-editable -> chỉ cho utci_vision gốc dự án (configs/, models/)
ENV UTCI_ROOT=/app

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://localhost:{os.environ[\"UTCI_API_PORT\"]}/api/v1/health')"
CMD ["python", "-m", "utci_vision.api"]
