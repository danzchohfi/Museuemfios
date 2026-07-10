# Museu em Fios — e-commerce

Projeto do e-commerce da **Museu em Fios** (museuemfios.com), conduzido pela
Vitamina Publicitária com a nova identidade visual do **Estúdio Agudo**
("MUSEU ƎM FIOS"): Inter + Fraunces, paleta amarelo/verde/azul pinçada das
obras, e o grafismo de linhas (o "fio") como assinatura.

## Estrutura

| Pasta | O que é | Status |
|---|---|---|
| **`tema/`** | **Tema Nuvemshop** — fork do Layout Base oficial (mesma base validada no projeto Alfa Pesca) com a identidade nova, motion GSAP e seções editoriais fixas na home. É o que sobe pra loja via CLI/LCI. | Pronto pra teste em rascunho |
| **`demo/`** | Demo estática de aprovação (HTML/CSS/JS puros) publicada no GitHub Pages — usa o catálogo, os preços e as **fotos reais** da loja atual. | No ar |
| `brand/` | Assets da identidade (logos vetoriais convertidos do manual do Estúdio Agudo). | Referência |

## Demo de aprovação (GitHub Pages)

O workflow `.github/workflows/demo-pages.yml` publica `demo/` no Pages a cada
push (URL: **https://danzchohfi.github.io/museuemfios**). Requer Pages
habilitado com source "GitHub Actions" — o workflow tenta habilitar sozinho na
primeira execução.

Páginas da demo: `index.html` (home completa), `loja.html` (vitrine + guias
digitais + filtros), `produto.html` (PDP do kit Femme à l'ombrelle),
`sobre.html` (Quem somos).

## Subir o tema na loja (sem tocar no que está no ar)

Fluxo recomendado — CLI oficial, direto num **rascunho** de tema:

```bash
npm install -g @tiendanube/cli     # requer Node 24+
cd tema
nuvemshop theme authorize          # login no navegador
nuvemshop theme list               # anote o ID do layout de teste/rascunho
nuvemshop theme push --theme-id <ID> --force
nuvemshop theme preview --theme-id <ID>   # 🔗 link compartilhável com o catálogo real
```

Alternativa FTP (LCI / "Personalização avançada" no admin) e o passo a passo
pós-upload: ver **`tema/README.md`**.

## Identidade — tokens principais

| Token | Valor |
|---|---|
| Preto | `#1D1D1B` |
| Papel (fundo) | `#FBFAF6` |
| Amarelo (Klimt) | `#F2C440` |
| Verde (Monet, Pont Japonais) | `#9CAD4E` |
| Azul (Monet, Femme à l'ombrelle) | `#6A9CC3` |
| Títulos | Inter (900 no display) |
| Texto | Fraunces |

Grafismo: duas metades abertas de hexágono em linha 1.5px (geradas em SVG pelo
JS — `data-fio` — e animadas com "desenho" de traço no scroll).
