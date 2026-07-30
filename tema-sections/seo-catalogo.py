#!/usr/bin/env python3
"""Preenche o SEO do catálogo: título, descrição e alt das imagens.

O QUE A AUDITORIA ACHOU (30/07/2026)

  · 10 dos 11 produtos com seo_title E seo_description VAZIOS. Sem eles o
    Google monta o resultado sozinho: o título vira o nome cadastrado
    ("KIT para Bordar: “Le Pont Japonais” – Claude Monet", que gasta os
    caracteres mais valiosos num prefixo genérico) e a descrição vira os
    primeiros 160 caracteres do texto, emendando o título da seção com o
    parágrafo seguinte sem ponto no meio.
  · As 4 categorias sem seo_title, seo_description e sem texto nenhum —
    incluindo /kits-de-bordado/, que é página de dinheiro.
  · TODAS as 47 imagens sem `alt`. (Contei 21 na primeira passada, e estava
    errado: as outras 26 tinham {"pt": ""} — dicionário não-vazio com string
    vazia, que passa num teste `if not alt`.)

Por que o alt importa aqui mais do que na média: o produto é visual e o
Google Imagens é canal de entrada real pra bordado. E alt é acessibilidade —
quem usa leitor de tela hoje ouve "imagem" e nada mais.

Os textos de alt foram escritos OLHANDO cada imagem (duas folhas de contato,
47 fotos), não deduzidos do nome do produto. Descrever a foto errada é pior
que não descrever.

O QUE ESTE SCRIPT GRAVA: seo_title e seo_description de produtos e
categorias. O alt ele NÃO grava — a API não deixa — e por isso vira o
arquivo SEO-ALT-IMAGENS.md, pra colar no admin.

Uso:  python3 seo-catalogo.py --ver    # mostra o que faria
      python3 seo-catalogo.py          # grava (backup antes)
"""

import base64
import json
import pathlib
import sys
import urllib.error
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent
BACKUP = RAIZ / "backup-seo-catalogo.json"
d = json.loads(base64.b64decode((RAIZ.parent / "tema" / ".nube").read_text().strip()))
API = d["theme-api"]
BASE = f"https://api.nuvemshop.com.br/2025-03/{API['storeId']}"
CAB = {"Authentication": f"bearer {API['publicApiToken']}",
       "User-Agent": "museu-em-fios (daniel@vitaminapublicitaria.com.br)",
       "Content-Type": "application/json"}


def req(metodo, caminho, corpo=None):
    r = urllib.request.Request(f"{BASE}/{caminho}", headers=CAB, method=metodo,
                               data=json.dumps(corpo).encode() if corpo else None)
    with urllib.request.urlopen(r, timeout=90) as resp:
        return json.load(resp)


# ------------------------------------------------------- produtos --
# title <= 60 caracteres: acima disso o Google corta no resultado. A obra e o
# artista vêm na frente porque é o que a pessoa digita ("bordado monet",
# "kit klimt"), não "kit para bordar".
# description entre 140 e 158: o que vem depois some, e abaixo de 120 o
# Google costuma reescrever por conta própria.
PRODUTOS = {
    311609908: (
        "Guia de Riscos Jardins de Giverny, de Monet | PDF",
        "Riscos prontos dos jardins de Giverny para bordar: 4 obras de Monet em "
        "tamanho A4, com sugestão de cores fiel à pintura. Download imediato.",
    ),
    312719592: (
        "Guia de Pontos: Pincelada Impressionista em Fios",
        "Aprenda os quatro pontos que reproduzem a pincelada de Monet no bordado, "
        "passo a passo e com foto de cada etapa. Guia digital, download imediato.",
    ),
    314339828: (
        "Guia de Bordado Nymphéas, de Claude Monet | PDF",
        "Borde as ninfeias de Monet do risco ao ponto final: transferência, guia "
        "de cores em duas partes e execução fotografada. Download imediato.",
    ),
    323041676: (
        "Kit de Bordado Le Pont Japonais – Claude Monet",
        "Kit completo para bordar a ponte japonesa de Monet: tela com risco "
        "impresso, linhas, bastidor e guia com foto de cada passo. Envio para "
        "todo o Brasil.",
    ),
    328468700: (
        "Guia de Riscos Art Nouveau: Entre Curvas e Flores",
        "Riscos autorais em Art Nouveau para bordar: curvas, flores e ornamentos "
        "em A4, com sugestão de cores e correspondência Anchor/DMC. Download "
        "imediato.",
    ),
    330154313: (
        "Kit de Bordado Die Umarmung, O Abraço – Klimt",
        "Kit completo para bordar O Abraço, de Gustav Klimt: tela com risco "
        "impresso, linhas selecionadas, bastidor e guia fotografado. Envio para "
        "todo o Brasil.",
    ),
    338097462: (
        "Kit de Bordado para Iniciantes: Nu Bleu II, Matisse",
        "Nunca bordou? Este kit foi desenhado para a primeira obra: material "
        "completo, guia passo a passo com foto de cada etapa e um recorte de "
        "Matisse para começar.",
    ),
    341519753: (
        "Padrões de Gustav Klimt em Bordado | Guia digital",
        "Os ornamentos de Klimt destrinchados em ponto: espirais, olhos e "
        "geometrias em riscos A4, com guia de cores e de execução. Download "
        "imediato.",
    ),
    342413954: (
        "Kit de Bordado Der Kuss, O Beijo – Gustav Klimt",
        "Kit completo para bordar O Beijo, de Klimt: tela com risco impresso, "
        "linhas em dourado e cor, bastidor e guia com foto de cada passo. Envio "
        "para todo o Brasil.",
    ),
    353589659: (
        "Kit de Bordado La Gerbe – Henri Matisse",
        "Kit completo para bordar o recorte de Matisse: tela com risco impresso, "
        "linhas nas cores da obra, bastidor e guia fotografado. Envio para todo "
        "o Brasil.",
    ),
}

