# Demo 2 — top-3 MCPs criando e lendo em destinos

Demonstração guiada nas ferramentas de um catálogo padrão (MCP): o mesmo
dado flui para três destinos — `filesystem` (escreve `resumo.md`),
`sqlite` (grava a tabela `top3`) e `fetch` (busca a cotação USD/BRL na
AwesomeAPI) — por linguagem natural, no Claude Code ou no OpenCode. Na
[demo-1](../demo-1/) as ferramentas eram escritas à mão; aqui o
protocolo entrega as três prontas.

| Arquivo | Papel |
|---|---|
| [roteiro-demo-2.md](roteiro-demo-2.md) | o guião completo: setup, sequência ao vivo, prompt de ponta a ponta e pontos de reflexão |
| [prompts/prompt-simples.md](prompts/prompt-simples.md) | instrução única: o agente decide ordem e formato |
| [prompts/prompt-medio.md](prompts/prompt-medio.md) | prompt como especificação: contrato de saída verificável |
| [prompts/prompt-avancado.md](prompts/prompt-avancado.md) | template reutilizável: papel, estilo, few-shots e variáveis |
| [.mcp.json.example](.mcp.json.example) | template dos 3 servers MCP para Claude Code |
| [opencode.json.example](opencode.json.example) | template equivalente para OpenCode |

## Antes de rodar

Além do `.env` da raiz (mesma chave usada pela demo-1, guia no
[Setup do README raiz](../README.md#setup)):

```
make demo2-setup    # Node.js 20+ + servers MCP Python via uv tool (pin mcp<2)
make demo2-config   # escreve .mcp.json e opencode.json com caminhos absolutos e copia o CSV
```

Confirme os servers com `/mcp` (Claude Code) ou `opencode mcp list`
(OpenCode). Alternativas manuais e detalhes dos pins:
[Setup no README raiz](../README.md#setup) e
[roteiro](roteiro-demo-2.md).

## Dicas desta pasta

- Entre um nível de prompt e outro, rode `make clean` +
  `make demo2-config`: os artefatos têm nomes diferentes e o segundo
  run pode ler o resultado do primeiro.
- No OpenCode, inicie com `opencode --standalone` dentro de demo-2: o
  serviço compartilhado pode ficar ancorado na raiz e não carregar o
  `opencode.json` local.
- As saídas geradas (`.mcp.json`, `opencode.json`, `reclamacoes.csv`,
  `demo.sqlite`, `resumo.md`) não são versionadas; `make clean`
  remove tudo.
