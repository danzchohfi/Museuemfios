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
     `code`: a pele completa (museu-skin-ipanema.css) e a assinatura © +
     Vitamina abaixo do rodapé. O footer.json renderiza em todas as páginas —
     é o nosso "arquivo global". O setting `code` para em 50.000 caracteres
     (custom_code), então a pele sobe comprimida — ver comprimir_css.

Rode DEPOIS do montar-tema.sh. Uso:  python3 aplicar-skin-sem-fork.py
"""

import json
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent
BUILD = RAIZ.parent / "build-tema"

# O block `code` aceita até 50.000 caracteres por setting — o limite é do
# tipo custom_code e a API responde HTTP 400 quando passa. A pele com os
# comentários já bateu nele; por isso ela viaja comprimida e o fonte, que é
# onde os comentários valem, fica intacto no repositório.
LIMITE_CODE = 50000


def comprimir_css(css: str) -> str:
    """Tira comentários e espaço supérfluo. Confere que nada se perdeu.

    As strings entre aspas saem de cena antes da compressão: `content: "a, b"`
    tem vírgula e espaço que SÃO significativos, e o regex que come espaço em
    volta de pontuação os destruiria sem avisar.
    """
    def normalizar(t):
        """Declarações numa forma que ignora só o espaço insignificante."""
        t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
        saida = []
        for d in re.findall(r"[-a-zA-Z]+\s*:[^;{}]+", t):
            d = " ".join(d.split())
            d = re.sub(r"\s*([:,])\s*", r"\1", d)
            saida.append(d)
        return sorted(saida)

    antes = normalizar(css)

    guardadas: list[str] = []

    def guardar(m):
        guardadas.append(m.group(0))
        return f"\x00{len(guardadas) - 1}\x00"

    curto = re.sub(r"\"[^\"\n]*\"|'[^'\n]*'", guardar, css)
    curto = re.sub(r"/\*.*?\*/", " ", curto, flags=re.S)  # espaço, não vazio:
    curto = re.sub(r"\s+", " ", curto)                    # comentário separa token
    curto = re.sub(r"\s*([{};:,>])\s*", r"\1", curto)
    curto = re.sub(r";}", "}", curto).strip()
    curto = re.sub(r"\x00(\d+)\x00", lambda m: guardadas[int(m.group(1))], curto)

    depois = normalizar(curto)
    if antes != depois:
        raise SystemExit("comprimir_css mudou o CSS — não vou subir isso. "
                         f"Diferenças: {sorted(set(antes) ^ set(depois))[:4]}")
    if curto.count("{") != curto.count("}"):
        raise SystemExit("comprimir_css desbalanceou as chaves")
    print(f"  pele comprimida: {len(css):,} → {len(curto):,} chars "
          f"({len(depois)} declarações conferidas)")
    return curto

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
    # Só os eixos que a folha realmente usa. O pedido anterior trazia `opsz`
    # (tamanho óptico) nas duas famílias e a faixa de peso 100..900 com
    # itálico completo: 349 KB de fonte na home do celular, o maior item
    # isolado da página depois das imagens. Medido arquivo por arquivo nos
    # subsets latin/latin-ext: 745 KB de catálogo contra 292 KB assim.
    # Nada abaixo de 400 é usado (os font-weight: 100 do CSS eram a FAIXA
    # declarada nos @font-face, que nem sobem), Roboto Serif não passa de
    # 700, e nenhum itálico vem com negrito — daí `1,400` sozinho.
    # Pesos discretos foram medidos e são PIORES (927 KB em 16 arquivos):
    # com fonte variável, uma faixa é um arquivo só.
    "@import url('https://fonts.googleapis.com/css2"
    "?family=Inter:wght@400..900"
    "&family=Roboto+Serif:ital,wght@0,400..700;1,400"
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

# PALIATIVO — o item "Blog" do menu aponta pra /blog1/, que responde 404; a
# página existe em /blog/. Clique morto na navegação principal, encontrado
# pelo auditar-cliques.py. A API da Nuvemshop não expõe menus (só o admin),
# então o link é reescrito aqui até a cliente corrigir em Loja online →
# Menus. Quando corrigir, isto vira no-op e pode sair.
CONSERTA_MENU = """<script>(function(){
  // 1. "Blog" aponta pra /blog1/, que responde 404; a página existe em /blog/.
  document.querySelectorAll('a[href$="/blog1/"],a[href$="/blog1"]').forEach(function (a) {
    a.href = a.href.replace(/\\/blog1\\/?$/, '/blog/');
  });

  // 2. Itens de menu SEM TEXTO. O menu tem três: os dois filhos de "Loja"
  //    (que apontam pra home) e um apontando pra um produto. Renderizam como
  //    linha em branco — o submenu de Loja abria uma caixa vazia, que é o
  //    que a gente via como "texto branco". Não é cor: não há texto.
  //    Link sem rótulo nunca é intencional, então some até a cliente
  //    corrigir em Loja online → Menus. Corrigido lá, isto vira no-op.
  document.querySelectorAll('.nav-list-link, .nav-item > a').forEach(function (a) {
    if ((a.textContent || '').trim() || a.querySelector('img, svg')) return;
    var li = a.closest('li') || a;
    li.style.display = 'none';
  });

  // 3. Dropdown que ficou sem nenhum filho visível vira caixa vazia ao
  //    passar o mouse — esconde o painel e a setinha. O "Loja" segue
  //    clicável, apontando pra /produtos/.
  document.querySelectorAll('.nav-dropdown').forEach(function (nav) {
    var vivos = [].slice.call(nav.querySelectorAll('li')).filter(function (li) {
      return li.style.display !== 'none';
    });
    if (vivos.length) return;
    nav.querySelectorAll('.nav-dropdown-content, .desktop-dropdown-container')
       .forEach(function (p) { p.style.display = 'none'; });
    nav.querySelectorAll('svg, .icon-inline').forEach(function (s) { s.style.display = 'none'; });
  });
})();</script>"""

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
  // O rastreio do clique fica no listener delegado do RASTREIO (cobre este
  // link E o widget flutuante Smartarget, com 1 disparo por pageview).
  a.innerHTML = '<svg class="icon-inline" aria-hidden="true">' +
    '<use xlink:href="#whatsapp"/></svg>' +
    'D\\u00favidas sobre o kit? Fale com a gente no WhatsApp <i>\\u2733</i>';
  acoes.insertAdjacentElement('afterend', a);
})();</script>"""

