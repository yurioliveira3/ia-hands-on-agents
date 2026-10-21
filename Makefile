.PHONY: setup env test notebooks evals demo2-config clean

setup:
	uv sync

env:
	@if [ -f .env ]; then \
		echo ".env ja existe (nao sobrescrevo)"; \
	else \
		cp .env.example .env; \
		echo ".env criado a partir de .env.example - preencha LLM_API_KEY, LLM_MODEL e LLM_BASE_URL"; \
	fi

test: env
	uv run --env-file .env python -c "from llm import chat; print(chat([{'role': 'user', 'content': 'diga ok'}]))"

notebooks: env
	uv run --env-file .env jupyter lab

evals: env
	uv run --env-file .env jupyter nbconvert --to notebook --execute demo-1/bonus_evals.ipynb --output-dir export
	@echo "notebook executado em export/bonus_evals.ipynb"

demo2-config:
	@if [ -f demo-2/.mcp.json ]; then \
		echo "demo-2/.mcp.json ja existe (nao sobrescrevo)"; \
	else \
		sed "s|{{DEMO2_DIR}}|$(CURDIR)/demo-2|g" demo-2/.mcp.json.example > demo-2/.mcp.json; \
		echo "demo-2/.mcp.json gerado com o caminho $(CURDIR)/demo-2"; \
	fi

clean:
	rm -rf __pycache__ .pytest_cache .ipynb_checkpoints
	find . -name ".ipynb_checkpoints" -type d -exec rm -rf {} +