# ------------------------------------------------------ categorias --
CATEGORIAS = {
    "Kits de Bordado": (
        "Kits de Bordado de Obras de Arte | Monet e Klimt",
        "Kits completos para bordar obras de Monet, Klimt e Matisse: tela com "
        "risco impresso, linhas, bastidor e guia com foto de cada passo.",
    ),
    "Produtos Digitais": (
        "Guias de Bordado em PDF: Riscos e Pontos | Monet",
        "Guias digitais para bordar arte: riscos em A4, guia de cores e execução "
        "fotografada passo a passo. Download imediato após a compra.",
    ),
}

# ------------------------------------------- alt das imagens (47) --
# A API NÃO grava este campo: o PUT na imagem responde 200 e ignora, o PUT
# pelo produto responde 422. É campo só do admin. Então aqui eles viram
# entregável — gera_lista_alt() escreve o arquivo pra colar em
# Produtos → [produto] → imagem → texto alternativo.
#
# Escritos OLHANDO cada imagem (duas folhas de contato, 47 fotos), não
# deduzidos do nome do produto. Alt errado é pior que alt vazio: quem usa
# leitor de tela ouve a descrição como se fosse a imagem.
#
# Chave: (produto_id, position).
ALTS = {
    # Femme à l’ombrelle — Monet
    (302470130, 1): "Bordado da Femme à l’ombrelle de Monet montado em cavalete de madeira, ao lado de um livro sobre o pintor",
    (302470130, 2): "Conteúdo do kit Femme à l’ombrelle: certificado de autenticidade, postal da obra com QR code, tela com risco impresso, seis meadas Anchor, estojo de algodão e tesoura",
    (302470130, 3): "Caixa do kit Femme à l’ombrelle aberta, com o cartão de agradecimento, a tela e o postal da obra de Monet",
    (302470130, 4): "Mão segurando o cartão com QR code que dá acesso ao guia, sobre a caixa aberta do kit",
    (302470130, 5): "Femme à l’ombrelle, de Claude Monet: mulher com sombrinha verde no alto de uma colina, contra o céu azul",
    # Jardins de Giverny — guia digital
    (311609908, 2): "Riscos do guia Jardins de Giverny impressos em A4, dois bastidores de madeira, tesoura e meadas verdes sobre fundo azul",
    (311609908, 3): "Folhas de risco do guia Jardins de Giverny com bastidores, tesoura e linhas prontas para começar o bordado",
    (311609908, 4): "Capa do guia Jardins de Giverny: pintura de Monet com os arcos de rosas refletidos no lago",
    (311609908, 5): "Sumário do guia Jardins de Giverny, com as quatro obras, riscos em A4 e correspondência de cores Anchor e DMC",
    # Pincelada Impressionista — guia digital
    (312719592, 2): "Capa do Guia de Pontos: amostras bordadas da pincelada impressionista em doze combinações de cor",
    (312719592, 3): "Mãos folheando as páginas do Guia de Pontos ao lado de um bordado impressionista sobre mesa de madeira",
    (312719592, 4): "Sumário do Guia de Pontos, com os quatro pontos da pincelada impressionista e a aplicação em uma obra de Monet",
    # Nymphéas — guia digital
    (314339828, 2): "Capa do Guia de Bordado Nymphéas: as ninfeias bordadas ao lado das folhas de risco e da tesoura",
    (314339828, 3): "Nymphéas bordado sobre tela: ninfeias em rosa e amarelo entre folhas verdes, com tesoura ao lado",
    (314339828, 4): "Mão transferindo o risco das ninfeias para o tecido esticado no bastidor quadrado",
    (314339828, 5): "Sumário do Guia de Bordado Nymphéas, de Claude Monet à execução passo a passo",
    (314339828, 6): "Nymphéas bordado erguido diante da pintura original de Monet, pendurada na parede do museu",
    # Le Pont Japonais — Monet
    (323041676, 1): "Mão segurando o bordado finalizado de Le Pont Japonais: a ponte verde sobre o lago de nenúfares em pontos de fio",
    (323041676, 2): "Caixa do kit Le Pont Japonais aberta, com a tela de risco, o postal da obra, certificado e tesoura",
    (323041676, 3): "Detalhe aproximado do bordado Le Pont Japonais: pontos verdes e creme formando a vegetação e a água",
    (323041676, 4): "Le Pont Japonais, de Claude Monet: a ponte verde sobre o lago de nenúfares do jardim de Giverny",
    # Art Nouveau — guia digital
    (328468700, 2): "Capa do guia Art Nouveau: riscos florais impressos, bastidores de madeira, linhas e tesoura sobre fundo azul-marinho",
    (328468700, 3): "Risco Art Nouveau com flores e curvas ao lado de bastidores, meadas verdes e tesoura de bordado",
    (328468700, 4): "Sumário do guia Art Nouveau: ritmo vertical, flores em silêncio e entre sombras e ouro, com guia de cores",
    # Die Umarmung — Klimt
    (330154313, 1): "Mão segurando o bordado finalizado de Die Umarmung: o casal de Klimt em fios dourados sobre tela",
    (330154313, 2): "Caixa do kit Die Umarmung aberta, com a tela de risco, o postal da obra de Klimt, certificado e tesoura",
    (330154313, 3): "Detalhe aproximado do bordado Die Umarmung: quadrados coloridos e pontos dourados do ornamento de Klimt",
    (330154313, 4): "Die Umarmung, de Gustav Klimt: o abraço entre espirais douradas do Friso Stoclet",
    # Nu Bleu II — Matisse, kit de iniciante
    (338097462, 1): "Mão segurando o bordado finalizado de Nu Bleu II: a figura azul de Matisse sobre tela branca",
    (338097462, 2): "Caixa do kit Nu Bleu II aberta, com a tela de risco, o postal da obra, certificado e tesoura",
    (338097462, 3): "Detalhe aproximado do bordado Nu Bleu II: pontos azuis formando a figura recortada de Matisse",
    # Entre Ornamento e fio — Klimt, guia digital
    (341519753, 1): "Mão segurando as páginas do guia Entre Ornamento e fio: risco A4, anatomia do ornamento e guia de pontos",
    (341519753, 2): "Capa do guia Entre Ornamento e fio: padrões de Gustav Klimt em bordado, com retrato do artista e amostras coloridas",
    (341519753, 3): "Índice do guia Entre Ornamento e fio, dos materiais aos quatro ornamentos de Klimt",
    (341519753, 4): "Referência visual do Ornamento Mosaico: mão segurando o padrão bordado em azul, verde e rosa",
    (341519753, 5): "Referência visual do Ornamento Geométrico: padrão bordado em verde e rosa sobre tela",
    (341519753, 6): "Referência visual do Ornamento Circular: círculos bordados em vermelho e laranja",
    (341519753, 7): "Referência visual do Ornamento Textural: padrão bordado em laranja e azul",
    # Der Kuss — Klimt
    (342413954, 1): "Kit Der Kuss bordado e finalizado sobre tela, segurado na mão: o casal de Klimt em fios dourados e coloridos",
    (342413954, 2): "Caixa do kit Der Kuss aberta, com a tela de risco, o postal da obra de Klimt, certificado e tesoura",
    (342413954, 3): "Detalhe aproximado do bordado Der Kuss: pontos em marrom, vermelho e creme formando o manto do casal",
    (342413954, 4): "Der Kuss, de Gustav Klimt: o casal envolto no manto dourado sobre o campo florido",
    (342413954, 5): "Mão segurando o bordado finalizado de Der Kuss sobre tela quadrada",
    # La Gerbe — Matisse
    (353589659, 1): "Mão segurando o bordado finalizado de La Gerbe: folhas recortadas de Matisse em azul, verde, amarelo e vermelho",
    (353589659, 2): "Caixa do kit La Gerbe aberta, com a tela de risco, o postal da obra de Matisse e tesoura",
    (353589659, 3): "Detalhe aproximado do bordado La Gerbe: folhas em amarelo, laranja e azul em pontos de fio",
    (353589659, 4): "La Gerbe, de Henri Matisse: recortes de folhas coloridas em azul, verde, amarelo e vermelho sobre fundo branco",
}


