from dotenv import load_dotenv
import anthropic
from embeddings import obter_colecao

load_dotenv()
cliente_ia = anthropic.Anthropic()
colecao = obter_colecao("v2")

INSTRUCAO = """Você é o assistente virtual da loja NovaTech.
Responda à pergunta do cliente usando APENAS as informações dos trechos fornecidos.

Regras:
- Se a resposta não estiver nos trechos, diga que não encontrou essa informação e oriente o cliente a falar com o atendimento. Nunca invente prazos, valores ou regras.
- Seja direto e cordial, em no máximo 4 frases.
- No final, indique a fonte no formato: Fonte: <documento> – <seção>.
- Quando o cliente relatar um problema, comece com empatia (ex.: "Sinto muito pelo transtorno").
- Responda apenas o que foi perguntado, sem acrescentar informações de outros assuntos."""


def buscar_trechos(pergunta, n=3):
    resultado = colecao.query(query_texts=[pergunta], n_results=n)
    trechos = []
    for texto, meta in zip(resultado["documents"][0], resultado["metadatas"][0]):
        trechos.append({"texto": texto, "arquivo": meta["arquivo"], "secao": meta["secao"]})
    return trechos


def responder(pergunta):
    trechos = buscar_trechos(pergunta)
    contexto = "\n\n".join(f"[{t['arquivo']} – {t['secao']}]\n{t['texto']}" for t in trechos)

    resposta = cliente_ia.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=INSTRUCAO,
        messages=[{"role": "user", "content": f"Trechos:\n{contexto}\n\nPergunta do cliente: {pergunta}"}],
    )
    return resposta.content[0].text, trechos


if __name__ == "__main__":
    while True:
        pergunta = input("\nPergunta (ou 'sair'): ")
        if pergunta.lower() == "sair":
            break
        texto, trechos = responder(pergunta)
        print("\n" + texto)