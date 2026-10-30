.PHONY: help setup test lint clean tree fmt typecheck

help: ## Mostra esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Cria ambiente virtual e instala dependências
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip
	. .venv/bin/activate && pip install -e ".[dev,solver]"

test: ## Executa testes com cobertura
	. .venv/bin/activate && python -m pytest

lint: ## Executa linter
	. .venv/bin/activate && ruff check src tests
	. .venv/bin/activate && ruff format --check src tests

fmt: ## Formata código
	. .venv/bin/activate && ruff format src tests
	. .venv/bin/activate && ruff check --fix src tests

typecheck: ## Executa verificação de tipos
	. .venv/bin/activate && mypy src

clean: ## Remove artefatos de build
	rm -rf .venv build dist *.egg-info src/*.egg-info .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

tree: ## Mostra estrutura do projeto
	find . -type f -not -path './.venv/*' -not -path './.git/*' | sort
