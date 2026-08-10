#!/usr/bin/env python3
"""Monta a home do tema sections SEM depender de fork.

POR QUE ESTE CAMINHO EXISTE

A API da Nuvemshop ainda recusa forkar esta loja:

    Fork installation failed (HTTP 400): Forking not yet allowed. Coming soon...

Sem fork, arquivos nossos em `sections/`, `blocks/`, `layouts/` e `static/` são
ignorados — o push "dá certo" e não muda nada (os `static/` chegam a responder
403). Três canais, porém, passam, e foram testados um a um contra o preview:

  1. `templates/pages/home.json` decide a composição da página;
  2. a seção nativa `custom` aceita blocks com tag "general";
  3. o block nativo `code` é injeção crua — `{{ code | raw }}` — de HTML, CSS e
     JS, sem o limite de 15.000 caracteres que trava o `settings.css_code`.

Então a home vira: uma seção `custom` por seção da marca, cada uma com um block
`code` carregando o markup autoral, mais um block com o CSS e outro com o JS.

O markup sai de `demo/index.html`, que é a V1 aprovada e já usa as mesmas
classes `mf-*` que o nosso CSS mira. É montagem, não reescrita.

QUANDO O FORK FOR LIBERADO, JOGUE ISTO FORA. As seções autorais de verdade
(`sections/museu-*.tpl`) continuam no repositório, editáveis pela cliente no
admin — que é o ponto da migração. Este arquivo é a ponte até lá, e o preço
dela é que a home volta a ser markup fixo.

Uso:  python3 montar-home-sem-fork.py [--imagens urls.json]
"""

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent
REPO = RAIZ.parent
BUILD = REPO / "build-tema"
DEMO = REPO / "demo" / "index.html"
INSTALACAO = "14038757"  # instalação publicada da loja

# Vídeo institucional da noite. É só o PADRÃO de primeira montagem: se a
# cliente trocar pelo editor, o valor publicado vence (ver home_publicada).
VIDEO_PADRAO = {
    "type": "youtube",
    "id": "U1xtk1YRrBM",
    # capa: o YouTube serve o frame em alta; sem isto o player abre num
    # retângulo preto até a pessoa clicar
    "thumbnail": "https://i.ytimg.com/vi/U1xtk1YRrBM/maxresdefault.jpg",
}

# As 6 seções da marca, na ordem da home aprovada. O seletor é o elemento de
# topo de cada uma dentro da demo.
SECOES = [
    ("museu-hero", r'<section class="mf-hero"'),
    ("museu-marquee", r'<div class="mf-marquee"'),
    ("museu-manifesto", r'<section class="mf-manifesto"'),
    ("museu-noite", r'<section class="mf-noite"'),
    ("museu-vitrine", r'<section class="mf-vitrine">'),
    ("museu-passos", r'<section class="mf-passos"'),
    ("museu-kit", r'<section class="mf-kit" id="kit"'),
    ("museu-iniciante", r'<section class="mf-kit mf-kit--claro"'),
    ("museu-digitais", r'<section class="mf-vitrine" id="digitais-home"'),
]
# Fora por decisão: mf-insta (grade decorativa, exige mais 6 imagens hospedadas) e mf-news
# (o rodapé já tem newsletter nativa funcionando, com o cupom).

# Vitrine de kits: a demo traz 6 cards com preços de outra época. Os dados
# abaixo vieram da API em 29/07/2026 — preço real, link real, e só produto
# PUBLICADO (femme e le-chevalier caem fora até serem publicados).
VITRINE_KITS = {
    "monet-ponte-japonesa": {
        "href": "/produtos/kit-de-bordado-le-pont-japonais-claude-monet/",
        "preco": "R$ 189"},
    "klimt-die-umarmung": {
        "href": "/produtos/pre-venda-kit-de-bordado-die-umarmung-gustav-klimt/",
        "preco": "R$ 199"},  # selo Pré-venda removido a pedido (29/07)
    "klimt-der-kuss": {
        "href": "/produtos/kit-de-bordado-der-kuss-gustav-klimt/",
        "preco": "R$ 199"},
    "la-gerbe": {
        "href": "/produtos/kit-para-bordado-la-gerbe-henri-matisse-pko6p/",
        "preco": "R$ 179"},
}


def cirurgia_vitrine(markup: str) -> str:
    """Poda e atualiza os cards da vitrine de kits contra o catálogo real."""
    partes = re.split(r'(<a class="obra-card".*?</a>)', markup, flags=re.S)
    out = []
    for parte in partes:
        if not parte.startswith('<a class="obra-card'):
            out.append(parte)
            continue
        chave = next((k for k in VITRINE_KITS if k in parte), None)
        if not chave:
            continue  # produto despublicado ou inexistente: card sai
        dados = VITRINE_KITS[chave]
        parte = re.sub(r'href="[^"]*"', f'href="{dados["href"]}"', parte, count=1)
        parte = re.sub(r'(<span class="obra-card__preco">).*?(</span>)',
                       rf'\g<1>{dados["preco"]}\g<2>', parte, flags=re.S)
        if dados.get("selo"):
            if "obra-card__selo" in parte:
                parte = re.sub(r'(<span class="obra-card__selo[^"]*">).*?(</span>)',
                               rf'\g<1>{dados["selo"]}\g<2>', parte, count=1, flags=re.S)
            else:
                parte = re.sub(r'(<a class="obra-card"[^>]*>)',
                               rf'\g<1><span class="obra-card__selo">{dados["selo"]}</span>',
                               parte, count=1)
        else:
            parte = re.sub(r'<span class="obra-card__selo[^"]*">.*?</span>\s*', '',
                           parte, flags=re.S)
        out.append(parte)
    return "".join(out)


