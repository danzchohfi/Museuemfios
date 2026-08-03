# Museu em Fios — o que já está no ar

Atualizado em 31/07/2026.

---

## A vitrine da home agora é de vocês

**O Nu Bleu II entrou na vitrine "Kits para bordar"**, com a obra do Matisse, a
foto do bordado no hover e o preço de R$ 149 — são cinco kits na home.

E, mais importante: **a vitrine deixou de ser código.** Cada kit virou um card
editável no *Loja online → Temas → Personalizar → Kits para bordar*. Para
colocar um kit novo:

1. duplique um card que já existe (ou crie um grupo novo);
2. **cor de fundo** do grupo: é a cor que emoldura a obra — o azul dos kits
   do Matisse, pedido pela Isabella, é o **#475DCA**; num fundo escuro assim,
   preencha também a **cor do texto** com o branco-papel **#FBFAF6**;
3. **primeira imagem**: a obra original;
4. **segunda imagem**: a foto do bordado pronto — é ela que aparece quando o
   mouse passa por cima;
5. nas duas imagens, o **link** vai para a página do kit;
6. no bloco de texto, o nome do artista, o nome da obra e o preço.

Um aviso sobre o preço: ele é digitado ali, não vem do cadastro do produto.
Se o preço mudar na loja, o card da home precisa ser atualizado junto.

**A etiqueta "INICIANTE"** no card do Nu Bleu II é a primeira linha do bloco
de texto do card. A palavra é editável ali mesmo (pode virar "Oferta",
"Pré-venda"…), e apagar a linha remove a etiqueta.

---

## Já resolvido

