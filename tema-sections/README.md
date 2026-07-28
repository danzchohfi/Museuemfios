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

## 🚧 O portão: o fork ainda pode não estar liberado

A documentação do CLI diz, sobre instalações de tema:

> *"Coming soon — Forking installations is coming soon… For now, running
> `tiendanube theme fork` returns a notice that forking isn't enabled yet."*

Isso importa muito, porque **sem fork a instalação só aceita três caminhos no
push**. Confirmei no código do próprio CLI 2.1.0
(`theme-api-fork-rules.ts`):

```js
var NON_FORK_PREFIXES = ["custom/", "templates/"];
var NON_FORK_EXACT = ["config/settings_data.json"];
```

Tudo fora disso é **descartado em silêncio** — inclusive `sections/`,
`blocks/`, `static/` e `settings_schema.json`, que é justamente onde mora a
nossa identidade.

E é ainda mais apertado do que essas duas listas sugerem: o push também aplica
`PUSH_UNSUPPORTED_PREFIXES = ["custom"]`, então `custom/` **não sobe de jeito
nenhum**. Sem fork, o que realmente passa é só **`templates/**` e
`config/settings_data.json`**.

> **Precedente do Alfa Pesca (mesma base, mesmo problema).** Conferi o
> repositório `danzchohfi/alfa-pesca`: mesmo Layout Base legado, mesma pasta
> `snipplets/`. Rodando o filtro do CLI sobre aquele tema: **40 arquivos
> subiriam, 129 seriam descartados** — 126 deles a `snipplets/` inteira, alvo
> de 79 includes em 82 templates. Aquele README também recomenda o
> `theme push`, e o status lá é "Pronto pra teste em rascunho" — ou seja, o
> caminho está descrito nos dois projetos, mas **não há registro de ter sido
> executado com sucesso em nenhum**. O precedente não valida o push: ele
> repete a mesma armadilha.

Ou seja, existem dois cenários:

- **Fork liberado para a loja** → esta pasta entra inteira e a migração se
  completa: seções autorais, CSS, motion, tudo.
- **Fork ainda bloqueado** → dá pra enviar só `templates/pages/home.json` +
  `settings_data.json`, ou seja, remontar a home com as **sections nativas do
  Ipanema** e as cores/fontes da marca. Fica no ar com a identidade aproximada,
  sem o hero do fio, o marquee e a noite — que esperam o fork.

Quem responde é a loja: `npx @tiendanube/cli@2 theme fork --theme-id <ID>`.
O CLI 2.1.0 já traz `fork`/`unfork` implementados e chamando a API, então a
documentação pode estar defasada — vale testar antes de assumir o pior.

## O que já está aqui

| Arquivo | Estado |
|---|---|
| `static/css/museu-theme.css` | ✅ **Portável, 1.318 linhas.** Tokens, tipografia e todos os componentes autorais (`.mf-*`, `.obra-card`, `.guia-card`, o grafismo do fio). Não depende de classe nenhuma do tema base. |
| `static/css/museu-ponte.css` | ⚠️ **154 linhas a refazer.** Reestilização dos componentes da plataforma (grade, botões, header, footer, produto). As regras miram classes do Layout Base e ficam como referência do efeito pretendido — reescrever contra as classes do Ipanema. |
| `static/js/museu-motion.js` | ✅ **Portável.** Motion GSAP (fio que se desenha, reveals, carrossel do hero, cursor-linha). Usa helper próprio sobre `querySelector`, sem jQuery, e mira só as nossas classes. |
| `static/js/gsap.min.js`, `ScrollTrigger.min.js` | ✅ GSAP 3.15.0 vendorizado (sem CDN). |
| `static/fonts/*.woff2` | ✅ Inter + Roboto Serif (variáveis, subset latin). |
| `static/images/obras/*.jpg` | ✅ As 4 obras usadas no hero e no "sobre". |

### As 6 seções autorais — prontas

No legado eram `.tpl` com texto fixo no código. Aqui todas viram seções
**editáveis no admin**, e o que era lista chumbada virou **blocks** que a
cliente adiciona, reordena e reescreve sozinha:

| Section | Blocks | O que a cliente edita sem código |
|---|---|---|
| `museu-hero` | `museu-obra` (até 6) | Cada obra em destaque: imagem, cor de fundo, ficha técnica, link do kit. Antes eram 3 destaques chumbados no `.tpl`. |
| `museu-marquee` | `museu-frase` (até 8) | As frases que rodam na faixa — endline, frete, cupom. |
| `museu-manifesto` | — | Frase do manifesto, apoio e link. |
| `museu-noite` | — | Copy do ritual e o **ID do vídeo** no YouTube (só o ID: o embed continua sempre em modo nocookie). |
| `museu-passos` | `museu-passo` | As sub-mensagens da marca. A numeração (01, 02…) vem da posição — reordenar renumera sozinho. |
| `museu-kit` | `museu-item-kit` | O que vem no kit, item a item. |

`templates/pages/home.json` já monta a home nessa ordem com toda a copy
aprovada, e `translations/pt.default.schema.json` traz os rótulos do editor.

**Validação feita aqui:** os 10 blocos `{% schema %}` são JSON válido; as 51
chaves `t:` usadas existem todas nas traduções; nenhuma referência órfã entre
`home.json`, `sections/` e `blocks/`; todo block aplica o filtro obrigatório
`block_attributes`; tags Twig balanceadas; e todo `setting_type` está dentro da
lista oficial documentada.

## O que falta — e depende de ver o Ipanema por dentro

- **Reescrever `museu-ponte.css`** contra a marcação do Ipanema (154 linhas).
- **`config/settings_schema.json`** com os tokens da marca. **Não escrevi de
  propósito:** a documentação mostra só um painel isolado, nunca a raiz do
  arquivo — não dá pra saber se é array ou objeto. Escrever no chute quebraria
  o tema inteiro; melhor copiar a estrutura do arquivo real após o `pull`. Os
  tokens da marca, por ora, vivem como custom properties no `museu-theme.css`,
  que é autossuficiente.
- **Como referenciar assets de `static/`** — a maior lacuna: `static_url` está
  documentado só para o tema legado e **não aparece em nenhuma página do formato
  novo**. As seções foram escritas evitando o problema (as imagens vêm de
  `image_picker`, que a cliente sobe pelo admin), mas o CSS/JS no `layout.tpl`
  vai precisar da sintaxe correta — que se lê direto do `layouts/layout.tpl` do
  Ipanema.
- **`translations/` vs `locales/`** — a doc do CLI diz `locales/`, a doc de
  temas diz `translations/`. Fui de `translations/` com base no código do CLI:
  a lista de sincronização (`SYNC_PREFIXES`) aceita `translations` e **não tem
  `locales`** — uma pasta `locales/` nem subiria. Confirmar no `pull`.

## Aberto — só a loja responde

- **A loja já tem o Ipanema?** O fork "está em rollout e pode ainda não estar
  disponível para todas as lojas". `./../tema/diagnostico-loja.sh` responde.
- **A loja aceita no máximo 2 instalações de tema** (a publicada + uma). A vaga
  de rascunho é a que esta migração vai ocupar.
