#!/usr/bin/env python3
"""Limpa o HTML das descrições de produto — títulos de verdade, sem emoji.

O PROBLEMA

As descrições foram escritas no editor do admin com a hierarquia improvisada:

    <p><strong>KIT para Bordar: "Le Pont Japonais" – Claude Monet</strong></p>
    <p>✳️ <strong>O que vem no kit</strong></p>

Parágrafo em negrito não é título: tem o mesmo corpo do texto, não entra em
leitor de tela como seção, e o emoji vira "marcador". Era isso que deixava a
página com cara amadora — CSS sozinho não conserta porque 2 produtos têm
<strong> misturado com texto corrido no MESMO parágrafo (um seletor cego
transformaria frase em título).

O QUE ESTE SCRIPT FAZ, POR PRODUTO (campo description.pt):

  1. <p> cujo único elemento é <strong>, sem texto relevante depois dele,
     vira <h3> de verdade. Emojis e símbolos decorativos na frente do
     título caem (✳️, 🎨, 🧵…).
  2. Se o PRIMEIRO título é o nome do produto repetido (o H1 já está logo
     acima na página), o parágrafo sai — repetição, não informação.
  3. Parágrafos mistos (negrito + texto corrido) NÃO são tocados.

ISSO EDITA DADO DA LOJA (as descrições aparecem também no tema publicado).
Por isso, antes de qualquer escrita, TODAS as descrições vão para
backup-descricoes.json ao lado deste script — restaurável na mão ou por
`--restaurar`.

Uso:  python3 limpar-descricoes.py            # aplica (grava backup antes)
      python3 limpar-descricoes.py --ver      # só mostra o que faria
      python3 limpar-descricoes.py --restaurar # devolve o backup pra loja
"""

import base64
import difflib
import json
import pathlib
import re
import sys
import urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent
BACKUP = RAIZ / "backup-descricoes.json"
NUBE = RAIZ.parent / "tema" / ".nube"

d = json.loads(base64.b64decode(NUBE.read_text().strip()))
API = d["theme-api"]
BASE = f"https://api.nuvemshop.com.br/2025-03/{API['storeId']}"
CAB = {
    "Authentication": f"bearer {API['publicApiToken']}",
    "User-Agent": "museu-em-fios (daniel@vitaminapublicitaria.com.br)",
    "Content-Type": "application/json",
}


def req(metodo, caminho, corpo=None):
    r = urllib.request.Request(f"{BASE}/{caminho}", headers=CAB, method=metodo,
                               data=json.dumps(corpo).encode() if corpo else None)
    return json.load(urllib.request.urlopen(r, timeout=60))


def todos_produtos():
    pagina, tudo = 1, []
    while True:
        ps = req("GET", f"products?per_page=50&page={pagina}")
        tudo += ps
        if len(ps) < 50:
            return tudo
        pagina += 1


# Emojis e símbolos decorativos que abrem os pseudo-títulos
DECORACAO = re.compile(
    "^[\\s\\u2600-\\u27bf\\ufe0f\\u200d\\U0001f000-\\U0001faff]+"
)


def normalizar(texto):
    return re.sub(r"[^a-z0-9]", "", texto.lower()
                  .replace("á", "a").replace("à", "a").replace("â", "a").replace("ã", "a")
                  .replace("é", "e").replace("ê", "e").replace("í", "i")
                  .replace("ó", "o").replace("ô", "o").replace("õ", "o")
                  .replace("ú", "u").replace("ç", "c"))