# Handle do kit de entrada. Guarda o nome antigo (le-chevalier) de quando o
# produto era o Klimt — trocar o handle quebraria link já indexado.
INICIANTE_URL = ("/produtos/kit-de-bordado-klimt-para-quem-nunca-bordou-"
                 "le-chevalier-material-completo-video-aulas/")


def atualizar_iniciante(markup: str) -> str:
    """Acerta a seção do kit de iniciante contra o catálogo de hoje.

    A demo foi escrita quando o kit de entrada era o "Le Chevalier", de
    Klimt. Hoje o produto é "Matisse para quem nunca Bordou — NU BLEU II".
    Publicado em 30/07/2026, então o botão passa a apontar pro produto — até
    aqui ele mandava pra categoria, porque o produto estava oculto.

    O handle guarda o nome antigo (le-chevalier) porque trocá-lo quebraria
    qualquer link já indexado; é cosmético na URL e não vale o risco.
    """
    # o texto da demo quebra linha no meio da frase, então a troca precisa
    # tolerar espaços/newlines (replace literal não pegava)
    markup = re.sub(r"O kit\s*<em>Le Chevalier</em>,\s*de Gustav Klimt,",
                    "O kit <em>Nu Bleu II</em>, de Henri Matisse,", markup)
    markup = re.sub(r"Começar pelo\s+Le Chevalier", "Começar pelo Nu Bleu II", markup)
    markup = re.sub(r"Kit Le Chevalier:", "Kit Nu Bleu II:", markup)
    markup = markup.replace('href="/kits-de-bordado/"', f'href="{INICIANTE_URL}"')
    return markup


# ------------------------------------------------ vitrine em blocks nativos --
# A vitrine deixou de ser markup fixo: cada card virou um `group` com um bloco
# de imagem e um de texto. A cliente adiciona, remove e reordena kit no editor
# do tema, sem depender da gente — que era o pedido, e o motivo de o Nu Bleu II
# ter ficado esperando.
#
# Por que group + image + text, e não o `category-item` (que tem imagem, texto
# e link num campo só): testei os dois no ar, e o campo de imagem do
# category-item não renderiza — o template dele tem um guard interno
# (`is_image_thumbnail`) que só é verdadeiro dentro da seção de categorias.
# O bloco `image`, esse aceita URL do CDN e sai com srcset e lazyload.
#
# Cada card leva DOIS blocos de imagem: a obra original e a foto do bordado
# pronto, que aparece no hover — a troca obra → interpretação em fios é a
# interação assinatura da demo, e ela sobrevive à conversão porque é só
# opacidade entre dois <img> empilhados.
#
# O texto usa as MESMAS classes da demo (.obra-card__*), então as regras de
# museu-theme.css valem sem cópia: o nome do artista grande sobre a obra, a
# ficha na base e a barra "Ver o kit →" subindo no hover. O que o skin precisa
# resolver é só o que a estrutura do tema muda de lugar.
VITRINE_CARDS = [
    {"id": "lepont", "artista": "Monet", "obra": "Le Pont Japonais",
     "preco": "R$ 189", "cor": "#9cad4e",
     "href": "/produtos/kit-de-bordado-le-pont-japonais-claude-monet/",
     "img": "obra-original-monet-ponte-japonesa-sq-e171a6d2007d0cab3817853430576079",
     "foto": "kit-para-bordar-le-pont-japonais-claude-monet-1-fc3f4d3c752c59d30617854169030794"},
    {"id": "umarmung", "artista": "Klimt", "obra": "Die Umarmung",
     "preco": "R$ 199", "cor": "#f2c440",
     "href": "/produtos/pre-venda-kit-de-bordado-die-umarmung-gustav-klimt/",
     "img": "obra-original-klimt-die-umarmung-sq-4a49c88016c9e7f85a17853430557773",
     "foto": "kit-para-bordar-die-umarmung-o-abraco-gustav-kli-1-ff5f3f301734e7d20b17854169091892"},
    # A foto do hover é a CAPA do produto (o bordado na mão), não a "-2-" (a
    # caixa do kit): o José apontou por print que a revelação mostrava a foto
    # errada. A capa era o PNG de 2,1 MB sem variantes — depois da troca
    # in-place pra JPG ela ganhou as variantes do CDN (conferido por HEAD).
    {"id": "derkuss", "artista": "Klimt", "obra": "Der Kuss",
     "preco": "R$ 199", "cor": "#f2c440",
     "href": "/produtos/kit-de-bordado-der-kuss-gustav-klimt/",
     "img": "obra-original-klimt-der-kuss-sq-1320433b3fa77518ee17853455183558",
     "foto": "kit-de-bordado-der-kuss-klimt-capa-cf3c808b125ead929a17853487083200"},
    # O azul dos dois Matisse é o tom que a Isabella mandou por swatch no
    # WhatsApp (31/07), amostrado do print: #475dca. Preto em cima dele dá
    # contraste 3,2:1 (reprova); papel dá 5,4:1 — por isso o texto= papel.
    {"id": "lagerbe", "artista": "Matisse", "obra": "La Gerbe",
     "preco": "R$ 179", "cor": "#475dca", "texto": "#fbfaf6",
     "href": "/produtos/kit-para-bordado-la-gerbe-henri-matisse-pko6p/",
     "img": "obra-original-matisse-la-gerbe-sq-e2052deae3c1306d8417853522411805",
     "foto": "kit-para-bordar-la-gerbe-henri-matisse-1-2430600b61db54733417854169294364"},
    # Publicado em 30/07 e com a obra subida pela cliente na posição 4.
    # O selo é o obra-card__selo da demo (o mesmo do "Pré-venda") — pedido
    # da cliente em 31/07: marcar o kit de entrada na home.
    {"id": "nubleu", "artista": "Matisse", "obra": "Nu Bleu II",
     "preco": "R$ 149", "cor": "#475dca", "texto": "#fbfaf6",
     "selo": "Iniciante",
     "href": INICIANTE_URL,
     "img": "nu-d881b9500f7785b21017855220489403",
     "foto": "kit-para-bordar-matisse-para-quem-nunca-bordou-n-1-02844faa3edde686a017854169153819"},
]

