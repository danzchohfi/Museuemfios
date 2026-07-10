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
4. **Home**: o hero editorial, o marquee, o manifesto, o "como funciona" e o
   "o que vem no kit" são fixos do tema (edição nos snipplets em
   `snipplets/museu/`). As demais seções (produtos em destaque, categorias,
   vídeo, instafeed…) seguem configuráveis em Layout → Personalizar.
5. **Hero**: os 3 destaques apontam pros produtos reais (Femme à l'ombrelle,
   Die Umarmung, Le Pont Japonais). Pra trocar um destaque, edite
   `snipplets/museu/hero.tpl` (imagem em `static/images/obras/` + URL).

## O que foi alterado vs. Layout Base

| Arquivo | Mudança |
|---|---|
| `config/defaults.txt` | Paleta da identidade + Inter/Fraunces como padrão; header claro |
| `layouts/layout.tpl` | `museu-theme.css` + GSAP vendorizado + `museu-motion.js`; fontes com peso 900 |
| `templates/home.tpl` | Inclui hero, marquee e manifesto no topo; passos e kit após as seções |
| `templates/product.tpl` | CTA "Dúvidas sobre o kit?" (WhatsApp) |
| `snipplets/museu/*` | Hero, marquee, manifesto, passos, kit, CTA WhatsApp (novos) |
| `static/css/museu-theme.css` | Skin completa: design system + ponte pros componentes nativos |
| `static/js/museu-motion.js` | Motion GSAP: hero, desenho do "fio", reveals, cursor-linha |
| `static/js/vendor/gsap*.js` | GSAP 3.15.0 + ScrollTrigger (licença gratuita GreenSock/Webflow) |

Nenhum hook `.js-*` do tema base foi alterado — atualizações de comportamento
da plataforma continuam compatíveis.

## Acessibilidade & motion

- Foco visível em tudo, alvos ≥44px, texto em PT-BR, skip-link.
- GSAP vendorizado (sem CDN) com guarda dupla: sem JS ou com
  `prefers-reduced-motion`, o site fica estático e 100% funcional — o conteúdo
  nunca depende da animação.
