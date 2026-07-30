#!/usr/bin/env python3
"""Auditoria de desempenho da loja no navegador, com bytes reais.

POR QUE NÃO É O PAGESPEED

A API do PageSpeed Insights sem chave cai num projeto público compartilhado
e devolve 429 (cota diária estourada). Então este script mede o que dá pra
medir aqui com precisão — e é a maior parte do que o PSI reporta de
acionável:

  REAL, confiável                       NÃO confiável daqui
  ─────────────────────────────         ──────────────────────────────
  peso em bytes por tipo e por host     tempo absoluto (LCP, FCP, TTI)
  nº de requests e de terceiros         nota de 0 a 100
  recursos que bloqueiam a renderização
  imagem servida maior que o exibido
  CLS (deslocamento de layout)
  tarefas longas na thread principal
  tamanho do DOM, fontes, cache

Os bytes são exatos porque cada resposta passa pelo urllib daqui — o
tamanho é medido no corpo que o navegador de fato recebeu. O tempo NÃO é
comparável porque as respostas vêm pelo proxy local, sem a latência real
de rede; para nota oficial, rode em pagespeed.web.dev.

Uso:  python3 medir-desempenho.py <url> [celular|desktop]
"""

import collections
import gzip
import json
import sys
import urllib.error
import urllib.parse
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

# host -> quem é, pra separar o que é nosso do que é app de terceiro
TERCEIROS = {
    "connect.facebook.net": "Meta Pixel",
    "www.facebook.com": "Meta",
    "googletagmanager.com": "Google Tag Manager",
    "www.google-analytics.com": "Google Analytics",
    "cdn.jsdelivr.net": "GSAP (nosso, via CDN)",
    "fonts.googleapis.com": "Google Fonts (CSS)",
    "fonts.gstatic.com": "Google Fonts (arquivos)",
    "smartarget.online": "Smartarget",
    "cdn.smartarget.online": "Smartarget",
    "www.clarity.ms": "Microsoft Clarity",
}

registro = []


def servir(rota):
    url = rota.request.url
    if url.startswith(("data:", "blob:")):
        return rota.continue_()
    cab = {"User-Agent": UA_CELULAR, "Accept": "*/*", "Accept-Language": "pt-BR,pt;q=0.9",
           "Accept-Encoding": "gzip"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=cab), timeout=45) as r:
            bruto = r.read()
            comprimido = r.headers.get("Content-Encoding") == "gzip"
            corpo = gzip.decompress(bruto) if comprimido else bruto
            registro.append({
                "url": url,
                "tipo": rota.request.resource_type,
                "host": urllib.parse.urlparse(url).netloc,
                "bytes_rede": len(bruto),          # o que trafega
                "bytes_abertos": len(corpo),       # o que o navegador processa
                "cache": r.headers.get("Cache-Control", "(sem)"),
                "status": r.status,
            })
            rota.fulfill(status=r.status, body=corpo,
                         headers={"content-type": r.headers.get("Content-Type", "application/octet-stream"),
                                  "access-control-allow-origin": "*"})
    except urllib.error.HTTPError as e:
        registro.append({"url": url, "tipo": rota.request.resource_type,
                         "host": urllib.parse.urlparse(url).netloc, "bytes_rede": 0,
                         "bytes_abertos": 0, "cache": "-", "status": e.code})
        rota.fulfill(status=e.code, body=b"")
    except Exception:
        rota.abort()


NAVEGADOR = r"""() => new Promise((resolve) => {
  let cls = 0, tarefasLongas = [], lcp = null;
  try {
    new PerformanceObserver((l) => { for (const e of l.getEntries())
      if (!e.hadRecentInput) cls += e.value; }).observe({ type: "layout-shift", buffered: true });
  } catch (e) {}
  try {
    new PerformanceObserver((l) => { const es = l.getEntries();
      const u = es[es.length - 1];
      lcp = { ms: Math.round(u.startTime), tam: Math.round(u.size),
              el: u.element ? (u.element.tagName.toLowerCase()
                 + (u.element.className ? "." + u.element.className.toString().trim().split(/\s+/).slice(0,2).join(".") : ""))
                 : (u.url || "?").slice(-52) };
    }).observe({ type: "largest-contentful-paint", buffered: true });
  } catch (e) {}
  try {
    new PerformanceObserver((l) => { for (const e of l.getEntries())
      tarefasLongas.push(Math.round(e.duration)); }).observe({ type: "longtask", buffered: true });
  } catch (e) {}

  setTimeout(() => {
    // imagem servida muito maior do que aparece na tela
    const desperdicio = [];
    for (const img of document.images) {
      const r = img.getBoundingClientRect();
      if (!r.width || !img.naturalWidth) continue;
      const dpr = devicePixelRatio || 1;
      const precisa = r.width * dpr;
      if (img.naturalWidth > precisa * 1.6)
        desperdicio.push({ src: img.currentSrc.slice(-46), servida: img.naturalWidth,
                           exibida: Math.round(r.width), precisaria: Math.round(precisa) });
    }
    // o que bloqueia a primeira pintura
    const bloqueia = [...document.querySelectorAll('link[rel="stylesheet"]:not([media="print"])')]
      .filter(l => !l.hasAttribute("disabled")).map(l => l.href.slice(-52));
    const scriptsBloqueando = [...document.querySelectorAll("script[src]")]
      .filter(s => !s.async && !s.defer).map(s => s.src.slice(-52));
    // fontes
    const fontes = performance.getEntriesByType("resource")
      .filter(e => /\.(woff2?|ttf|otf)(\?|$)/i.test(e.name)).length;

    resolve({
      cls: +cls.toFixed(4), lcp, tarefasLongas: tarefasLongas.sort((a,b) => b-a).slice(0, 6),
      somaTarefasLongas: tarefasLongas.reduce((a,b) => a+b, 0),
      elementosDOM: document.querySelectorAll("*").length,
      profundidadeDOM: (() => { let max = 0; for (const el of document.querySelectorAll("*")) {
        let d = 0; for (let n = el; n; n = n.parentElement) d++; max = Math.max(max, d); } return max; })(),
      imagensSemDimensao: [...document.images].filter(i => !i.getAttribute("width") && !i.getAttribute("height")).length,
      totalImagens: document.images.length,
      desperdicioImagem: desperdicio.sort((a,b) => b.servida - a.servida).slice(0, 8),
      cssBloqueando: bloqueia, scriptsBloqueando, arquivosDeFonte: fontes,
      iframes: document.querySelectorAll("iframe").length,
    });
  }, 5000);
})"""


