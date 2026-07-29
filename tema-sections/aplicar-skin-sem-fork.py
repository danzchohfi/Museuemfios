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

ASSINATURA = """<div class="mf-assinatura">
  <div class="mf-assinatura__wrap">
    <span>© 2026 Museu em Fios — Sua hora com a arte. Borde um museu.</span>
    <a class="mf-credito" href="https://vitaminapublicitaria.com.br" target="_blank" rel="noopener" aria-label="Site por Vitamina Publicitária">
      <span class="rotulo">Site por</span>
      <span class="marca">vitamina<i>.</i></span>
    </a>
  </div>
</div>"""


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

    # footer.json: pele + assinatura
    skin = (RAIZ / "static" / "css" / "museu-skin-ipanema.css").read_text(encoding="utf8")
    p_footer = BUILD / "templates" / "layout" / "footer.json"
    footer = json.loads(p_footer.read_text(encoding="utf8"))
    footer["sections"]["museu-extra"] = {
        "type": "custom",
        "settings": {
            "section_width": "full",
            "direction": "column",
            "mobile_direction_enabled": False,
            "gap": 0,
            "vertical_padding": 0,
            "horizontal_padding": 0,
        },
        "blocks": {
            "pele": {"type": "code", "settings": {"code": f"<style>\n{skin}\n</style>"}},
            "assinatura": {"type": "code", "settings": {"code": ASSINATURA}},
        },
    }
    if "museu-extra" not in footer["order"]:
        footer["order"].append("museu-extra")
    p_footer.write_text(json.dumps(footer, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"  footer.json: pele ({len(skin) / 1024:.0f} KB) + assinatura Vitamina")


if __name__ == "__main__":
    main()
