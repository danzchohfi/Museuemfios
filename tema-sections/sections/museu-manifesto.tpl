{# MUSEU EM FIOS — endline + posicionamento público (Direção de Marca).
   Bloco de texto: a frase em serifada grande e o apoio alinhado à direita. #}

<section class="mf-manifesto">
    <div class="mf-manifesto__fio" data-fio></div>
    <div class="mf-wrap">
        {% if section.settings.eyebrow %}
            <p class="mf-eyebrow" data-reveal>{{ section.settings.eyebrow }}</p>
        {% endif %}
        <p class="mf-manifesto__frase mf-serif">{{ section.settings.frase }}</p>
        <div class="mf-manifesto__apoio" data-reveal>
            {{ section.settings.apoio | raw }}
            {% if section.settings.link %}
                <p><a class="mf-link" href="{{ section.settings.link }}">{{ section.settings.link_texto }}</a></p>
            {% endif %}
        </div>
    </div>
</section>

{% schema %}
{
  "name": "t:names.museu_manifesto",
  "class": "mf-secao-manifesto",
  "limit": 1,
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "eyebrow",
      "label": "t:settings.museu_eyebrow",
      "default": "t:defaults.museu_marca"
    },
    {
      "type": "setting",
      "setting_type": "text",
      "id": "frase",
      "label": "t:settings.museu_frase_manifesto",
      "default": "t:defaults.museu_endline"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "apoio",
      "label": "t:settings.museu_apoio"
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
      "default": "t:defaults.museu_conheca"
    }
  ],
  "enabled_on": {
    "page_templates": ["home"]
  },
  "presets": [
    {
      "name": "t:names.museu_manifesto",
      "category": "t:categories.museu",
      "settings": {
        "eyebrow": "t:defaults.museu_marca",
        "frase": "t:defaults.museu_endline",
        "link_texto": "t:defaults.museu_conheca"
      }
    }
  ]
}
{% endschema %}