CDN = "https://acdn-us.mitiendanube.com/stores/006/671/481/products/"


def vitrine_em_blocks() -> dict:
    """Monta os blocks da vitrine: um `group` por kit."""
    blocks = {
        "topo": bloco_code(
            '<div class="mf-vitrine__topo">'
            '<div><p class="mf-eyebrow">Coleção permanente</p>'
            '<h2 class="mf-h2">Kits para bordar</h2></div>'
            '<a class="mf-link" href="/kits-de-bordado/">Ver todos os kits</a>'
            "</div>"),
    }
    for c in VITRINE_CARDS:
        imagem = lambda arquivo: {"type": "image", "settings": {
            "image": f"{CDN}{arquivo}-640-0.webp",
            "link": c["href"], "width": "fill"}}
        estilo = {
            "direction": "column", "gap": 0,
            "vertical_padding": 0, "horizontal_padding": 0,
            "custom_background_color": c["cor"],
        }
        if c.get("texto"):
            # fundo escuro pede ficha clara; o nome do artista fica preto
            # via CSS, porque ele está sobre a obra, não sobre o fundo
            estilo["custom_text_color"] = c["texto"]
        blocks[c["id"]] = {
            "type": "group",
            "settings": estilo,
            "blocks": {
                "obra": imagem(c["img"]),
                "foto": imagem(c["foto"]),
                "ficha": {"type": "text", "settings": {"text":
                    (f'<p class="obra-card__selo">{c["selo"]}</p>'
                     if c.get("selo") else "")
                    + f'<p class="obra-card__artista">{c["artista"]}</p>'
                    f'<p class="obra-card__base">'
                    f'<span class="obra-card__obra">'
                    f'<span class="obra-card__tipo">Kit de bordado</span>'
                    f'{c["obra"]}</span>'
                    f'<span class="obra-card__preco">{c["preco"]}</span></p>'
                    f'<p class="obra-card__cta">Ver o kit →</p>'}},
            },
        }
    return blocks


# A CDN da Nuvemshop gera variantes por tamanho E em webp — basta pedir a
# extensão na URL (o header Accept não muda nada). Conferido por HEAD nas 15
# imagens do mapa: as quatro variantes existem em todas.
#
# O PSI apontou "melhorar a entrega de imagens: 8.987 KiB" e LCP de 31,2 s. A
# causa é que seis das capas foram salvas em PNG: foto 1024x1024 em PNG dá
# ~2 MB, a mesma em webp dá ~180 KB. Somando as 15: 15,16 MB hoje contra
# 2,06 MB em -640-0.webp — e o -640-0.webp é MENOR que o arquivo atual em
# todos os 15 casos, medido um por um.
#
# Sem <picture> de fallback de propósito: o próprio tema já serve o logo em
# .webp sem fallback, ou seja a plataforma assume suporte.
VARIANTES_IMG = (320, 480, 640)


def otimizar_imagens(markup: str, teto: int = 640) -> str:
    """Troca as imagens do CDN por webp com srcset.

    `teto` é a maior variante oferecida. 640 para os cards, que aparecem em
    no máximo 390px de tela; o hero vai a 1024 porque é o elemento do LCP e
    é um por slide. Não incluir a variante maior é deliberado: se ela estiver
    no srcset, aparelho com DPR 3 escolhe ela e o ganho vai embora.
    """
    larguras = [w for w in VARIANTES_IMG if w <= teto]

    def trocar(m: re.Match) -> str:
        tag, src = m.group(0), m.group(1)
        if "mitiendanube" not in src or "-1024-1024." not in src or "srcset=" in tag:
            return tag
        base = src.rsplit("-1024-1024.", 1)[0]
        fontes = [f"{base}-{w}-0.webp {w}w" for w in larguras]
        if teto >= 1024:
            fontes.append(f"{base}-1024-1024.webp 1024w")
        principal = (f"{base}-1024-1024.webp" if teto >= 1024
                     else f"{base}-{larguras[-1]}-0.webp")
        tag = tag.replace(src, principal)
        return tag[:-1] + (f' srcset="{", ".join(fontes)}"'
                           ' sizes="(max-width: 768px) 92vw, 30rem">')

    return re.sub(r'<img[^>]*src="([^"]+)"[^>]*>', trocar, markup)


