{# MUSEU EM FIOS — hero editorial da home.
   3 destaques fixos do tema (obra + artista + link para o produto real).
   Para trocar um destaque: ajuste imagem (static/images/obras/), textos e URL. #}

<section class="mf-hero" aria-label="Kits em destaque">

    <article class="mf-hero__slide is-active" data-cor="azul">
        <p class="mf-hero__intro">
            Inspirado na icônica obra <em>Femme à l'ombrelle</em> de Claude Monet,
            este kit transforma a delicadeza e a poesia impressionista do artista
            em uma experiência criativa através do bordado.
        </p>
        <div class="mf-hero__palco">
            <div class="mf-hero__fio"></div>
            <div class="mf-hero__obra">
                <img src="{{ 'images/obras/monet-femme-ombrelle-sq.jpg' | static_url }}" alt="Pintura Femme à l'ombrelle, de Claude Monet" fetchpriority="high">
            </div>
            <p class="mf-hero__nome mf-display" aria-hidden="true">Monet</p>
        </div>
        <div class="mf-hero__rodape">
            <span></span>
            <div>
                <p class="mf-hero__kit">Kit para<br>bordar</p>
                <a class="mf-link" href="/produtos/kit-de-bordado-femme-a-lombrelle-claude-monet/">Ver o kit</a>
            </div>
        </div>
    </article>

    <article class="mf-hero__slide" data-cor="amarelo">
        <p class="mf-hero__intro">
            Inspirado na obra <em>Die Umarmung</em> de Gustav Klimt, este kit
            transforma a riqueza ornamental e o simbolismo do artista em uma
            experiência criativa através do bordado.
        </p>
        <div class="mf-hero__palco">
            <div class="mf-hero__fio"></div>
            <div class="mf-hero__obra">
                <img src="{{ 'images/obras/klimt-die-umarmung-sq.jpg' | static_url }}" alt="Pintura Die Umarmung (O Abraço), de Gustav Klimt" loading="lazy">
            </div>
            <p class="mf-hero__nome mf-display" aria-hidden="true">Klimt</p>
        </div>
        <div class="mf-hero__rodape">
            <span></span>
            <div>
                <p class="mf-hero__kit">Kit para<br>bordar</p>
                <a class="mf-link" href="/produtos/pre-venda-kit-de-bordado-die-umarmung-gustav-klimt/">Ver o kit</a>
            </div>
        </div>
    </article>

    <article class="mf-hero__slide" data-cor="verde">
        <p class="mf-hero__intro">
            Inspirado na obra <em>Le Pont Japonais</em> de Claude Monet, este kit
            recria as cores, luzes e texturas do jardim de Giverny — ponto a ponto,
            em uma interpretação em fios.
        </p>
        <div class="mf-hero__palco">
            <div class="mf-hero__fio"></div>
            <div class="mf-hero__obra">
                <img src="{{ 'images/obras/monet-ponte-japonesa-sq.jpg' | static_url }}" alt="Pintura Le Pont Japonais, de Claude Monet" loading="lazy">
            </div>
            <p class="mf-hero__nome mf-display" aria-hidden="true">Monet</p>
        </div>
        <div class="mf-hero__rodape">
            <span></span>
            <div>
                <p class="mf-hero__kit">Kit para<br>bordar</p>
                <a class="mf-link" href="/produtos/kit-de-bordado-le-pont-japonais-claude-monet/">Ver o kit</a>
            </div>
        </div>
    </article>

    <div class="mf-hero__nav" role="tablist" aria-label="Trocar destaque">
        <button class="mf-hero__dot is-active" role="tab" aria-label="Destaque 1"><span class="prog"></span></button>
        <button class="mf-hero__dot" role="tab" aria-label="Destaque 2"><span class="prog"></span></button>
        <button class="mf-hero__dot" role="tab" aria-label="Destaque 3"><span class="prog"></span></button>
    </div>
</section>
