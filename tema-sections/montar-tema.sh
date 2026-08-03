#!/usr/bin/env bash
# Monta o tema pronto pra subir: árvore do Ipanema + nossa identidade por cima.
#
# POR QUE MONTAR EM VEZ DE VERSIONAR TUDO
#
# O tema que sobe na loja tem ~310 arquivos, e só ~26 são nossos. Os outros são
# o Ipanema, que é da Nuvemshop e recebe atualizações deles. Versionar a árvore
# inteira misturaria as duas coisas e tornaria impossível responder "o que aqui
# é autoral?" daqui a seis meses. Então o repositório guarda só o que é nosso, e
# este script refaz a mistura quando precisa subir.
#
# Efeito colateral bom: para pegar uma versão nova do Ipanema, basta rodar de
# novo. Nada de merge manual.
#
# Uso:  cd tema-sections && ./montar-tema.sh <ID_DA_INSTALACAO>
# Saída: ../build-tema/  (fora do Git, é artefato)
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="$RAIZ/../build-tema"
CLI="npx @tiendanube/cli@1.2.1"
ID="${1:-}"

if [[ -z "$ID" ]]; then
  echo "Uso: ./montar-tema.sh <ID_DA_INSTALACAO>" >&2
  echo "     (o ID sai de: $CLI theme installation list)" >&2
  exit 1
fi

if [[ ! -f "$RAIZ/../tema/.nube" ]]; then
  echo "Falta o .nube. Rode antes: cd ../tema && ./nube-a-partir-do-nuvem.sh" >&2
  exit 1
fi

echo "==> 1/6  Baixando a árvore do Ipanema (instalação $ID)"
rm -rf "$DESTINO"
mkdir -p "$DESTINO"
cp "$RAIZ/../tema/.nube" "$DESTINO/.nube"
chmod 600 "$DESTINO/.nube"
(cd "$DESTINO" && $CLI theme pull --installation-id "$ID" -y >/dev/null)

BAIXADOS=$(find "$DESTINO" -type f ! -name .nube | wc -l | tr -d ' ')
if [[ "$BAIXADOS" -lt 100 ]]; then
  echo "    Só vieram $BAIXADOS arquivos — esperava a árvore inteira do Ipanema." >&2
  echo "    Confira se o ID $ID é mesmo a instalação sectionable." >&2
  exit 1
fi
echo "    $BAIXADOS arquivos do tema base."

echo "==> 2/6  Copiando nossas seções e blocks"
cp "$RAIZ"/sections/museu-*.tpl "$DESTINO/sections/"
cp "$RAIZ"/blocks/museu-*.tpl  "$DESTINO/blocks/"
echo "    $(ls -1 "$RAIZ"/sections/museu-*.tpl | wc -l | tr -d ' ') seções, $(ls -1 "$RAIZ"/blocks/museu-*.tpl | wc -l | tr -d ' ') blocks."

echo "==> 3/6  Copiando CSS, JS, fontes e imagens"
mkdir -p "$DESTINO/static/css" "$DESTINO/static/js" "$DESTINO/static/fonts" "$DESTINO/static/images"
cp -r "$RAIZ"/static/css/*      "$DESTINO/static/css/"
cp -r "$RAIZ"/static/js/*       "$DESTINO/static/js/"
cp -r "$RAIZ"/static/fonts/*    "$DESTINO/static/fonts/"
cp -r "$RAIZ"/static/images/*   "$DESTINO/static/images/"

echo "==> 4/6  Fundindo as traduções do editor"
# As nossas ENTRAM nas do Ipanema — não substituem. O arquivo nativo tem 719
# chaves que as seções nativas usam; sobrescrever o arquivo quebraria todas.
python3 - "$RAIZ" "$DESTINO" <<'PY'
import json, sys, pathlib

raiz, destino = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])

def fundir(base, novo):
    """Merge recursivo: o `novo` acrescenta e sobrescreve folha a folha."""
    for chave, valor in novo.items():
        if isinstance(valor, dict) and isinstance(base.get(chave), dict):
            fundir(base[chave], valor)
        else:
            base[chave] = valor
    return base

for nome in ("pt.default.json", "pt.default.schema.json"):
    nosso = raiz / "translations" / nome
    alvo = destino / "translations" / nome
    if not nosso.exists():
        continue
    base = json.loads(alvo.read_text(encoding="utf8")) if alvo.exists() else {}
    antes = len(json.dumps(base))
    fundido = fundir(base, json.loads(nosso.read_text(encoding="utf8")))
    alvo.write_text(json.dumps(fundido, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"    {nome}: {antes} → {len(json.dumps(fundido))} bytes")
PY

echo "==> 5/6  Instalando a home"
cp "$RAIZ/templates/pages/home.json" "$DESTINO/templates/pages/home.json"

echo "==> 6/6  Ligando nosso CSS e JS no layout"
python3 - "$DESTINO" <<'PY'
import sys, pathlib

layout = pathlib.Path(sys.argv[1]) / "layouts" / "layout.tpl"
texto = layout.read_text(encoding="utf8")

if "museu-theme.css" in texto:
    print("    layout já estava ligado — nada a fazer.")
    raise SystemExit

# O CSS entra DEPOIS do style-async do Ipanema e ANTES do css_code do admin:
# assim a nossa identidade vence o tema base, mas o campo de CSS customizado do
# admin continua sendo a última palavra da cliente.
ancora_css = "    {# Custom CSS from settings #}"
nosso_css = """    {# Museu em Fios — identidade #}
    <link rel="stylesheet" href="{{ 'css/museu-theme.css' | static_url }}">
    <link rel="stylesheet" href="{{ 'css/museu-ponte.css' | static_url }}">

"""
if ancora_css not in texto:
    raise SystemExit("ERRO: não achei a âncora do CSS no layout.tpl")
texto = texto.replace(ancora_css, nosso_css + ancora_css, 1)

# O JS entra depois do libraries-standalone (que traz o Swiper e o Lazysizes e
# é carregado de forma bloqueante justamente pra estar disponível). O GSAP e o
# nosso motion vão na mesma linha de raciocínio: o ScrollTrigger precisa existir
# antes do museu-motion rodar.
ancora_js = "    {# JavaScript - Non-critical libraries and theme store: loaded after LS.ready #}"
nosso_js = """    {# Museu em Fios — motion (GSAP + ScrollTrigger, sem jQuery) #}
    {{ 'js/gsap.min.js' | static_url | script_tag }}
    {{ 'js/ScrollTrigger.min.js' | static_url | script_tag }}
    {{ 'js/museu-motion.js' | static_url | script_tag }}

"""
if ancora_js not in texto:
    raise SystemExit("ERRO: não achei a âncora do JS no layout.tpl")
texto = texto.replace(ancora_js, nosso_js + ancora_js, 1)

layout.write_text(texto, encoding="utf8")
print("    CSS antes do css_code do admin; JS depois do libraries-standalone.")
PY

rm -f "$DESTINO/.nube"
TOTAL=$(find "$DESTINO" -type f | wc -l | tr -d ' ')

cat <<FIM

Tema montado em $DESTINO ($TOTAL arquivos)

Conferir antes de subir:
    ./conferir-tema.sh

Subir (NÃO publica — só manda os arquivos pro rascunho):
    cd ../build-tema && cp ../tema/.nube . && \\
      npx @tiendanube/cli@1.2.1 theme push --installation-id $ID -y

FIM
