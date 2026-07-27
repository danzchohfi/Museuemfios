# Museu em Fios — tema Nuvemshop

Tema da loja **museuemfios.com**, construído sobre o [Layout Base oficial da
Nuvemshop](https://github.com/TiendaNube/base-theme) (fork da v1.14.0, a mesma
base validada em produção no projeto Alfa Pesca) com a nova identidade do
Estúdio Agudo: Inter + Roboto Serif, paleta amarelo/verde/azul, grafismo de linhas
("fio") e motion GSAP.

Por ser fork do Layout Base, **tudo da plataforma continua funcionando**:
carrinho AJAX, variantes, frete, contas de cliente, blog, busca e checkout.

## Como testar SEM mexer na loja no ar (CLI — recomendado)

```bash
# 1. Requisito: Node.js 24+. Instale o CLI oficial:
npm install -g @tiendanube/cli

# 2. Na pasta deste tema:
cd tema
nuvemshop theme authorize        # abre o navegador; faça login na loja

# 3. Descubra o ID do seu layout de teste (rascunho):
nuvemshop theme list

# 4. Suba este tema pro rascunho (NÃO toca no que está no ar):
nuvemshop theme push --theme-id <ID_DO_RASCUNHO> --force

# 5. Gere o link de pré-visualização COMPARTILHÁVEL (manda pro cliente):
nuvemshop theme preview --theme-id <ID_DO_RASCUNHO>
```

Extras úteis:

```bash
nuvemshop theme watch --theme-id <ID>    # dev ao vivo: salva arquivo → recarrega a loja
nuvemshop theme publish --theme-id <ID>  # quando aprovado, publica o rascunho
nuvemshop theme fork --theme-id <ID>     # destrava rascunho que não aceita push
nuvemshop theme create --title "Museu em Fios — Identidade 2026"
```

> ⚠️ O `authorize` grava o token em `.nuvem` nesta pasta — já está no
> `.gitignore`, **não commite**.

## Alternativa: FTP / LCI (só alcança o tema publicado)

1. No admin: **Loja online → Layout → Editar o código / Personalização
   avançada** (precisa do plano com edição de código). Anote host/usuário/senha.
2. Envie o **conteúdo** desta pasta — `config/`, `layouts/`, `snipplets/`,
   `static/`, `templates/` — pra raiz do FTP (FileZilla em **modo binário**).
3. A Nuvemshop compila em ~1 min. Teste em aba anônima.

> Dica: prefira sempre o fluxo de **rascunho via CLI** pra não mexer na loja
> no ar até a aprovação.

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
