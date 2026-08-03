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
# A VERSÃO DO CLI IMPORTA: o 1.2.1 baixa e envia a pasta inteira; o 2.x só
# sincroniza uma lista de pastas que NÃO inclui `snipplets/`. Num backup isso
# seria pior ainda — a cópia sairia incompleta parecendo completa.
#
# Requisitos: Node.js 24.15+ e `theme authorize` já feito.
# Uso:  cd tema && ./backup-tema-no-ar.sh <ID_DA_INSTALACAO_PUBLICADA>
#       (o ID sai do `theme list` — é a instalação marcada como publicada)
set -euo pipefail

DATA="$(date +%Y-%m-%d)"
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINO="$RAIZ/../backup-tema-no-ar/$DATA"
CLI="npx @tiendanube/cli@1.2.1"

echo "==> Instalações da loja (ache a publicada e anote o ID):"
$CLI theme installation list

ID_PUBLICADA="${1:-}"
if [[ -z "$ID_PUBLICADA" ]]; then
  cat <<'USO'

    Falta o ID da instalação publicada. Rode de novo passando o ID que
    aparece na lista acima:

        ./backup-tema-no-ar.sh <ID_DA_INSTALACAO_PUBLICADA>

USO
  exit 1
fi

echo
echo "==> Baixando os arquivos da instalação $ID_PUBLICADA para:"
echo "    $DESTINO"
mkdir -p "$DESTINO"

# O CLI procura a credencial na PASTA ATUAL. Como o pull roda dentro da pasta
# de destino, o `.nube` precisa ir junto — sem isso o comando responde
# "Store configuration not found" e mesmo assim sai com código 0, produzindo
# um backup vazio com cara de completo.
if [[ ! -f "$RAIZ/.nube" ]]; then
  echo "    Falta o $RAIZ/.nube — rode antes: ./nube-a-partir-do-nuvem.sh" >&2
  exit 1
fi
cp "$RAIZ/.nube" "$DESTINO/.nube"
chmod 600 "$DESTINO/.nube"
cd "$DESTINO"

# `theme pull` sai com 0 mesmo quando não baixa nada, então o `if` abaixo não
# basta: quem decide se o backup vale é a contagem de arquivos, mais adiante.
if $CLI theme pull --installation-id "$ID_PUBLICADA" -y; then
  echo "    Comando de download retornou sucesso — falta conferir o conteúdo."
else
  cat <<'AVISO'

    O pull por API não funcionou. Isso costuma significar que o tema no ar é
    um tema legado, que só é alcançado por FTP. Nesse caso:

      1. No admin: Loja online → Layout → Editar o código
         (anote servidor, usuário e senha; exige plano com acesso ao código)
      2. Rode, dentro da pasta de destino:
           npx @tiendanube/cli@1.2.1 theme ftp setup \
             --ftp-server HOST --ftp-username USUARIO --ftp-password SENHA \
             --store-url https://museuemfios2.lojavirtualnuvem.com.br
           npx @tiendanube/cli@1.2.1 theme ftp pull

    ATENÇÃO: abrir o FTP tem efeitos permanentes na loja — o layout deixa de
    receber as atualizações automáticas da Nuvemshop, a troca de layout fica
    bloqueada enquanto estiver aberto, e ao FECHAR o FTP todas as alterações
    feitas no código são perdidas. Só abra sabendo disso.

AVISO
  exit 1
fi

echo
echo "==> Conferindo o que veio:"
rm -f "$DESTINO/.nube"                      # a credencial não fica no backup
TOTAL=$(find "$DESTINO" -type f | wc -l | tr -d ' ')
echo "    arquivos: $TOTAL"
du -sh "$DESTINO" | cut -f1 | xargs echo "    tamanho:"

# Um backup vazio é pior que nenhum: passa a sensação de estar protegido.
if [[ "$TOTAL" -eq 0 ]]; then
  cat >&2 <<'VAZIO'

    BACKUP VAZIO — nenhum arquivo baixado.

    O `theme pull` sai com código 0 mesmo quando não baixa nada, então não dá
    pra confiar no código de saída dele. Causas comuns, em ordem:

      1. A instalação não é `fork`. Sem fork a API não entrega os arquivos.
         Confira a coluna `fork` no `theme installation list`.
      2. O tema é `legacy`. O acesso ao código nesse formato é por FTP.
      3. O `.nube` não chegou na pasta de destino.

    NÃO SIGA para o push enquanto isso não estiver resolvido.

VAZIO
  exit 1
fi

cat <<EOF

Backup local pronto em $DESTINO ($TOTAL arquivos)
Commite essa pasta pra ter o histórico fora da plataforma:

    git add backup-tema-no-ar && git commit -m "Backup do tema no ar ($DATA)"

EOF
