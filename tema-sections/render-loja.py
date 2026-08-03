#!/usr/bin/env python3
"""Renderiza uma página da loja no Chromium e audita o layout.

POR QUE ESTE ARQUIVO EXISTE

O Chromium deste ambiente não atravessa o relay do proxy para o domínio da
loja (ERR_CONNECTION_RESET), mas o urllib do Python atravessa. Então toda
request é interceptada pelo Playwright e respondida com o que o Python
baixou — inclusive scripts de terceiros, que é onde moram o banner de
cookie e widgets de app.

Sem isso, a verificação era só "o seletor chegou no CSS servido?", que não
pega bug de RENDERIZAÇÃO. Foi só medindo de verdade que apareceu o motivo
dos vãos no rodapé do celular: --footer-foreground estava no default claro
do tema, e o ícone do Instagram, a seta do accordion, o botão Enviar da
newsletter e o selo da Nuvemshop estavam PRETOS SOBRE PRETO — invisíveis.

O que o relatório traz:
  · altura do documento e sobra depois do último bloco (pega espaço morto);
  · overflow horizontal (elemento passando da largura da tela);
  · caixas altas cujo conteúdo visível é muito menor (vão vazio);
  · contraste de cada texto/ícone contra o fundo real herdado — é isso que
    encontra elemento invisível, que nenhuma medida de altura revela;
  · alvo de toque menor que 44px.

Uso:
    python3 render-loja.py <url> [celular|desktop] [prefixo-dos-prints]
"""

import gzip
import json
import sys
import urllib.error
import urllib.request

from playwright.sync_api import sync_playwright

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


def servir(rota):
    """Responde a request com o que o urllib baixou (ele passa pelo proxy)."""
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