def melhorar_hero(markup: str) -> str:
    """Ajustes de SEO e conversão no hero, depois dos links resolvidos.

    - o descritor vira <h2>: o h1 do tema é invisível e a página ficava sem
      heading com palavra-chave no topo;
    - a imagem da obra vira link pro mesmo destino do "Acessar kit" do slide —
      antes o único clicável era um link de texto de 15px;
    - no slide sem produto publicado o rótulo diz a verdade: "Ver a coleção".
      Com os três produtos publicados isso não pega hoje; fica pro dia em que
      entrar obra nova antes do kit dela.

    As variantes de imagem saíram daqui: agora é otimizar_imagens(), que vale
    pra TODAS as seções, não só o hero.
    """
    markup = re.sub(r'<p class="mf-hero__descritor"(.*?)</p>',
                    r'<h2 class="mf-hero__descritor"\1</h2>', markup, flags=re.S)

    palcos = re.split(r'(?=<div class="mf-hero__palco")', markup)
    for i, chunk in enumerate(palcos):
        if not chunk.startswith('<div class="mf-hero__palco'):
            continue
        destino = re.search(r'href="([^"]+)"', chunk)
        if destino:
            chunk = re.sub(
                r'(<div class="mf-hero__obra">\s*)(<img[^>]+>)',
                rf'\g<1><a href="{destino.group(1)}" tabindex="-1" aria-hidden="true">\g<2></a>',
                chunk, count=1)
        palcos[i] = chunk
    markup = "".join(palcos)

    markup = re.sub(r'(href="/kits-de-bordado/"[^>]*>)Acessar kit<',
                    r'\g<1>Ver a coleção<', markup)
    return markup



def limpar(texto: str) -> str:
    """Normaliza espaços do markup da demo, preservando <br> e <em>."""
    return re.sub(r"\s+", " ", texto).strip()


def home_publicada():
    """Baixa o home.json PUBLICADO na loja.

    A preservação ANTES lia o home.json do build — que este mesmo script
    acabara de reescrever. Circular: toda remontagem devolvia os valores
    padrão e apagava o que a cliente tinha editado no editor (aconteceu com
    o vídeo). A fonte de verdade é a loja, então buscamos de lá.

    Devolve None se o pull falhar; nesse caso o chamador AVISA e usa o
    padrão, em vez de sobrescrever no escuro.
    """
    nube = REPO / "tema" / ".nube"
    if not nube.exists():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        destino = pathlib.Path(tmp)
        shutil.copy(nube, destino / ".nube")
        try:
            subprocess.run(
                ["npx", "@tiendanube/cli@1.2.1", "theme", "pull",
                 "--installation-id", INSTALACAO, "-y"],
                cwd=destino, check=True, capture_output=True, timeout=420)
            return json.loads((destino / "templates" / "pages" / "home.json")
                              .read_text(encoding="utf8"))
        except (subprocess.SubprocessError, OSError, json.JSONDecodeError):
            return None


# Seções que o `--refazer` mandou remontar do código. Vive aqui, e não só no
# main(), pra valer nos quatro pontos de preservação sem repetir a checagem.
REFAZER: set[str] = set()


def blocks_preservados(vivo, nome_secao, chave):
    """Devolve a seção publicada se ela já está em blocks nativos."""
    if not vivo or nome_secao in REFAZER:
        return None
    try:
        secao = vivo["sections"][nome_secao]
        if chave in secao.get("blocks", {}):
            return secao
    except (KeyError, TypeError):
        pass
    return None



def com_layout(preservado: dict, **ajustes) -> dict:
    """Mantém os blocks publicados (conteúdo da cliente) e reaplica o layout.

    A preservação inteira congelava também os settings da seção — então uma
    correção de largura/cor no código nunca chegava ao ar. A divisão certa é:
    conteúdo (blocks, que a cliente edita) vem da loja; layout (settings da
    seção) vem daqui.

    O otimizador de imagem roda também aqui: o visual do kit vive num block
    `code` preservado, e sem isso ele ficava de fora — justamente uma capa de
    2,1 MB em PNG. Como a troca é idempotente (só casa `-1024-1024.` e pula o
    que já tem srcset), rodar em conteúdo já otimizado não faz nada.
    """
    blocks = json.loads(json.dumps(preservado.get("blocks", {})))  # não mexe no original
    for bloco in blocks.values():
        code = bloco.get("settings", {}).get("code")
        if isinstance(code, str) and "mitiendanube" in code:
            bloco["settings"]["code"] = otimizar_imagens(code)
    secao = secao_custom(blocks, **ajustes)
    if "block_order" in preservado:
        secao["block_order"] = preservado["block_order"]
    return secao


def extrair(html: str, inicio_re: str) -> str:
    """Recorta um elemento inteiro, casando as tags de abertura e fechamento.

    Regex sozinha não serve: as seções têm divs aninhadas com a mesma tag, e
    parar no primeiro `</section>` cortaria a seção pela metade.
    """
    m = re.search(inicio_re, html)
    if not m:
        raise SystemExit(f"não achei o trecho {inicio_re!r} em {DEMO}")
    tag = re.match(r"<(\w+)", m.group(0)).group(1)
    pos, profundidade = m.start(), 0
    for t in re.finditer(rf"<(/?){tag}\b[^>]*?(/?)>", html[m.start():]):
        profundidade += 1 if not t.group(1) and not t.group(2) else (-1 if t.group(1) else 0)
        if profundidade == 0:
            return html[m.start(): m.start() + t.end()]
    raise SystemExit(f"não achei o fechamento de <{tag}> a partir de {pos}")


