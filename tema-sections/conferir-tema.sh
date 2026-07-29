#!/usr/bin/env bash
# Confere o tema montado ANTES do push.
#
# Um tema quebrado só se manifesta quando renderiza, e aí já está na loja. As
# checagens abaixo são as que pegam erro de graça, em segundos, na nossa mão:
# referência a seção que não existe, chave de tradução faltando (o editor mostra
# "t:names.museu_hero" cru pra cliente), block órfão, asset que o layout pede e
# não subiu.
#
# Uso:  cd tema-sections && ./conferir-tema.sh
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="$RAIZ/../build-tema"

if [[ ! -d "$BUILD" ]]; then
  echo "Não achei $BUILD. Rode antes: ./montar-tema.sh <ID>" >&2
  exit 1
fi

python3 - "$BUILD" <<'PY'
import json, re, sys, pathlib

build = pathlib.Path(sys.argv[1])
falhas, avisos = [], []

def schema_de(p):
    m = re.search(r'\{%\s*schema\s*%\}(.*?)\{%\s*endschema\s*%\}',
                  p.read_text(encoding='utf8'), re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        falhas.append(f"{p.relative_to(build)}: schema com JSON inválido — {e}")
        return None

# ---------- 1. traduções ----------
def achatar(o, prefixo=''):
    plano = {}
    for k, v in o.items():
        plano.update(achatar(v, f"{prefixo}{k}.") if isinstance(v, dict)
                     else {f"{prefixo}{k}": v})
    return plano

traducoes = achatar(json.loads(
    (build / 'translations' / 'pt.default.schema.json').read_text(encoding='utf8')))

usadas = set()
for sub in ('sections', 'blocks'):
    for p in (build / sub).glob('*.tpl'):
        usadas |= set(re.findall(r'"t:([a-zA-Z0-9_.]+)"', p.read_text(encoding='utf8')))

faltando = sorted(usadas - set(traducoes))
if faltando:
    falhas.append(f"{len(faltando)} chave(s) t: sem tradução: {', '.join(faltando[:8])}")

# ---------- 2. home.json aponta pra seções que existem ----------
home = json.loads((build / 'templates' / 'pages' / 'home.json').read_text(encoding='utf8'))
secoes_existentes = {p.stem for p in (build / 'sections').glob('*.tpl')}
blocks_existentes = {p.stem for p in (build / 'blocks').glob('*.tpl')}

def conferir_blocks(dono, blocos, caminho):
    for nome, b in (blocos or {}).items():
        tipo = b.get('type')
        if tipo and tipo not in blocks_existentes:
            falhas.append(f"{caminho}.{nome}: block '{tipo}' não existe em blocks/")
        conferir_blocks(dono, b.get('blocks'), f"{caminho}.{nome}")

for nome, s in home.get('sections', {}).items():
    tipo = s.get('type')
    if tipo not in secoes_existentes:
        falhas.append(f"home.json → seção '{tipo}' não existe em sections/")
    conferir_blocks(tipo, s.get('blocks'), f"home.json.{nome}")

ordem = home.get('order')
if ordem:
    orfas = [o for o in ordem if o not in home.get('sections', {})]
    if orfas:
        falhas.append(f"home.json → 'order' cita seções ausentes: {orfas}")

# ---------- 3. blocks declarados nos schemas das nossas seções ----------
for p in sorted((build / 'sections').glob('museu-*.tpl')):
    s = schema_de(p)
    if not s:
        continue
    for b in s.get('blocks', []) or []:
        if 'type' in b and b['type'] not in blocks_existentes:
            falhas.append(f"{p.name}: declara block '{b['type']}' que não existe")

# ---------- 4. assets que o layout pede existem ----------
layout = (build / 'layouts' / 'layout.tpl').read_text(encoding='utf8')
for asset in sorted(set(re.findall(r"'([^']+\.(?:css|js))'\s*\|\s*static_url", layout))):
    if not (build / 'static' / asset).exists():
        falhas.append(f"layout.tpl pede static/{asset}, que não está no build")

# ---------- 5. nossos assets subiram ----------
# Contagem recursiva: as obras vivem em static/images/obras/, então olhar só o
# primeiro nível dava aviso falso.
nossos_assets = {
    'css':    ['museu-theme.css', 'museu-ponte.css'],
    'js':     ['gsap.min.js', 'ScrollTrigger.min.js', 'museu-motion.js'],
    'fonts':  ['inter-var-latin.woff2', 'roboto-serif-var-latin.woff2',
               'roboto-serif-italic-var-latin.woff2'],
}
for pasta, arquivos in nossos_assets.items():
    for arq in arquivos:
        if not (build / 'static' / pasta / arq).exists():
            falhas.append(f"static/{pasta}/{arq} não chegou no build")

obras = list((build / 'static' / 'images' / 'obras').glob('*')) \
    if (build / 'static' / 'images' / 'obras').exists() else []
if len(obras) < 4:
    avisos.append(f"static/images/obras/ com {len(obras)} imagem(ns), esperava 4")

# ---------- resultado ----------
print(f"  seções: {len(secoes_existentes)} ({len([s for s in secoes_existentes if s.startswith('museu-')])} nossas)")
print(f"  blocks: {len(blocks_existentes)} ({len([b for b in blocks_existentes if b.startswith('museu-')])} nossos)")
print(f"  chaves t: usadas nas nossas: {len(usadas)} — todas resolvidas"
      if not faltando else f"  chaves t: FALTANDO: {len(faltando)}")
print(f"  home.json: {len(home.get('sections', {}))} seções")

for a in avisos:
    print(f"  aviso: {a}")

if falhas:
    print("\nREPROVADO:")
    for f in falhas:
        print(f"  · {f}")
    sys.exit(1)

print("\nAprovado — pode subir.")
PY
