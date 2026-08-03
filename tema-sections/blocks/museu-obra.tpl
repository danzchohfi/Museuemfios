{# MUSEU EM FIOS — um destaque do hero: a obra, a ficha de catálogo e o link
   pro kit. Usado dentro de sections/museu-hero.tpl.

   O `indice` vem do laço da section: só o primeiro destaque nasce visível
   (.is-active) e carrega a imagem com prioridade alta — os outros entram no
   carrossel do museu-motion.js. #}

{% set s = block.settings %}
{% set primeiro = indice == 0 %}

<article class="mf-hero__slide{% if primeiro %} is-active{% endif %}"
         data-cor="{{ s.cor }}"
         {{ block | block_attributes }}
         data-store="museu-hero-slide-{{ block.id }}">

    <p class="mf-hero__intro">
        {% if s.pergunta %}<span class="pergunta">{{ s.pergunta }}</span>{% endif %}
        {{ s.texto | raw }}
    </p>

    <div class="mf-hero__palco">
        <div class="mf-hero__fio"></div>
        <div class="mf-hero__obra">
            {% if s.imagem %}
                <img src="{{ s.imagem }}" alt="{{ s.imagem_alt }}"
                     {% if primeiro %}fetchpriority="high"{% else %}loading="lazy"{% endif %}>
            {% endif %}
        </div>
        {% if s.artista_display %}
            <p class="mf-hero__nome mf-display" aria-hidden="true">{{ s.artista_display }}</p>
        {% endif %}
    </div>

    <div class="mf-hero__rodape">
        <p class="mf-hero__ficha">{{ s.ficha | raw }}</p>
        <div>
            <p class="mf-hero__kit">{{ s.rotulo_kit | raw }}</p>
            {% if s.link %}
                <a class="mf-link" href="{{ s.link }}">{{ s.link_texto }}</a>
            {% endif %}
        </div>
    </div>
</article>

{% schema %}
{
  "name": "t:names.museu_obra",
  "settings": [
    { "type": "header", "content": "t:names.museu_a_obra" },
    {
      "type": "setting",
      "setting_type": "image_picker",
      "id": "imagem",
      "label": "t:settings.museu_imagem_obra"
    },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "imagem_alt",
      "label": "t:settings.museu_imagem_alt"
    },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "artista_display",
      "label": "t:settings.museu_artista_display",
      "default": "Monet"
    },
    {
      "type": "setting",
      "setting_type": "radio",
      "id": "cor",
      "label": "t:settings.museu_cor",
      "options": [
        { "value": "azul",    "label": "t:options.museu_azul" },
        { "value": "amarelo", "label": "t:options.museu_amarelo" },
        { "value": "verde",   "label": "t:options.museu_verde" }
      ],
      "default": "azul"
    },
    { "type": "header", "content": "t:names.museu_textos" },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "pergunta",
      "label": "t:settings.museu_pergunta",
      "default": "t:defaults.museu_pergunta"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "texto",
      "label": "t:settings.museu_texto_obra"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "ficha",
      "label": "t:settings.museu_ficha"
    },
    { "type": "header", "content": "t:names.museu_chamada" },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "rotulo_kit",
      "label": "t:settings.museu_rotulo_kit",
      "default": "t:defaults.museu_rotulo_kit"
    },
    {
      "type": "setting",
      "setting_type": "url",
      "id": "link",
      "label": "t:settings.museu_link_kit"
    },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "link_texto",
      "label": "t:settings.museu_link_texto",
      "default": "t:defaults.museu_ver_kit"
    }
  ],
  "presets": [
    {
      "name": "t:names.museu_obra",
      "category": "t:categories.museu",
      "settings": {
        "pergunta": "t:defaults.museu_pergunta",
        "rotulo_kit": "t:defaults.museu_rotulo_kit",
        "link_texto": "t:defaults.museu_ver_kit",
        "cor": "azul"
      }
    }
  ]
}
{% endschema %}
