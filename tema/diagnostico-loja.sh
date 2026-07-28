#!/usr/bin/env bash
# Diagnóstico da loja — SÓ LEITURA, não altera nada.
#
# Roda antes de qualquer upload pra responder as três perguntas que decidem
# o caminho da subida do tema:
#
#   1. Qual tema está no ar hoje e quantas instalações a loja já tem?
#      (o limite é 2 por loja: a publicada + uma de rascunho)
#   2. A loja já tem acesso ao tema base novo (Ipanema / sections)?
#      É o que habilita o fluxo de rascunho + link de preview pelo CLI.
#   3. As instalações são "fork" (código liberado) ou não?
#
# A VERSÃO DO CLI IMPORTA: o 1.2.1 manda a pasta inteira (só pula arquivos
# ocultos), enquanto o 2.x só sincroniza uma lista de pastas que NÃO inclui
# `snipplets/` — com ele este tema subiria sem 130 arquivos, em silêncio.
# Por isso a versão está fixada aqui. Nunca rode sem versão.
#
# Requisitos: Node.js 24.15+ e `theme authorize` já feito.
# Uso:  cd tema && ./diagnostico-loja.sh
set -euo pipefail

CLI="npx @tiendanube/cli@1.2.1"

echo "==> Versão do Node (o CLI exige 24.15.0 ou superior):"
node --version

echo
echo "==> Instalação vinculada a esta pasta:"
$CLI theme get-current || true

echo
echo "==> Temas da loja:"
echo "    Leia as colunas: prod = está no ar · fork = código liberado"
echo "    base_theme = tema base · base_theme_type = geração do tema"
$CLI theme list

echo
echo "==> Mesma lista em JSON (guarde este bloco, é o retrato de hoje):"
$CLI theme list --json