AUDITAR = r"""(larguraTela) => {
  // ATENÇÃO: usa a largura da TELA pedida, não innerWidth. Quando algo
  // transborda, o navegador estica o viewport de layout (na home ele foi de
  // 430 pra 445) — comparar contra innerWidth esconde exatamente o bug que
  // se quer achar, porque aí a largura do documento sempre "cabe".
  const vw = larguraTela, doc = document.documentElement;
  const nomeDe = (el) => el.tagName.toLowerCase()
    + (el.id ? "#" + el.id : "")
    + (el.className && el.className.toString().trim()
       ? "." + el.className.toString().trim().split(/\s+/).slice(0, 2).join(".") : "");

  const lum = (cor) => { const m = (cor || "").match(/[\d.]+/g); if (!m) return null;
    const [r, g, b] = m.map(Number); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  // Sobe até achar um fundo opaco. Se no caminho aparecer background-image
  // (gradiente ou foto), devolve null: a cor de trás é desconhecida e medir
  // contraste ali dá falso positivo — foi o que aconteceu com a seção da
  // noite, cujo céu é um linear-gradient sobre background-color transparente.
  const fundoReal = (el) => { let n = el; while (n) {
      const s = getComputedStyle(n);
      if (s.backgroundImage && s.backgroundImage !== "none") return null;
      const c = s.backgroundColor;
      if (c && c !== "rgba(0, 0, 0, 0)" && c !== "transparent") return c;
      n = n.parentElement; } return "rgb(255, 255, 255)"; };

  const overflow = [], vazios = [], invisiveis = [], alvos = [];

  for (const el of document.querySelectorAll("body *")) {
    const s = getComputedStyle(el);
    if (s.display === "none" || s.visibility === "hidden") continue;
    const r = el.getBoundingClientRect();
    if (!r.width && !r.height) continue;

    // Overflow só conta se NADA acima recorta: carrossel (swiper) tem slide
    // fora da tela de propósito, e reportar isso enterra o achado de verdade.
    const recortado = (() => { let n = el.parentElement; while (n && n !== document.body) {
        const o = getComputedStyle(n); if (o.overflowX !== "visible" || o.overflow === "clip") return true;
        n = n.parentElement; } return false; })();
    if ((r.right > vw + 2 || r.left < -2) && s.position !== "fixed" && !recortado)
      overflow.push({ el: nomeDe(el).slice(0, 70), esq: Math.round(r.left), dir: Math.round(r.right) });

    // Vão vazio = altura do bloco menos a faixa vertical que o conteúdo DE
    // FATO cobre. Três coisas que a versão anterior errava, todas medidas na
    // vitrine em blocks nativos:
    //   · somava a altura dos filhos, o que só vale quando eles empilham. Os
    //     filhos do card são `absolute` e se sobrepõem: a soma acusou 488px de
    //     vão num card cheio. Agora é união de intervalos.
    //   · `display: contents` devolve retângulo zero, então o filho "sumia" e
    //     o pai parecia vazio. Agora desce até quem tem caixa.
    //   · caixa fora do fluxo não empurra página nenhuma, logo não pode ser a
    //     causa de um vão — o <a> esticado por cima do card caía aqui.
    // Elemento com texto próprio também sai: o conteúdo dele é o texto.
    const temTextoProprio = [...el.childNodes]
      .some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (r.height > 150 && ["static", "relative"].includes(s.position)
        && el.children.length && !temTextoProprio) {
      const comCaixa = [];
      const desce = (pai) => { for (const c of pai.children) {
        const d = getComputedStyle(c).display;
        if (d === "none") continue;
        const b = c.getBoundingClientRect();
        // desce por quem não tem caixa própria: `display: contents` não gera
        // nenhuma, e um wrapper cujos filhos são todos `absolute` colapsa a 0
        if (d === "contents" || (b.height === 0 && c.children.length)) desce(c);
        else comCaixa.push(b); } };
      desce(el);
      const faixas = comCaixa.filter(b => b.height > 0)
        .map(b => [b.top, b.bottom]).sort((a, b) => a[0] - b[0]);
      let coberta = 0, fim = -Infinity;
      for (const [ini, termino] of faixas) {
        coberta += Math.max(0, termino - Math.max(ini, fim));
        fim = Math.max(fim, termino);
      }
      if (r.height - coberta > 120)
        vazios.push({ el: nomeDe(el).slice(0, 70), alt: Math.round(r.height),
                      sobra: Math.round(r.height - coberta), topo: Math.round(r.top + scrollY) });
    }

    // texto invisível / ícone invisível: contraste contra o fundo herdado
    const temTexto = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    const ehSvg = el.tagName.toLowerCase() === "svg";
    if (temTexto || ehSvg) {
      const frente = ehSvg ? s.fill : s.color;
      const lf = lum(frente), lb = lum(fundoReal(el));
      if (lf !== null && lb !== null) {
        const k = (Math.max(lf, lb) + 13) / (Math.min(lf, lb) + 13);
        if (k < 1.8) invisiveis.push({ el: nomeDe(el).slice(0, 60), contraste: +k.toFixed(2),
                                       frente, fundo: fundoReal(el),
                                       texto: (el.innerText || "").trim().slice(0, 30) });
      }
    }

    // alvo de toque (só o que é clicável de fato)
    if (["a", "button"].includes(el.tagName.toLowerCase()) && el.offsetParent
        && r.height > 0 && (r.height < 40 || r.width < 40) && (el.innerText || "").trim().length < 30)
      alvos.push({ el: nomeDe(el).slice(0, 56), larg: Math.round(r.width), alt: Math.round(r.height) });
  }

  const ultimo = [...document.body.children].filter(e => {
    const s = getComputedStyle(e); return s.display !== "none" && s.position === "static";
  }).pop();
  const fimConteudo = ultimo ? Math.round(ultimo.getBoundingClientRect().bottom + scrollY) : null;

  return { viewport: vw, viewportEsticado: innerWidth,
           larguraDoc: doc.scrollWidth, alturaDoc: doc.scrollHeight,
           fimConteudo, sobraNoFim: fimConteudo === null ? null : doc.scrollHeight - fimConteudo,
           overflow: overflow.slice(0, 12),
           vazios: vazios.sort((a, b) => b.sobra - a.sobra).slice(0, 8),
           invisiveis: invisiveis.slice(0, 12), alvosPequenos: alvos.slice(0, 12) };
}"""


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__.strip().splitlines()[-1])
    url = sys.argv[1]
    tela = sys.argv[2] if len(sys.argv) > 2 else "celular"
    prefixo = sys.argv[3] if len(sys.argv) > 3 else tela
    if tela not in TELAS:
        raise SystemExit(f"tela deve ser {' ou '.join(TELAS)}")

    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        ctx = nav.new_context(**TELAS[tela])
        ctx.route("**/*", servir)
        pg = ctx.new_page()
        pg.goto(url, wait_until="load", timeout=120000)
        # rola até o fim: dispara lazyload e revela o rodapé
        pg.evaluate("scrollTo(0, document.documentElement.scrollHeight)")
        pg.wait_for_timeout(6000)

        r = pg.evaluate(AUDITAR, TELAS[tela]["viewport"]["width"])
        print(f"\n{url}  [{tela}]")
        print(f"  documento: {r['larguraDoc']}x{r['alturaDoc']}  (tela {r['viewport']}"
              + (f", ESTICADA pra {r['viewportEsticado']}" if r["viewportEsticado"] != r["viewport"] else "")
              + f")   sobra depois do último bloco: {r['sobraNoFim']}px")
        for titulo, chave, vazio in [
            ("OVERFLOW HORIZONTAL", "overflow", "nenhum elemento passa da largura da tela"),
            ("INVISÍVEL (contraste < 1.8)", "invisiveis", "nada invisível"),
            ("VÃO VAZIO (> 120px sem conteúdo)", "vazios", "sem vão suspeito"),
            ("ALVO DE TOQUE < 40px", "alvosPequenos", "todos os alvos ok"),
        ]:
            print(f"\n  {titulo}: {len(r[chave]) or vazio}")
            for x in r[chave]:
                print(f"    {json.dumps(x, ensure_ascii=False)}")

        pg.screenshot(path=f"{prefixo}-fim.png")
        pg.evaluate("scrollTo(0, 0)")
        pg.wait_for_timeout(1200)
        pg.screenshot(path=f"{prefixo}-topo.png")
        print(f"\n  prints: {prefixo}-topo.png  {prefixo}-fim.png")
        nav.close()


if __name__ == "__main__":
    main()
