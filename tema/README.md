# Museu em Fios — tema Nuvemshop

Tema da loja **museuemfios.com**, construído sobre o [Layout Base oficial da
Nuvemshop](https://github.com/TiendaNube/base-theme) (fork da v1.14.0, a mesma
base validada em produção no projeto Alfa Pesca) com a nova identidade do
Estúdio Agudo: Inter + Fraunces, paleta amarelo/verde/azul, grafismo de linhas
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
   `#FBFAF6`, amarelo `#F2C440`, Inter títulos + Fraunces texto). Se o tema já
   estava instalado, confira em Layout → Personalizar.
2. **Logo**: subir o logo vertical preto (SVG/PNG em `../brand/logos/`) em
   Layout → Personalizar → Logo. O favicon amarelo está em
   `../demo/assets/img/favicon-amarelo.png`.
3. **WhatsApp**: conferir o número da loja em Configurações (alimenta o botão
   flutuante e o CTA "Dúvidas sobre o kit?" no produto).
4. **Home (conceito V5 · "O Fio" — aprovado)**: o hero do entardecer com a
   meada 3D, o manifesto e a faixa do certificado são fixos do tema (edição
   nos snipplets em `snipplets/museu/`). As seções nativas (produtos em
   destaque, categorias, vídeo, instafeed…) seguem configuráveis em Layout →
   Personalizar e correm sobre o fundo escuro, com o fio-costura passando
   por trás.
5. **Produto em destaque do hero**: Der Kuss (Klimt) finalizado — foto real
   do bordado sobre tela — apontando pro produto. Pra trocar, edite
   `snipplets/museu/hero-fio.tpl` (imagem em `static/images/obras/`, ficha
   e URL do produto).

## O que foi alterado vs. Layout Base

| Arquivo | Mudança |
|---|---|
| `config/defaults.txt` | Paleta da identidade + Inter/Fraunces como padrão; header claro |
| `layouts/layout.tpl` | `museu-theme.css` + GSAP vendorizado + `museu-motion.js`; fontes com peso 900; `<main>` em volta do conteúdo; na home: classes `v4 v5` no body + `museu-home-fio.css` + `museu-3d.js` |
| `templates/home.tpl` | Home V5: hero "O Fio" + manifesto no topo; seções nativas dentro de `.v4-fundo`; faixa do certificado no fim |
| `templates/product.tpl` | CTA "Dúvidas sobre o kit?" (WhatsApp) |
| `snipplets/museu/*` | `hero-fio`, `manifesto-fio`, `certificado` (home V5) + `hero`, `marquee`, `manifesto`, `passos`, `kit` (conceito V1, guardados) + CTA WhatsApp |
| `snipplets/footer.tpl` | Crédito "Site por vitamina." com link |
| `static/css/museu-theme.css` | Skin completa: design system + ponte pros componentes nativos |
| `static/css/museu-home-fio.css` | Só na home: céu do entardecer, tela do bordado, costura + ponte escura pros componentes nativos |
| `static/js/museu-motion.js` | Motion GSAP: desenho do "fio", reveals, cursor-linha |
| `static/js/museu-3d.js` | Só na home: three.js 0.185 + meada 3D + fio-costura, num único IIFE (sem CDN, sem módulos ES) |
| `static/js/gsap*.js` | GSAP 3.15.0 + ScrollTrigger (licença gratuita GreenSock/Webflow) |

Nenhum hook `.js-*` do tema base foi alterado — atualizações de comportamento
da plataforma continuam compatíveis.

## Animações na Nuvemshop — o que está validado

- **GSAP + ScrollTrigger (fio que se desenha, reveals, costura): funciona.**
  Validação em produção no projeto Alfa Pesca (GSAP rodando na vitrine
  Nuvemshop sem conflito com o jQuery/carrinho da plataforma). Aqui está
  ainda mais robusto: os arquivos são servidos do próprio tema
  (`static/js/gsap.min.js`, via `static_url`) — sem CDN externo. A vitrine
  não impõe CSP restritiva e nenhum hook `.js-*` da plataforma é tocado.
- **three.js (a meada 3D da home): funciona, com um cuidado já resolvido.**
  Módulos ES importados do CDN da Nuvemshop poderiam esbarrar em CORS; por
  isso o 3D vai empacotado como script clássico em
  **`static/js/museu-3d.js`** (three 0.185 + cena da meada + fio-costura,
  IIFE, 576 KB / ~148 KB gzip), carregado com `defer` **só na home** pelo
  `layout.tpl`.
- **Sempre com rede de segurança**: sem WebGL, sem o arquivo ou com
  `prefers-reduced-motion`, a home mantém o céu do entardecer em CSS e a
  tela do bordado estática — tudo continua legível e 100% funcional.

## Home: voltar do conceito V5 pro V1 (editorial claro)

O conceito V1 continua no tema, guardado. Se um dia quiserem trocar:

1. Em `templates/home.tpl`: troque os includes `museu/hero-fio.tpl` +
   `museu/manifesto-fio.tpl` por `museu/hero.tpl` + `museu/marquee.tpl` +
   `museu/manifesto.tpl`; remova o wrapper `<div class="v4-fundo">` e o
   include `museu/certificado.tpl`; re-inclua `museu/passos.tpl` +
   `museu/kit.tpl` depois do container de seções.
2. Em `layouts/layout.tpl`: apague os 3 blocos condicionais
   `{% if template == 'home' %}` (classes `v4 v5` do body, link do
   `museu-home-fio.css` e script do `museu-3d.js`). O `<main>` pode ficar.

## Acessibilidade & motion

- Foco visível em tudo, alvos ≥44px, texto em PT-BR, skip-link.
- GSAP vendorizado (sem CDN) com guarda dupla: sem JS ou com
  `prefers-reduced-motion`, o site fica estático e 100% funcional — o conteúdo
  nunca depende da animação.
