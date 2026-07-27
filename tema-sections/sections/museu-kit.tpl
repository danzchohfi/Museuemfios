{# MUSEU EM FIOS — o que vem no kit. Responde às duas objeções que mais
   aparecem: "vem tudo o que eu preciso?" e "e se eu travar no meio?".
   Cada item da lista é um block. #}

<section class="mf-kit" id="kit">
    <div class="mf-wrap">
        <div class="mf-kit__visual" data-reveal>
            <div class="mf-kit__fio" data-fio></div>
            {% if section.settings.imagem %}
                <img src="{{ section.settings.imagem }}" alt="{{ section.settings.imagem_alt }}" loading="lazy">
            {% endif %}
        </div>
        <div>
            {% if section.settings.eyebrow %}
                <p class="mf-eyebrow" data-reveal>{{ section.settings.eyebrow }}</p>
            {% endif %}
            {% if section.settings.titulo %}
                <h2 class="mf-h2" data-reveal>{{ section.settings.titulo | raw }}</h2>
            {% endif %}
            {% if section.blocks | length > 0 %}
                <ul class="mf-kit__lista" data-reveal="grupo">
                    {% for block in section.blocks %}
                        {% include 'blocks/museu-item-kit.tpl' with { block: block, numero: loop.index } %}
                    {% endfor %}
                </ul>
            {% endif %}
            {% if section.settings.nota %}
                <div class="mf-kit__nota" data-reveal>{{ section.settings.nota | raw }}</div>
            {% endif %}
            {% if section.settings.link %}
                <a class="mf-btn" href="{{ section.settings.link }}" data-reveal>{{ section.settings.link_texto }}</a>
            {% endif %}
        </div>
    </div>
</section>

{% schema %}
{
  "name": "t:names.museu_kit",
  "class": "mf-secao-kit",
  "max_blocks": 10,
  "blocks": [
    { "type": "museu-item-kit" }
  ],
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "eyebrow",
      "label": "t:settings.museu_eyebrow",
      "default": "t:defaults.museu_o_que_vem"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "titulo",
      "label": "t:settings.museu_titulo"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "nota",
      "label": "t:settings.museu_nota"
    },
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
    { "type": "header", "content": "t:names.museu_chamada" },
    {
      "type": "setting",
      "setting_type": "url",
      "id": "link",
      "label": "t:settings.museu_link"
    },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "link_texto",
      "label": "t:settings.museu_link_texto",
      "default": "t:defaults.museu_escolher_kit"
    }
  ],
  "presets": [
    {
      "name": "t:names.museu_kit",
      "category": "t:categories.museu",
      "settings": {
        "eyebrow": "t:defaults.museu_o_que_vem",
        "link_texto": "t:defaults.museu_escolher_kit"
      }
    }
  ]
}
{% endschema %}
