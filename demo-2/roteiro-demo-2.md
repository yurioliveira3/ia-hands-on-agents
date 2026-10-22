# Demo 2 - top-3 MCPs ao vivo

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
   Python, um pacote por comando - ou `make demo2-setup`, que roda
   os mesmos comandos de uma vez:
   ```
   uv tool install mcp-server-fetch
   uv tool install mcp-server-sqlite --with 'mcp<2'
   ```
   O pin `mcp<2` importa: sem ele o uv resolve um `mcp` 2.x, e a
   linha 2.x removeu a API que o sqlite server (2025.4.25) usa
   (lowlevel `Server` com `list_resources`) - o processo quebra
   antes de responder ao protocolo. Os comandos `mcp-server-fetch`
   e `mcp-server-sqlite` precisam ficar no PATH (o `uv tool`
   instala em `~/.local/bin`; verificar com `which`).
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
| 1 | abrir `claude` e rodar `/mcp` (ou `opencode` e `opencode mcp list`) na pasta | os 3 servers conectados surgem sozinhos |
| 2 | "Analise reclamacoes.csv e grave `resumo.md` na pasta com as principais categorias" | o server filesystem escrevendo um arquivo que fica visível no editor |
| 3 | "Grave em podcast.sqlite uma tabela top3 com as 3 categorias mais frequentes e as contagens" | o server sqlite criando a tabela |
| 4 | "Leia o resumo.md e a tabela top3 e me diga em uma frase o maior problema" | o LLM lendo de volta os próprios artefatos |
| 5 | opcional (só na versão separada): "Busque em https://economia.awesomeapi.com.br/json/last/USD-BRL a cotação do dólar e acrescente ao resumo" | o fetch somando um destino remoto |

## O prompt de ponta a ponta (mão livre)

Passos 2 a 4 separados provam cada destino; o prompt abaixo prova o
conjunto: uma única instrução, o agente planeja a ordem, usa os três
servers (filesystem, sqlite e fetch) e lê de volta o que criou - sem
pedir cada etapa. Cole e deixe girar até terminar.

## Prompts em três níveis

Versões do prompt ponta a ponta em três degraus de engenharia - cada
arquivo em `demo-2/prompts/` traz o prompt completo pronto para colar,
com uma nota de "o que a plateia espera ver":

| Nível | Arquivo | O que acrescenta |
|---|---|---|
| Simples | `prompts/prompt-simples.md` | o ciclo completo em uma instrução única, sem contrato de saída - o agente decide tudo |
| Médio | `prompts/prompt-medio.md` | "contrato de saída": entregas nomeadas, estrutura exata do resumo.md, schema da tabela, regras de desempate - prompt como especificação |
| Avançado | `prompts/prompt-avancado.md` | template reutilizável com few-shots, estilo de saída e variáveis `{{CSV_PATH}}`, `{{PASTA_SAIDA}}`, `{{URL_EXTERNA}}` - troca as chaves (mesma técnica `sed` do `make demo2-config`) e roda em outra base sem reescrever |

No nível simples, na tela o que se vê é o agente decidindo a sequência
sozinho (escrever → gravar → buscar externo → reabrir os artefatos e
concluir): a camada 3 da demo 1 acontecendo sobre o catálogo MCP. A URL
do AwesomeAPI é pública, sem chave de API, e devolve um JSON com a
cotação USD/BRL — dado que conversa com o tema (reclamações de cobrança
de um e-commerce). O "liste quais MCPs você usou" do nível simples
serve de prova visual de que os três servers entraram no fluxo.

## Pontos de reflexão

- O que levaria semanas à mão - SDKs, autenticação e tipos diferentes
  para cada destino - aqui se configurou em minutos.
- Todo server MCP fala o mesmo protocolo: o teste de integração também
  ganha uma forma padrão de escrever.
- Amarração com a demo 1: na camada 3, as ferramentas foram escritas à
  mão. Aqui, o catálogo padrão veio pronto - foi isso que o MCP mudou.