def limpar(html, nome_produto):
    """Devolve (html_novo, relatorio)."""
    relatorio = []
    primeiro = True

    def trata(m):
        nonlocal primeiro
        par = m.group(0)
        interno = m.group(1)
        els = re.findall(r"<(?!/)(\w+)", interno)
        if els != ["strong"]:
            return par  # tem outros elementos: não é pseudo-título
        depois = re.sub(r"<[^>]+>", "", interno[interno.find("</strong>") + 9:])
        if len(depois.strip()) > 2:
            return par  # negrito + frase no mesmo parágrafo: texto, não título
        titulo = re.sub(r"<[^>]+>", "", interno)
        titulo = DECORACAO.sub("", titulo).strip()
        if not titulo:
            return par
        era_primeiro, primeiro = primeiro, False
        # &ndash; etc. atrapalham a comparação com o nome
        titulo_puro = titulo.replace("&ndash;", "-").replace("&quot;", '"')
        # "Repete o nome" tolera variação pequena — o cadastro tem subtítulos
        # entre parênteses que o título da descrição omite (ou vice-versa).
        na, nb = normalizar(titulo_puro), normalizar(nome_produto)
        parecido = (na and nb and (na in nb or nb in na
                    or difflib.SequenceMatcher(None, na, nb).ratio() >= 0.72))
        if era_primeiro and parecido:
            relatorio.append(f"− removido (repetia o nome): {titulo_puro[:48]}")
            return ""
        relatorio.append(f"h2: {titulo_puro[:48]}")
        # h2, não h3: a página só tem o h1 do nome — os títulos da descrição
        # são o segundo nível de verdade (achado da auditoria de SEO)
        return f"<h2>{titulo}</h2>"

    novo = re.sub(r"<p[^>]*>((?:(?!</p>).)*?)</p>", trata, html, flags=re.S)

    # Segunda passada — faxina do HTML colado do editor:
    # 1. títulos que a primeira rodada gravou como h3 sobem pra h2
    novo = novo.replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    # 2. classes de editor (font-claude-response-body, utilitários colados)
    novo = re.sub(r"<(p|ul|ol|li|strong|em|h2|span)\s+class=\"[^\"]*\"", r"<\1", novo)
    # 3. parágrafos vazios (&nbsp;) que criavam vãos espúrios
    novo = re.sub(r"<p[^>]*>(?:\s|&nbsp;|<br\s*/?>)*</p>\s*", "", novo)
    # 4. emoji decorativo abrindo parágrafo (a 1ª frase vira meta description
    #    e og:description — abria com o emoji escapado, lixo no Google)
    novo = re.sub(r"(<p[^>]*>)\s*(?:[☀-➿️‍\U0001f000-\U0001faff]\s*)+",
                  r"\1", novo)
    return novo, relatorio


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else ""

    if modo == "--restaurar":
        backup = json.loads(BACKUP.read_text(encoding="utf8"))
        for pid, dados in backup.items():
            req("PUT", f"products/{pid}", {"description": {"pt": dados["description_pt"]}})
            print(f"  restaurado: {dados['name'][:50]}")
        return

    produtos = todos_produtos()

    if modo != "--ver" and not BACKUP.exists():
        BACKUP.write_text(json.dumps({
            str(p["id"]): {
                "name": (p["name"].get("pt") if isinstance(p["name"], dict) else p["name"]),
                "description_pt": ((p.get("description") or {}).get("pt")
                                   if isinstance(p.get("description"), dict)
                                   else p.get("description")) or "",
            } for p in produtos
        }, ensure_ascii=False, indent=1), encoding="utf8")
        print(f"backup gravado: {BACKUP.name} ({len(produtos)} produtos)")

    for p in produtos:
        nome = p["name"].get("pt") if isinstance(p["name"], dict) else p["name"]
        desc = (p.get("description") or {})
        html = desc.get("pt") if isinstance(desc, dict) else desc
        if not html:
            continue
        novo, relatorio = limpar(html, nome)
        if novo == html:
            continue
        print(f"\n{nome[:60]}")
        for linha in relatorio:
            print(f"   {linha}")
        if modo != "--ver":
            req("PUT", f"products/{p['id']}", {"description": {"pt": novo}})
            print("   gravado.")


if __name__ == "__main__":
    main()
