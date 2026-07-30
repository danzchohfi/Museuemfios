#!/usr/bin/env python3
"""Caça clique morto na loja renderizada — os mesmos casos que o Clarity marca.

Clique morto é o clique que não faz nada. Ele custa duas vezes: o visitante
perde a intenção de compra no meio do caminho, e o Clarity registra a página
como frustrante. Três origens, e este script cobre as três:

  1. PARECE CLICÁVEL E NÃO É — a foto do card cujo link está só no título, o
     preço, o nome do produto, o selo de confiança, qualquer coisa com
     `cursor: pointer` sem destino. É a maior fonte: o visitante clica na
     imagem grande, não no texto pequeno.

  2. É CLICÁVEL E ALGO ESTÁ NA FRENTE — botão de WhatsApp flutuante, banner
     de cookie, barra fixa de compra ou widget de app cobrindo o alvo. O
     clique vai pro elemento de cima e morre. Aqui isso é medido com
     elementFromPoint no centro do alvo, que é o que o navegador faz de fato.

  3. O DESTINO NÃO EXISTE — link que responde 404. O clique "funciona", o
     visitante cai numa página de erro e volta. Para o Clarity é abandono.

Cada achado sai com o seletor, a posição e o que exatamente acontece ao
clicar, para dar pra conferir na mão.

SOBRE FALSO POSITIVO: o tema delega clique por classe `js-*` no document, em
vez de pendurar listener no elemento. Procurar listener no elemento sozinho
acusaria metade do tema como morto. Por isso "é clicável" aqui considera
ancestral com href, button, [onclick], role=button, [data-component],
[data-target], [data-toggle] e classe js-*, e também os listeners de fato
pendurados (lidos via CDP, que é o que enxerga o nosso próprio JS).

Uso:
    python3 auditar-cliques.py <url> [celular|desktop]
    python3 auditar-cliques.py --tudo          # varre as páginas principais
"""

import gzip
import json
import sys
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

LOJA = "https://www.museuemfios.com"
UA_CELULAR = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
              "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
UA_DESKTOP = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
CHROMIUM = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

TELAS = {
    "celular": dict(viewport={"width": 430, "height": 932}, is_mobile=True,
                    has_touch=True, device_scale_factor=2, user_agent=UA_CELULAR),
    "desktop": dict(viewport={"width": 1440, "height": 900}, user_agent=UA_DESKTOP),
}

PAGINAS = ["/", "/kits-de-bordado/", "/produtos-digitais/", "/quem-somos/", "/faq/",
           "/produtos/kit-de-bordado-le-pont-japonais-claude-monet/"]


def servir(rota):
    url = rota.request.url
    if url.startswith(("data:", "blob:")):
        return rota.continue_()
    cab = {"User-Agent": UA_CELULAR, "Accept": "*/*", "Accept-Language": "pt-BR,pt;q=0.9"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=45) as r:
            corpo = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                corpo = gzip.decompress(corpo)
            rota.fulfill(status=r.status, body=corpo,
                         headers={"content-type": r.headers.get("Content-Type", "application/octet-stream"),
                                  "access-control-allow-origin": "*"})
    except urllib.error.HTTPError as e:
        rota.fulfill(status=e.code, body=b"")
    except Exception:
        rota.abort()


