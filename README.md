# Museu em Fios — e-commerce

Projeto do e-commerce da **Museu em Fios** (museuemfios.com), conduzido pela
Vitamina Publicitária com a nova identidade visual do **Estúdio Agudo**
("MUSEU ƎM FIOS"): Inter + Roboto Serif, paleta amarelo/verde/azul pinçada das
obras, e o grafismo de linhas (o "fio") como assinatura.

## Estrutura

| Pasta | O que é | Status |
|---|---|---|
| **`tema/`** | **Tema Nuvemshop** — fork do Layout Base oficial (mesma base validada no projeto Alfa Pesca) com a identidade nova, motion GSAP e a **home no conceito V1 "editorial claro"** (o conceito aprovado pelo cliente). Formato legado: sobe por FTP, não pelo `theme push`. | Aguardando decisão do caminho de subida |
| **`demo/`** | Demo estática de aprovação (HTML/CSS/JS puros) publicada no GitHub Pages — usa o catálogo, os preços e as **fotos reais** da loja atual. | No ar |
| `brand/` | Assets da identidade (logos vetoriais convertidos do manual do Estúdio Agudo). | Referência |

## Demo de aprovação (GitHub Pages)

O workflow `.github/workflows/demo-pages.yml` publica `demo/` no Pages a cada
push (URL: **https://danzchohfi.github.io/Museuemfios**). Requer Pages
habilitado com source "GitHub Actions" — o workflow tenta habilitar sozinho na
primeira execução.

Páginas da demo: `index.html` (home completa, com a seção da noite e o
vídeo institucional em player grande), `loja.html` (vitrine + guias digitais + filtros),
`produto.html` (PDP do kit Femme à l'ombrelle), `sobre.html` (Quem somos),
`educativo.html` (blog/recursos educativos — dicas, vídeos avulsos e
conteúdo gratuito), `faq.html` (perguntas frequentes, com o conteúdo do
site no ar).

> **Conceito aprovado: V1 ("editorial claro").** O cliente escolheu a versão 1,
> então o seletor de conceitos e as versões alternativas (V3 e V5) saíram da
> demo e do tema. O histórico do Git guarda tudo, caso alguém precise
> reconsultar (`git log -- demo/v5`).

## Subir o tema na loja

Comece **sempre** por diagnóstico e backup — a Nuvemshop não guarda backup do
código da loja:

```bash
cd tema
npx @tiendanube/cli@2 theme authorize   # requer Node 24.15+
./diagnostico-loja.sh                   # só leitura: tema no ar e instalações
./backup-tema-no-ar.sh                  # baixa o tema publicado
```

> ⚠️ **`nuvemshop theme push` não serve para este tema.** O fluxo de API do CLI
> 2.x só sincroniza temas no formato novo (sections/Ipanema) e descarta em
> silêncio a pasta `snipplets/` do formato legado — 130 dos nossos 180 arquivos.
> O tema subiria quebrado. Os dois caminhos possíveis (FTP legado ou migrar o
> tema pro formato sections) estão comparados em **`tema/README.md`**.

## Direção de Marca (Vitamina) — copy travada

Fonte: entrega navegável dos 4 workshops (Notion · rev. 25/06). Toda edição de
texto no site/tema deve respeitar:

- **Endline (assinatura pública):** "Sua hora com a arte. Borde um museu."
- **Descritor de categoria (1ª dobra):** "Releitura autoral de obras icônicas.
  Imersão na arte, no seu tempo."
- **Sub-mensagens (4 ângulos):** Autoria "Você não copia. Você interpreta." ·
  Ritual "O seu tempo, sem culpa." · Curadoria "Aprenda com os grandes
  mestres." · Certificado "Ao final, a obra é sua."
- **Voz:** a obra é o rosto · diferenciação por afirmação (nunca negar/
  comparar) · convida, não dá aula · autora, não copiadora.
- **Léxico usa:** obra, releitura, autoral, interpretação, imersão, ritual,
  o seu tempo, sem culpa, grandes mestres, curadoria, "Você conhece esta obra?"
- **Léxico evita:** florzinha, fofo/fofinho, diminutivos, "hobby de vovó",
  "terapia", "relaxa que é fácil", cópia/réplica/reprodução, excesso de emoji.
- **Dispositivos no site:** ficha técnica de catálogo (Autor · Obra · Edição),
  "Coleção permanente" como nome da vitrine, certificado como prova, seção
  de iniciantes respondendo "será que eu consigo?".

## Identidade — tokens principais

| Token | Valor |
|---|---|
| Preto | `#1D1D1B` |
| Papel (fundo) | `#FBFAF6` |
| Amarelo (Klimt) | `#F2C440` |
| Verde (Monet, Pont Japonais) | `#9CAD4E` |
| Azul (Monet, Femme à l'ombrelle) | `#6A9CC3` |
| Títulos | Inter (900 no display) |
| Texto | Roboto Serif |

Grafismo: duas metades abertas de hexágono em linha 1.5px (geradas em SVG pelo
JS — `data-fio` — e animadas com "desenho" de traço no scroll).
