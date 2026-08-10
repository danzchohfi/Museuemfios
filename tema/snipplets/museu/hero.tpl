{# MUSEU EM FIOS — hero editorial da home.
   Copy conforme Direção de Marca (Vitamina): descritor de categoria na 1ª
   dobra, obra como protagonista, convite "Você conhece esta obra?" e ficha
   técnica de catálogo. 3 destaques fixos (obra + link para o produto real).
   Para trocar um destaque: ajuste imagem (static/images/obras/), textos e URL. #}

<section class="mf-hero" aria-label="Kits em destaque">
    <p class="mf-hero__descritor">Releitura autoral de obras icônicas. Imersão na arte, no seu tempo.</p>

    <article class="mf-hero__slide is-active" data-cor="azul">
        <p class="mf-hero__intro">
            <span class="pergunta">Você conhece esta obra?</span>
            <em>Femme à l'ombrelle</em>, Claude Monet, 1886. Neste kit, você
            aprende com o mestre do impressionismo enquanto cria a sua própria
            interpretação em fio.
        </p>
        <div class="mf-hero__palco">
            <div class="mf-hero__fio"></div>
            <div class="mf-hero__obra">
                <img src="{{ 'images/obras/monet-femme-ombrelle-sq.jpg' | static_url }}" alt="Pintura Femme à l'ombrelle, de Claude Monet" fetchpriority="high">
            </div>
            <p class="mf-hero__nome mf-display" aria-hidden="true">Monet</p>
        </div>
        <div class="mf-hero__rodape">
            <p class="mf-hero__ficha">Autor — Claude Monet<br>Obra — Femme à l'ombrelle, 1886</p>
            <div>
                <p class="mf-hero__kit">Kit para<br>bordar</p>
                <a class="mf-link" href="/produtos/kit-de-bordado-femme-a-lombrelle-claude-monet/">Acessar kit</a>
            </div>
        </div>
    </article>

    <article class="mf-hero__slide" data-cor="amarelo">
        <p class="mf-hero__intro">
            <span class="pergunta">Você conhece esta obra?</span>
            <em>Die Umarmung</em>, Gustav Klimt, c. 1908. A riqueza ornamental do
            mestre vienense, relida ponto a ponto na sua interpretação em fio.
        </p>
        <div class="mf-hero__palco">
            <div class="mf-hero__fio"></div>
            <div class="mf-hero__obra">
                <img src="{{ 'images/obras/klimt-die-umarmung-sq.jpg' | static_url }}" alt="Pintura Die Umarmung (O Abraço), de Gustav Klimt" loading="lazy">
            </div>
            <p class="mf-hero__nome mf-display" aria-hidden="true">Klimt</p>
        </div>
        <div class="mf-hero__rodape">
            <p class="mf-hero__ficha">Autor — Gustav Klimt<br>Obra — Die Umarmung, c. 1908</p>
            <div>
                <p class="mf-hero__kit">Kit para<br>bordar</p>
                <a class="mf-link" href="/produtos/pre-venda-kit-de-bordado-die-umarmung-gustav-klimt/">Acessar kit</a>
            </div>
        </div>
    </article>

    <article class="mf-hero__slide" data-cor="verde">
        <p class="mf-hero__intro">
            <span class="pergunta">Você conhece esta obra?</span>
            <em>Le Pont Japonais</em>, Claude Monet, 1899. O jardim de Giverny
            relido em linhas — cor, luz e movimento na sua interpretação.
        </p>
        <div class="mf-hero__palco">
            <div class="mf-hero__fio"></div>
            <div class="mf-hero__obra">
                <img src="{{ 'images/obras/monet-ponte-japonesa-sq.jpg' | static_url }}" alt="Pintura Le Pont Japonais, de Claude Monet" loading="lazy">
            </div>
            <p class="mf-hero__nome mf-display" aria-hidden="true">Monet</p>
        </div>
        <div class="mf-hero__rodape">
            <p class="mf-hero__ficha">Autor — Claude Monet<br>Obra — Le Pont Japonais, 1899</p>
            <div>
                <p class="mf-hero__kit">Kit para<br>bordar</p>
                <a class="mf-link" href="/produtos/kit-de-bordado-le-pont-japonais-claude-monet/">Acessar kit</a>
            </div>
        </div>
    </article>

    <div class="mf-hero__nav" role="group" aria-label="Trocar destaque">
        <button class="mf-hero__dot is-active" aria-pressed="true" aria-label="Destaque 1"><span class="prog"></span></button>
        <button class="mf-hero__dot" aria-pressed="false" aria-label="Destaque 2"><span class="prog"></span></button>
        <button class="mf-hero__dot" aria-pressed="false" aria-label="Destaque 3"><span class="prog"></span></button>
    </div>
</section>
