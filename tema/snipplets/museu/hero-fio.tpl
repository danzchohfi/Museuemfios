{# MUSEU EM FIOS — hero "O Fio" (conceito V5, aprovado).
   Golden hour + meada de fios em 3D (three.js via static/js/museu-3d.js,
   carregado só na home pelo layout.tpl) + obra no bastidor de bordado.
   Copy conforme Direção de Marca (endline, descritor e ficha de catálogo).
   Sem WebGL/JS ou com prefers-reduced-motion fica o céu em CSS e o bastidor
   estático — nada quebra. Para trocar a obra em destaque: imagem em
   static/images/obras/ + ficha + URL do produto. #}

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
                <a class="mf-link" href="/produtos/kit-de-bordado-femme-a-lombrelle-claude-monet/">Ver o kit em destaque</a>
            </div>
            <p class="v4-descritor" data-reveal>
                Releitura autoral de obras icônicas. Imersão na arte, no seu tempo.
            </p>
            <p class="v5-meada" data-reveal>
                <svg viewBox="0 0 68 20" aria-hidden="true">
                    <path d="M2 4  q17 -6 34 0 t30 0" stroke="#f2c440"/>
                    <path d="M2 7  q17 -6 34 0 t30 0" stroke="#e0a94f"/>
                    <path d="M2 10 q17 -6 34 0 t30 0" stroke="#9cad4e"/>
                    <path d="M2 13 q17 -6 34 0 t30 0" stroke="#6a9cc3"/>
                    <path d="M2 16 q17 -6 34 0 t30 0" stroke="#d98e4f"/>
                </svg>
                Meadas Anchor Mouliné na paleta do artista
            </p>
        </div>

        <figure class="v4-quadro" data-reveal>
            <div class="v5-bastidor">
                <span class="v5-bastidor__parafuso" aria-hidden="true"></span>
                <div class="v5-bastidor__tecido">
                    <img src="{{ 'images/obras/monet-femme-ombrelle-sq.jpg' | static_url }}"
                         alt="Femme à l'ombrelle, de Claude Monet, no bastidor de bordado, na luz do entardecer"
                         fetchpriority="high">
                </div>
                <svg class="v5-bastidor__fio" viewBox="0 0 200 260" aria-hidden="true">
                    <path vector-effect="non-scaling-stroke" d="M104 224 q10 14 -4 24 q-14 10 -2 12 q22 4 12 -22 q-6 -14 6 -20"/>
                </svg>
            </div>
            <figcaption class="v4-quadro__ficha">
                Claude Monet
                <em>Femme à l'ombrelle, 1886 — Coleção permanente</em>
            </figcaption>
        </figure>
    </div>

    <p class="v4-hero__scroll" aria-hidden="true">A coleção ↓</p>
</section>
