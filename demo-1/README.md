# Demo 1 — da engenharia de prompt ao agente

Quatro notebooks auto-contidos: cada um importa `chat()` de `../llm.py`
e lê `../data/reclamacoes.csv` (18 reclamações, 5 categorias). Rode na
ordem ou pule para o que interessar — o mapa completo das camadas está
no [README raiz](../README.md).

| Notebook | Camada | O que acontece |
|---|---|---|
| [01_zero_shot.ipynb](01_zero_shot.ipynb) | 1 | classificador sem exemplos: erra as armadilhas multimotivo (placar salvo: 4/6) |
| [02_few_shot.ipynb](02_few_shot.ipynb) | 2 | 4 âncoras mudam o placar; tuning de amostragem não conserta (6/9 em qualquer config); um exemplo novo + regra resolve o índice 16 |
| [03_agent_loop.ipynb](03_agent_loop.ipynb) | 3 | o laço decidir/agir/observar escrito à mão, com 3 ferramentas (`load_csv`, `exec_python`, `wiki_busca`) e freio em `max_steps=6` |
| [bonus_evals.ipynb](bonus_evals.ipynb) | 5 (bônus) | suíte com gabarito, 11 casos x 2 prompts: zero-shot 82%, few-shot 91% |

## Antes de rodar

Requer o ambiente da raiz pronto (`.venv` + `.env` com `LLM_API_KEY`,
`LLM_MODEL` e `LLM_BASE_URL`). Guia completo:
[Setup no README raiz](../README.md#setup).

```
make setup
make env        # preencher as chaves
make test       # caminho feliz (consome uma chamada pequena)
make notebooks  # abrir os notebooks
```

No VS Code, selecione o kernel `.venv` do projeto (**Select Kernel** >
**Python Environments...** > `.venv`). Se o editor pedir para instalar o
`ipykernel`, ele está num Python que não é o do projeto: veja o passo 4
do [Setup](../README.md#setup).

## Dicas desta pasta

- Os placares citados vêm do output salvo nos notebooks; os seus variam
  com o modelo (o output registra qual foi usado).
- Os prompts de `01`, `02` e `bonus_evals` são duplicados de propósito
  para cada notebook ser auto-contido; ao mudar um, replique nos outros
  para o placar continuar comparável.
- `exec_python` (notebook 03) roda código gerado pelo modelo no seu
  processo, sem sandbox: use ambiente descartável e não deixe dados
  sensíveis ao alcance.
- Os índices dos casos citados são posições 0-based do DataFrame
  (`df.iloc`); no CSV físico, a linha é o índice + 2.
