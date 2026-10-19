from pathlib import Path


def carregar_documentos(pasta):
    documentos = []
    for arquivo in sorted(Path(pasta).glob("*.md")):
        texto = arquivo.read_text(encoding="utf-8")
        documentos.append({"arquivo": arquivo.name, "texto": texto})
    return documentos


def dividir_em_chunks(documento):
    linhas = documento["texto"].splitlines()
    titulo_doc = linhas[0].removeprefix("# ").strip()

    chunks = []
    secao_atual = None
    conteudo = []

    for linha in linhas[1:]:
        if linha.startswith("## "):
            if secao_atual:
                chunks.append(montar_chunk(documento["arquivo"], titulo_doc, secao_atual, conteudo))
            secao_atual = linha.removeprefix("## ").strip()
            conteudo = []
        else:
            conteudo.append(linha)

    if secao_atual:
        chunks.append(montar_chunk(documento["arquivo"], titulo_doc, secao_atual, conteudo))

    return chunks


def montar_chunk(arquivo, titulo_doc, secao, conteudo):
    texto = "\n".join(conteudo).strip()
    return {
        "id": f"{arquivo}#{secao}",
        "arquivo": arquivo,
        "secao": secao,
        "texto": f"{titulo_doc} – {secao}\n{texto}",
    }


if __name__ == "__main__":
    documentos = carregar_documentos("docs")
    todos_chunks = []
    for doc in documentos:
        todos_chunks.extend(dividir_em_chunks(doc))

    print(f"{len(documentos)} documentos → {len(todos_chunks)} chunks\n")
    for chunk in todos_chunks[:3]:
        print("ID:", chunk["id"])
        print(chunk["texto"])
        print("-" * 40)