# Conversão no carrinho, montada por JS (o drawer re-renderiza via AJAX, daí
# o MutationObserver re-aplicando com guarda de duplicata):
# · barra de progresso do frete grátis — SÓ aparece quando a regra estiver
#   ativa no admin (lê o data-pricemin que o tema publica); acende sozinha
#   no dia em que o Daniel ativar;
# · lembrete do cupom PRIMEIROPONTO (o campo de cupom só existe no checkout);
# · linha de confiança compacta com os ícones do próprio sprite.
CARRINHO = """<script>(function () {
  function reais(cents) {
    return 'R$ ' + (cents / 100).toFixed(2).replace('.', ',').replace(/,00$/, '');
  }
  function melhorar() {
    var enviar = document.querySelector('#modal-cart .js-ajax-cart-submit') ||
                 document.querySelector('.js-ajax-cart-submit');
    if (!enviar) return;
    var caixa = enviar.parentElement;
    if (!caixa) return;

    var minEl = document.querySelector('.js-ship-free-min');
    var min = minEl ? parseInt(minEl.getAttribute('data-pricemin') || '0', 10) : 0;
    var subEl = document.querySelector('.js-cart-subtotal');
    var sub = subEl ? parseInt(subEl.getAttribute('data-priceraw') || '0', 10) : 0;
    var prog = caixa.querySelector('.mf-frete-progresso');
    if (min > 0 && sub > 0) {
      if (!prog) {
        prog = document.createElement('div');
        prog.className = 'mf-frete-progresso';
        prog.innerHTML = '<span class="mf-frete-progresso__texto"></span>' +
          '<div class="mf-frete-progresso__trilho"><div class="mf-frete-progresso__fio"></div></div>';
        enviar.insertAdjacentElement('beforebegin', prog);
      }
      var falta = Math.max(0, min - sub);
      // Só escreve quando o valor MUDA: escrever innerHTML dispara o
      // MutationObserver, que chama melhorar de novo — sem esta guarda é
      // loop infinito e página travada (aconteceu quando o frete ativou).
      if (prog.dataset.mfFalta !== String(falta)) {
        prog.dataset.mfFalta = String(falta);
        var texto = prog.querySelector('.mf-frete-progresso__texto');
        var fio = prog.querySelector('.mf-frete-progresso__fio');
        if (falta > 0) {
          prog.classList.remove('is-ganho');
          texto.innerHTML = 'Faltam <strong>' + reais(falta) + '</strong> para o frete grátis';
          fio.style.width = Math.min(100, Math.round(sub / min * 100)) + '%';
        } else {
          prog.classList.add('is-ganho');
          texto.innerHTML = '<strong>Frete grátis desbloqueado \\u2733</strong>';
          fio.style.width = '100%';
        }
      }
    } else if (prog) {
      prog.remove();
    }

    if (!caixa.querySelector('.mf-carrinho-cupom')) {
      var cupom = document.createElement('p');
      cupom.className = 'mf-carrinho-cupom';
      cupom.innerHTML = 'Primeira compra? Use o cupom <strong>PRIMEIROPONTO</strong> no pagamento.';
      caixa.appendChild(cupom);
      var conf = document.createElement('p');
      conf.className = 'mf-carrinho-confianca';
      conf.innerHTML = '<svg class="icon-inline"><use xlink:href="#security"/></svg> Compra segura' +
        ' \\u00b7 <svg class="icon-inline"><use xlink:href="#returns"/></svg> Devolu\\u00e7\\u00e3o gr\\u00e1tis em 30 dias';
      caixa.appendChild(conf);
    }
  }
  // O #modal-cart renderiza DEPOIS deste script no body — armar direto
  // falhava em silêncio. Tenta agora e re-tenta até o drawer existir.
  var armado = false;
  function armar() {
    if (armado) return true;
    var alvo = document.getElementById('modal-cart');
    if (!alvo) return false;
    armado = true;
    if ('MutationObserver' in window) {
      // Debounce: o re-render AJAX do drawer emite rajadas de mutações
      var agendado = false;
      new MutationObserver(function () {
        if (agendado) return;
        agendado = true;
        setTimeout(function () { agendado = false; melhorar(); }, 120);
      }).observe(alvo, { childList: true, subtree: true });
    }
    melhorar();
    return true;
  }
  if (!armar()) {
    document.addEventListener('DOMContentLoaded', armar);
    window.addEventListener('load', armar);
    if ('MutationObserver' in window) {
      var espera = new MutationObserver(function () {
        if (armar()) espera.disconnect();
      });
      espera.observe(document.documentElement, { childList: true, subtree: true });
    }
  }
})();</script>"""

