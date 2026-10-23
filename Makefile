# UTCI-VISION — Makefile CHỈ dành cho DevOps: môi trường, kiểm tra chất lượng (CI), Docker.
# Việc dữ liệu / fine-tune / đánh giá / chạy dev dùng trực tiếp scripts/, notebook, npm — xem README.
# Windows: chạy trong Git Bash (GNU Make 4.x). torch/CUDA tự cài trước `make install` (ADR-005).

-include .env
export
export PYTHONUTF8 := 1

ifeq ($(OS),Windows_NT)
  PY ?= .venv/Scripts/python
else
  PY ?= .venv/bin/python
endif
COMPOSE := docker compose

.DEFAULT_GOAL := help
.PHONY: help env venv install check-env freeze lint format test ci build up up-gpu down logs ps clean

help: ## Danh sách lệnh
	@grep -hE '^[a-zA-Z_-]+:.*?## ' Makefile | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------- môi trường
env: ## Tạo .env từ .env.example (cổng custom)
	@test -f .env || cp .env.example .env && echo ".env: API=$(UTCI_API_PORT) WEB=$(UTCI_WEB_PORT) DEV=$(UTCI_DEV_PORT) JUPYTER=$(UTCI_JUPYTER_PORT)"

venv: ## Tạo .venv (sau đó TỰ cài torch theo GPU: https://pytorch.org/get-started/locally/)
	python -m venv .venv && $(PY) -m pip install --upgrade pip

install: ## Thư viện dùng chung + VietOCR (--no-deps) + package + frontend + pre-commit (yêu cầu đã có torch)
	$(PY) -m pip install -r requirements.txt -r requirements-dev.txt
	$(PY) -m pip install --no-deps -r requirements-nodeps.txt
	$(PY) -m pip install --no-deps -e .
	cd web && npm ci
	$(PY) -m pre_commit install

check-env: ## Kiểm tra torch/CUDA/GPU, thư viện, cổng
	$(PY) scripts/env.py check

freeze: ## requirements.lock (đã loại torch/CUDA)
	$(PY) scripts/env.py freeze

# ---------------------------------------------------------------- chất lượng / CI
lint: ## ruff + format check + tsc
	$(PY) -m ruff check src scripts tests notebooks/train/_template.py
	$(PY) -m ruff format --check src scripts tests
	cd web && npm run typecheck

format: ## Tự sửa lint/format Python
	$(PY) -m ruff check --fix src scripts tests notebooks/train/_template.py
	$(PY) -m ruff format src scripts tests

test: ## pytest
	$(PY) -m pytest -q

ci: lint test ## Giống GitHub Actions: + notebook khớp template, build web, compose hợp lệ
	$(PY) scripts/build_notebooks.py --check
	cd web && npm run build
	$(COMPOSE) --profile cpu config -q && $(COMPOSE) --profile gpu config -q

# ---------------------------------------------------------------- Docker
build: env ## Build image (CPU)
	$(COMPOSE) --profile cpu build

up: env ## Chạy demo (CPU) -> http://localhost:$UTCI_WEB_PORT
	$(COMPOSE) --profile cpu up --build -d && echo "http://localhost:$(UTCI_WEB_PORT)"

up-gpu: env ## Chạy demo (GPU; NVIDIA driver + Docker Desktop WSL2)
	$(COMPOSE) --profile gpu up --build -d && echo "http://localhost:$(UTCI_WEB_PORT)"

down: ## Dừng container
	$(COMPOSE) --profile cpu --profile gpu down

logs: ## Xem log
	$(COMPOSE) --profile cpu --profile gpu logs -f --tail 100

ps: ## Trạng thái container
	$(COMPOSE) --profile cpu --profile gpu ps

clean: ## Xoá cache build/test
	rm -rf .pytest_cache .ruff_cache web/dist
	find src scripts tests -name __pycache__ -type d -prune -exec rm -rf {} +
