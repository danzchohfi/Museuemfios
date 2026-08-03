{# MUSEU EM FIOS — um passo da experiência. A numeração (01, 02…) vem da
   posição no laço, então reordenar no editor renumera sozinho. #}

<article class="mf-passo" {{ block | block_attributes }}>
    <p class="mf-passo__num">{{ '%02d' | format(numero) }}</p>
    {% if block.settings.titulo %}<h3>{{ block.settings.titulo }}</h3>{% endif %}
    {{ block.settings.texto | raw }}
</article>

{% schema %}
{
  "name": "t:names.museu_passo",
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "titulo",
      "label": "t:settings.museu_titulo"
    },
    {
      "type": "setting",
      "setting_type": "richtext",
      "id": "texto",
      "label": "t:settings.museu_texto"
    }
  ],
  "presets": [
    {
      "name": "t:names.museu_passo",
      "category": "t:categories.museu"
    }
  ]
}
{% endschema %}