# Sinais pra Meta (desenho da auditoria de CAPI):
# · WhatsApp -> Contact PADRÃO (entra em público, AEM e otimização), com o
#   produto no payload e SEM value/currency — valor inventado polui o sinal.
#   Listener delegado com capture: pega o nosso .mf-wa E o widget Smartarget
#   (injetado em runtime), exclui o botão de COMPARTILHAR no WhatsApp
#   (data-network) e dispara 1x por pageview. Sem eventID: é browser-only,
#   não há espelho de servidor pra deduplicar.
# · Newsletter -> Lead.
# · De propósito SEM evento no clique da barra de comprar: o AddToCart
#   nativo já dispara nesse fluxo com dedup browser+servidor.
RASTREIO = """<script>(function () {
  var enviado = false;
  document.addEventListener('click', function (e) {
    if (enviado || typeof fbq !== 'function' || !e.target.closest) return;
    var a = e.target.closest('a,button,[role="button"]');
    if (!a) return;
    var href = (a.getAttribute('href') || '').toLowerCase();
    var cls = ((a.className || '') + ' ' + (a.id || '')).toLowerCase();
    var whats = href.indexOf('wa.me') > -1 || href.indexOf('api.whatsapp.com') > -1 ||
                href.indexOf('whatsapp://') === 0 || cls.indexOf('smartarget') > -1;
    if (!whats || a.getAttribute('data-network') === 'whatsapp') return;
    enviado = true;
    var d = { content_category: 'whatsapp' };
    if (window.LS && LS.product) {
      d.content_name = LS.product.name;
      d.content_type = 'product';
      if (LS.product.selected_variant_id) d.content_ids = [String(LS.product.selected_variant_id)];
    }
    fbq('track', 'Contact', d);
    if (window.gtag) gtag('event', 'whatsapp_click', d);
  }, true);
  document.addEventListener('submit', function (e) {
    if (typeof fbq !== 'function' || !e.target || !e.target.matches) return;
    if (e.target.matches('.newsletter-form, .footer-newsletter-form, .js-home-newsletter-form, .js-news-form')) {
      fbq('track', 'Lead', { content_name: 'newsletter' });
    }
  }, true);
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
      var ligada = !e.isIntersecting && e.boundingClientRect.top < 0;
      barra.classList.toggle('is-on', ligada);
      // A classe no body deixa o CSS empurrar o banner de cookie pra cima da
      // barra. Sem isso os dois ocupam a mesma faixa, o banner tem z-index
      // 1000 contra 60 da barra, e o toque em Comprar caía no "Entendi" —
      // primeiro toque de todo visitante novo não comprava, só fechava o
      // aviso. Medido no navegador, em toda posição de rolagem.
      document.body.classList.toggle('mf-com-barra', ligada);
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


# "Você conhece esta obra?" — a seção editorial da demo, por produto. O
# texto é POR PRODUTO e sem fork não há campo por produto no template: o
# conteúdo curado viaja num mapa por handle e o JS escolhe a entrada da
# página (produto sem entrada: a seção nem aparece). Voz editorial da demo:
# 1º parágrafo sobre a obra, 2º amarrando ao bordado.
OBRAS_EDITORIAL = {
    "kit-de-bordado-le-pont-japonais-claude-monet": {
        "titulo": "Le Pont Japonais",
        "p1": ("Pintada por Claude Monet em 1899, a ponte japonesa sobre o "
               "lago de nenúfares de Giverny é um dos motivos mais amados do "
               "impressionismo — o jardim que o próprio pintor desenhou e "
               "retratou por mais de vinte anos."),
        "p2": ("No bordado, essa vegetação densa vira camadas de pontos: a "
               "observação se transforma em fio, e o fio em memória. Cada "
               "interpretação é única, bordada à mão — tempo, contemplação e "
               "técnica."),
    },
    "pre-venda-kit-de-bordado-die-umarmung-gustav-klimt": {
        "titulo": "Die Umarmung",
        "p1": ("Desenhada por Gustav Klimt por volta de 1908 como estudo para "
               "o friso do Palácio Stoclet, Die Umarmung — o abraço — condensa "
               "o período dourado do artista: ornamento, geometria e afeto na "
               "mesma superfície."),
        "p2": ("No bordado, a riqueza ornamental vira textura: espirais e "
               "campos dourados refeitos ponto a ponto, à mão — tempo, "
               "contemplação e técnica."),
    },
    "kit-de-bordado-der-kuss-gustav-klimt": {
        "titulo": "Der Kuss",
        "p1": ("Pintado por Gustav Klimt entre 1907 e 1908, O Beijo é a obra "
               "máxima do período dourado — o abraço coberto de ouro que virou "
               "um dos quadros mais reconhecidos do mundo."),
        "p2": ("No bordado, o dourado vira linha: padrões e mosaicos refeitos "
               "ponto a ponto. Cada interpretação é única, bordada à mão — "
               "tempo, contemplação e técnica."),
    },
    "kit-para-bordado-la-gerbe-henri-matisse-pko6p": {
        "titulo": "La Gerbe",
        "p1": ("Criada por Henri Matisse em 1953, La Gerbe — o feixe — é uma "
               "das últimas grandes obras do artista: papel recortado em "
               "formas vivas, quando o mestre trocou o pincel pela tesoura."),
        "p2": ("No bordado, cada folha recortada vira um campo de pontos "
               "cheios de cor. Cada interpretação é única, bordada à mão — "
               "tempo, contemplação e técnica."),
    },
}

OBRA_EDITORIAL_BLOCO = (
    '<section class="mf-obra-editorial" hidden>'
    '<div class="mf-obra-editorial__wrap">'
    '<div><p class="mf-obra-editorial__eyebrow">Você conhece esta obra?</p>'
    '<h2 class="mf-obra-editorial__titulo"></h2></div>'
    '<div class="mf-obra-editorial__texto"><p class="lead"></p><p class="apoio"></p></div>'
    "</div></section>"
    "<script>(function(){"
    "var DADOS=" + json.dumps(OBRAS_EDITORIAL, ensure_ascii=False) + ";"
    "var h=(location.pathname.match(/\\/produtos\\/([^\\/]+)/)||[])[1];"
    "var d=h&&DADOS[h];if(!d)return;"
    "var s=document.querySelector('.mf-obra-editorial');if(!s)return;"
    "s.querySelector('.mf-obra-editorial__titulo').textContent=d.titulo;"
    "s.querySelector('.lead').textContent=d.p1;"
    "s.querySelector('.apoio').textContent=d.p2;"
    "s.hidden=false;"
    "})();</script>"
)

# O slogan é a frase-mestra da marca e o Daniel pediu ela recorrente:
# páginas internas (sob o título), contato e produto (faixa após a compra).
SLOGAN_PAGINA = ('<p class="mf-slogan">Sua hora com a arte. '
                 "<strong>Borde um museu.</strong></p>")
SLOGAN_FAIXA = ('<p class="mf-slogan mf-slogan--faixa">Sua hora com a arte. '
                "<strong>Borde um museu.</strong></p>")


def secao_slogan(codigo: str) -> dict:
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
        "blocks": {"slogan": {"type": "code", "settings": {"code": codigo}}},
    }


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
    page["sections"]["museu-slogan"] = secao_slogan(SLOGAN_PAGINA)
    if "museu-slogan" not in page["order"]:
        page["order"].insert(page["order"].index("heading") + 1, "museu-slogan")
    p_page.write_text(json.dumps(page, ensure_ascii=False, indent=2), encoding="utf8")
    print("  page.json: vídeo (só quem-somos) + slogan sob o título")

    # contato usa template próprio — slogan lá também
    p_cont = BUILD / "templates" / "pages" / "contact.json"
    cont = json.loads(p_cont.read_text(encoding="utf8"))
    cont["sections"]["museu-slogan"] = secao_slogan(SLOGAN_PAGINA)
    if "museu-slogan" not in cont["order"]:
        cont["order"].insert(cont["order"].index("heading") + 1, "museu-slogan")
    p_cont.write_text(json.dumps(cont, ensure_ascii=False, indent=2), encoding="utf8")
    print("  contact.json: slogan sob o título")


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
    cab = head["sections"]["header"]
    cab["settings"]["background_color"] = "#FBFAF6"
    # Logo bem maior no celular. O default do tema é 30px, e a nossa marca é
    # um lockup de DUAS linhas ("MUSEU / EM FIOS") — em 30px de altura cada
    # linha fica com ~13px e a assinatura desaparece ao lado dos ícones.
    # Vai pelo setting NATIVO (height_mobile, faixa 20–90), então a cliente
    # segue ajustando no editor. 64px é o limite antes de o lockup competir
    # por espaço com o menu e os ícones na largura de um iPhone.
    cab["blocks"]["logo"]["settings"].update({
        "use_different_mobile_height": True,
        "height_mobile": 64,
    })
    # O respiro lateral de 40px era o que sobrava de espaço pro logo crescer;
    # no celular vai a 20 e o vertical encurta pra faixa não ficar alta demais.
    cab["settings"].update({
        "use_different_mobile_padding": True,
        "vertical_padding_mobile": 12,
        "horizontal_padding_mobile": 20,
    })
    p_head.write_text(json.dumps(head, ensure_ascii=False, indent=2), encoding="utf8")
    print("  header.json: barra de anúncio, fundo papel, logo mobile 64px")


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

    # faixa do slogan entre o produto e as vitrines de relacionados
    prod["sections"]["museu-slogan"] = secao_slogan(SLOGAN_FAIXA)
    if "museu-slogan" not in prod["order"]:
        prod["order"].insert(prod["order"].index("main_product") + 1, "museu-slogan")

    # "Você conhece esta obra?" logo após o slogan; conteúdo por handle
    prod["sections"]["museu-obra-editorial"] = secao_slogan(OBRA_EDITORIAL_BLOCO)
    if "museu-obra-editorial" not in prod["order"]:
        prod["order"].insert(prod["order"].index("museu-slogan") + 1, "museu-obra-editorial")

    # As vitrines de relacionados falam a língua da demo
    prod["sections"]["alternative_products"]["blocks"]["alternative_heading"][
        "settings"]["title"] = "Outras obras"

    p_prod.write_text(json.dumps(prod, ensure_ascii=False, indent=2), encoding="utf8")
    print("  product.json: 3º selo, ícones 32px, selos antes da descrição, slogan")


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
    skin = comprimir_css(
        (RAIZ / "static" / "css" / "museu-skin-ipanema.css").read_text(encoding="utf8"))
    logo_svg = (RAIZ.parent / "demo" / "assets" / "img" / "logo-horizontal-branco.svg").read_text(encoding="utf8")
    p_footer = BUILD / "templates" / "layout" / "footer.json"
    footer = json.loads(p_footer.read_text(encoding="utf8"))

    # Cores do rodapé pelos settings NATIVOS. Sem isso, --footer-foreground
    # ficava no default claro do tema (#1D1D1B) enquanto a pele pintava o
    # fundo de preto: tudo que o tema desenha a partir do token saía preto no
    # preto — o ícone do Instagram e a seta do accordion ficavam INVISÍVEIS,
    # e o lugar deles lia como vão vazio no rodapé do celular.
    footer["sections"]["footer"]["settings"].update({
        "background_color": "#1D1D1B",
        "text_color": "#FBFAF6",
    })

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
        "pele": {"type": "code", "settings": {"code": f"<style>\n{skin}\n</style>\n{ROTEADOR}\n{CONSERTA_MENU}\n{WHATSAPP}\n{BARRA_COMPRA}\n{CARRINHO}\n{RASTREIO}"}},
        "assinatura": {"type": "code", "settings": {"code": ASSINATURA}},
    })
    footer["order"] = ["museu-topo", "footer", "museu-extra"]

    # Falha aqui, com o nome do block, em vez de tomar HTTP 400 no push
    for secao in ("museu-topo", "museu-extra"):
        for nome, bloco in footer["sections"][secao]["blocks"].items():
            tamanho = len(bloco["settings"]["code"])
            if tamanho > LIMITE_CODE:
                raise SystemExit(
                    f'block "{nome}" com {tamanho:,} chars — o setting custom_code '
                    f"para em {LIMITE_CODE:,}. Divida em dois blocks `code` ou "
                    "corte CSS morto."
                )

    p_footer.write_text(json.dumps(footer, ensure_ascii=False, indent=2), encoding="utf8")
    folga = LIMITE_CODE - len(footer["sections"]["museu-extra"]["blocks"]["pele"]["settings"]["code"])
    print(f"  footer.json: conteúdo da marca, logo ({len(logo_svg)} b), "
          f"pele ({len(skin) / 1024:.0f} KB, folga de {folga:,} chars no limite), assinatura")

    ajustar_header()
    ajustar_produto()
    ajustar_paginas()


if __name__ == "__main__":
    main()
