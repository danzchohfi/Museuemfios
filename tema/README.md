# Museu em Fios — tema Nuvemshop

Tema da loja **museuemfios.com**, construído sobre o [Layout Base oficial da
Nuvemshop](https://github.com/TiendaNube/base-theme) (fork da v1.14.0, a mesma
base validada em produção no projeto Alfa Pesca) com a nova identidade do
Estúdio Agudo: Inter + Roboto Serif, paleta amarelo/verde/azul, grafismo de linhas
("fio") e motion GSAP.

Por ser fork do Layout Base, **tudo da plataforma continua funcionando**:
carrinho AJAX, variantes, frete, contas de cliente, blog, busca e checkout.

## ⚠️ Antes de subir: duas gerações de tema na Nuvemshop

A Nuvemshop tem hoje **duas arquiteturas de tema convivendo**, e isso decide
como este tema pode subir:

| | **Legado ("Layout Base")** | **Sections (base Ipanema)** |
|---|---|---|
| Pastas | `config/`, `layouts/`, `snipplets/`, `templates/` (`.tpl`), `static/` | `blocks/`, `sections/`, `snippets/`, `locales/`, `templates/` (`.json`), `config/*.json`, `manifest.json` |
| Sincroniza por | FTP legado (`nuvemshop theme ftp …`) | API (`nuvemshop theme push/pull/preview`) |
| Rascunho + link de preview pelo CLI | ❌ | ✅ |

**Este tema é do formato legado** (fork do Layout Base v1.14.0), com a pasta
`snipplets/` — grafia antiga, com dois "p".

### Por que `nuvemshop theme push` NÃO serve pra este tema

O CLI 2.x sincroniza pela API apenas os caminhos `blocks, config, custom,
layouts, sections, snippets, static, templates, translations, manifest.json`.
A pasta `snipplets/` **não está nessa lista** e é descartada em silêncio.
Rodando o filtro do CLI sobre esta pasta: **47 arquivos subiriam e 130 seriam
ignorados** — todos os 130 da `snipplets/`, alvo de 302 `{% include %}`
espalhados por 82 templates. O tema subiria quebrado, sem erro aparente.

Ou seja: o caminho da API exige **migrar o tema pro formato sections** antes.

## Passo 1 — diagnóstico e backup (rodar sempre antes)

```bash
# Requisito: Node.js 24.15+ (o CLI 2.x não roda em versões menores)
cd tema
npx @tiendanube/cli@2 theme authorize   # login no navegador

./diagnostico-loja.sh      # só leitura: mostra o tema no ar e as instalações
./backup-tema-no-ar.sh     # baixa o tema publicado pra ../backup-tema-no-ar/
```

O diagnóstico responde o que falta pra decidir o caminho: qual tema está no ar,
quantas instalações existem (**a loja aceita no máximo 2**: a publicada + uma
de rascunho) e se a loja já recebeu o tema base novo (Ipanema) — cujo rollout,
segundo a própria documentação, "pode ainda não estar disponível para todas as
lojas".

> A Nuvemshop **não guarda backup do código** pra gente: "é super importante que
> o profissional tenha o backup dos arquivos originais… nosso time técnico nem
> sempre vai conseguir recuperar todos eles". O backup é nosso.

## Passo 2 — os dois caminhos de subida

### A) FTP legado — sobe este tema como está

```bash
cd tema
npx @tiendanube/cli@2 theme ftp setup \
  --ftp-server HOST --ftp-username USUARIO --ftp-password SENHA \
  --store-url https://museuemfios2.lojavirtualnuvem.com.br
npx @tiendanube/cli@2 theme ftp push     # sobe tudo, inclusive snipplets/
npx @tiendanube/cli@2 theme ftp watch    # opcional: dev ao vivo
```

Credenciais em **Loja online → Layout → Editar o código** (exige plano com
acesso ao código-fonte). Diferente do fluxo de API, o FTP envia a pasta inteira
— só ignora arquivos ocultos (`.nuvem`, `.git`).

**O preço, documentado pela Nuvemshop:** com o FTP aberto o layout **deixa de
receber as atualizações automáticas**, a **troca de layout fica bloqueada**
enquanto estiver aberto, e ao **fechar o FTP todas as alterações no código são
perdidas** — sem recuperação. Some-se a isso que o FTP alcança o espaço de
código do layout da loja, não uma instalação de rascunho separada: não é o
"vejo em rascunho e publico depois" que o fluxo novo oferece.

### B) Migrar pro formato sections — habilita rascunho + preview

Converte este tema pra estrutura nova (`snipplets/` → `snippets/`, templates
`.tpl` → `.json` + `sections/` e `blocks/`, `config/*.txt` →
`settings_schema.json`/`settings_data.json`, mais o `manifest.json`). Depois
disso o fluxo vira o que queremos:

```bash
nuvemshop theme create --base-theme ipanema --title "Museu em Fios — Identidade 2026"
nuvemshop theme fork --theme-id <ID>      # libera todos os arquivos (mão única)
nuvemshop theme push --theme-id <ID>
nuvemshop theme preview --theme-id <ID>   # link de pré-visualização
nuvemshop theme publish --theme-id <ID>   # só quando aprovado
```

