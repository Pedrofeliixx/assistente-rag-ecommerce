from embeddings import MODELOS, obter_colecao

PERGUNTAS = [
    ("posso devolver um produto que não gostei?", "Arrependimento da compra"),
    ("quanto tempo demora o boleto?", "Boleto bancário"),
    ("vocês entregam hoje?", "Entrega no mesmo dia"),
    ("parcelam no cartão?", "Cartão de crédito"),
    ("meu fone veio com problema", "Produto com defeito"),
    ("tem frete grátis?", "Frete grátis"),
    ("qual o desconto no pix?", "Pix"),
    ("meu pedido está atrasado, o que faço?", "Pedido atrasado"),
    ("quanto tempo de garantia tem o produto?", "Garantia legal"),
    ("o entregador não me encontrou em casa", "Tentativas de entrega"),
]

for versao in MODELOS:
    colecao = obter_colecao(versao)
    acertos_top1 = 0
    acertos_top3 = 0

    print(f"\n===== {versao} =====")
    for pergunta, esperada in PERGUNTAS:
        resultado = colecao.query(query_texts=[pergunta], n_results=3)
        secoes = [m["secao"] for m in resultado["metadatas"][0]]

        if secoes[0] == esperada:
            acertos_top1 += 1
            marca = "✅"
        elif esperada in secoes:
            acertos_top3 += 1
            marca = "🟡"
        else:
            marca = "❌"
        print(f"{marca} {pergunta}  →  {secoes[0]}")

    total = len(PERGUNTAS)
    print(f"Top-1: {acertos_top1}/{total}  |  Top-3: {acertos_top1 + acertos_top3}/{total}")