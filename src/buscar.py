import chromadb

cliente = chromadb.PersistentClient(path="banco_vetorial")
colecao = cliente.get_collection(name="politicas_novatech")

pergunta = input("Pergunta: ")

resultado = colecao.query(query_texts=[pergunta], n_results=3)

for i in range(len(resultado["ids"][0])):
    print(f"\n#{i + 1}  distância: {resultado['distances'][0][i]:.3f}")
    print("Fonte:", resultado["metadatas"][0][i]["arquivo"], "→", resultado["metadatas"][0][i]["secao"])