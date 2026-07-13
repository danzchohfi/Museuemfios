{# MUSEU EM FIOS — hero "O Fio" (conceito V5, aprovado).
   Golden hour + meada de fios em 3D (three.js via static/js/museu-3d.js,
   carregado só na home pelo layout.tpl) + o produto finalizado: foto real
   do bordado sobre tela. Copy conforme Direção de Marca (endline, descritor
   e ficha de catálogo). Sem WebGL/JS ou com prefers-reduced-motion fica o
   céu em CSS e a tela estática — nada quebra. Em destaque: Der Kuss (Klimt).
   Para trocar: imagem em static/images/obras/ + ficha + URL do produto. #}

<section class="v4-hero" aria-label="Sua hora com a arte, no entardecer">
    <div class="v4-fio3d" aria-hidden="true"></div>
    <div class="v4-grao" aria-hidden="true"></div>

    <div class="v4-hero__inner">
        <div>
            <p class="v4-hero__momento" data-reveal>Ponto a ponto · O entardecer</p>
            <h1 class="v4-hero__titulo" data-reveal>
                Sua hora<br>com a arte.<br><em>Borde um museu.</em>
            </h1>
            <p class="v4-hero__apoio" data-reveal>
                A luz baixa e o fio atravessa o tecido. Entre o fim do dia e a
                noite, uma obra da história da arte passa, ponto a ponto,
                pelas suas mãos.
            </p>
            <div class="v4-hero__acoes" data-reveal>
                <a class="mf-btn" href="/kits-de-bordado/">Escolher minha obra</a>
                <a class="mf-link" href="/produtos/kit-de-bordado-der-kuss-gustav-klimt/">Ver o kit em destaque</a>
            </div>
            <p class="v4-descritor" data-reveal>
                Releitura autoral de obras icônicas. Imersão na arte, no seu tempo.
            </p>
        </div>

        <figure class="v4-quadro" data-reveal>
            <div class="v5-tela">
                <img src="{{ 'images/obras/der-kuss-tela.jpg' | static_url }}"
                     alt="Kit Der Kuss finalizado: o bordado sobre tela, pendurado no cavalete"
                     fetchpriority="high">
            </div>
            <figcaption class="v4-quadro__ficha">
                Gustav Klimt
                <em>Der Kuss, 1908 — Coleção permanente</em>
            </figcaption>
        </figure>
    </div>

    <p class="v4-hero__scroll" aria-hidden="true">A coleção ↓</p>
</section>