def gera_lista_alt(prods):
    """Escreve o arquivo pra colar no admin, na ordem em que ele aparece lá."""
    linhas = ["# Texto alternativo das imagens — Museu em Fios", "",
              "A API da Nuvemshop nao grava este campo (o PUT na imagem responde 200 e",
              "ignora; pelo produto responde 422), entao ele so entra pelo admin:",
              "**Produtos → [produto] → clicar na imagem → Texto alternativo**.", "",
              "As 47 imagens estao sem alt hoje. Descricoes escritas olhando cada foto.", ""]
    for p in prods:
        nome = texto(p["name"])
        itens = [(i["position"], ALTS.get((p["id"], i["position"])))
                 for i in sorted(p.get("images", []), key=lambda i: i["position"])]
        if not any(a for _, a in itens):
            continue
        linhas += [f"## {nome}", ""]
        for pos, alt in itens:
            linhas.append(f"{pos}. {alt}" if alt else f"{pos}. _(sem descricao)_")
        linhas.append("")
    (RAIZ / "SEO-ALT-IMAGENS.md").write_text("\n".join(linhas), encoding="utf8")
    print(f"\nlista pra colar no admin: SEO-ALT-IMAGENS.md ({len(ALTS)} descricoes)")


def texto(v):
    return v.get("pt") if isinstance(v, dict) else v