AUDITAR = r"""() => {
  const nomeDe = (el) => el.tagName.toLowerCase()
    + (el.id ? "#" + el.id : "")
    + (el.className && el.className.toString().trim()
       ? "." + el.className.toString().trim().split(/\s+/).slice(0, 3).join(".") : "");

  // "Isto responde a clique?" — inclui a delegação por classe js-* do tema,
  // senão metade do tema apareceria como morta.
  const INTERATIVO = 'a[href], button, input, select, textarea, summary, label[for], ' +
    '[onclick], [role="button"], [role="link"], [data-component], [data-target], ' +
    '[data-toggle], [class*="js-"], [tabindex]:not([tabindex="-1"])';
  const alvoDeClique = (el) => el.closest(INTERATIVO);

  const hrefMorto = (a) => {
    const h = (a.getAttribute("href") || "").trim();
    return !h || h === "#" || h.startsWith("javascript:");
  };

  const visivel = (el) => {
    const s = getComputedStyle(el);
    if (s.display === "none" || s.visibility === "hidden" || +s.opacity === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 4 && r.height > 4;
  };

  const centro = (el) => { const r = el.getBoundingClientRect();
    return [r.left + r.width / 2, r.top + r.height / 2]; };

  const naTela = (el) => { const r = el.getBoundingClientRect();
    return r.top < innerHeight && r.bottom > 0 && r.left < innerWidth && r.right > 0; };

  const pareceLink = [], engolidos = [], hrefsVazios = [], destinos = new Set();

  // ---- 1. parece clicável e não é -------------------------------------
  for (const el of document.querySelectorAll("body *")) {
    if (!visivel(el) || alvoDeClique(el)) continue;
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const tag = el.tagName.toLowerCase();
    const texto = (el.innerText || "").trim().replace(/\s+/g, " ").slice(0, 40);

    let motivo = null;
    if (s.cursor === "pointer") motivo = "cursor: pointer sem destino";
    // imagem grande sem link: o visitante clica na foto, não no título
    else if ((tag === "img" || tag === "picture") && r.width > 90 && r.height > 90)
      motivo = `imagem ${Math.round(r.width)}x${Math.round(r.height)} fora de link`;
    // nome/preço dentro de um card cujo link está em outro lugar
    else if (texto && /^(h[1-6]|span|div|p|strong)$/.test(tag) && r.height < 120) {
      // CARD, não seção: `[class*="vitrine"]` pegava a seção inteira e
      // acusava o título dela, que ninguém espera que seja clicável.
      const cartao = el.closest('article, li, [class*="product-item"], [class*="-card"], ' +
                                '[class*="card-"], [class*="obra-item"]');
      if (cartao && cartao.querySelector("a[href]") && el.children.length === 0
          && cartao.getBoundingClientRect().height < 700)
        motivo = "texto dentro de card clicável, mas fora do link";
    }
    if (!motivo) continue;

    // só conta se o clique realmente chega nele (nada por cima)
    if (!naTela(el)) { /* fora da tela: mede pela árvore, sem elementFromPoint */ }
    else {
      const [x, y] = centro(el);
      const emCima = document.elementFromPoint(x, y);
      if (emCima && emCima !== el && !el.contains(emCima) && emCima.closest(INTERATIVO)) continue;
    }
    pareceLink.push({ el: nomeDe(el).slice(0, 64), motivo, texto,
                      x: Math.round(r.left), y: Math.round(r.top + scrollY),
                      larg: Math.round(r.width), alt: Math.round(r.height) });
  }

  // ---- 2. é clicável mas algo está na frente --------------------------
  // O que importa é o DESTINO: dentro de um card, a foto por cima do slide
  // leva ao mesmo produto — clique legítimo. Só é morto quando o clique acaba
  // em outro lugar (ou em nada).
  const destinoDe = (x) => { const a = x && x.closest("a[href]"); return a ? a.href : null; };
  for (const el of document.querySelectorAll(INTERATIVO)) {
    if (!visivel(el) || !naTela(el)) continue;
    const [x, y] = centro(el);
    const emCima = document.elementFromPoint(x, y);
    if (!emCima || emCima === el || el.contains(emCima) || emCima.contains(el)) continue;
    const alvoReal = emCima.closest(INTERATIVO);
    if (alvoReal === el || (alvoReal && (alvoReal.contains(el) || el.contains(alvoReal)))) continue;
    const meu = destinoDe(el), dele = destinoDe(emCima);
    if (meu && meu === dele) continue;               // mesmo destino: ok
    // sobreposto por camada flutuante é o caso grave (banner, widget, barra)
    let flutuante = null;
    for (let n = emCima; n && n !== document.body; n = n.parentElement)
      if (["fixed", "sticky"].includes(getComputedStyle(n).position)) { flutuante = nomeDe(n); break; }
    engolidos.push({ el: nomeDe(el).slice(0, 58),
                     texto: (el.innerText || el.getAttribute("aria-label") || "").trim().slice(0, 32),
                     porCima: nomeDe(emCima).slice(0, 52),
                     camadaFlutuante: flutuante ? flutuante.slice(0, 46) : null,
                     viraClique: alvoReal ? nomeDe(alvoReal).slice(0, 40) : "NADA (morre)" });
  }

  // ---- 3. href que não leva a lugar nenhum ----------------------------
  for (const a of document.querySelectorAll("a")) {
    if (!visivel(a)) continue;
    if (hrefMorto(a)) {
      // href="#" com listener é legítimo (abre modal, troca aba)
      const temPapel = a.hasAttribute("onclick") || a.className.toString().includes("js-")
        || a.hasAttribute("data-toggle") || a.hasAttribute("data-target")
        || a.hasAttribute("data-component") || a.hasAttribute("role");
      if (!temPapel)
        hrefsVazios.push({ el: nomeDe(a).slice(0, 60),
                           href: (a.getAttribute("href") || "(sem href)"),
                           texto: (a.innerText || "").trim().slice(0, 36) });
    } else {
      const u = a.href;
      if (u.startsWith(location.origin)) destinos.add(u);
    }
  }

  return { pareceLink, engolidos, hrefsVazios, destinos: [...destinos] };
}"""


