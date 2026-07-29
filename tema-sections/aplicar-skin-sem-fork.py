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

# WhatsApp logo abaixo do comprar (mobile e desktop), como na demo aprovada.
# O número é o do rodapé/demo; a mensagem já vai com o nome do produto.
WHATSAPP = """<script>(function(){
  if (!document.body.classList.contains('template-product')) return;
  var acoes = document.querySelector('.product-actions');
  if (!acoes || document.querySelector('.mf-wa')) return;
  var nome = document.querySelector('.js-product-name');
  var texto = 'Ol\\u00e1! Estou vendo o ' +
    (nome ? nome.textContent.trim() : 'um kit') +
    ' e queria tirar uma d\\u00favida.';
  var a = document.createElement('a');
  a.className = 'mf-wa';
  a.href = 'https://wa.me/5511971147355?text=' + encodeURIComponent(texto);
  a.target = '_blank';
  a.rel = 'noopener';
  a.addEventListener('click', function () {
    // Meta: Contact e o padrao certo pra clique de atendimento; o custom
    // WhatsAppClick permite recorte fino no Gerenciador de Eventos
    if (window.fbq) {
      fbq('track', 'Contact', { content_name: nome ? nome.textContent.trim() : '' });
      fbq('trackCustom', 'WhatsAppClick', { origem: 'pagina-produto' });
    }
    if (window.gtag) {
      gtag('event', 'whatsapp_click', { origem: 'pagina-produto' });
    }
  });
  a.innerHTML = '<svg class="icon-inline" aria-hidden="true">' +
    '<use xlink:href="#whatsapp"/></svg>' +
    'D\\u00favidas sobre o kit? Fale com a gente no WhatsApp <i>\\u2733</i>';
  acoes.insertAdjacentElement('afterend', a);
})();</script>"""

# Barra fixa de compra no produto (só mobile): clona preço + um botão que
# aciona o comprar original, e só aparece quando o original já rolou pra
# fora da tela — sem duplicar CTA à vista. Conversão: o comprar nunca fica
# a mais de um toque.
BARRA_COMPRA = """<script>(function(){
  if (!document.body.classList.contains('template-product')) return;
  if (window.innerWidth > 768) return;
  var botao = document.querySelector('.buy-button-container .btn-primary');
  var preco = document.querySelector('.product-price-display');
  var alvo = document.querySelector('.product-actions') || botao;
  if (!botao || !alvo) return;
  var barra = document.createElement('div');
  barra.className = 'mf-barra-compra';
  var p = document.createElement('span');
  p.className = 'mf-barra-compra__preco';
  p.textContent = preco ? preco.textContent.trim() : '';
  var b = document.createElement('button');
  b.type = 'button';
  b.className = 'btn btn-primary';
  b.textContent = 'Comprar';
  b.addEventListener('click', function () { botao.click(); });
  barra.appendChild(p); barra.appendChild(b);
  document.body.appendChild(barra);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (en) {
      var e = en[0];
      barra.classList.toggle('is-on', !e.isIntersecting && e.boundingClientRect.top < 0);
    }, { threshold: 0 }).observe(alvo);
  }
})();</script>"""

# Conteúdo do rodapé: o footer.json de fábrica vem com o placeholder da
# Nuvemshop ("tradição há 3 gerações") e DOIS menus apontando pro mesmo
# menu "navigation" — colunas duplicadas na tela.
INSTITUCIONAL = (
    "O Museu em Fios une bordado e história da arte na releitura autoral de "
    "obras icônicas. Cada kit é um convite: sua hora com a arte, no seu tempo."
)
NEWSLETTER = ("Assine e use o cupom PRIMEIROPONTO na primeira compra — "
              "lançamentos de coleção e conteúdos sobre arte, direto no seu e-mail.")


