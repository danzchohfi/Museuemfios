{# MUSEU EM FIOS — hero editorial da home.

   No tema legado os 3 destaques eram markup fixo no .tpl. Aqui cada obra é um
   BLOCK: a cliente adiciona, remove e reordena destaques pelo editor, sem
   pedir código pra gente.

   Copy conforme a Direção de Marca: descritor de categoria na 1ª dobra,
   a obra como protagonista, o convite "Você conhece esta obra?" e a ficha
   técnica de catálogo. #}

<section class="mf-hero" aria-label="{{ 'museu.hero.aria' | t }}">
    {% if section.settings.descritor %}
        <p class="mf-hero__descritor">{{ section.settings.descritor }}</p>
    {% endif %}

    {% for block in section.blocks %}
        {% include 'blocks/museu-obra.tpl' with { block: block, indice: loop.index0 } %}
    {% endfor %}

    {% if section.blocks | length > 1 %}
        <div class="mf-hero__nav" role="group" aria-label="{{ 'museu.hero.trocar' | t }}">
            {% for block in section.blocks %}
                <button class="mf-hero__dot{% if loop.first %} is-active{% endif %}"
                        aria-pressed="{{ loop.first ? 'true' : 'false' }}"
                        aria-label="{{ 'museu.hero.destaque' | t }} {{ loop.index }}"><span class="prog"></span></button>
            {% endfor %}
        </div>
    {% endif %}
</section>

{% schema %}
{
  "name": "t:names.museu_hero",
  "class": "mf-secao-hero",
  "limit": 1,
  "max_blocks": 6,
  "blocks": [
    { "type": "museu-obra" }
  ],
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "descritor",
      "label": "t:settings.museu_descritor",
      "default": "t:defaults.museu_descritor"
    }
  ],
  "enabled_on": {
    "page_templates": ["home"]
  },
  "presets": [
    {
      "name": "t:names.museu_hero",
      "category": "t:categories.museu",
      "settings": {
        "descritor": "t:defaults.museu_descritor"
      }
    }
  ]
}
{% endschema %}