def trocar_imagens(markup: str, mapa: dict) -> tuple[str, list]:
    """Troca os caminhos locais da demo pelas URLs do CDN da loja."""
    pendentes = []
    for local in sorted(set(re.findall(r'(?:src|href)="(assets/img/[^"]+)"', markup))):
        arquivo = local.rsplit("/", 1)[-1]
        if arquivo in mapa:
            markup = markup.replace(f'"{local}"', f'"{mapa[arquivo]}"')
        else:
            pendentes.append(arquivo)
    return markup, pendentes


# A demo navega entre arquivos .html; a loja tem URLs próprias. Sem esta
# troca os links quebrados vazam pro ar (aconteceu: "Ver o kit" levava a
# /produto.html, que não existe).
LINKS_GLOBAIS = {
    "index.html": "/",
    "loja.html#digitais": "/produtos-digitais/",  # antes de loja.html, que é prefixo
    "loja.html": "/kits-de-bordado/",
    "sobre.html": "/quem-somos/",
}

# `produto.html` aparece três vezes no hero — uma por obra — e o destino
# certo depende de QUAL obra. A âncora vem depois da imagem no markup, então
# a imagem `obra-original-…` mais próxima ANTES do href identifica o produto.
PRODUTO_POR_IMAGEM = {
    # O Femme (id 302470130) foi PUBLICADO — conferido em 10/08/2026, a URL
    # responde produto com preço e estoque. Enquanto estava despublicado o
    # slide mandava pra categoria; agora vai pro produto, que é o pedido do
    # Daniel: a obra do hero abre o kit dela, não a loja inteira.
    "obra-original-monet-femme-ombrelle": "/produtos/kit-de-bordado-femme-a-lombrelle-claude-monet/",
    "obra-original-klimt-die-umarmung": "/produtos/pre-venda-kit-de-bordado-die-umarmung-gustav-klimt/",
    "obra-original-monet-ponte-japonesa": "/produtos/kit-de-bordado-le-pont-japonais-claude-monet/",
}


def trocar_links(markup: str, com_obras: bool = False) -> tuple[str, list]:
    """Reescreve a navegação da demo para as URLs reais da loja.

    com_obras: no hero, o alvo do link depende de QUAL obra está ao lado — e
    a demo não ajuda: só o Femme tinha mockup de produto, então os slides 2 e
    3 apontavam pra loja.html. Aqui, dentro do hero, produto.html E loja.html
    viram o produto da obra-original mais próxima ANTES do link (a âncora vem
    depois da imagem no markup). Sem obra antes — caso do descritor no topo —
    cai na loja, que é o destino honesto.
    """
    if com_obras:
        def produto_certo(m: re.Match) -> str:
            antes = markup[: m.start()]
            ultima = None
            for chave in PRODUTO_POR_IMAGEM:
                pos = antes.rfind(chave)
                if pos >= 0 and (ultima is None or pos > ultima[0]):
                    ultima = (pos, chave)
            if ultima:
                return f'href="{PRODUTO_POR_IMAGEM[ultima[1]]}"'
            return 'href="/kits-de-bordado/"'

        markup = re.sub(r'href="(?:produto|loja)\.html"', produto_certo, markup)

    for demo, loja in LINKS_GLOBAIS.items():
        markup = markup.replace(f'href="{demo}"', f'href="{loja}"')
    markup = markup.replace('href="produto.html"', 'href="/kits-de-bordado/"')

    sobras = sorted(set(re.findall(r'href="([a-z-]+\.html[^"]*)"', markup)))
    return markup, sobras


def bloco_code(codigo: str, largura: str = "fill") -> dict:
    return {"type": "code", "settings": {"code": codigo, "width": largura}}


