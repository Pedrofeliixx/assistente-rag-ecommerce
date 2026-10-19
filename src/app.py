import streamlit as st
from chunking import carregar_documentos, dividir_em_chunks
from responder import colecao, responder

st.set_page_config(page_title="Assistente NovaTech", page_icon="🛒")

if colecao.count() == 0:
    chunks = []
    for doc in carregar_documentos("docs"):
        chunks.extend(dividir_em_chunks(doc))
    colecao.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["texto"] for c in chunks],
        metadatas=[{"arquivo": c["arquivo"], "secao": c["secao"]} for c in chunks],
    )

st.title("🛒 Assistente NovaTech")
st.caption("Demo de RAG: respostas baseadas nas políticas de uma loja fictícia, sempre com a fonte citada.")

if "historico" not in st.session_state:
    st.session_state.historico = []

for mensagem in st.session_state.historico:
    with st.chat_message(mensagem["papel"]):
        st.markdown(mensagem["texto"])

pergunta = st.chat_input("Pergunte sobre trocas, frete, pagamento, rastreio ou garantia")

if pergunta:
    st.session_state.historico.append({"papel": "user", "texto": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Buscando nas políticas..."):
            texto, trechos = responder(pergunta)
        st.markdown(texto)
        with st.expander("Trechos usados na resposta"):
            for t in trechos:
                st.markdown(f"**{t['arquivo']} – {t['secao']}**")
                st.text(t["texto"])

    st.session_state.historico.append({"papel": "assistant", "texto": texto})