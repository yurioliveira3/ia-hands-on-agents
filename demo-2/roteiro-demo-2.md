# Demo 2 - top-3 MCPs ao vivo (~5 min)

Objetivo: mostrar configuração rápida e o dado criado, gravado e
relido em dois destinos locais, com o fetch somando um dado externo -
tudo pelo LLM e somente com linguagem natural. Esta é a camada
"protocolo": no agente da demo-1, as ferramentas eram as que nós
escrevemos; aqui, o MCP entrega ao cliente um catálogo de ferramentas
padrão, pronto para usar.

Servers dos configs gerados (`.mcp.json` para Claude Code,
`opencode.json` para OpenCode; um por destino/função):
- filesystem: escreve e lê arquivos (resumo em markdown)
- sqlite: grava dados estruturados (tabela com o top 3)
- fetch: busca um dado externo (cotação, alguma URL pública)

## Setup

1. Pré-requisitos: Node.js 20+ com npx (o server filesystem está
   pinado em `1.0.0`; a linha `2.0.0` exige Node 24) e dois servers
   Python, um pacote por comando:
   ```
   uv tool install mcp-server-fetch
   uv tool install mcp-server-sqlite
   ```
   Os comandos `mcp-server-fetch` e `mcp-server-sqlite` precisam ficar
   no PATH (o `uv tool` instala em `~/.local/bin`; verificar com
   `which`).
2. Rodar `make demo2-config` na raiz do projeto: gera
   `demo-2/.mcp.json` e `demo-2/opencode.json` com o caminho absoluto
   da pasta (a partir dos templates versionados; não sobrescreve os
   existentes) e copia `data/reclamacoes.csv` para `demo-2/`.
3. Claude Code: o `.mcp.json` gerado na pasta demo-2 é lido
   automaticamente ao iniciar `claude` dentro dessa pasta.
   OpenCode: o `opencode.json` gerado é lido ao iniciar `opencode` na
   mesma pasta.
4. Claude Code: rodar `/mcp` para conferir os três servers.
   OpenCode: rodar `opencode mcp list` na pasta para listar os servers
   configurados.
5. O `make demo2-config` já deixa a cópia de `reclamacoes.csv` em
   `demo-2/`; se rodar o cliente de outro diretório, ajuste o caminho
   no prompt ou use o caminho absoluto do CSV.

## Sequência ao vivo

| Passo | O que o dev digita | O que aparece na tela |
|---|---|---|
| 1 (~1 min) | abrir `claude` e rodar `/mcp` (ou `opencode` e `opencode mcp list`) na pasta | os 3 servers conectados surgem sozinhos |
| 2 (~1,5 min) | "Analise reclamacoes.csv e grave `resumo.md` na pasta com as principais categorias" | o server filesystem escrevendo um arquivo que fica visível no editor |
| 3 (~1 min) | "Grave em podcast.sqlite uma tabela top3 com as 3 categorias mais frequentes e as contagens" | o server sqlite criando a tabela |
| 4 (~1 min) | "Leia o resumo.md e a tabela top3 e me diga em uma frase o maior problema" | o LLM lendo de volta os próprios artefatos |
| 5 (30 s) | opcional: "Busque em <url pública> um dado externo e junte ao resumo" | o fetch somando um destino remoto |

## O prompt de ponta a ponta (mão livre)

Passos 2 a 4 separados provam cada destino; o prompt abaixo prova o
conjunto: uma única instrução, o agente planeja a ordem, usa os três
servers e lê de volta o que criou - sem pedir cada etapa. Cole e
deixe girar até terminar:

```
Leia reclamacoes.csv e faça o ciclo completo:
1. escreva um resumo.md com as categorias e suas contagens;
2. crie em podcast.sqlite uma tabela top3 com as três categorias
   mais frequentes e suas contagens;
3. leia de volta o resumo.md e a tabela top3 e responda em uma
   frase qual é o maior problema da base, citando os números.
```

Na tela, o que se vê é o agente decidindo a sequência sozinho
(escrever → gravar → reabrir os artefatos e concluir): a camada 3 da
demo 1 acontecendo sobre o catálogo MCP.

## Pontos de fala

- "Isso que configurei em cinco minutos seria semanas de integração à
  mão: SDKs, autenticação e tipos diferentes para cada destino."
- "E a parte de testes? Todo server MCP fala o mesmo protocolo, então
  o teste de integração também ganha uma forma padrão de escrever."
- Amarração com a demo 1: "na camada 3, eu escrevi as ferramentas.
  Aqui, o catálogo padrão veio pronto - foi isso que o MCP mudou."
