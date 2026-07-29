#!/usr/bin/env bash
# Converte o `.nuvem` (escrito pelo CLI 2.x) no `.nube` que o CLI 1.2.1 lê.
#
# POR QUE ISSO EXISTE
#
# As duas versões guardam a credencial em arquivos diferentes, com esquemas
# diferentes, e nenhuma das duas lê o arquivo da outra:
#
#   CLI 2.x  → `.nuvem`, base64 de:
#              {"store_id": 6671481, "access_token": "…"}
#
#   CLI 1.2.1 → `.nube`, base64 de:
#              {"themeManagement":"api",
#               "theme-api":{"publicApiToken":"…","storeId":"…"}}
#
# Detalhe que quebra em silêncio: em `theme-api`, o `storeId` tem que ser
# STRING. Number reprova na validação e o CLI diz que a configuração é
# inválida, sem explicar o motivo.
#
# Sintomas de estar sem o `.nube` correto, rodando o 1.2.1:
#   "Store configuration not found. Please run nuvemshop theme authorize first."
#   "Theme API is not active. Run nuvemshop theme authorize …"
#
# O `theme authorize` do 1.2.1 escreveria esse arquivo sozinho, mas ele abre o
# navegador — e num sandbox sem sessão do usuário isso não acontece. Daí a
# conversão a partir do token que o 2.x já obteve.
#
# Uso:  cd tema && ./nube-a-partir-do-nuvem.sh [caminho-do-.nuvem]
#       (sem argumento, procura `.nuvem` na pasta atual)
set -euo pipefail

ORIGEM="${1:-.nuvem}"

if [[ ! -f "$ORIGEM" ]]; then
  cat <<USO
    Não achei "$ORIGEM".

    Rode antes, na sua máquina:
        npx @tiendanube/cli@2 theme authorize

    e traga o .nuvem gerado para esta pasta — ou passe o caminho dele:
        ./nube-a-partir-do-nuvem.sh ~/museu-auth/.nuvem
USO
  exit 1
fi

python3 - "$ORIGEM" <<'PY'
import base64, json, sys, pathlib

origem = pathlib.Path(sys.argv[1])
bruto = origem.read_text().strip()

try:
    dados = json.loads(bruto if bruto.startswith("{") else base64.b64decode(bruto))
except Exception as erro:
    sys.exit(f"Não consegui ler {origem}: {erro}")

for campo in ("store_id", "access_token"):
    if campo not in dados:
        sys.exit(f"Falta o campo {campo!r} em {origem}.")

doc = {
    "themeManagement": "api",
    "theme-api": {
        "publicApiToken": dados["access_token"],
        "storeId": str(dados["store_id"]),  # string, não number
    },
}

destino = pathlib.Path(".nube")
destino.write_text(base64.b64encode(json.dumps(doc).encode()).decode())
destino.chmod(0o600)
print(f"    .nube gravado para a loja {dados['store_id']}.")
PY

cat <<'FIM'

Pronto. Agora o CLI 1.2.1 enxerga a loja:

    npx @tiendanube/cli@1.2.1 theme installation list

Os dois arquivos (.nuvem e .nube) carregam a credencial em claro e estão no
.gitignore. Ao terminar o trabalho, revogue o acesso no admin da loja:
Aplicativos → aplicativos autorizados → remover o CLI.

FIM
