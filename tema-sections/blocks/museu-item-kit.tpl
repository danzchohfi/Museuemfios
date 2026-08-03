{# MUSEU EM FIOS — um item da lista do kit. A numeração acompanha a ordem. #}

<li {{ block | block_attributes }}>
    <span class="num">{{ '%02d' | format(numero) }}</span> {{ block.settings.texto }}
</li>

{% schema %}
{
  "name": "t:names.museu_item_kit",
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "texto",
      "label": "t:settings.museu_texto"
    }
  ],
  "presets": [
    {
      "name": "t:names.museu_item_kit",
      "category": "t:categories.museu"
    }
  ]
}
{% endschema %}
