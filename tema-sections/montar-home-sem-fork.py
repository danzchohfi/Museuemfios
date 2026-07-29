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
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
REPO = RAIZ.parent
BUILD = REPO / "build-tema"
DEMO = REPO / "demo" / "index.html"

# As 6 seções da marca, na ordem da home aprovada. O seletor é o elemento de
# topo de cada uma dentro da demo.
SECOES = [
    ("museu-hero", r'<section class="mf-hero"'),
    ("museu-marquee", r'<div class="mf-marquee"'),
    ("museu-manifesto", r'<section class="mf-manifesto"'),
    ("museu-noite", r'<section class="mf-noite"'),
    ("museu-passos", r'<section class="mf-passos"'),
    ("museu-kit", r'<section class="mf-kit" id="kit"'),
]


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
    "loja.html": "/kits-de-bordado/",
    "sobre.html": "/quem-somos/",
}

# `produto.html` aparece três vezes no hero — uma por obra — e o destino
# certo depende de QUAL obra. A âncora vem depois da imagem no markup, então
# a imagem `obra-original-…` mais próxima ANTES do href identifica o produto.
PRODUTO_POR_IMAGEM = {
    # O produto do Femme existe (id 302470130, handle
    # kit-de-bordado-femme-a-lombrelle-claude-monet) mas está DESPUBLICADO na
    # loja (published: false, conferido em 29/07/2026) — a URL dele responde
    # 404. Até ser publicado, o slide manda pra categoria; depois, é só
    # devolver "/produtos/kit-de-bordado-femme-a-lombrelle-claude-monet/"
    # aqui e remontar.
    "obra-original-monet-femme-ombrelle": "/kits-de-bordado/",
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
    args = ap.parse_args()

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
    motion = (RAIZ / "static/js/museu-motion.js").read_text(encoding="utf8")

    sections, ordem, todas_pendentes = {}, [], []

    # O CSS vai primeiro, numa seção de altura zero: precisa estar no documento
    # antes do markup pra não haver salto de layout.
    sections["museu-estilo"] = secao_custom(
        {"css": bloco_code(f"<style>\n{css}\n</style>")})
    ordem.append("museu-estilo")

    for nome, seletor in SECOES:
        markup = extrair(html, seletor)
        markup, pendentes = trocar_imagens(markup, mapa)
        markup, links_sobrando = trocar_links(markup, com_obras=(nome == "museu-hero"))
        todas_pendentes += pendentes
        sections[nome] = secao_custom({"markup": bloco_code(markup)})
        ordem.append(nome)
        print(f"  {nome:18} {len(markup):6} bytes"
              + (f"   IMAGENS PENDENTES: {pendentes}" if pendentes else "")
              + (f"   LINKS .html SEM MAPA: {links_sobrando}" if links_sobrando else ""))

    # GSAP e ScrollTrigger vêm de CDN porque `static/` não é servido sem fork.
    # O motion só roda depois deles, e só se ambos carregarem — daí a guarda.
    js = (
        '<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>\n'
        '<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>\n'
        "<script>\n"
        "if (window.gsap && window.ScrollTrigger) {\n"
        f"{motion}\n"
        "} else {\n"
        "  console.warn('Museu em Fios: GSAP não carregou; o motion fica desligado.');\n"
        "}\n"
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
