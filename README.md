# 🛒 Assistente NovaTech – RAG para atendimento de e-commerce

Um assistente que responde às dúvidas de clientes de uma loja fictícia (**NovaTech**) usando **somente** as políticas da própria loja, com citação da fonte em cada resposta.

**▶️ Demonstração:** https://assistente-novatech.streamlit.app/

![Assistente NovaTech respondendo com a fonte citada](docs/img/app.png)

---

## O problema

Um modelo de linguagem sozinho responde com o que "acha provável", e não com as regras reais da loja. Em atendimento, isso vira prazo de troca inventado, frete errado ou promessa que a empresa não cumpre.

Com **RAG (Retrieval-Augmented Generation)**, o assistente primeiro **busca** os trechos relevantes nas políticas e só então **gera** a resposta com base neles. Quando a informação não existe nos documentos, ele diz que não sabe e indica um caminho, em vez de inventar.

---

## Como funciona

```
Pergunta do cliente
      │
      ▼
Embedding da pergunta (modelo multilíngue)
      │
      ▼
Busca vetorial no ChromaDB  ──►  3 trechos mais parecidos
      │
      ▼
Claude Haiku 4.5 + instruções (usar só os trechos, citar a fonte)
      │
      ▼
Resposta + "Fonte: <documento> – <seção>"
```

1. **Chunking:** 5 documentos de política (trocas, frete, pagamento, rastreamento e garantia), divididos por seção (`##`), geram **18 trechos**.
2. **Indexação:** cada trecho vira um vetor (embedding) e é salvo no ChromaDB.
3. **Busca:** a pergunta vira um vetor, e os 3 trechos mais próximos são recuperados.
4. **Geração:** o Claude recebe a pergunta e os trechos, com regras para não inventar, responder em até 4 frases e citar a fonte.
5. **Interface:** chat em Streamlit, com a opção de ver os trechos usados em cada resposta.

---

## Stack

| Camada | Tecnologia |
| --- | --- |
| Linguagem | Python 3.12 |
| Banco vetorial | ChromaDB (`PersistentClient`) |
| Embeddings | `paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers) |
| LLM | Claude Haiku 4.5 (API da Anthropic) |
| Interface e deploy | Streamlit + Streamlit Community Cloud |

---

## Avaliação: o que mudou a qualidade

Criei **10 perguntas de teste**, cada uma com a seção que deveria ser encontrada, e medi:

- **Top-1:** o trecho certo veio em 1º lugar.
- **Top-3:** o trecho certo estava entre os 3 enviados ao modelo.

| Versão | O que mudou | Top-3 |
| --- | --- | --- |
| v1 | Embedding padrão do ChromaDB (treinado em inglês) | 6/10 |
| v2 | Embedding multilíngue | 9/10 |
| v2 + documento enriquecido | Seção "Produto com defeito" reescrita com o vocabulário do cliente | **10/10** |

Na versão final, o trecho certo também ficou em 1º lugar (Top-1) em 7 das 10 perguntas.

### Decisões e o porquê

- **Por que trocar o modelo de embeddings?** O modelo padrão do ChromaDB foi treinado em inglês e não aproximava bem as perguntas em português dos trechos certos. O modelo multilíngue resolveu a maior parte dos erros de busca sem mudar mais nada.
- **Por que enriquecer o documento em vez de mexer no prompt?** A pergunta "meu fone chegou com problema" recuperava a seção errada, e o assistente dava uma resposta **errada, mas convincente**. A causa estava no documento, que falava em "defeito" enquanto o cliente fala em "problema", "quebrado" e "não funciona". Incluir essas palavras na política corrigiu a busca e, por consequência, a resposta.
- **Por que Top-3 e não só Top-1?** O modelo recebe 3 trechos. Se o certo está entre eles, a resposta tende a sair correta, mesmo que ele não esteja em 1º.
- **Por que Haiku?** É o modelo mais econômico da família e suficiente quando o contexto já chega filtrado pela busca.

### Testes manuais de resposta

| Pergunta | Comportamento esperado | Resultado |
| --- | --- | --- |
| Parcelamento de compra de R$ 80 | Aplicar a regra de valor mínimo da parcela | ✅ |
| Pergunta sobre geladeira (não coberta) | Admitir que não sabe e indicar um caminho | ✅ |
| Entrega no mesmo dia em um sábado | Não cair na "pegadinha" do dia da semana | ✅ |
| Fone chegou com problema | Troca em até 30 dias por defeito | ✅ (após enriquecer o documento) |

---

## Limitações

- **Base pequena e fictícia:** 5 documentos e 18 trechos. Em uma base maior, o chunking por seção e o Top-3 precisariam ser reavaliados.
- **Avaliação com 10 perguntas:** serve para comparar versões, mas não é estatisticamente robusta.
- **Sem memória de conversa:** cada pergunta é respondida de forma independente; perguntas de continuação ("e se for celular?") podem perder o contexto.
- **Limite da demonstração:** cada visitante pode fazer até 10 perguntas, para controlar o custo da API.
- **Primeiro acesso mais lento:** o modelo de embeddings é baixado quando o app "acorda".

## Próximos passos

- Ampliar o conjunto de avaliação e medir também a qualidade da resposta (não só da busca).
- Adicionar memória de conversa.
- Testar busca híbrida (palavra-chave + vetor) para termos exatos como valores e prazos.

---

## Como rodar localmente

```powershell
git clone https://github.com/Pedrofeliixx/assistente-rag-ecommerce.git
cd assistente-rag-ecommerce
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz:

```
ANTHROPIC_API_KEY=sua-chave
```

Rode:

```powershell
streamlit run src/app.py      # interface de chat
python src/avaliar.py         # avaliação Top-1 / Top-3
python src/responder.py       # chat no terminal
```

O índice vetorial é criado automaticamente na primeira execução.

## Estrutura

```
assistente-rag-ecommerce/
├── docs/                 # políticas da loja fictícia (.md)
├── src/
│   ├── chunking.py       # carrega os documentos e divide por seção
│   ├── embeddings.py     # ChromaDB + modelos de embedding (v1 e v2)
│   ├── indexar.py        # indexa os trechos em cada versão
│   ├── avaliar.py        # 10 perguntas de teste, Top-1 e Top-3
│   ├── responder.py      # busca + Claude (resposta com fonte)
│   └── app.py            # interface Streamlit
├── requirements.txt
└── .streamlit/config.toml
```

---

Projeto de portfólio com dados 100% fictícios. Autor: **Pedro Vitório** · [LinkedIn](https://www.linkedin.com/in/pedro-vitório-985540206) · [GitHub](https://github.com/Pedrofeliixx)