def main():
    ver = "--ver" in sys.argv
    prods, pagina = [], 1
    while True:
        p = req("GET", f"products?per_page=50&page={pagina}")
        prods += p
        if len(p) < 50:
            break
        pagina += 1
    cats = req("GET", "categories?per_page=50")

    if not ver and not BACKUP.exists():
        BACKUP.write_text(json.dumps({
            "produtos": {str(p["id"]): {"seo_title": texto(p.get("seo_title")),
                                        "seo_description": texto(p.get("seo_description")),
                                        "imagens": {str(i["id"]): i.get("alt")
                                                    for i in p.get("images", [])}}
                         for p in prods},
            "categorias": {str(c["id"]): {"seo_title": texto(c.get("seo_title")),
                                          "seo_description": texto(c.get("seo_description"))}
                           for c in cats},
        }, ensure_ascii=False, indent=1), encoding="utf8")
        print(f"backup gravado: {BACKUP.name}\n")

    for p in prods:
        nome = texto(p["name"])
        if p["id"] in PRODUTOS:
            t, dsc = PRODUTOS[p["id"]]
            assert len(t) <= 60, f"title com {len(t)} chars: {t}"
            assert 130 <= len(dsc) <= 165, f"description com {len(dsc)} chars: {dsc}"
            print(f"\n{nome[:58]}")
            print(f"   title ({len(t):2}) {t}")
            print(f"   desc  ({len(dsc):3}) {dsc[:96]}…")
            if not ver:
                req("PUT", f"products/{p['id']}",
                    {"seo_title": {"pt": t}, "seo_description": {"pt": dsc}})

    for c in cats:
        nome = texto(c["name"])
        if nome in CATEGORIAS:
            t, dsc = CATEGORIAS[nome]
            assert len(t) <= 60, f"title com {len(t)} chars: {t}"
            print(f"\ncategoria {nome}")
            print(f"   title ({len(t):2}) {t}")
            print(f"   desc  ({len(dsc):3}) {dsc[:96]}…")
            if not ver:
                req("PUT", f"categories/{c['id']}",
                    {"seo_title": {"pt": t}, "seo_description": {"pt": dsc}})

    gera_lista_alt(prods)
    print("\n(conferência, nada gravado)" if ver else "\ngravado.")


if __name__ == "__main__":
    main()