**Os kits do Matisse estão no azul que a Isabella mandou.** O tom exato do
swatch (#475DCA), nos dois cards — La Gerbe e Nu Bleu II — com a ficha em
branco-papel para ler bem sobre o azul.

**A foto revelada do Der Kuss é a do bordado.** Estava aparecendo a foto da
caixa do kit; agora, ao passar o mouse, aparece o bordado pronto na mão —
como nos outros cards. No celular a revelação foi desligada de propósito: em
iPhone o "passar o mouse" gruda no primeiro toque (era o print do José), então
lá o card mostra a obra e o toque abre direto a página do kit.

**Os dois links que davam erro 404 estão funcionando.** O "Ver todos os kits" e
o "Ver todos os guias" voltaram a abrir as páginas de coleção. Foi uma falha
nossa ao atualizar as configurações de busca das categorias, corrigida assim
que a Isabella avisou.

**O kit de iniciante agora leva ao produto.** Com o "Nu Bleu II" publicado, o
botão "Começar pelo Nu Bleu II" abre a página do kit, em vez da listagem.

**O menu não mostra mais itens em branco.** O submenu de "Loja" abria uma caixa
vazia porque os dois itens estão sem nome no painel — eles ficam ocultos até
serem preenchidos. O "Blog" também parou de dar erro.

---

## Velocidade do site

O Google apontava as imagens como o maior problema da loja: **10 MB por
visita**, com nota de desempenho 48 e um tempo de carregamento da imagem
principal de 31 segundos no celular.

A causa: seis fotos de produto tinham sido salvas em PNG, formato que deixa
uma foto em cerca de 2 MB — a mesma imagem em formato adequado fica em 180 KB.

O que foi feito:

- as imagens da home caíram de **15,1 MB para 2,0 MB** (87% menos);
- as 19 fotos em PNG foram substituídas pelas versões otimizadas, sem perda de
  qualidade visual, mantendo a ordem e a capa de cada produto;
- as fontes do site caíram de **349 KB para 139 KB**;
- as animações saíram do caminho crítico, então a primeira tela aparece antes.

Vamos medir de novo daqui a uma semana, quando o Google já tiver dados
suficientes do site novo para comparar.

---

## Onde a compra estava travando

**O botão "Comprar" no celular não funcionava no primeiro toque.** A barra fixa
de compra e o aviso de cookies ocupavam a mesma faixa da tela, e o toque caía
no aviso. Para quem entrava pela primeira vez, o primeiro toque no botão
principal apenas fechava o aviso. Corrigido — o aviso agora sobe e os dois
ficam visíveis.

O mesmo aviso também engolia cliques em cards de produto na página de coleção.
Agora o clique atravessa a faixa de texto.

**Botões pequenos demais para o dedo** foram ampliados: os ícones de busca,
sacola e menu no topo, e o botão "Entendi" do aviso.

---

## Rodapé

Quatro elementos estavam **invisíveis** no rodapé, em celular e computador,
porque a cor do texto ficou igual à do fundo:

- os ícones de Instagram, TikTok e X;
- o "+" que abre o menu de navegação;
- o botão "Enviar" da newsletter;
- o selo "criado com Nuvemshop".

Todos voltaram a aparecer. O rodapé também ficou mais compacto no celular.

---

## Busca no Google

- **Títulos e descrições** foram escritos para os 11 produtos e para as duas
  coleções. Antes, o Google montava o texto sozinho a partir do começo da
  descrição, o que resultava em frases cortadas no meio.
- As fotos de produto ganharam **nomes de arquivo descritivos**
  (`kit-para-bordar-le-pont-japonais-claude-monet-1.jpg` em vez de
  `5-af2223db...`). O nome do arquivo conta para a busca por imagens.
- As descrições dos produtos foram organizadas com títulos de verdade, sem
  emojis fazendo papel de marcador.

---

## Precisamos de vocês

**1. O vídeo das obras prontas nos produtos.** Só o La Gerbe tem vídeo hoje. Os
arquivos convertidos vão pra vocês — o upload é pelo painel, em *Produtos →
produto → adicionar vídeo*, do mesmo jeito que foi feito no La Gerbe.

**2. Três ajustes no painel** que só podem ser feitos por vocês:

- **Menu → os dois itens do submenu "Loja"**: dar nome e link (sugestão: *Kits
  de Bordado* e *Produtos Digitais*). Há também um item sem nome apontando para
  o guia da Femme à l'ombrelle — dar nome ou remover.
- **Texto do "Sobre Nós"**: o texto novo da Isabella está pronto, mas o sistema
  da Nuvemshop está recusando a alteração por fora. É colar em *Páginas → Sobre
  Nós*. O texto vai no arquivo em anexo.
- **Descrição das imagens (texto alternativo)**: as 47 fotos estão sem
  descrição, o que pesa na busca por imagens e para quem usa leitor de tela.
  Escrevemos as 47, uma a uma, olhando cada foto — lista em anexo, é colar em
  *Produtos → produto → clicar na imagem*.

**3. Duas configurações de rastreamento:**

- o código do Google Tag Manager está com um ID inválido e responde erro a cada
  visita (parece um ID de Google Ads colado no campo errado);
- o título da loja no Google é hoje só "Museu em Fios", sem nenhuma palavra
  sobre o que vocês vendem. Sugestão pronta: *Kits de Bordado de Obras de Arte:
  Monet e Klimt | Museu em Fios*. Fica em *nome da loja → Dados do meu negócio*,
  e é preciso marcar "Utilizar o nome e a descrição do negócio para o SEO".

---

## Texto novo do "Sobre Nós", pronto para colar

O Museu em Fios é um projeto brasileiro que transforma grandes obras da
História da Arte em experiências de bordado contemporâneo. Unimos arte,
educação e criação manual por meio de kits cuidadosamente desenvolvidos, que
permitem ao público conhecer artistas, movimentos e obras enquanto aprende a
bordar.

Mais do que ensinar uma técnica, buscamos aproximar as pessoas do patrimônio
artístico de forma sensível, acessível e criativa, valorizando o bordado como
uma linguagem de expressão e contemplação.