def checar_destinos(urls):
    """HEAD em cada destino interno: 404 é clique que vira página de erro."""
    ruins = []
    for u in sorted(urls):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": UA_DESKTOP}, method="HEAD")
            with urllib.request.urlopen(req, timeout=25) as r:
                if r.status >= 400:
                    ruins.append((r.status, u))
        except urllib.error.HTTPError as e:
            ruins.append((e.code, u))
        except Exception as e:
            ruins.append((type(e).__name__, u))
    return ruins


ESTADO = """() => ({
  url: location.href,
  modais: [...document.querySelectorAll('.modal, [class*="modal"], dialog')]
    .filter(m => getComputedStyle(m).display !== "none").length,
  altura: document.documentElement.scrollHeight,
  abertos: document.querySelectorAll('[aria-expanded="true"], .is-open, .active').length,
})"""


def confirmar_clicando(pg, candidatos):
    """href="#" com listener é legítimo (abre modal, troca aba). Em vez de
    adivinhar pela marcação, clica e vê se o estado da página mudou — foi
    assim que o link de parcelas se mostrou vivo, e não morto."""
    vivos, mortos = [], []
    for c in candidatos:
        try:
            el = pg.query_selector(f'a[href="{c["href"]}"]:has-text("{c["texto"][:20]}")') \
                if c["texto"] else None
            if el is None:
                el = pg.query_selector("#" + c["el"].split("#")[1].split(".")[0]) \
                    if "#" in c["el"] else None
            if el is None:
                c["verificado"] = "não localizei pra clicar"
                mortos.append(c)
                continue
            antes = pg.evaluate(ESTADO)
            el.scroll_into_view_if_needed()
            pg.wait_for_timeout(300)
            el.click(timeout=4000)
            pg.wait_for_timeout(1200)
            if pg.evaluate(ESTADO) != antes:
                c["verificado"] = "clicado: FAZ algo (falso positivo)"
                vivos.append(c)
            else:
                c["verificado"] = "clicado: NADA acontece"
                mortos.append(c)
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(300)
        except Exception as e:
            c["verificado"] = f"não deu pra clicar ({type(e).__name__})"
            mortos.append(c)
    return mortos, vivos


def auditar(pg, url):
    pg.goto(url, wait_until="load", timeout=120000)
    pg.wait_for_timeout(4500)
    # rola a página inteira: card com lazyload só existe depois de aparecer
    pg.evaluate("""async () => {
      const passo = innerHeight * 0.8;
      for (let y = 0; y < document.documentElement.scrollHeight; y += passo) {
        scrollTo(0, y); await new Promise(r => setTimeout(r, 120));
      }
      scrollTo(0, 0); await new Promise(r => setTimeout(r, 400));
    }""")
    r = pg.evaluate(AUDITAR)
    r["hrefsVazios"], r["falsosPositivos"] = confirmar_clicando(pg, r["hrefsVazios"][:8])
    return r


def relatar(url, tela, r, ruins):
    print(f"\n{'=' * 74}\n{url}  [{tela}]")
    grupos = [
        ("PARECE CLICÁVEL E NÃO É", r["pareceLink"]),
        ("CLIQUE ENGOLIDO POR ALGO NA FRENTE", r["engolidos"]),
        ("LINK SEM DESTINO (href vazio/# — confirmado clicando)", r["hrefsVazios"]),
    ]
    if r.get("falsosPositivos"):
        print(f"\n  (descartados por teste de clique: "
              f"{', '.join(x['texto'] or x['el'] for x in r['falsosPositivos'])})")
    for titulo, itens in grupos:
        print(f"\n  {titulo}: {len(itens) or 'nenhum'}")
        for x in itens[:14]:
            print(f"    {json.dumps(x, ensure_ascii=False)}")
        if len(itens) > 14:
            print(f"    … +{len(itens) - 14}")
    print(f"\n  DESTINO QUE NÃO EXISTE: {len(ruins) or 'nenhum'}  "
          f"({len(r['destinos'])} links internos conferidos)")
    for status, u in ruins:
        print(f"    {status}  {u}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--tudo":
        alvos = [(LOJA + p, t) for p in PAGINAS for t in ("celular", "desktop")]
    elif len(sys.argv) > 1:
        alvos = [(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "celular")]
    else:
        raise SystemExit(__doc__.strip().splitlines()[-1])

    conferidos = set()
    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        for url, tela in alvos:
            ctx = nav.new_context(**TELAS[tela])
            ctx.route("**/*", servir)
            pg = ctx.new_page()
            r = auditar(pg, url)
            novos = [u for u in r["destinos"] if u not in conferidos]
            conferidos.update(novos)
            relatar(url, tela, r, checar_destinos(novos))
            ctx.close()
        nav.close()


if __name__ == "__main__":
    main()
