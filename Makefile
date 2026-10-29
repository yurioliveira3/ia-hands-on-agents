.PHONY: setup env test test-jev notebooks evals demo3-run demo2-setup demo2-config clean

setup:
	uv sync --locked

env:
	@if [ -f .env ]; then \
		echo ".env ja existe (nao sobrescrevo)"; \
	else \
		cp .env.example .env; \
		echo ".env criado a partir de .env.example - preencha LLM_API_KEY, LLM_MODEL e LLM_BASE_URL"; \
	fi

test: env
	uv run --locked --env-file .env python -c "from llm import chat; print(chat([{'role': 'user', 'content': 'diga ok'}]))"

test-jev: env
	uv run --locked --env-file .env python -c "from jev import system_one, Noul; r = system_one('Cobraram o frete duas vezes na minha fatura do cartão', {'cobranca_duplicada': Noul('Esta reclamação fala de cobrança em duplicidade?')}); print(r); assert 0.0 <= r['cobranca_duplicada']['valor'] <= 1.0"

notebooks: env
	uv run --locked --env-file .env jupyter lab

evals: env
	uv run --locked --env-file .env jupyter nbconvert --to notebook --execute demo-1/bonus_evals.ipynb --output-dir export
	@echo "notebook executado em export/bonus_evals.ipynb"

demo3-run: env
	uv run --locked --env-file .env jupyter nbconvert --to notebook --execute demo-3/01_triagem_jev.ipynb demo-3/02_agente_juiz.ipynb demo-3/03_model_route.ipynb --output-dir export/demo3

demo2-setup:
	uv tool install --reinstall mcp-server-fetch
	uv tool install --reinstall mcp-server-sqlite --with "mcp<2"

demo2-config:
	@if [ -f demo-2/.mcp.json ]; then \
		echo "demo-2/.mcp.json ja existe (nao sobrescrevo)"; \
	else \
		sed "s|{{DEMO2_DIR}}|$(CURDIR)/demo-2|g" demo-2/.mcp.json.example > demo-2/.mcp.json; \
		echo "demo-2/.mcp.json gerado com o caminho $(CURDIR)/demo-2"; \
	fi
	@if [ -f demo-2/opencode.json ]; then \
		echo "demo-2/opencode.json ja existe (nao sobrescrevo)"; \
	else \
		sed "s|{{DEMO2_DIR}}|$(CURDIR)/demo-2|g" demo-2/opencode.json.example > demo-2/opencode.json; \
		echo "demo-2/opencode.json gerado com o caminho $(CURDIR)/demo-2"; \
	fi
	@cp data/reclamacoes.csv demo-2/reclamacoes.csv
	@echo "demo-2/reclamacoes.csv copiado de data/"

clean:
	rm -rf __pycache__ .pytest_cache .ipynb_checkpoints export
	rm -f demo-2/.mcp.json demo-2/opencode.json demo-2/reclamacoes.csv demo-2/demo.sqlite demo-2/resumo.md demo-2/parecer.md
	find . -name ".ipynb_checkpoints" -type d -exec rm -rf {} +
