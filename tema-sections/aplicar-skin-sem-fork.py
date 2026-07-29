#!/usr/bin/env python3
"""Aplica a identidade nas páginas da plataforma, sem fork.

Complemento do montar-home-sem-fork.py: aquele cuida da HOME (markup autoral
por blocks `code`); este veste o RESTO — produto, categoria, header, rodapé —
pelos três canais que passam sem fork:

  1. config/settings_data.json — fontes, cores e botões pelos settings
     NATIVOS do Ipanema. Vira token (--heading-font, --button-primary-…) e
     chega em toda página sem custo de FOUC.

  2. settings.css_code — só o crítico (@import das fontes com itálico, que o
     google_fonts_url do tema não carrega, + tokens). Limite de 15.000
     caracteres, então aqui entra o mínimo.

  3. templates/layout/footer.json — ganha uma seção `custom` com dois blocks
     `code`: a pele completa (museu-skin-ipanema.css, sem limite de tamanho)
     e a assinatura © + Vitamina abaixo do rodapé. O footer.json renderiza em
     todas as páginas — é o nosso "arquivo global".

Rode DEPOIS do montar-tema.sh. Uso:  python3 aplicar-skin-sem-fork.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent
BUILD = RAIZ.parent / "build-tema"

if not BUILD.exists():
    raise SystemExit(f"Rode antes: ./montar-tema.sh <ID>  (não achei {BUILD})")

# ----------------------------------------------------------- 1. settings --
AJUSTES = {
    # Fontes da marca. O valor é a string CSS que os tokens recebem crua.
    "font_headings": '"Inter", sans-serif',
    "font_rest": '"Roboto Serif", serif',
    "headings_bold": True,

    # Cores base: papel, tinta e o amarelo pinçado do Klimt
    "background_color": "#FBFAF6",
    "text_color": "#1D1D1B",
    "accent_color": "#1D1D1B",

    # Botões no desenho do .mf-btn: preto, cheio, canto reto
    "button_primary_background_color": "#1D1D1B",
    "button_primary_foreground_color": "#FFFFFF",
    "button_primary_style": "filled",
    "button_primary_border_radius": 0,
    "button_secondary_background_color": "#FBFAF6",
    "button_secondary_foreground_color": "#1D1D1B",
    "button_secondary_style": "outline",
    "button_secondary_border_radius": 0,
    "button_tertiary_border_radius": 0,

    # Selos (Oferta, frete): o chip amarelo da demo
    "label_background_color": "#F2C440",
    "label_border_radius": 0,
    "label_shipping_background_color": "#F2C440",
    "label_shipping_border_radius": 0,
}

# --------------------------------------------------------- 2. css_code --
# O itálico do Roboto Serif é parte da identidade (subtítulo da obra, fichas)
# e o google_fonts_url do tema só pede 400,700 sem itálico — daí o @import,
# que precisa ser a primeira regra do bloco de estilo.
CSS_CRITICO = (
    "@import url('https://fonts.googleapis.com/css2"
    "?family=Inter:opsz,wght@14..32,100..900"
    "&family=Roboto+Serif:ital,opsz,wght@0,8..144,100..900;1,8..144,100..900"
    "&display=swap');\n"
    ':root{--heading-font:"Inter",-apple-system,sans-serif;'
    '--body-font:"Roboto Serif",Georgia,serif}\n'
    "body{font-family:var(--body-font)}\n"
    ".btn{font-family:var(--heading-font)}"
)

# O copyright nativo (escondido pela pele) carregava o CNPJ — ele migra pra cá.
# Sem "Site por" a pedido do Daniel: só o wordmark da Vitamina.
ASSINATURA = """<div class="mf-assinatura">
  <div class="mf-assinatura__wrap">
    <span>© 2026 Museu em Fios · CNPJ 47.035.343/0001-55 — Sua hora com a arte. Borde um museu.</span>
    <a class="mf-credito" href="https://vitaminapublicitaria.com.br" target="_blank" rel="noopener" aria-label="Vitamina Publicitária">
      <span class="marca">vitamina<i>.</i></span>
    </a>
  </div>