def secao_custom(blocks: dict, **ajustes) -> dict:
    # ATENÇÃO: `custom_background_color` vira STYLE INLINE na section
    # (custom.tpl), então ele — não o CSS da pele — é quem manda no fundo.
    # Seção com fundo próprio (a noite é preta) precisa passar a cor AQUI;
    # tentar pintar pelo CSS perde do inline e a seção sai clara.
    settings = {
        "section_width": "full",
        "direction": "column",
        "mobile_direction_enabled": False,
        "alignment": "start",
        "gap": 0,
        "vertical_padding": 0,
        "horizontal_padding": 0,
        "custom_background_color": "transparent",
    }
    settings.update(ajustes)
    return {"type": "custom", "settings": settings, "blocks": blocks}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--imagens", default=str(RAIZ / "imagens-cdn.json"),
                    help="JSON {nome-do-arquivo.jpg: url-do-cdn}")
    # A preservação existe pra não apagar o que a cliente editou no editor —
    # e por isso ela também congela um erro NOSSO que já subiu. Quando é o
    # nosso código que precisa vencer, o descarte tem que ser dito em voz alta.
    # Só use sabendo que os blocks publicados daquela seção vão embora.
    ap.add_argument("--refazer", default="", metavar="secao,secao",
                    help="remonta estas seções do código, DESCARTANDO os "
                         "blocks publicados (ex.: --refazer museu-vitrine)")
    args = ap.parse_args()
    REFAZER.update(s.strip() for s in args.refazer.split(",") if s.strip())
    if REFAZER:
        print(f"  --refazer: {', '.join(sorted(REFAZER))} "
              "— os blocks publicados destas seções serão DESCARTADOS")

    if not BUILD.exists():
        raise SystemExit(f"Rode antes: ./montar-tema.sh <ID>  (não achei {BUILD})")

    mapa = {}
    caminho_mapa = pathlib.Path(args.imagens)
    if caminho_mapa.exists():
        # chaves com "_" são comentários do arquivo; valor vazio é pendência
        mapa = {k: v for k, v in json.loads(caminho_mapa.read_text(encoding="utf8")).items()
                if not k.startswith("_") and v}

    html = DEMO.read_text(encoding="utf8")
    css = ((RAIZ / "static/css/museu-theme.css").read_text(encoding="utf8")
           + "\n" + (RAIZ / "static/css/museu-ponte.css").read_text(encoding="utf8"))
    # Os @font-face apontam pra ../fonts/, que não existe quando o CSS viaja
    # inline — eram três requests 404 por visita. As fontes chegam pelo
    # @import do css_code (Inter + Roboto Serif variáveis, com itálico).
    css = re.sub(r"@font-face\s*\{[^}]*\}\s*", "", css)
    motion = (RAIZ / "static/js/museu-motion.js").read_text(encoding="utf8")

    sections, ordem, todas_pendentes = {}, [], []

    # O CSS vai primeiro, numa seção de altura zero: precisa estar no documento
    # antes do markup pra não haver salto de layout.
    sections["museu-estilo"] = secao_custom(
        {"css": bloco_code(f"<style>\n{css}\n</style>")})
    ordem.append("museu-estilo")

    # Se a cliente trocou o vídeo pelo editor, o valor vive no home.json da
    # loja — preserva o que estiver no build (REGRA: antes de remontar a
    # home, rode `theme pull` pra trazer edições feitas no editor).
    print("  lendo o que está publicado na loja (pra não sobrescrever edições)…")
    vivo = home_publicada()
    if vivo is None:
        print("  AVISO: não consegui ler a loja — vou usar os padrões do código.")
        print("         Se a cliente editou algo no editor, confira antes de subir.")
    destino_home = BUILD / "templates" / "pages" / "home.json"

    video_atual = VIDEO_PADRAO
    if vivo:
        try:
            guardado = (vivo["sections"]["museu-noite"]["blocks"]["player"]
                        ["settings"]["video_url"])
            # a edição da cliente só vence se for OUTRO vídeo (não o antigo
            # que este script mesmo plantou antes de o padrão ser corrigido)
            if guardado and guardado.get("id") not in (None, "", "Q2dJHg6M9jw"):
                video_atual = guardado
        except (KeyError, TypeError):
            pass
    print(f"  vídeo da noite: {video_atual.get('id')}")

    for nome, seletor in SECOES:
        if nome == "museu-vitrine":
            # Blocks NATIVOS: a cliente adiciona kit sozinha no editor. Preserva
            # o que estiver publicado (cards que ela tenha criado ou editado) e
            # só reaplica o layout, como nas outras seções convertidas.
            if preservado := blocks_preservados(vivo, nome, "topo"):
                sections[nome] = com_layout(preservado, section_width="full")
                print(f"  {nome:18}    (cards preservados da loja)")
            else:
                sections[nome] = secao_custom(vitrine_em_blocks(), section_width="full")
                print(f"  {nome:18}    {len(VITRINE_CARDS)} cards em blocks nativos")
            ordem.append(nome)
            continue

        markup = extrair(html, seletor)
        markup, pendentes = trocar_imagens(markup, mapa)
        markup, links_sobrando = trocar_links(markup, com_obras=(nome == "museu-hero"))
        # webp + srcset em toda seção. O hero vai a 1024 porque a obra dele é
        # o elemento do LCP; o resto para em 640, que já é 2x pro maior card.
        markup = otimizar_imagens(markup, teto=1024 if nome == "museu-hero" else 640)
        if nome == "museu-hero":
            markup = melhorar_hero(markup)

        if nome == "museu-iniciante":
            markup = atualizar_iniciante(markup)

        if nome == "museu-manifesto":
            # PILOTO da editabilidade sem fork (aprovado pelo Daniel): o
            # manifesto vira blocks NATIVOS — a cliente edita a frase, o
            # apoio e o botão em campos de verdade no editor. O grafismo do
            # fio segue num code block; a pele estiliza via .mf-alvo-manifesto.
            # Preservação: se o build já tem a versão em blocks (possível
            # edição da cliente trazida por `theme pull`), mantém como está.
            if preservado := blocks_preservados(vivo, nome, "frase"):
                sections[nome] = com_layout(preservado, alignment="start",
                                            section_width="full")
                ordem.append(nome)
                print(f"  {nome:18}    (blocks preservados da loja)")
                continue
            eyebrow = re.search(r'class="mf-eyebrow"[^>]*>\s*(.*?)\s*</p>', markup, re.S)
            frase = re.search(r'class="mf-manifesto__frase[^"]*"[^>]*>\s*(.*?)\s*</p>', markup, re.S)
            apoio = re.search(r'class="mf-manifesto__apoio"[^>]*>\s*(.*?)\s*</p>', markup, re.S)
            if frase and apoio:
                corpo = apoio.group(1)
                botao = re.search(r'<a class="mf-link" href="([^"]+)"[^>]*>(.*?)</a>', corpo, re.S)
                corpo = re.sub(r'(<br>\s*)*<a class="mf-link".*?</a>', '', corpo, flags=re.S).strip()
                corpo = re.sub(r'\s+', ' ', corpo)
                sections[nome] = secao_custom({
                    "abre": bloco_code('<span class="mf-alvo-manifesto" hidden></span>'
                                       '<div class="mf-manifesto__fio" data-fio></div>'),
                    "eyebrow": {"type": "text", "settings": {
                        "text": re.sub(r'\s+', ' ', eyebrow.group(1)) if eyebrow else "Museu em Fios",
                        "size": "small"}},
                    "frase": {"type": "heading", "settings": {
                        "title": re.sub(r'\s+', ' ', frase.group(1)), "size": "h2"}},
                    "apoio": {"type": "text", "settings": {"text": f"<p>{corpo}</p>"}},
                    "botao": {"type": "button", "settings": {
                        "label": re.sub(r'\s+', ' ', botao.group(2)) if botao else "Conheça o projeto",
                        "link": (LINKS_GLOBAIS.get(botao.group(1), botao.group(1))
                                 if botao else "/quem-somos/"),
                        "variant": "primary"}},
                }, alignment="start", section_width="full")
                ordem.append(nome)
                print(f"  {nome:18}    (blocks nativos editáveis)")
                continue

        if nome == "museu-passos":
            if preservado := blocks_preservados(vivo, nome, "titulo"):
                sections[nome] = com_layout(preservado, section_width="full",
                                            custom_background_color="#1D1D1B")
                ordem.append(nome)
                print(f"  {nome:18}    (blocks preservados da loja)")
                continue
            eyebrow = re.search(r'class="mf-eyebrow"[^>]*>\s*(.*?)\s*</p>', markup, re.S)
            titulo = re.search(r'class="mf-h2"[^>]*>\s*(.*?)\s*</h2>', markup, re.S)
            blocos = {
                "eyebrow": {"type": "text", "settings": {
                    "text": limpar(eyebrow.group(1)) if eyebrow else "A experiência",
                    "size": "small"}},
                "titulo": {"type": "heading", "settings": {
                    "title": limpar(titulo.group(1)) if titulo else "", "size": "h2"}},
            }
            # Cada passo vira um `group` com título e texto — a numeração
            # 01..NN sai de counter no CSS, então passo novo numera sozinho.
            for n, art in enumerate(re.finditer(
                    r'<article class="mf-passo">(.*?)</article>', markup, re.S), start=1):
                corpo = art.group(1)
                h3 = re.search(r"<h3>(.*?)</h3>", corpo, re.S)
                p = re.search(r"<p>(.*?)</p>", corpo, re.S)
                blocos[f"passo{n}"] = {"type": "group", "settings": {
                    "direction": "column", "gap": 8,
                    "vertical_padding": 0, "horizontal_padding": 0,
                }, "blocks": {
                    "titulo": {"type": "heading", "settings": {
                        "title": limpar(h3.group(1)) if h3 else "", "size": "h4"}},
                    "texto": {"type": "text", "settings": {
                        "text": f"<p>{limpar(p.group(1))}</p>" if p else ""}},
                }}
            sections[nome] = secao_custom(blocos, section_width="full",
                                          custom_background_color="#1D1D1B")
            ordem.append(nome)
            print(f"  {nome:18}    ({len(blocos) - 2} passos em blocks nativos)")
            continue

        if nome == "museu-kit":
            preservado = blocks_preservados(vivo, nome, "titulo")
            # NÃO preserva versão contaminada: se o markup do visual carrega o
            # eyebrow, veio da extração antiga (bug abaixo) e precisa refazer
            if preservado:
                code_visual = (preservado.get("blocks", {}).get("visual", {})
                               .get("settings", {}).get("code", ""))
                if "mf-eyebrow" in code_visual:
                    print(f"  {nome:18}    (visual contaminado na loja — remontando)")
                    preservado = None
            if preservado:
                sections[nome] = com_layout(preservado, section_width="full",
                                            custom_background_color="#F2C440")
                ordem.append(nome)
                print(f"  {nome:18}    (conteúdo da loja + layout do código)")
                continue
            # extrair() conta as tags. O regex antigo (`.*?</div>\\s*</div>`)
            # passava do fim do visual e engolia a abertura da coluna de texto,
            # jogando eyebrow/título/lista DENTRO do bloco da imagem — fora da
            # grade, e o kit virava coluna única.
            visual_html = extrair(markup, r'<div class="mf-kit__visual"')
            eyebrow = re.search(r'class="mf-eyebrow"[^>]*>\s*(.*?)\s*</p>', markup, re.S)
            titulo = re.search(r'class="mf-h2"[^>]*>\s*(.*?)\s*</h2>', markup, re.S)
            lista = re.search(r'(<ul class="mf-kit__lista".*?</ul>)', markup, re.S)
            nota = re.search(r'class="mf-kit__nota"[^>]*>\s*(.*?)\s*</p>', markup, re.S)
            botao = re.search(r'<a class="mf-btn" href="([^"]+)"[^>]*>\s*(.*?)\s*</a>', markup, re.S)
            # A lista virou <ol> editável: os números saem de counter, então a
            # cliente adiciona/remove item sem renumerar na mão.
            itens = re.findall(r'<li>.*?</span>\s*(.*?)</li>', lista.group(1), re.S) if lista else []
            sections[nome] = secao_custom({
                "visual": bloco_code(visual_html),
                "eyebrow": {"type": "text", "settings": {
                    "text": limpar(eyebrow.group(1)) if eyebrow else "O que vem no kit",
                    "size": "small"}},
                "titulo": {"type": "heading", "settings": {
                    "title": limpar(titulo.group(1)) if titulo else "", "size": "h2"}},
                "lista": {"type": "text", "settings": {
                    "text": "<ol>" + "".join(f"<li>{limpar(i)}</li>" for i in itens) + "</ol>"}},
                "nota": {"type": "text", "settings": {
                    "text": f"<p>{limpar(nota.group(1))}</p>" if nota else ""}},
                "botao": {"type": "button", "settings": {
                    "label": limpar(botao.group(2)) if botao else "Escolher meu kit",
                    "link": (LINKS_GLOBAIS.get(botao.group(1), botao.group(1))
                             if botao else "/kits-de-bordado/"),
                    "variant": "primary"}},
            }, section_width="full", custom_background_color="#F2C440")
            ordem.append(nome)
            print(f"  {nome:18}    ({len(itens)} itens do kit em lista editável)")
            continue

        if nome == "museu-noite":
            # O player sai do markup e vira o block NATIVO de vídeo do
            # Ipanema, que dá à cliente um campo de URL no editor ("colar o
            # link e pronto"). Os três blocks concatenam no DOM: o código
            # "abre" deixa a <div class="mf-noite__video"> aberta, o block
            # nativo rende dentro dela, e o "fecha" fecha as tags.
            # O tema embrulha cada block num contêiner e o parser fecha as
            # divs no limite do block — deixar a moldura aberta num block e
            # fechar noutro rende moldura VAZIA (caixa preta órfã) com o
            # player fora dela. Então: a moldura sai do markup e o block de
            # vídeo É o player, vestido pela pele via .section-custom:has(.mf-noite).
            sem_video = re.sub(r'<div class="mf-noite__video"[^>]*>.*?</div>\s*',
                               '', markup, flags=re.S)
            if sem_video != markup:
                sections[nome] = secao_custom({
                    "markup": bloco_code(sem_video),
                    "player": {"type": "video", "settings": {
                        "video_url": video_atual,
                        "video_type": "manual",
                        "show_cover_image": False,
                        "aspect_ratio": "16by9",
                    }},
                })  # fundo: transparent de propósito — o céu da noite é um
                    # GRADIENTE, e gradiente entra por background-image na
                    # pele (o inline do setting só toca background-color).
                ordem.append(nome)
                print(f"  {nome:18} {len(sem_video):6} bytes   (player nativo, URL editável)")
                continue
        todas_pendentes += pendentes
        sections[nome] = secao_custom({"markup": bloco_code(markup)})
        ordem.append(nome)
        print(f"  {nome:18} {len(markup):6} bytes"
              + (f"   IMAGENS PENDENTES: {pendentes}" if pendentes else "")
              + (f"   LINKS .html SEM MAPA: {links_sobrando}" if links_sobrando else ""))

    # GSAP e ScrollTrigger vêm de CDN porque `static/` não é servido sem fork.
    # O motion só roda depois deles, e só se ambos carregarem — daí a guarda.
    #
    # `defer` nos dois: sem ele eram 45 KB BLOQUEANDO a primeira pintura, num
    # script que só serve pra animar no scroll — nada dele é necessário pra
    # tela aparecer. A guarda passa a rodar no DOMContentLoaded porque script
    # inline NÃO é adiado: sem isso ele executaria antes do GSAP existir e o
    # motion ficaria desligado. Script com defer executa antes desse evento,
    # então a ordem está garantida.
    js = (
        '<script defer src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>\n'
        '<script defer src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>\n'
        "<script>\n"
        "document.addEventListener('DOMContentLoaded', function () {\n"
        "if (window.gsap && window.ScrollTrigger) {\n"
        f"{motion}\n"
        "} else {\n"
        "  console.warn('Museu em Fios: GSAP não carregou; o motion fica desligado.');\n"
        "}\n"
        "});\n"
        "</script>"
    )
    sections["museu-motion"] = secao_custom({"js": bloco_code(js)})
    ordem.append("museu-motion")

    home = {"sections": sections, "order": ordem}
    destino = BUILD / "templates" / "pages" / "home.json"
    destino.write_text(json.dumps(home, ensure_ascii=False, indent=2), encoding="utf8")

    print(f"\n  home.json: {len(ordem)} seções, {destino.stat().st_size / 1024:.0f} KB")

    if todas_pendentes:
        print("\n  ATENÇÃO — imagens ainda apontando pra demo (vão quebrar no ar):")
        for p in sorted(set(todas_pendentes)):
            print(f"    · {p}")
        print(f"\n  Preencha {caminho_mapa} com {{\"arquivo.jpg\": \"https://…\"}} e rode de novo.")
        return 1

    print("  Todas as imagens apontam pro CDN da loja.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