def kb(n):
    return f"{n / 1024:,.0f} KB".replace(",", ".")


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://www.museuemfios.com/"
    tela = sys.argv[2] if len(sys.argv) > 2 else "celular"

    with sync_playwright() as pw:
        nav = pw.chromium.launch(executable_path=CHROMIUM)
        ctx = nav.new_context(**TELAS[tela])
        ctx.route("**/*", servir)
        pg = ctx.new_page()
        pg.goto(url, wait_until="load", timeout=120000)
        r = pg.evaluate(NAVEGADOR)
        nav.close()

    print(f"\n{'=' * 74}\n{url}  [{tela}]\n{'=' * 74}")

    por_tipo = collections.Counter()
    bytes_tipo = collections.Counter()
    bytes_host = collections.Counter()
    for x in registro:
        por_tipo[x["tipo"]] += 1
        bytes_tipo[x["tipo"]] += x["bytes_rede"]
        bytes_host[x["host"]] += x["bytes_rede"]
    total = sum(bytes_tipo.values())

    print(f"\nPESO DA PÁGINA: {kb(total)} em {len(registro)} requests")
    for t, b in bytes_tipo.most_common():
        print(f"   {t:12} {por_tipo[t]:3} req   {kb(b):>10}   {100*b//max(total,1):3}%")

    proprio = sum(b for h, b in bytes_host.items() if "museuemfios" in h or "mitiendanube" in h)
    print(f"\nNOSSO x TERCEIRO: nosso {kb(proprio)} ({100*proprio//max(total,1)}%)  "
          f"| terceiros {kb(total - proprio)} ({100*(total-proprio)//max(total,1)}%)")
    for h, b in bytes_host.most_common(10):
        quem = TERCEIROS.get(h, "loja/CDN" if ("museuemfios" in h or "mitiendanube" in h) else "?")
        print(f"   {kb(b):>10}  {h[:44]:46} {quem}")

    ruins = [x for x in registro if x["status"] >= 400]
    if ruins:
        print(f"\nREQUESTS COM ERRO: {len(ruins)}")
        for x in ruins[:8]:
            print(f"   {x['status']}  {x['url'][:76]}")

    print(f"\nRENDERIZAÇÃO")
    print(f"   CLS (deslocamento de layout): {r['cls']}"
          f"   {'ok (<0.1)' if r['cls'] < 0.1 else 'PRECISA MELHORAR' if r['cls'] < 0.25 else 'RUIM'}")
    if r["lcp"]:
        print(f"   maior elemento pintado: {r['lcp']['el']}  ({r['lcp']['tam']} px²)")
    print(f"   tarefas longas na thread principal: {len(r['tarefasLongas'])}"
          f"  somando {r['somaTarefasLongas']} ms   maiores: {r['tarefasLongas']}")
    print(f"   CSS bloqueando a pintura: {len(r['cssBloqueando'])}")
    for c in r["cssBloqueando"]:
        print(f"      {c}")
    print(f"   scripts bloqueando (sem async/defer): {len(r['scriptsBloqueando'])}")
    for s in r["scriptsBloqueando"][:8]:
        print(f"      {s}")

    print(f"\nDOM E MÍDIA")
    print(f"   elementos: {r['elementosDOM']}  (PSI reclama acima de 1.400)"
          f"   profundidade: {r['profundidadeDOM']}  (acima de 32 é alerta)")
    print(f"   imagens: {r['totalImagens']}   sem width/height declarados: "
          f"{r['imagensSemDimensao']}  (é a maior causa de CLS)")
    print(f"   arquivos de fonte: {r['arquivosDeFonte']}   iframes: {r['iframes']}")
    if r["desperdicioImagem"]:
        print(f"\n   IMAGEM SERVIDA MAIOR DO QUE APARECE ({len(r['desperdicioImagem'])}):")
        for d in r["desperdicioImagem"]:
            print(f"      {d['servida']:5}px servida → {d['exibida']:4}px na tela "
                  f"(precisaria {d['precisaria']}px)  …{d['src']}")

    sem_cache = [x for x in registro if x["cache"] in ("(sem)", "no-cache", "no-store")
                 and x["tipo"] in ("script", "stylesheet", "image", "font")]
    if sem_cache:
        print(f"\n   ESTÁTICO SEM CACHE ({len(sem_cache)}):")
        for x in sem_cache[:6]:
            print(f"      {x['tipo']:10} {kb(x['bytes_rede']):>9}  …{x['url'][-56:]}")


if __name__ == "__main__":
    main()
