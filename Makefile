# UTCI-VISION — môi trường, kiểm tra chất lượng, Docker và khởi động local.
# Việc dữ liệu / fine-tune / đánh giá dùng scripts/ và notebook — xem README.
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
ifeq ($(OS),Windows_NT)
  NPM := npm.cmd
else
  NPM := npm
endif

.DEFAULT_GOAL := help
.PHONY: help env venv install check-env freeze lint format test ci build up up-gpu down logs ps clean dev dev-api dev-web dev-status

help: ## Danh sách lệnh
	@python -c "import re; from pathlib import Path; print('\n'.join('  {:<14} {}'.format(*m.groups()) for m in re.finditer(r'^([\w-]+):[^\n]*?## (.+)$$', Path('Makefile').read_text(encoding='utf-8'), re.M)))"

# ---------------------------------------------------------------- môi trường
env: ## Tạo .env từ .env.example (cổng custom)
	@python -c "from pathlib import Path; p = Path('.env'); p.exists() or p.write_bytes(Path('.env.example').read_bytes())"

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

# ---------------------------------------------------------------- chạy local
dev: env ## Chạy API + web local cùng lúc; Ctrl+C để dừng cả hai
	$(PY) scripts/dev.py

dev-api: env ## Chạy riêng API local; Ctrl+C để dừng
	$(PY) -m utci_vision.api

dev-web: env ## Chạy riêng giao diện local; Ctrl+C để dừng
	$(NPM) --prefix web run dev

dev-status: ## Kiểm tra cổng API và web local
	$(PY) scripts/dev.py --status

clean: ## Xoá cache build/test
	rm -rf .pytest_cache .ruff_cache web/dist
	find src scripts tests -name __pycache__ -type d -prune -exec rm -rf {} +
