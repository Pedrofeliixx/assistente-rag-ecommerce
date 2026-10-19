import chromadb
from chromadb.utils import embedding_functions

cliente = chromadb.PersistentClient(path="banco_vetorial")

MODELOS = {
    "v1": None,
    "v2": "paraphrase-multilingual-MiniLM-L12-v2",
}


def obter_colecao(versao):
    nome_modelo = MODELOS[versao]
    if nome_modelo is None:
        return cliente.get_or_create_collection(name=f"politicas_{versao}")
    funcao = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=nome_modelo)
    return cliente.get_or_create_collection(name=f"politicas_{versao}", embedding_function=funcao)