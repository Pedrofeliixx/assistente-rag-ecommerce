from chunking import carregar_documentos, dividir_em_chunks
from embeddings import MODELOS, obter_colecao

documentos = carregar_documentos("docs")
chunks = []
for doc in documentos:
    chunks.extend(dividir_em_chunks(doc))

for versao in MODELOS:
    colecao = obter_colecao(versao)
    colecao.upsert(
        ids=[c["id"] for c in chunks],
        documents=[c["texto"] for c in chunks],
        metadatas=[{"arquivo": c["arquivo"], "secao": c["secao"]} for c in chunks],
    )
    print(f"{versao}: {colecao.count()} chunks salvos")