É o caminho alinhado com pra onde a plataforma está indo, mas é **reescrita de
arquitetura**, não conversão mecânica: a home V1 (hero, marquee, manifesto,
noite, passos, kit) teria de virar sections/blocks configuráveis. E `fork` é
**operação de mão única** — dali em diante o tema não recebe mais updates
automáticos do tema base.

> ⚠️ O `authorize` grava o token em `.nuvem` nesta pasta — já está no
> `.gitignore`, **não commite**. O arquivo é ofuscado, não criptografado.

### Pontos ainda em aberto (confirmar na prática)

- **O link do `theme preview` é compartilhável?** As fontes oficiais se
  contradizem: a documentação diz que "a pré-visualização é visível apenas para
  você", o README do CLI no GitHub diz "shareable". Testar em aba anônima antes
  de mandar pro cliente.
- **A loja já tem Ipanema?** Só o `theme list` do diagnóstico responde.

## Pós-upload (checklist no admin)

1. **Cores/fontes**: os defaults já vêm certos (preto `#1D1D1B`, papel
   `#FBFAF6`, amarelo `#F2C440`, Inter títulos + Roboto Serif texto). Se o tema já
   estava instalado, confira em Layout → Personalizar.
2. **Logo**: subir o logo vertical preto (SVG/PNG em `../brand/logos/`) em
   Layout → Personalizar → Logo. O favicon amarelo está em
   `../demo/assets/img/favicon-amarelo.png`.
3. **WhatsApp**: conferir o número da loja em Configurações (alimenta o botão
   flutuante e o CTA "Dúvidas sobre o kit?" no produto).
4. **Home (conceito V1 · "editorial claro" — aprovado pelo cliente)**: o hero
   da obra, o marquee da endline, o manifesto, os passos da experiência e o
   "o que vem no kit" são fixos do tema (edição nos snipplets em
   `snipplets/museu/`). As seções nativas (produtos em destaque, categorias,
   vídeo, instafeed…) seguem configuráveis em Layout → Personalizar e entram
   entre o manifesto e os passos.
5. **Obras em destaque do hero**: Femme à l'ombrelle (Monet), Die Umarmung
   (Klimt) e Le Pont Japonais (Monet), cada uma apontando pro produto real.
   Pra trocar, edite `snipplets/museu/hero.tpl` (imagem em
   `static/images/obras/`, ficha e URL do produto).
6. **Vídeo institucional (seção da noite)**: a home quebra pra um gradiente
   de noite com o vídeo da cliente bordando (YouTube). Pra trocar o vídeo,
   edite o `src` do iframe em `snipplets/museu/noite.tpl`.
7. **Educativo (blog/recursos)**: a demo mostra o conceito em
   `educativo.html`. Na loja, o caminho é o **blog nativo** da Nuvemshop —
   os templates `templates/blog.tpl` e `blog-post.tpl` já vêm do Layout Base
   com a skin aplicada. Ative o blog no admin, crie os primeiros posts
   (dicas, vídeos avulsos, histórias das obras) e adicione "Educativo" ao
   menu de navegação.

## O que foi alterado vs. Layout Base

| Arquivo | Mudança |
|---|---|
| `config/defaults.txt` | Paleta da identidade + Inter/Roboto Serif como padrão; header claro |
| `layouts/layout.tpl` | `museu-theme.css` + GSAP vendorizado + `museu-motion.js`; fontes com peso 900; `<main>` em volta do conteúdo |
| `templates/home.tpl` | Home V1: hero + marquee + manifesto no topo; seções nativas no meio; passos e "o que vem no kit" no fim |
| `templates/product.tpl` | CTA "Dúvidas sobre o kit?" (WhatsApp) |
| `snipplets/museu/*` | `hero`, `marquee`, `manifesto`, `noite` (vídeo institucional no gradiente da noite), `passos`, `kit` (home V1) + CTA WhatsApp |
| `snipplets/footer.tpl` | Crédito "Site por vitamina." com link |
| `static/css/museu-theme.css` | Skin completa: design system + ponte pros componentes nativos |
| `static/js/museu-motion.js` | Motion GSAP: desenho do "fio", reveals, cursor-linha, carrossel do hero |
| `static/js/gsap*.js` | GSAP 3.15.0 + ScrollTrigger (licença gratuita GreenSock/Webflow) |

Nenhum hook `.js-*` do tema base foi alterado — atualizações de comportamento
da plataforma continuam compatíveis.

## Animações na Nuvemshop — o que está validado

- **GSAP + ScrollTrigger (fio que se desenha, reveals, carrossel do hero):
  funciona.** Validação em produção no projeto Alfa Pesca (GSAP rodando na
  vitrine Nuvemshop sem conflito com o jQuery/carrinho da plataforma). Aqui
  está ainda mais robusto: os arquivos são servidos do próprio tema
  (`static/js/gsap.min.js`, via `static_url`) — sem CDN externo. A vitrine
  não impõe CSP restritiva e nenhum hook `.js-*` da plataforma é tocado.
- **Sempre com rede de segurança**: sem JS ou com `prefers-reduced-motion`,
  a home fica estática — o hero mostra o primeiro destaque e todo o conteúdo
  continua legível e 100% funcional.

## Acessibilidade & motion

- Foco visível em tudo, alvos ≥44px, texto em PT-BR, skip-link.
- GSAP vendorizado (sem CDN) com guarda dupla: sem JS ou com
  `prefers-reduced-motion`, o site fica estático e 100% funcional — o conteúdo
  nunca depende da animação.
