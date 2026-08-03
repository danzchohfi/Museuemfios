{# MUSEU EM FIOS — a experiência, nas sub-mensagens da Direção de Marca
   (Autoria · Ritual · Curadoria · Certificado). Cada passo é um block, então a
   cliente pode reescrever, reordenar ou acrescentar um quinto. #}

<section class="mf-passos">
    <div class="mf-wrap">
        {% if section.settings.eyebrow %}
            <p class="mf-eyebrow" data-reveal>{{ section.settings.eyebrow }}</p>
        {% endif %}
        {% if section.settings.titulo %}
            <h2 class="mf-h2" data-reveal>{{ section.settings.titulo | raw }}</h2>
        {% endif %}
        {% if section.blocks | length > 0 %}
            <div class="mf-passos__grade" data-reveal="grupo">
                {% for block in section.blocks %}
                    {% include 'blocks/museu-passo.tpl' with { block: block, numero: loop.index } %}
                {% endfor %}
            </div>
        {% endif %}
    </div>
</section>

{% schema %}
{
  "name": "t:names.museu_passos",
  "class": "mf-secao-passos",
  "max_blocks": 6,
  "blocks": [
    { "type": "museu-passo" }
  ],
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "eyebrow",
      "label": "t:settings.museu_eyebrow",
      "default": "t:defaults.museu_experiencia"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "titulo",
      "label": "t:settings.museu_titulo"
    }
  ],
  "presets": [
    {
      "name": "t:names.museu_passos",
      "category": "t:categories.museu",
      "settings": { "eyebrow": "t:defaults.museu_experiencia" }
    }
  ]
}
{% endschema %}
