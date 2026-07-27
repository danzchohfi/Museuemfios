#!/usr/bin/env bash
# Backup do tema que está no ar em museuemfios.com, ANTES de qualquer mudança.
#
# A Nuvemshop não guarda backup do código pra gente — a documentação deles é
# explícita: "é super importante que o profissional tenha o backup dos arquivos
# originais", e o time técnico "nem sempre vai conseguir recuperar todos eles".
# Então o backup é nosso.
#
# Este script baixa os arquivos do tema publicado pra uma pasta local, que
# depois vai pro Git. Ele NÃO cria cópia dentro da loja de propósito: a loja
# aceita no máximo duas instalações de tema (a publicada + uma), e essa segunda
# vaga é justamente a que vamos querer pro nosso tema em rascunho.
#
# Requisitos: Node.js 24.15+ e `nuvemshop theme authorize` já feito.
# Uso:  cd tema && ./backup-tema-no-ar.sh
set -euo pipefail

DATA="$(date +%Y-%m-%d)"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="$RAIZ/../backup-tema-no-ar/$DATA"
CLI="npx @tiendanube/cli@2"

echo "==> Tema publicado hoje:"
$CLI theme list

echo
echo "==> Baixando os arquivos do tema publicado para:"
echo "    $DESTINO"
mkdir -p "$DESTINO"
cd "$DESTINO"

if $CLI theme pull --published; then
  echo "    Download concluído pelo fluxo de API."
else
  cat <<'AVISO'

    O pull por API não funcionou. Isso costuma significar que o tema no ar é
    um tema legado, que só é alcançado por FTP. Nesse caso:

      1. No admin: Loja online → Layout → Editar o código
         (anote servidor, usuário e senha; exige plano com acesso ao código)
      2. Rode, dentro da pasta de destino:
           npx @tiendanube/cli@2 theme ftp setup \
             --ftp-server HOST --ftp-username USUARIO --ftp-password SENHA \
             --store-url https://museuemfios2.lojavirtualnuvem.com.br
           npx @tiendanube/cli@2 theme ftp pull

    ATENÇÃO: abrir o FTP tem efeitos permanentes na loja — o layout deixa de
    receber as atualizações automáticas da Nuvemshop, a troca de layout fica
    bloqueada enquanto estiver aberto, e ao FECHAR o FTP todas as alterações
    feitas no código são perdidas. Só abra sabendo disso.

AVISO
  exit 1
fi

echo
echo "==> Conferindo o que veio:"
find "$DESTINO" -type f | wc -l | xargs echo "    arquivos:"
du -sh "$DESTINO" | cut -f1 | xargs echo "    tamanho:"

cat <<EOF

Backup local pronto em $DESTINO
Commite essa pasta pra ter o histórico fora da plataforma:

    git add backup-tema-no-ar && git commit -m "Backup do tema no ar ($DATA)"

EOF