def ajustar_paginas() -> None:
    """Vídeo institucional da home também no quem-somos (pedido do Daniel).

    O template `page` serve TODAS as páginas de conteúdo (quem-somos, FAQ,
    políticas), então o bloco entra escondido por padrão e a pele só o exibe
    em body.pagina-quem-somos (classe do roteador). O iframe é lazy: em
    display:none não tem caixa, logo o embed nem carrega nas outras páginas.
    """
    p_page = BUILD / "templates" / "pages" / "page.json"
    page = json.loads(p_page.read_text(encoding="utf8"))
    video = (
        '<div class="mf-video-pagina">'
        '<p class="mf-video-pagina__eyebrow">O ritual</p>'
        '<div class="mf-video-pagina__quadro">'
        '<iframe src="https://www.youtube-nocookie.com/embed/Q2dJHg6M9jw?rel=0" '
        'title="Museu em Fios — a sua hora com a arte, à noite" '
        'loading="lazy" allowfullscreen '
        'allow="accelerometer; encrypted-media; picture-in-picture"></iframe>'
        "</div></div>"
    )
    page["sections"]["museu-video"] = {
        "type": "custom",
        "settings": {
            "section_width": "full",
            "direction": "column",
            "mobile_direction_enabled": False,
            "gap": 0,
            "vertical_padding": 0,
            "horizontal_padding": 0,
        },
        "blocks": {"video": {"type": "code", "settings": {"code": video}}},
    }
    if "museu-video" not in page["order"]:
        page["order"].append("museu-video")
    p_page.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf8")
    print("  page.json: vídeo institucional (visível só no quem-somos)")


def ajustar_header() -> None:
    """Liga a barra de anúncio em todas as páginas.

    O marquee com o cupom só roda na home; a barra nativa do header vinha
    DESLIGADA de fábrica. Ligada em amarelo da marca, ela põe o cupom de
    primeira compra e o frete grátis na frente de quem cai direto numa
    página de produto — que é onde o tráfego de anúncio chega.
    """
    p_head = BUILD / "templates" / "layout" / "header.json"
    head = json.loads(p_head.read_text(encoding="utf8"))
    an = head["sections"]["announcement"]
    an["disabled"] = False
    an["settings"].update({
        "background_color": "#F2C440",
        "text_color": "#1D1D1B",
        "section_width": "full",
    })
    an["blocks"] = {
        "cupom": {"type": "announcement", "settings": {
            "text": "Cupom de primeira compra: PRIMEIROPONTO"}},
        "frete": {"type": "announcement", "settings": {
            "text": "Frete grátis acima de R$ 300 — envios para todo o Brasil"}},
    }
    an["block_order"] = ["cupom", "frete"]
    # header na cor de papel da marca, não branco puro
    head["sections"]["header"]["settings"]["background_color"] = "#FBFAF6"
    p_head.write_text(json.dumps(head, ensure_ascii=False, indent=2), encoding="utf8")
    print("  header.json: barra de anúncio ligada (cupom + frete) e fundo papel")


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
    # Orientação da cliente (29/07/2026): "frete grátis para pedidos acima de
    # 300 reais. Envios para todo o Brasil". A regra ainda não aparece
    # configurada no checkout (data-pricemin="0") — cobrar a ativação no
    # admin pra promessa e cobrança baterem.
    compra["blocks"]["icon_frete"] = {
        "type": "icon-text-item",
        "settings": {
            "icon": "truck",
            "title": "Frete grátis acima de R$ 300",
            "description": "Envios para todo o Brasil",
        },
    }
    if "icon_frete" not in compra["block_order"]:
        compra["block_order"].append("icon_frete")

    # Os selos vinham DEPOIS da descrição, no fim da coluna — longe da decisão
    # de compra. Sobem pra antes da descrição (achado do revisor de UX).
    ordem = info.get("block_order") or list(info["blocks"].keys())
    if "purchase_info" in ordem and "description" in ordem:
        ordem.remove("purchase_info")
        ordem.insert(ordem.index("description"), "purchase_info")
        info["block_order"] = ordem

    p_prod.write_text(json.dumps(prod, ensure_ascii=False, indent=2), encoding="utf8")
    print("  product.json: 3º selo, ícones 32px, selos antes da descrição")


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
        "pele": {"type": "code", "settings": {"code": f"<style>\n{skin}\n</style>\n{ROTEADOR}\n{WHATSAPP}\n{BARRA_COMPRA}"}},
        "assinatura": {"type": "code", "settings": {"code": ASSINATURA}},
    })
    footer["order"] = ["museu-topo", "footer", "museu-extra"]
    p_footer.write_text(json.dumps(footer, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"  footer.json: conteúdo da marca, logo ({len(logo_svg)} b), pele ({len(skin) / 1024:.0f} KB), assinatura")

    ajustar_header()
    ajustar_produto()
    ajustar_paginas()


if __name__ == "__main__":
    main()
