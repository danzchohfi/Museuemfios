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
        todas_pendentes += pendentes
        sections[nome] = secao_custom({"markup": bloco_code(markup)})
        ordem.append(nome)
        print(f"  {nome:18} {len(markup):6} bytes"
              + (f"   IMAGENS PENDENTES: {pendentes}" if pendentes else ""))

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
