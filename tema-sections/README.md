# Museu em Fios — tema no formato sections (em migração)

Reconstrução do tema no **formato sections** da Nuvemshop (tema base
**Ipanema**), que é o que habilita o fluxo que a gente quer: instalação de
**rascunho**, **link de pré-visualização** e publicação só na aprovação — tudo
pelo CLI, sem abrir FTP na loja.

> A pasta **`../tema/`** (formato legado, funcionando) **continua intacta** e é
> o plano B. Nada aqui substitui aquilo até a migração estar validada na loja.

## Por que migrar

O CLI 2.x sincroniza pela API só os caminhos `blocks, config, custom, layouts,
sections, snippets, static, templates, translations, manifest.json`. O tema
legado usa `snipplets/` (dois "p"), que **não está na lista**: um `theme push`
descartaria 130 dos 180 arquivos em silêncio. Detalhes em `../tema/README.md`.

## Como esta migração funciona

O formato sections não é um tema "do zero": ele nasce de um tema base do
catálogo. O caminho é **criar uma instalação do Ipanema, forkar (libera todos os
arquivos) e aplicar a nossa identidade por cima**. Ou seja, esta pasta é a
**carga autoral** — o que é nosso — pronta pra entrar num Ipanema forkado:

```bash
cd tema-sections
npx @tiendanube/cli@2 theme authorize
npx @tiendanube/cli@2 theme create --base-theme ipanema --title "Museu em Fios — Identidade 2026"
npx @tiendanube/cli@2 theme fork --theme-id <ID>    # mão única: para de receber updates do base
npx @tiendanube/cli@2 theme pull --theme-id <ID>    # traz a árvore do Ipanema pra cá
# ... aplicar a carga autoral sobre a árvore ...
npx @tiendanube/cli@2 theme push --theme-id <ID>
npx @tiendanube/cli@2 theme preview --theme-id <ID>
```

## O que já está aqui

| Arquivo | Estado |
|---|---|
| `static/css/museu-theme.css` | ✅ **Portável, 1.318 linhas.** Tokens, tipografia e todos os componentes autorais (`.mf-*`, `.obra-card`, `.guia-card`, o grafismo do fio). Não depende de classe nenhuma do tema base. |
| `static/css/museu-ponte.css` | ⚠️ **154 linhas a refazer.** Reestilização dos componentes da plataforma (grade, botões, header, footer, produto). As regras miram classes do Layout Base e ficam como referência do efeito pretendido — reescrever contra as classes do Ipanema. |
| `static/js/museu-motion.js` | ✅ **Portável.** Motion GSAP (fio que se desenha, reveals, carrossel do hero, cursor-linha). Usa helper próprio sobre `querySelector`, sem jQuery, e mira só as nossas classes. |
| `static/js/gsap.min.js`, `ScrollTrigger.min.js` | ✅ GSAP 3.15.0 vendorizado (sem CDN). |
| `static/fonts/*.woff2` | ✅ Inter + Roboto Serif (variáveis, subset latin). |
| `static/images/obras/*.jpg` | ✅ As 4 obras usadas no hero e no "sobre". |

## O que falta

- **As 6 seções autorais** (`sections/`): hero, marquee, manifesto, noite,
  passos, kit. No legado eram `.tpl` com texto fixo; aqui viram seções
  **configuráveis no admin** — o hero, em especial, deixa de ter 3 destaques
  chumbados no código e passa a usar **blocks** repetíveis (obra, ficha, link
  do produto).
- **`templates/home.json`** ordenando as seções.
- **`config/settings_schema.json`** com os tokens da marca (paleta, fontes).
- **`translations/`** — atenção: a documentação fala em `locales/`, mas a lista
  de sincronização do CLI aceita **`translations`**. Confirmar na árvore real do
  Ipanema qual das duas o tema usa.
- **Reescrever `museu-ponte.css`** contra a marcação do Ipanema.

## Aberto — só a loja responde

- **A loja já tem o Ipanema?** O fork "está em rollout e pode ainda não estar
  disponível para todas as lojas". `./../tema/diagnostico-loja.sh` responde.
- **A loja aceita no máximo 2 instalações de tema** (a publicada + uma). A vaga
  de rascunho é a que esta migração vai ocupar.
