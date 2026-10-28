# Ponto único de integração com o Jev (System One): decisões tipadas
# (choice/score/noul) numa única chamada HTTP, sem SDK, sem prompt e
# sem parse de texto. Par do llm.py na tese do repo: modelo e endpoint
# são peças substituíveis, tudo vem do .env.
import random
import time
from dataclasses import dataclass

import requests

# Importar de llm já executa o loader único do .env e entrega os mesmos
# headers da demo: o User-Agent próprio evita o bloqueio 1010 do
# Cloudflare, que rejeita o User-Agent de biblioteca.
from llm import _DEFAULT_HEADERS, _env

# SPEC_DEVIATION: .env local sem JEV_* (arquivo do usuário intocado); fallback = defaults do .env.example
# Razão: o fallback garante o make test-jev sem editar o .env do usuário.
# O .env sempre ganha; a chave vazia reusa a LLM_API_KEY do chat (verificado em 2026-10-28).
_DEFAULT_BASE_URL = "https://opencode.ai/inference/systemone/v1/systemone"
_DEFAULT_MODEL = "jev-1.13-free"


@dataclass
class Choice:
    """Pergunta fechada: o modelo escolhe um dos critérios nomeados."""

    instructions: str
    criteria: dict[str, str]

    def wire(self) -> dict:
        return {"type": "choice", "instructions": self.instructions, "criteria": self.criteria}


@dataclass
class Score:
    """Pergunta de severidade: o modelo pontua os critérios."""

    instructions: str
    criteria: list[str]

    def wire(self) -> dict:
        return {"type": "score", "instructions": self.instructions, "criteria": self.criteria}


@dataclass
class Noul:
    """Pergunta de julgamento: o modelo devolve um grau, de 0.0 a 1.0."""

    instructions: str

    def wire(self) -> dict:
        return {"type": "noul", "instructions": self.instructions}


# Mesmo papel dos contadores do llm.py, nos campos do protocolo: tokens
# por request e o custo real devolvido pelo gateway (0 no modelo -free).
_LAST_USAGE: dict | None = None
_USAGE_TOTAL = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0}


def _registrar_uso(usage: dict | None) -> None:
    global _LAST_USAGE
    if usage is None:
        _LAST_USAGE = None
        return
    _LAST_USAGE = {
        "input_tokens": usage.get("input_tokens") or 0,
        "output_tokens": usage.get("output_tokens") or 0,
        "cost": usage.get("cost") or 0,
        # billing_source (ex.: "free") é um dado da chamada, não um
        # acumulável; por isso ele fica só no last_usage().
        "billing_source": (usage.get("opencode") or {}).get("billing_source"),
    }
    for chave in ("input_tokens", "output_tokens", "cost"):
        _USAGE_TOTAL[chave] += _LAST_USAGE[chave]


def last_usage() -> dict | None:
    """Uso da última chamada (tokens, cost, billing_source), ou None."""
    return dict(_LAST_USAGE) if _LAST_USAGE else None


def usage_total() -> dict:
    """Uso acumulado neste processo (todas as chamadas system_one)."""
    return dict(_USAGE_TOTAL)


def system_one(
    state: str,
    questions: dict[str, Choice | Score | Noul],
    model: str | None = None,
) -> dict[str, dict]:
    """Uma chamada, N perguntas tipadas sobre o mesmo estado.

    Variáveis de ambiente (arquivo .env junto do llm.py):
      JEV_API_KEY   - chave do Jev (vazia reusa a LLM_API_KEY do chat)
      JEV_BASE_URL  - endpoint do protocolo System One
      JEV_MODEL     - modelo; o parâmetro model tem preferência

    Cada pergunta volta mapeada em {"tipo", "valor"} e ganha "confianca"
    e "probabilidades" quando o modelo os devolve (choice os traz). O
    uso fica em last_usage() (última chamada) e usage_total() (acumulado
    do processo), com o cost devolvido pelo gateway.
    """
    api_key = _env("JEV_API_KEY") or _env("LLM_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Variáveis faltando: JEV_API_KEY (ou LLM_API_KEY). Copie "
            ".env.example para .env, preencha e tente de novo (o arquivo "
            "fica na mesma pasta do llm.py). Para criar uma chave, veja "
            "'Chaves de API' no README."
        )
    corpo = {
        "model": model or _env("JEV_MODEL") or _DEFAULT_MODEL,
        "state": state,
        "questions": {nome: pergunta.wire() for nome, pergunta in questions.items()},
    }
    for attempt in range(4):
        try:
            resposta = requests.post(
                _env("JEV_BASE_URL") or _DEFAULT_BASE_URL,
                json=corpo,
                headers={"Authorization": f"Bearer {api_key}", **_DEFAULT_HEADERS},
                timeout=60,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                "Não foi possível conectar ao gateway do Jev. Confira "
                "JEV_BASE_URL no .env e sua conexão."
            ) from exc
        if resposta.status_code != 429:
            break
        if attempt == 3:
            raise RuntimeError(
                "Rate limit persistente após 4 tentativas. Aguarde e "
                "tente de novo ou troque JEV_MODEL no .env (as opções "
                "estão no .env.example)."
            )
        # 429 no free tier é parte da vida da demo, não uma exceção.
        wait = 15 * (attempt + 1) + random.uniform(0, 3)
        print(f"(rate limit; aguardando {wait:.0f}s antes de tentar de novo)")
        time.sleep(wait)

    if resposta.status_code in (401, 403):
        raise RuntimeError(
            f"A chave foi recusada pelo gateway ({resposta.status_code}). "
            "Confira JEV_API_KEY/LLM_API_KEY no .env. O Jev é pay-as-you-go "
            "do console (opencode.ai/console): a assinatura Go/Go Plus não "
            "o inclui, pode exigir créditos próprios."
        )
    if resposta.status_code == 404:
        raise RuntimeError(
            "Endpoint ou modelo não encontrado (404). Confira JEV_BASE_URL "
            "e JEV_MODEL no .env; se o jev-1.13-free saiu do ar (o free é "
            "tempo limitado), troque JEV_MODEL para jev-1.13 (fallback "
            "pago, US$0.042 por milhão de tokens de input)."
        )
    if resposta.status_code == 422:
        raise RuntimeError(
            "O gateway recusou a requisição (422). Pergunta do tipo score? "
            "É a limitação conhecida do upstream do free (choice e noul "
            "funcionam; o material documenta a jagged edge). Senão "
            "confira o estado e os critérios. Mensagem do gateway: "
            + resposta.text[:200]
        )
    if not resposta.ok:
        raise RuntimeError(
            f"O gateway respondeu HTTP {resposta.status_code}. Confira "
            "JEV_BASE_URL e JEV_MODEL no .env; se for 402, o free pode ter "
            "acabado, troque JEV_MODEL para jev-1.13 (fallback pago) ou "
            "confira os créditos no console."
        )

    data = resposta.json()
    _registrar_uso(data.get("usage"))
    resultado: dict[str, dict] = {}
    for nome, bruto in data.get("answers", {}).items():
        # Cada tipo devolve o valor numa chave homônima: choice -> o
        # nome escolhido, noul -> o grau, score -> a pontuação.
        tipo = bruto.get("type")
        item = {"tipo": tipo, "valor": bruto.get(tipo)}
        if "confidence" in bruto:
            item["confianca"] = bruto["confidence"]
        if "probabilities" in bruto:
            item["probabilidades"] = bruto["probabilities"]
        resultado[nome] = item
    return resultado
