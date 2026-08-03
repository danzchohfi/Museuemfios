{# MUSEU EM FIOS — uma frase da faixa marquee (endline, frete, cupom…). #}

<span {{ block | block_attributes }}>{{ block.settings.texto }}</span>

{% schema %}
{
  "name": "t:names.museu_frase",
  "settings": [
    {
      "type": "setting",
      "setting_type": "text",
      "id": "texto",
      "label": "t:settings.museu_frase_texto",
      "default": "t:defaults.museu_endline"
    }
  ],
  "presets": [
    {
      "name": "t:names.museu_frase",
      "category": "t:categories.museu",
      "settings": { "texto": "t:defaults.museu_endline" }
    }
  ]
}
{% endschema %}