</div>"""

# Identifica a página no <body> pra pele poder tratar página a página —
# o tema só marca o TEMPLATE (body.template-page vale pra qualquer página
# de conteúdo; quem-somos precisa de tratamento próprio).
ROTEADOR = (
    "<script>(function(){"
    "var s=(location.pathname.replace(/\\/+$/,'').split('/').pop()||'home')"
    ".toLowerCase().replace(/[^a-z0-9-]/g,'');"
    "document.body.classList.add('pagina-'+(s||'home'));"
    "})();</script>"
)

# Conteúdo do rodapé: o footer.json de fábrica vem com o placeholder da
# Nuvemshop ("tradição há 3 gerações") e DOIS menus apontando pro mesmo
# menu "navigation" — colunas duplicadas na tela.
INSTITUCIONAL = (
    "O Museu em Fios une bordado e história da arte na releitura autoral de "
    "obras icônicas. Cada kit é um convite: sua hora com a arte, no seu tempo."
)
NEWSLETTER = "Lançamentos de coleção e conteúdos sobre arte, direto no seu e-mail."


def ajustar_produto() -> None:
    """Selos de confiança da página de produto (bloco purchase-info).

    De fábrica vêm dois (devolução, compra segura) com ícone de 24px. Entra o
    terceiro — o frete grátis acima de R$ 300, que é copy aprovada e argumento
    de venda — e o ícone sobe pra 32 na origem (o resto do tamanho é a pele,
    que transforma os três num painel destacado).
    """
    p_prod = BUILD / "templates" / "pages" / "product.json"
    prod = json.loads(p_prod.read_text(encoding="utf8"))
    info = prod["sections"]["main_product"]["blocks"]["product_info"]
    compra = info["blocks"]["purchase_info"]
    compra["settings"]["icon_size"] = 32
    # "Frete rápido", não "grátis": a loja NÃO tem frete grátis configurado
    # (data-pricemin="0" no HTML servido, conferido em 29/07/2026). Selo não
    # pode prometer o que o checkout não cumpre.
    compra["blocks"]["icon_frete"] = {
        "type": "icon-text-item",
        "settings": {
            "icon": "truck",
            "title": "Frete rápido",
            "description": "Para todo o Brasil",
        },
    }
    if "icon_frete" not in compra["block_order"]:
        compra["block_order"].append("icon_frete")
    p_prod.write_text(json.dumps(prod, ensure_ascii=False, indent=2), encoding="utf8")
    print("  product.json: 3º selo (frete grátis) + ícones em 32px")


def main() -> None:
    # settings
    p_settings = BUILD / "config" / "settings_data.json"
    dados = json.loads(p_settings.read_text(encoding="utf8"))
    dados["settings"].update(AJUSTES)
    if len(CSS_CRITICO) > 15000:
        raise SystemExit(f"css_code com {len(CSS_CRITICO)} chars — estourou o limite de 15.000")
    dados["settings"]["css_code"] = CSS_CRITICO
    p_settings.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"  settings: {len(AJUSTES)} ajustes + css_code de {len(CSS_CRITICO)} chars")

    # footer.json: conteúdo da marca no bloco nativo + logo + pele + assinatura
    skin = (RAIZ / "static" / "css" / "museu-skin-ipanema.css").read_text(encoding="utf8")
    logo_svg = (RAIZ.parent / "demo" / "assets" / "img" / "logo-horizontal-branco.svg").read_text(encoding="utf8")
    p_footer = BUILD / "templates" / "layout" / "footer.json"
    footer = json.loads(p_footer.read_text(encoding="utf8"))

    blocos = footer["sections"]["footer"]["blocks"]
    blocos["institutional"]["settings"]["description"] = INSTITUCIONAL
    if "menu_1" in blocos:
        blocos["menu_1"]["settings"]["title"] = "Navegação"
    if "menu_2" in blocos:  # segunda coluna do MESMO menu — fora
        del blocos["menu_2"]
        footer["sections"]["footer"]["block_order"] = [
            b for b in footer["sections"]["footer"]["block_order"] if b != "menu_2"
        ]
    if "newsletter" in blocos:
        blocos["newsletter"]["settings"]["description"] = NEWSLETTER

    def secao_code(blocks):
        return {
            "type": "custom",
            "settings": {
                "section_width": "full",
                "direction": "column",
                "mobile_direction_enabled": False,
                "gap": 0,
                "vertical_padding": 0,
                "horizontal_padding": 0,
            },
            "blocks": blocks,
        }

    # O logo vem ANTES da section footer: as duas faixas são pretas e leem
    # como um rodapé só, abrindo com a marca — o desenho da demo.
    footer["sections"]["museu-topo"] = secao_code({
        "logo": {"type": "code", "settings": {"code":
            f'<div class="mf-rodape-logo"><a href="/" aria-label="Museu em Fios">{logo_svg}</a></div>'}},
    })
    footer["sections"]["museu-extra"] = secao_code({
        "pele": {"type": "code", "settings": {"code": f"<style>\n{skin}\n</style>\n{ROTEADOR}"}},
        "assinatura": {"type": "code", "settings": {"code": ASSINATURA}},
    })
    footer["order"] = ["museu-topo", "footer", "museu-extra"]
    p_footer.write_text(json.dumps(footer, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"  footer.json: conteúdo da marca, logo ({len(logo_svg)} b), pele ({len(skin) / 1024:.0f} KB), assinatura")

    ajustar_produto()


if __name__ == "__main__":
    main()
