# Subir o tema na loja — passo a passo

Guia operacional. O **caminho comprovado** é o mesmo que a Vitamina já executou
na Alfa Pesca e que está **no ar hoje** em alfapesca.com.br.

---

## O que a Alfa provou (verificado no site no ar, 28/07/2026)

Baixei a home de `alfapesca.com.br` e li o HTML. O tema que está servindo a
loja é:

```
https://…mitiendanube.com/stores/006/259/472/themes/ipanema/style-critical-….min.css
https://…mitiendanube.com/stores/006/259/472/themes/ipanema/style-utilities-….min.css
https://…mitiendanube.com/stores/006/259/472/themes/ipanema/style-async-….min.css
https://…mitiendanube.com/stores/006/259/472/themes/ipanema/alfa-theme-….min.css   ← nosso CSS
```

**`themes/ipanema/` — formato sections.** E na home, as classes das seções:

| Seções autorais (nossas) | Seções nativas do Ipanema |
|---|---|
| `section-alfa-hero` | `announcement-bar`, `header`, `featured-categories` |
| `section-alfa-kit-banner` | `full-width`, `video`, `product-list`, `rich-text`, `icon-text`, `footer` |

Zero marcadores do formato legado: nenhuma ocorrência de `snipplets`,
`dart-style`, `jquery`. E 282 slots `nubesdk-slot` + 91 atributos `data-store`,
que são a assinatura do formato novo.

**Conclusão: a Alfa foi convertida para sections e subiu assim.** Bate com a
memória do cliente — a primeira tentativa (formato antigo) não vingou; a
conversão para a versão nova da plataforma foi a que subiu.

Três coisas que isso resolve de vez:

1. **O `fork` funciona.** Ter seção autoral (`alfa-hero`) e CSS próprio
   (`alfa-theme.css`) dentro de `themes/ipanema/` só é possível numa instalação
   forkada. A documentação diz "coming soon"; a produção diz que já vai.
2. **O desenho da nossa migração está certo.** A Alfa usa exatamente o padrão
   que adotei em `tema-sections/`: seções autorais prefixadas com a marca
   (`alfa-hero` ↔ `museu-hero`) convivendo com as nativas, mais um CSS próprio
   ao lado dos do Ipanema.
3. **É o CLI 2.x que serve** — porque o formato sections está inteiro dentro
   da lista de pastas que ele sincroniza.

> **Nota de economia:** a Alfa fez só **2 seções autorais** e resolveu o resto
> com seções nativas estilizadas por CSS. Nós temos 6. Vale a conversa de
> trocar `museu-passos` por `icon-text` nativa e `museu-manifesto` por
> `rich-text` — menos código nosso pra manter. As que carregam identidade de
> verdade (hero com o fio, marquee, noite) continuam autorais.

---

## Passo 1 — Você me autoriza (é o único passo que só você pode dar)

O `theme authorize` abre o navegador pra login na sua conta. Eu rodo num
sandbox sem sessão sua, então **o login tem que sair da sua máquina**. Depois
disso o CLI aceita `--token`, e é por aí que eu assumo.

Na sua máquina (precisa de Node.js 24.15+):

```bash
mkdir -p ~/museu-auth && cd ~/museu-auth
npx @tiendanube/cli@2 theme authorize
```

Vai abrir o navegador. Faça login na conta da **Museu em Fios** e autorize.
Ao terminar, o CLI grava um arquivo **`.nuvem`** nessa pasta.

```bash
cat .nuvem
```

**Me mande o conteúdo desse arquivo.** Ele carrega o token da API, o ID da
loja e a URL da loja — é com ele que eu consigo rodar `push`, `preview` e
`publish` daqui.

### Antes de mandar, saiba o que está mandando

- Esse token **dá acesso de escrita ao tema da sua loja**, inclusive publicar.
  Quem tiver o arquivo consegue mexer no que o público vê.
- O arquivo é **ofuscado, não criptografado** — não é segredo forte.
- Eu **nunca** commito o `.nuvem` (já está no `.gitignore` do projeto).
- O sandbox onde eu rodo é **efêmero**: quando a sessão morre, o token some
  junto. Mas enquanto durar, ele fica lá.
- **Pra revogar depois:** admin da loja → **Aplicativos → aplicativos
  autorizados** → remover o acesso do CLI. Vale fazer quando terminarmos.

**Se preferir não mandar o token** — é uma escolha legítima — o plano B é você
rodar os comandos e me colar a saída. Eu escrevo cada comando, você executa,
me manda o resultado, eu digo o próximo. Mais lento, e você fica com a chave.

---

## Passo 2 — Diagnóstico e backup (antes de qualquer escrita)

```bash
cd tema
./diagnostico-loja.sh          # só leitura: instalações, qual está no ar, se há Ipanema
```

O backup do que está no ar **usa o CLI 1.2.1 de propósito** — o tema publicado
hoje é legado, e o 2.x não baixa a pasta `snipplets/`:

```bash
./backup-tema-no-ar.sh <ID_DA_INSTALACAO_PUBLICADA>
```

> A Nuvemshop **não guarda backup do código** pra gente. O backup é nosso.

---

## Passo 3 — Criar o rascunho no Ipanema e forkar

```bash
cd tema-sections
npx @tiendanube/cli@2 theme create --base-theme ipanema \
    --title "Museu em Fios — Identidade 2026"
npx @tiendanube/cli@2 theme fork --theme-id <ID>    # mão única
npx @tiendanube/cli@2 theme pull --theme-id <ID>    # baixa a árvore do Ipanema
```

⚠️ A loja aceita **no máximo 2 instalações** (a publicada + uma). O `create`
ocupa a vaga livre.

⚠️ `fork` é **mão única**: dali em diante o tema não recebe mais atualizações
automáticas do tema base.

O `pull` é o momento que responde as duas lacunas que a documentação não
resolve, e que deixei de propósito em aberto no código:

- a raiz do `config/settings_schema.json` (array ou objeto?);
- como o `layouts/layout.tpl` referencia CSS/JS de `static/`.

Com a árvore em mãos, eu fecho as duas em minutos.

---

## Passo 4 — Aplicar a nossa identidade e subir

Com o Ipanema baixado, eu:

1. copio nossas `sections/`, `blocks/`, `templates/pages/home.json`,
   `translations/` e `static/` por cima;
2. reescrevo `museu-ponte.css` contra as classes reais do Ipanema (as 154
   linhas que hoje miram o Layout Base);
3. escrevo o `settings_schema.json` no formato que o `pull` revelar.

```bash
npx @tiendanube/cli@2 theme push --theme-id <ID>
npx @tiendanube/cli@2 theme preview --theme-id <ID>   # link COMPARTILHÁVEL
```

O `preview` do 2.x é descrito no próprio CLI como *"Print a shareable preview
URL for the theme (use before publishing)"* — resolve a dúvida antiga sobre o
link ser compartilhável ou não. É o link que vai pra cliente aprovar.

---

## Passo 5 — Publicar (só depois do aceite)

```bash
npx @tiendanube/cli@2 theme publish --theme-id <ID>
```

---

## Resumo de qual CLI usar

| Tarefa | Versão | Por quê |
|---|---|---|
| Backup do tema legado no ar | **1.2.1** | manda/baixa a pasta inteira; o 2.x pula `snipplets/` |
| Subir o tema legado (plano B) | **1.2.1** | idem |
| Tudo no formato sections | **2.x** | o formato novo está inteiro na lista de sincronização |

**Nunca rode sem fixar a versão.** `npx @tiendanube/cli` hoje resolve pro 2.x,
e num tema legado isso descarta 130 arquivos em silêncio.
